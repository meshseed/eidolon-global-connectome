#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
"""
merge_and_backfill.py — Merge old wave spores into the global connectome + backfill missing fields.

What this script does (one pass):
  1. Copies old spores from SOURCE_DIR into the connectome wave-spores/ folder
     (skips any with duplicate IDs — no overwrites)
  2. Loads ALL spores (old + new combined)
  3. Computes shimmer sub-scores (S1, S2b, S3, S5, composite) for spores missing them
     — uses the combined neighborhood so all scores are in the same reference frame
  4. Regenerates the delta-basis from the full combined corpus (new barycenter + eigenvectors)
  5. Writes delta_tier1 (32 int16) and delta_tier3 (130 int16) back to ALL spore JSON files
     (since the delta-basis changes when corpus grows, both old AND new need updating)
  6. Prints a summary

Run after this:
  python regenerate-indexes.py   (from the connectome repo root)

Then:
  git add -A && git commit -m "🌊 Merge 2,831 old spores + backfill shimmer/delta fields"
  git push origin main

Usage:
  python analysis/merge_and_backfill.py [--dry-run]

  --dry-run  Print counts and plan without copying or writing anything.
"""

import argparse
import json
import os
import shutil
import sys
import hashlib
from collections import defaultdict
from pathlib import Path

import numpy as np

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

# Adjust these paths if your layout is different
REPO_ROOT = Path(__file__).parent.parent
DEST_DIR = REPO_ROOT / "wave-spores"
SEED_DIR = REPO_ROOT / "seeds"

# Old spores to merge in
SOURCE_DIR = Path(r"C:\EIDOLON\Github\eidolon\data\wave-spores")

# k-NN settings for shimmer computation
K_S5 = 20    # neighbours for S5 (tag/topology mismatch)
K_S1 = 10    # neighbours for S1/S2b (topological surprise / coherence peak)

# Shimmer S3 tag co-occurrence settings
MIN_TAG_PAIR_COUNT = 2   # ignore pairs that appear only once (noise)

# Delta encoding tiers
TIER1_K = 32
TIER3_K = 130
QUANT_SCALE = 10000      # ×10000 → int16

# System tag prefixes excluded from shimmer semantic tag computation
SYSTEM_TAG_PREFIXES = (
    "#embed:", "#dna:", "#synthesis:", "#source:", "#calibration",
    "#public", "#tier:", "#P-series", "#golden_connectome",
    "#calibration_anchor", "#invariance",
)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def is_semantic_tag(tag: str) -> bool:
    for prefix in SYSTEM_TAG_PREFIXES:
        if tag.startswith(prefix) or tag == prefix:
            return False
    return True


def semantic_tags(spore: dict) -> set:
    return {t for t in spore.get("tags", []) if is_semantic_tag(t)}


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def minmax_normalize(arr: np.ndarray) -> np.ndarray:
    mn, mx = arr.min(), arr.max()
    if mx - mn < 1e-15:
        return np.zeros_like(arr)
    return (arr - mn) / (mx - mn)


# ─────────────────────────────────────────────
# Load spores
# ─────────────────────────────────────────────

def load_all_spores() -> list[dict]:
    """Load all spores from DEST_DIR and SEED_DIR (deduped by id)."""
    seen = {}
    spores = []
    for d in [DEST_DIR, SEED_DIR]:
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if "amplitudes" not in data:
                    continue
                sid = data.get("id", f.stem)
                if sid not in seen:
                    seen[sid] = True
                    data["_path"] = str(f)   # remember where this file lives
                    spores.append(data)
            except Exception:
                pass
    return spores


# ─────────────────────────────────────────────
# Step 1: Copy old spores
# ─────────────────────────────────────────────

def copy_old_spores(dry_run: bool) -> tuple[int, int]:
    """Copy spores from SOURCE_DIR → DEST_DIR. Returns (copied, skipped)."""
    if not SOURCE_DIR.exists():
        print(f"  ⚠️  SOURCE_DIR not found: {SOURCE_DIR}")
        return 0, 0

    existing = {f.stem for f in DEST_DIR.glob("*.json")}
    source_files = list(SOURCE_DIR.glob("*.json"))

    copied = 0
    skipped = 0
    for f in source_files:
        if f.stem in existing:
            skipped += 1
        else:
            if not dry_run:
                shutil.copy2(f, DEST_DIR / f.name)
            copied += 1

    return copied, skipped


# ─────────────────────────────────────────────
# Step 2: Compute shimmer sub-scores
# ─────────────────────────────────────────────

def compute_shimmer(spores: list[dict]) -> dict[str, dict]:
    """
    Compute S1, S2b, S3, S5, shimmer_composite for all spores.
    Returns dict[id] → {shimmer_s1, shimmer_s2b, shimmer_s3, shimmer_s5, shimmer_composite}.
    Uses combined neighborhood (all spores together).
    """
    n = len(spores)
    ids = [s["id"] for s in spores]
    amps = np.array([s["amplitudes"] for s in spores], dtype=np.float64)
    cohs = np.array([s.get("coherence_score", 0.95) for s in spores])
    tags = [semantic_tags(s) for s in spores]

    # Pairwise cosine similarity (chunked to avoid OOM on large N)
    print(f"  Computing {n}×{n} cosine similarity matrix...")
    # Normalize rows
    norms = np.linalg.norm(amps, axis=1, keepdims=True)
    norms[norms < 1e-12] = 1e-12
    amps_norm = amps / norms
    # Chunked matmul
    chunk = 256
    sim_matrix = np.zeros((n, n), dtype=np.float32)
    for i in range(0, n, chunk):
        end = min(i + chunk, n)
        sim_matrix[i:end] = (amps_norm[i:end] @ amps_norm.T).astype(np.float32)
    np.fill_diagonal(sim_matrix, -1.0)   # exclude self
    print("  ✓ Similarity matrix done")

    # ── S1: Topological Surprise ──────────────────────────────
    centroid = amps_norm.mean(axis=0)
    centroid /= (np.linalg.norm(centroid) + 1e-12)
    dist_from_centroid = 1.0 - (amps_norm @ centroid)   # cosine distance
    max_dist = dist_from_centroid.max() + 1e-12
    s1_raw = cohs * (dist_from_centroid / max_dist)

    # ── S2b: Local Coherence Peak ─────────────────────────────
    top_k_idx = np.argsort(-sim_matrix, axis=1)[:, :K_S1]
    s2b_raw = np.zeros(n)
    for i in range(n):
        nbr_idx = top_k_idx[i]
        mean_nbr_coh = cohs[nbr_idx].mean()
        mean_nbr_dist = (1.0 - sim_matrix[i, nbr_idx]).mean()
        excess = max(0.0, cohs[i] - mean_nbr_coh)
        s2b_raw[i] = excess * (1.0 / (mean_nbr_dist + 1e-8))

    # ── S3: Semantic Bridging (tag co-occurrence rarity) ──────
    pair_counts: dict[tuple, int] = defaultdict(int)
    for tag_set in tags:
        tag_list = sorted(tag_set)
        for a in range(len(tag_list)):
            for b in range(a + 1, len(tag_list)):
                pair_counts[(tag_list[a], tag_list[b])] += 1

    s3_raw = np.zeros(n)
    for i, tag_set in enumerate(tags):
        tag_list = sorted(tag_set)
        if len(tag_list) < 2:
            s3_raw[i] = 0.0
            continue
        pair_scores = []
        for a in range(len(tag_list)):
            for b in range(a + 1, len(tag_list)):
                cnt = pair_counts[(tag_list[a], tag_list[b])]
                if cnt >= MIN_TAG_PAIR_COUNT:
                    pair_scores.append(1.0 / cnt)
        if pair_scores:
            s3_raw[i] = cohs[i] * np.mean(pair_scores)

    # ── S5: Phase Boundary Detection (tag/topology mismatch) ──
    top_k5_idx = np.argsort(-sim_matrix, axis=1)[:, :K_S5]
    s5_raw = np.zeros(n)
    for i in range(n):
        nbr_idx = top_k5_idx[i]
        if len(tags[i]) == 0:
            s5_raw[i] = 0.0
            continue
        overlaps = []
        for j in nbr_idx:
            if len(tags[i]) == 0 and len(tags[j]) == 0:
                overlaps.append(1.0)
            elif len(tags[i]) == 0 or len(tags[j]) == 0:
                overlaps.append(0.0)
            else:
                inter = len(tags[i] & tags[j])
                union = len(tags[i] | tags[j])
                overlaps.append(inter / union if union > 0 else 0.0)
        s5_raw[i] = cohs[i] * (1.0 - np.mean(overlaps))

    # ── Composite (arithmetic mean of normalized sub-scores) ──
    s1_n = minmax_normalize(s1_raw)
    s2b_n = minmax_normalize(s2b_raw)
    s3_n = minmax_normalize(s3_raw)
    s5_n = minmax_normalize(s5_raw)
    composite = (s1_n + s2b_n + s3_n + s5_n) / 4.0

    results = {}
    for i, sid in enumerate(ids):
        results[sid] = {
            "shimmer_s1": round(float(s1_raw[i]), 4),
            "shimmer_s2b": round(float(s2b_raw[i]), 4),
            "shimmer_s3": round(float(s3_raw[i]), 4),
            "shimmer_s5": round(float(s5_raw[i]), 4),
            "shimmer_composite": round(float(composite[i]), 4),
        }
    return results


# ─────────────────────────────────────────────
# Step 3: Delta basis + per-spore delta fields
# ─────────────────────────────────────────────

def compute_delta_basis(spores: list[dict]) -> tuple[np.ndarray, np.ndarray, str]:
    """Compute barycenter + eigenvectors from all spore amplitudes.
    Returns (barycenter, eigenvectors[200, TIER3_K], basis_hash)."""
    amps = np.array([s["amplitudes"] for s in spores], dtype=np.float64)
    barycenter = np.mean(amps, axis=0)
    deltas = amps - barycenter
    cov = np.cov(deltas.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvectors = eigenvectors[:, idx][:, :TIER3_K]   # (200, TIER3_K)

    basis_bytes = barycenter.tobytes() + eigenvectors.tobytes()
    basis_hash = hashlib.sha256(basis_bytes).hexdigest()[:16]
    return barycenter, eigenvectors, basis_hash


def encode_delta(amp: np.ndarray, barycenter: np.ndarray, evecs: np.ndarray, k: int) -> list[int]:
    """Project amplitude onto delta-PCA space, quantize to int16."""
    delta = amp - barycenter
    coeffs = delta @ evecs[:, :k]   # (k,)
    quantized = np.round(coeffs * QUANT_SCALE).clip(-32768, 32767).astype(np.int16)
    return [int(x) for x in quantized]


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Merge old wave spores + backfill fields")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without writing anything")
    parser.add_argument("--skip-shimmer", action="store_true",
                        help="Skip shimmer recomputation (faster; shimmer scores may be stale)")
    args = parser.parse_args()
    dry_run = args.dry_run

    print("=" * 70)
    print("MERGE + BACKFILL — Eidolon Global Connectome")
    print("=" * 70)
    if dry_run:
        print("  *** DRY RUN — no files will be written ***")
    print()

    # ── Step 1: Copy old spores ───────────────────────────────
    print("STEP 1: Copy old spores")
    print(f"  Source: {SOURCE_DIR}")
    print(f"  Dest:   {DEST_DIR}")
    copied, skipped = copy_old_spores(dry_run)
    print(f"  Copied: {copied}  |  Skipped (already exist): {skipped}")
    print()

    if dry_run:
        # Just show what would happen
        existing_count = len(list(DEST_DIR.glob("*.json")))
        print(f"  After merge: ~{existing_count + copied} spores total")
        print("\nDry run complete. Remove --dry-run to execute.")
        return

    # ── Step 2: Load all spores ───────────────────────────────
    print("STEP 2: Load all spores")
    spores = load_all_spores()
    print(f"  Loaded: {len(spores)} spores")
    missing_shimmer = [s for s in spores if "shimmer_s1" not in s]
    print(f"  Missing shimmer sub-scores: {len(missing_shimmer)}")
    print()

    # ── Step 3: Compute shimmer ───────────────────────────────
    shimmer_results = {}
    if not args.skip_shimmer:
        print("STEP 3: Compute shimmer sub-scores (S1/S2b/S3/S5/composite)")
        print("  (This uses all spores together for consistent neighborhood)")
        shimmer_results = compute_shimmer(spores)
        print(f"  ✓ Computed for {len(shimmer_results)} spores")
    else:
        print("STEP 3: Shimmer computation skipped (--skip-shimmer)")
    print()

    # ── Step 4: Compute delta basis ───────────────────────────
    print("STEP 4: Compute delta basis from full corpus")
    barycenter, evecs, basis_hash = compute_delta_basis(spores)
    print(f"  New delta-basis hash: {basis_hash}")
    print(f"  Tier 1: {TIER1_K} modes  |  Tier 3: {TIER3_K} modes")
    print()

    # ── Step 5: Write updated fields to all spore files ───────
    print("STEP 5: Write shimmer + delta fields back to spore files")
    updated = 0
    errors = 0
    for spore in spores:
        path = spore.get("_path")
        if not path:
            continue
        try:
            # Re-read to get clean version (avoid stale in-memory _path key)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            changed = False

            # Shimmer sub-scores
            if shimmer_results:
                scores = shimmer_results.get(data.get("id", ""), {})
                if scores:
                    for field, val in scores.items():
                        if data.get(field) != val:
                            data[field] = val
                            changed = True

            # Delta fields — always update since basis changed
            amp = np.array(data["amplitudes"], dtype=np.float64)
            t1 = encode_delta(amp, barycenter, evecs, TIER1_K)
            t3 = encode_delta(amp, barycenter, evecs, TIER3_K)
            if data.get("delta_tier1") != t1:
                data["delta_tier1"] = t1
                changed = True
            if data.get("delta_tier3") != t3:
                data["delta_tier3"] = t3
                changed = True

            if changed:
                # Remove internal tracking key before writing
                data.pop("_path", None)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, separators=(",", ":"))
                updated += 1

        except Exception as e:
            print(f"    ⚠️  {path}: {e}")
            errors += 1

    print(f"  ✓ Updated: {updated}  |  Errors: {errors}")
    print()

    # ── Step 6: Summary ────────────────────────────────────────
    total = len(list(DEST_DIR.glob("*.json"))) + len(list(SEED_DIR.glob("*.json")))
    print("=" * 70)
    print("MERGE + BACKFILL COMPLETE")
    print(f"  Total spores in connectome: {total}")
    print(f"  New delta-basis hash:       {basis_hash}")
    print()
    print("Next steps:")
    print("  1. cd to the connectome repo root")
    print("  2. python regenerate-indexes.py")
    print("  3. git add -A")
    print('  4. git commit -m "🌊 Merge 2,831 old spores + backfill shimmer/delta fields"')
    print("  5. git push origin main")
    print("=" * 70)


if __name__ == "__main__":
    main()

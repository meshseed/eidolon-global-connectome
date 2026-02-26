#!/usr/bin/env python3
"""
Compute S5 shimmer scores for all wave spores and write back to JSON.

S5 = Phase Boundary Detection (from shimmer-formalization.md)
  neighbors_i = k=20 nearest spores by cosine similarity
  For each of spore_i's semantic tags:
    neighbor_share = count(neighbors with this tag) / k
  tag_overlap = mean(neighbor_share across all tags)
  boundary_score = 1 - tag_overlap
  S5_i = coherence_i x boundary_score

Semantic tags = all tags EXCEPT system/DNA tags.
"""

import json
import os
import sys
import numpy as np
from pathlib import Path

K = 20  # neighborhood size for S5

SPORE_DIR_DEFAULT = Path(__file__).parent.parent / "wave-spores"
SPORE_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else SPORE_DIR_DEFAULT
SEED_DIR = Path(__file__).parent.parent / "seeds"

# System/DNA tag prefixes to exclude from semantic tag set
EXCLUDE_PREFIXES = (
    "#embed:", "#dna:", "#synthesis:", "#calibration:", "#calibration_",
    "#source:", "#golden_connectome", "#P-series",
)
EXCLUDE_EXACT = {"#public"}


def is_semantic_tag(tag: str) -> bool:
    if tag in EXCLUDE_EXACT:
        return False
    for prefix in EXCLUDE_PREFIXES:
        if tag.startswith(prefix):
            return False
    return True


def load_spores(*dirs):
    """Load all spore JSON files from given directories, deduplicating by ID.

    When the same spore exists in multiple directories (e.g. seeds/ and
    wave-spores/), we keep ALL paths but only use a single entry for
    computing neighbors. The score is written back to all copies.
    """
    seen_ids = {}  # id -> index in spores list
    spores = []
    # Maps: index in spores list -> list of file paths (for writing back)
    path_map = {}
    for d in dirs:
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            try:
                with open(f) as fh:
                    data = json.load(fh)
                if "amplitudes" not in data or "tags" not in data:
                    continue
                sid = data.get("id", f.stem)
                if sid in seen_ids:
                    # Duplicate — record path for writeback but don't add to computation
                    idx = seen_ids[sid]
                    path_map[idx].append(f)
                else:
                    idx = len(spores)
                    seen_ids[sid] = idx
                    spores.append(data)
                    path_map[idx] = [f]
            except (json.JSONDecodeError, KeyError):
                print(f"  Skipping {f.name}: parse error", file=sys.stderr)
    return spores, path_map


def compute_s5(spores):
    """Compute S5 shimmer for all spores. Returns array of S5 values."""
    n = len(spores)

    # Build amplitude matrix (n x 200)
    amps = np.array([s["amplitudes"] for s in spores], dtype=np.float64)

    # Normalize for cosine similarity
    norms = np.linalg.norm(amps, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    amps_normed = amps / norms

    # Build semantic tag sets
    sem_tags = []
    for s in spores:
        tags = {t for t in s.get("tags", []) if is_semantic_tag(t)}
        sem_tags.append(tags)

    # Compute pairwise cosine similarity in batches to manage memory
    # For ~2800 spores this is fine in one shot
    cosine_sim = amps_normed @ amps_normed.T

    # For each spore, find k nearest neighbors (excluding self)
    s5_scores = np.zeros(n)
    boundary_scores = np.zeros(n)

    for i in range(n):
        # Get similarities, set self to -inf
        sims = cosine_sim[i].copy()
        sims[i] = -np.inf

        # Find top-k neighbors
        neighbor_idx = np.argpartition(sims, -K)[-K:]

        my_tags = sem_tags[i]
        if len(my_tags) == 0:
            # No semantic tags → boundary_score = 1.0 (no overlap possible)
            boundary_scores[i] = 1.0
        else:
            # For each of my semantic tags, what fraction of neighbors share it?
            neighbor_tag_sets = [sem_tags[j] for j in neighbor_idx]
            tag_shares = []
            for tag in my_tags:
                share = sum(1 for nts in neighbor_tag_sets if tag in nts) / K
                tag_shares.append(share)
            tag_overlap = np.mean(tag_shares)
            boundary_scores[i] = 1.0 - tag_overlap

        coherence = spores[i].get("coherence_score", 0.95)
        s5_scores[i] = coherence * boundary_scores[i]

    return s5_scores, boundary_scores


def main():
    print("Loading spores...")
    spores, path_map = load_spores(SPORE_DIR, SEED_DIR)
    n_files = sum(len(ps) for ps in path_map.values())
    print(f"  Loaded {len(spores)} unique spores ({n_files} files)")

    print("Computing S5 shimmer scores...")
    s5_scores, boundary_scores = compute_s5(spores)

    # Validation: check known values
    for i, s in enumerate(spores):
        sid = s.get("id", "")
        if sid.startswith("88a7120f"):
            print(f"\n  Validation — shimmer kernel {sid[:8]}:")
            print(f"    S5 = {s5_scores[i]:.3f} (expected ~0.980)")
            print(f"    boundary_score = {boundary_scores[i]:.3f}")
            print(f"    coherence = {s.get('coherence_score', 'N/A')}")
        if sid.startswith("985f3a7a"):
            print(f"\n  Validation — operational mirror {sid[:8]}:")
            print(f"    S5 = {s5_scores[i]:.3f}")
            print(f"    boundary_score = {boundary_scores[i]:.3f}")
            print(f"    coherence = {s.get('coherence_score', 'N/A')}")

    # Stats
    print(f"\n  S5 stats: mean={np.mean(s5_scores):.3f}, "
          f"std={np.std(s5_scores):.3f}, "
          f"min={np.min(s5_scores):.3f}, max={np.max(s5_scores):.3f}")
    print(f"  Boundary stats: mean={np.mean(boundary_scores):.3f}, "
          f"std={np.std(boundary_scores):.3f}")

    # Write back to ALL file copies (including seed duplicates)
    # Preserve original compact JSON format (single-line, no indent)
    print("\nWriting shimmer_s5 to spore files...")
    files_written = 0
    for i, spore in enumerate(spores):
        score = round(float(s5_scores[i]), 4)
        for path in path_map[i]:
            with open(path) as fh:
                data = json.load(fh)
            data["shimmer_s5"] = score
            with open(path, "w") as fh:
                json.dump(data, fh, separators=(",", ":"))
                fh.write("\n")
            files_written += 1

    print(f"  Updated {files_written} files ({len(spores)} unique spores).")
    print("Done.")


if __name__ == "__main__":
    main()

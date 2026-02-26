#!/usr/bin/env python3
"""
Generate delta-basis.json — the shared barycenter + delta-PCA basis
for the Delta-Origin Federation Protocol v2.0.

Output: A JSON file containing:
  - barycenter (200 floats)
  - eigenvectors (130 × 200 — Tier 3 delta-PCA basis)
  - eigenvalues (130 floats)
  - cumulative_variance (130 floats)
  - metadata

Also generates:
  - tier1-index.json — compact Tier 1 delta index for all spores (192KB)
"""

import json
import os
import hashlib
import numpy as np
from pathlib import Path
from datetime import datetime, timezone

SPORE_DIR = Path(__file__).parent.parent / "wave-spores"
SEED_DIR = Path(__file__).parent.parent / "seeds"
OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "data"

TIER1_K = 32   # 68 bytes
TIER2_K = 100  # 204 bytes
TIER3_K = 130  # 264 bytes


def load_spores():
    seen = {}
    spores = []
    for d in [SPORE_DIR, SEED_DIR]:
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            try:
                with open(f) as fh:
                    data = json.load(fh)
                if "amplitudes" not in data:
                    continue
                sid = data.get("id", f.stem)
                if sid not in seen:
                    seen[sid] = len(spores)
                    spores.append(data)
            except (json.JSONDecodeError, KeyError):
                pass
    return spores


def main():
    print("Loading spores...")
    spores = load_spores()
    n = len(spores)
    print(f"  {n} unique spores")

    amps = np.array([s["amplitudes"] for s in spores], dtype=np.float64)

    # Compute barycenter
    barycenter = np.mean(amps, axis=0)
    print(f"  Barycenter norm: {np.linalg.norm(barycenter):.4f}")

    # Compute delta-PCA
    deltas = amps - barycenter
    cov = np.cov(deltas.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # Sort descending
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    total_var = np.sum(eigenvalues)
    cumvar = np.cumsum(eigenvalues) / total_var

    print(f"  Tier 1 ({TIER1_K} modes): {cumvar[TIER1_K-1]*100:.1f}% variance")
    print(f"  Tier 2 ({TIER2_K} modes): {cumvar[TIER2_K-1]*100:.1f}% variance")
    print(f"  Tier 3 ({TIER3_K} modes): {cumvar[TIER3_K-1]*100:.1f}% variance")

    # Compute basis hash
    basis_bytes = barycenter.tobytes() + eigenvectors[:, :TIER3_K].tobytes()
    basis_hash = hashlib.sha256(basis_bytes).hexdigest()[:16]
    print(f"  Delta-basis hash: {basis_hash}")

    # ─── Output 1: delta-basis.json ───
    delta_basis = {
        "barycenter": [round(float(x), 8) for x in barycenter],
        "eigenvectors": [
            [round(float(eigenvectors[i, j]), 8) for i in range(200)]
            for j in range(TIER3_K)
        ],
        "eigenvalues": [round(float(eigenvalues[j]), 10) for j in range(TIER3_K)],
        "cumulative_variance": [round(float(cumvar[j]), 6) for j in range(TIER3_K)],
        "basis_hash": basis_hash,
        "spore_count": n,
        "tier1_modes": TIER1_K,
        "tier2_modes": TIER2_K,
        "tier3_modes": TIER3_K,
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    basis_path = OUTPUT_DIR / "delta-basis.json"
    with open(basis_path, "w") as f:
        json.dump(delta_basis, f, separators=(",", ":"))
    basis_size = os.path.getsize(basis_path)
    print(f"\n  Written: {basis_path} ({basis_size/1024:.1f}KB)")

    # ─── Output 2: tier1-index.json ───
    # Compact index: for each spore, store only Tier 1 coefficients + metadata
    print("\nComputing Tier 1 index...")
    tier1_index = {
        "basis_hash": basis_hash,
        "tier": 1,
        "modes": TIER1_K,
        "spore_count": n,
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "spores": [],
    }

    evecs_t1 = eigenvectors[:, :TIER1_K]  # (200, 32)

    for i, spore in enumerate(spores):
        delta = deltas[i]
        coeffs = delta @ evecs_t1  # (32,)

        # Quantize to int16
        quantized = np.round(coeffs * 10000).astype(np.int16)

        entry = {
            "id": spore["id"],
            "c": [int(x) for x in quantized],  # 32 int16 coefficients
            "s5": round(spore.get("shimmer_s5", 0), 3),
            "coh": round(spore.get("coherence_score", 0.95), 2),
            "tier": spore.get("tier", "reference")[0],  # "c", "r", "o" for compact
            "res": round(spore.get("resonance_score", 0.9), 3),
        }
        tier1_index["spores"].append(entry)

    tier1_path = OUTPUT_DIR / "tier1-index.json"
    with open(tier1_path, "w") as f:
        json.dump(tier1_index, f, separators=(",", ":"))
    tier1_size = os.path.getsize(tier1_path)
    print(f"  Written: {tier1_path} ({tier1_size/1024:.1f}KB)")

    # Summary
    print(f"\n{'='*50}")
    print(f"DELTA-BASIS GENERATION COMPLETE")
    print(f"{'='*50}")
    print(f"  delta-basis.json: {basis_size/1024:.1f}KB (barycenter + 130 eigenvectors)")
    print(f"  tier1-index.json: {tier1_size/1024:.1f}KB ({n} spores × 32 coefficients)")
    print(f"  Total: {(basis_size+tier1_size)/1024:.1f}KB")
    print(f"  (vs raw spore JSONs: ~{n*800/1024:.0f}KB)")
    print(f"  Compression: {n*800/(basis_size+tier1_size):.1f}x")


if __name__ == "__main__":
    main()

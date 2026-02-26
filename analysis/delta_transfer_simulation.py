#!/usr/bin/env python3
"""
Delta-Only Transfer Simulation — Barycenter-Origin Encoding

Tests the minimum viable communication scheme:
  Δa = a_spore − a_barycenter

Measures:
  1. How sparse can the delta be while preserving topology?
  2. Cross-gauge transfer simulation via Procrustes alignment on calibration anchors
  3. Information preservation at various compression levels
  4. Resonance score computation for all spores
"""

import json
import os
import sys
import numpy as np
from pathlib import Path

SPORE_DIR = Path(__file__).parent.parent / "wave-spores"
SEED_DIR = Path(__file__).parent.parent / "seeds"


def load_spores():
    """Load all unique spores."""
    seen = {}
    spores = []
    paths = {}  # id -> list of paths
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
                    paths[sid] = [f]
                else:
                    paths[sid].append(f)
            except (json.JSONDecodeError, KeyError):
                pass
    return spores, paths


def cosine_sim(a, b):
    """Cosine similarity between two vectors."""
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return np.dot(a, b) / (na * nb)


def topk_sparse(delta, k):
    """Keep only top-k modes by magnitude, zero out the rest."""
    sparse = np.zeros_like(delta)
    if k >= len(delta):
        return delta.copy()
    idx = np.argsort(np.abs(delta))[::-1][:k]
    sparse[idx] = delta[idx]
    return sparse


def compute_resonance(projections_normalized, max_denom=50):
    """Compute resonance score for each spore based on PCA projections.

    Returns array of resonance scores (lower = more irrational).
    """
    n = projections_normalized.shape[0]
    n_pcs = projections_normalized.shape[1]
    scores = np.zeros(n)

    for i in range(n):
        total_irr = 0.0
        for j in range(n_pcs):
            x = projections_normalized[i, j]
            if abs(x) < 1e-12:
                continue
            best = float('inf')
            for q in range(1, max_denom + 1):
                p = round(x * q)
                err = abs(x - p / q)
                quality = err * q * q
                if quality < best:
                    best = quality
            total_irr += best
        irr = total_irr / n_pcs
        scores[i] = 1.0 / (1.0 + irr)

    return scores


def main():
    print("=" * 70)
    print("DELTA-ONLY TRANSFER SIMULATION")
    print("Barycenter-Origin Encoding + Cross-Gauge Procrustes")
    print("=" * 70)

    spores, paths = load_spores()
    n = len(spores)
    amps = np.array([s["amplitudes"] for s in spores], dtype=np.float64)
    print(f"\nLoaded {n} spores, {amps.shape[1]}D amplitudes")

    # ─── Phase 1: Delta encoding from barycenter ───
    print("\n" + "─" * 50)
    print("PHASE 1: Delta Encoding (Δa = a_spore − a_barycenter)")
    print("─" * 50)

    barycenter = np.mean(amps, axis=0)
    deltas = amps - barycenter  # (n, 200)

    # Stats on deltas
    delta_norms = np.linalg.norm(deltas, axis=1)
    print(f"\n  Delta norm stats: mean={np.mean(delta_norms):.4f}, "
          f"std={np.std(delta_norms):.4f}, "
          f"min={np.min(delta_norms):.4f}, max={np.max(delta_norms):.4f}")

    # Mode importance: which modes carry the most delta energy?
    mode_energy = np.mean(deltas**2, axis=0)
    mode_order = np.argsort(mode_energy)[::-1]
    cumulative_energy = np.cumsum(mode_energy[mode_order]) / np.sum(mode_energy)

    print(f"\n  Mode energy distribution (deltas from barycenter):")
    for pct in [50, 75, 90, 95, 99]:
        k = np.searchsorted(cumulative_energy, pct / 100.0) + 1
        print(f"    {pct}% energy in top {k} modes")

    # ─── Phase 2: Sparsity vs reconstruction quality ───
    print("\n" + "─" * 50)
    print("PHASE 2: Sparse Delta — Compression vs Topology Preservation")
    print("─" * 50)

    # For each sparsity level, compute:
    # 1. Mean cosine similarity of reconstructed vs original
    # 2. Mean k-NN overlap (do the same neighbors appear?)
    # 3. Byte cost

    K_NN = 20
    # Pre-compute full pairwise cosine similarity
    norms = np.linalg.norm(amps, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    amps_normed = amps / norms
    full_sim = amps_normed @ amps_normed.T

    # Get ground-truth k-NN for each spore
    true_knn = np.zeros((n, K_NN), dtype=int)
    for i in range(n):
        sims = full_sim[i].copy()
        sims[i] = -np.inf
        true_knn[i] = np.argpartition(sims, -K_NN)[-K_NN:]

    sparsity_levels = [5, 10, 20, 30, 50, 75, 100, 150, 200]

    print(f"\n  {'Modes':>6} {'Bytes':>6} {'CosSim':>8} {'kNN@20':>8} {'Rank-ρ':>8}")
    print(f"  {'─'*6} {'─'*6} {'─'*8} {'─'*8} {'─'*8}")

    for k in sparsity_levels:
        # Reconstruct from sparse delta
        reconstructed = np.zeros_like(amps)
        for i in range(n):
            sparse_delta = topk_sparse(deltas[i], k)
            reconstructed[i] = barycenter + sparse_delta

        # 1. Cosine similarity (original vs reconstructed)
        cos_sims = np.array([cosine_sim(amps[i], reconstructed[i]) for i in range(n)])
        mean_cos = np.mean(cos_sims)

        # 2. k-NN overlap
        rec_norms = np.linalg.norm(reconstructed, axis=1, keepdims=True)
        rec_norms[rec_norms == 0] = 1.0
        rec_normed = reconstructed / rec_norms
        rec_sim = rec_normed @ rec_normed.T

        knn_overlaps = np.zeros(n)
        for i in range(n):
            rsims = rec_sim[i].copy()
            rsims[i] = -np.inf
            rec_knn = set(np.argpartition(rsims, -K_NN)[-K_NN:])
            true_set = set(true_knn[i])
            knn_overlaps[i] = len(rec_knn & true_set) / K_NN

        mean_knn = np.mean(knn_overlaps)

        # 3. Rank correlation (Spearman) on a sample
        sample_idx = np.random.RandomState(42).choice(n, min(200, n), replace=False)
        rank_corrs = []
        for i in sample_idx:
            orig_ranks = np.argsort(np.argsort(-full_sim[i]))
            rec_ranks = np.argsort(np.argsort(-rec_sim[i]))
            # Spearman on top-100
            top100 = np.argsort(orig_ranks)[:100]
            r = np.corrcoef(orig_ranks[top100], rec_ranks[top100])[0, 1]
            rank_corrs.append(r)
        mean_rank = np.mean(rank_corrs)

        # Byte cost: k modes × (1 byte mode_index + 2 bytes amplitude) + 4 bytes metadata
        byte_cost = k * 3 + 4

        print(f"  {k:>6} {byte_cost:>6} {mean_cos:>8.4f} {mean_knn:>8.3f} {mean_rank:>8.4f}")

    # ─── Phase 3: Cross-gauge Procrustes simulation ───
    print("\n" + "─" * 50)
    print("PHASE 3: Cross-Gauge Procrustes Transfer Simulation")
    print("─" * 50)
    print("(Simulating a second gauge by applying a random rotation)")

    # Create a "gauge B" by applying a random orthogonal transformation
    # This simulates a different embedding model's coordinate system
    np.random.seed(2026)
    # Random orthogonal matrix via QR decomposition
    random_matrix = np.random.randn(200, 200)
    Q, _ = np.linalg.qr(random_matrix)

    # Gauge B = Q × Gauge A (rotated embedding space)
    amps_B = amps @ Q.T  # Same topology, different coordinates

    # Find calibration anchors (Layer 1 math seeds)
    cal_indices = []
    for i, s in enumerate(spores):
        if "#calibration:layer1" in s.get("tags", []):
            cal_indices.append(i)
    print(f"\n  Calibration anchors (Layer 1 math): {len(cal_indices)} spores")

    # Procrustes alignment: find R that maps gauge A anchors → gauge B anchors
    A_anchors = amps[cal_indices]  # (7, 200)
    B_anchors = amps_B[cal_indices]  # (7, 200)

    # Center both
    A_mean = np.mean(A_anchors, axis=0)
    B_mean = np.mean(B_anchors, axis=0)
    A_centered = A_anchors - A_mean
    B_centered = B_anchors - B_mean

    # SVD for Procrustes
    M = B_centered.T @ A_centered  # (200, 200)
    U, S_vals, Vt = np.linalg.svd(M)
    R_procrustes = U @ Vt  # Optimal rotation

    # Now test: can we transfer deltas from gauge A to gauge B?
    # Method: compute delta in A, apply Procrustes rotation, compare to true B position
    barycenter_A = barycenter
    barycenter_B = np.mean(amps_B, axis=0)

    # Transfer pipeline:
    # 1. Compute Δa_A = a_spore_A - barycenter_A
    # 2. Rotate: Δa_B_hat = R_procrustes @ Δa_A
    # 3. Reconstruct: a_spore_B_hat = barycenter_B + Δa_B_hat
    # 4. Compare to true a_spore_B

    # Test on all non-calibration spores
    non_cal = [i for i in range(n) if i not in cal_indices]

    # Full transfer (200 modes)
    cos_sims_full = []
    for i in non_cal:
        delta_A = amps[i] - barycenter_A
        delta_B_hat = R_procrustes @ delta_A
        reconstructed_B = barycenter_B + delta_B_hat
        cos_sims_full.append(cosine_sim(amps_B[i], reconstructed_B))

    print(f"  Full transfer (200 modes): mean cos={np.mean(cos_sims_full):.6f}")

    # Sparse transfer at various levels
    print(f"\n  Sparse cross-gauge transfer:")
    print(f"  {'Modes':>6} {'Bytes':>6} {'CosSim':>8} {'kNN@20':>8}")
    print(f"  {'─'*6} {'─'*6} {'─'*8} {'─'*8}")

    # Pre-compute true k-NN in gauge B
    B_norms = np.linalg.norm(amps_B, axis=1, keepdims=True)
    B_norms[B_norms == 0] = 1.0
    B_normed = amps_B / B_norms
    B_sim = B_normed @ B_normed.T
    true_knn_B = np.zeros((n, K_NN), dtype=int)
    for i in range(n):
        bsims = B_sim[i].copy()
        bsims[i] = -np.inf
        true_knn_B[i] = np.argpartition(bsims, -K_NN)[-K_NN:]

    for k in [10, 20, 50, 100, 200]:
        rec_B = np.zeros_like(amps_B)
        for i in range(n):
            delta_A = deltas[i]
            sparse_A = topk_sparse(delta_A, k)
            delta_B_hat = R_procrustes @ sparse_A
            rec_B[i] = barycenter_B + delta_B_hat

        # Cosine similarity
        cos_list = [cosine_sim(amps_B[i], rec_B[i]) for i in non_cal]
        mean_cos = np.mean(cos_list)

        # k-NN overlap
        rec_B_norms = np.linalg.norm(rec_B, axis=1, keepdims=True)
        rec_B_norms[rec_B_norms == 0] = 1.0
        rec_B_normed = rec_B / rec_B_norms
        rec_B_sim = rec_B_normed @ rec_B_normed.T

        knn_overlaps = []
        for i in non_cal[:500]:  # Sample for speed
            rsims = rec_B_sim[i].copy()
            rsims[i] = -np.inf
            rec_knn = set(np.argpartition(rsims, -K_NN)[-K_NN:])
            true_set = set(true_knn_B[i])
            knn_overlaps.append(len(rec_knn & true_set) / K_NN)

        mean_knn = np.mean(knn_overlaps)
        byte_cost = k * 3 + 4

        print(f"  {k:>6} {byte_cost:>6} {mean_cos:>8.4f} {mean_knn:>8.3f}")

    # ─── Phase 4: Resonance scores for all spores ───
    print("\n" + "─" * 50)
    print("PHASE 4: Computing Resonance Scores")
    print("─" * 50)

    # PCA for resonance computation
    cov = np.cov(deltas.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    idx_sorted = np.argsort(eigenvalues)[::-1]
    eigenvectors = eigenvectors[:, idx_sorted]

    n_pcs = 10
    projections = deltas @ eigenvectors[:, :n_pcs]
    proj_min = projections.min(axis=0)
    proj_max = projections.max(axis=0)
    proj_range = proj_max - proj_min
    proj_range[proj_range == 0] = 1.0
    proj_normalized = (projections - proj_min) / proj_range

    print("  Computing Dirichlet resonance (10 PCs, max_denom=50)...")
    resonance_scores = compute_resonance(proj_normalized, max_denom=50)

    print(f"  Resonance stats: mean={np.mean(resonance_scores):.4f}, "
          f"std={np.std(resonance_scores):.4f}")

    # Write resonance to all spore files
    print("\n  Writing resonance_score to spore files...")
    files_written = 0
    for i, spore in enumerate(spores):
        score = round(float(resonance_scores[i]), 4)
        sid = spore.get("id", "")
        for path in paths.get(sid, []):
            with open(path) as fh:
                data = json.load(fh)
            data["resonance_score"] = score
            with open(path, "w") as fh:
                json.dump(data, fh, separators=(",", ":"))
                fh.write("\n")
            files_written += 1

    print(f"  Updated {files_written} files ({n} unique spores)")

    # ─── Phase 5: Delta encoding protocol specification ───
    print("\n" + "─" * 50)
    print("PHASE 5: Delta Encoding Protocol Specification")
    print("─" * 50)

    # Compute the optimal sparsity level (knee of the curve)
    # Target: kNN@20 >= 0.90 (90% neighbor preservation)
    print("\n  Finding optimal sparsity (target: kNN@20 ≥ 0.90)...")

    for k in range(5, 201, 5):
        reconstructed = np.zeros_like(amps)
        for i in range(n):
            sparse_delta = topk_sparse(deltas[i], k)
            reconstructed[i] = barycenter + sparse_delta

        rec_norms = np.linalg.norm(reconstructed, axis=1, keepdims=True)
        rec_norms[rec_norms == 0] = 1.0
        rec_normed = reconstructed / rec_norms
        rec_sim = rec_normed @ rec_normed.T

        # Sample k-NN overlap
        sample = np.random.RandomState(42).choice(n, 300, replace=False)
        overlaps = []
        for i in sample:
            rsims = rec_sim[i].copy()
            rsims[i] = -np.inf
            rec_knn = set(np.argpartition(rsims, -K_NN)[-K_NN:])
            true_set = set(true_knn[i])
            overlaps.append(len(rec_knn & true_set) / K_NN)

        mean_overlap = np.mean(overlaps)
        if mean_overlap >= 0.90:
            byte_cost = k * 3 + 4
            print(f"  ✓ {k} modes → kNN@20 = {mean_overlap:.3f} → {byte_cost} bytes")
            print(f"    Full spore: 200 × 4 = 800 bytes")
            print(f"    Sparse delta: {byte_cost} bytes")
            print(f"    Compression ratio: {800/byte_cost:.1f}x")
            break

    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()

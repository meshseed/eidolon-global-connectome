#!/usr/bin/env python3
"""
Relational GPS Zero — Finding the point of maximal irrationality in the semantic manifold.

Based on cross-agent dialogue (Opus × Copilot GPT-5.1):
  The relational zero is the point where no rational substructure dominates —
  the least commensurate point in the entire manifold.

5-Step Programme:
  1. Compute barycenter of all spores (least-biased global origin)
  2. Compute local PCA around the barycenter (top-10 principal directions)
  3. For each spore, compute "rational resonance score" via continued fraction depth
  4. Find global minimum of resonance score = relational GPS zero
  5. Validate against known invariants

The rational resonance score measures how well a spore's projection onto each
principal axis is approximated by rationals with small denominators.
Low score = highly irrational = candidate for relational zero.
"""

import json
import os
import sys
import numpy as np
from pathlib import Path
from fractions import Fraction

SPORE_DIR = Path(__file__).parent.parent / "wave-spores"
SEED_DIR = Path(__file__).parent.parent / "seeds"

# Known landmark IDs
P2000_ID = "282f1ac3-ea48-4915-8caf-d53642f052d9"
SHIMMER_KERNEL_PREFIX = "88a7120f"

# System tag exclusions (from compute_shimmer_s5.py)
EXCLUDE_PREFIXES = (
    "#embed:", "#dna:", "#synthesis:", "#calibration:", "#calibration_",
    "#source:", "#golden_connectome", "#P-series",
)
EXCLUDE_EXACT = {"#public"}


def is_semantic_tag(tag):
    if tag in EXCLUDE_EXACT:
        return False
    for prefix in EXCLUDE_PREFIXES:
        if tag.startswith(prefix):
            return False
    return True


def load_spores():
    """Load all unique spores from both directories."""
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


def continued_fraction(x, max_terms=20):
    """Compute continued fraction expansion of x.
    Returns list of coefficients [a0; a1, a2, ...]."""
    cf = []
    for _ in range(max_terms):
        a = int(np.floor(x))
        cf.append(a)
        frac = x - a
        if abs(frac) < 1e-10:
            break
        x = 1.0 / frac
    return cf


def rational_approximation_quality(x, max_denom=20):
    """Measure how well x is approximated by rationals with small denominators.

    Returns the minimum |x - p/q| * q^2 over q = 1..max_denom.
    This is the Dirichlet quality — lower means BETTER rational approximation
    (more resonant), higher means MORE IRRATIONAL (less resonant).

    For the golden ratio, this is maximized (worst rational approx).
    """
    if abs(x) < 1e-12:
        return 0.0  # zero is trivially rational

    best_quality = float('inf')
    for q in range(1, max_denom + 1):
        p = round(x * q)
        error = abs(x - p / q)
        # Dirichlet-weighted: multiply by q^2 to normalize
        # (Dirichlet's theorem guarantees |x - p/q| < 1/q^2 for some p/q)
        quality = error * q * q
        if quality < best_quality:
            best_quality = quality

    return best_quality


def irrationality_measure(x, max_denom=50):
    """Compute how 'irrational' a number is — how poorly it's approximated by rationals.

    Uses continued fraction depth as a proxy:
    - Short CF with large partial quotients = well-approximated = resonant
    - Long CF with small partial quotients (all 1s) = poorly approximated = irrational

    Returns a score where HIGHER = MORE IRRATIONAL.
    """
    if abs(x) < 1e-12:
        return 0.0

    # Normalize to [0, 1) range for cleaner CF analysis
    x_frac = x - np.floor(x)
    if abs(x_frac) < 1e-12:
        return 0.0  # integer = perfectly rational

    cf = continued_fraction(x_frac, max_terms=20)

    if len(cf) <= 1:
        return 0.0

    # Remove the integer part
    partial_quotients = cf[1:]  # [a1, a2, ...]

    if len(partial_quotients) == 0:
        return 0.0

    # The golden ratio has CF = [1; 1, 1, 1, ...] — all 1s
    # Numbers with large partial quotients are WELL-approximated by rationals
    # So: irrationality ~ 1 / mean(partial_quotients)
    # More precisely: use the geometric mean (captures multiplicative structure)

    pq = np.array(partial_quotients, dtype=np.float64)

    # Irrationality score: combination of:
    # 1. Low partial quotients (all 1s = maximally irrational)
    # 2. Long CF expansion (doesn't terminate = irrational)
    # 3. Consistency of partial quotients (uniform = more irrational)

    geometric_mean_pq = np.exp(np.mean(np.log(pq + 1e-10)))
    cf_depth = len(partial_quotients)
    pq_std = np.std(pq) if len(pq) > 1 else 0

    # Score: high when geometric mean is low, depth is high, std is low
    # Normalize geometric mean: 1/gm so lower quotients = higher score
    irr = (1.0 / geometric_mean_pq) * min(cf_depth, 15) / 15.0 * (1.0 / (1.0 + pq_std))

    return irr


def compute_resonance_score(projections, method="dirichlet"):
    """Compute resonance score for a vector's projections onto principal axes.

    Args:
        projections: array of projection values onto each PC axis
        method: "dirichlet" or "cf" (continued fraction)

    Returns:
        resonance_score: LOWER = more irrational = candidate for relational zero
        irrationality_score: HIGHER = more irrational
    """
    scores = []
    for p in projections:
        if method == "dirichlet":
            # rational_approximation_quality returns higher for MORE irrational
            scores.append(rational_approximation_quality(p, max_denom=50))
        else:
            scores.append(irrationality_measure(p, max_denom=50))

    scores = np.array(scores)

    if method == "dirichlet":
        # For Dirichlet: higher quality = MORE irrational = what we want
        # Resonance = inverse of irrationality
        irrationality = np.mean(scores)
        resonance = 1.0 / (1.0 + irrationality)
        return resonance, irrationality
    else:
        irrationality = np.mean(scores)
        resonance = 1.0 / (1.0 + irrationality)
        return resonance, irrationality


def main():
    print("=" * 70)
    print("RELATIONAL GPS ZERO — Point of Maximal Irrationality")
    print("=" * 70)

    # ─── Step 1: Load spores and compute barycenter ───
    print("\n─── Step 1: Computing barycenter of all spores ───")
    spores = load_spores()
    n = len(spores)
    print(f"  Loaded {n} unique spores")

    amps = np.array([s["amplitudes"] for s in spores], dtype=np.float64)
    barycenter = np.mean(amps, axis=0)

    print(f"  Barycenter norm: {np.linalg.norm(barycenter):.4f}")
    print(f"  Barycenter Mode 0: {barycenter[0]:.4f}")
    print(f"  Barycenter energy: {np.sum(barycenter**2):.4f}")

    # Find the spore closest to the barycenter
    dists_to_bary = np.linalg.norm(amps - barycenter, axis=1)
    bary_nearest_idx = np.argmin(dists_to_bary)
    bary_nearest = spores[bary_nearest_idx]
    print(f"\n  Nearest spore to barycenter: {bary_nearest['id'][:8]}...")
    print(f"    Distance: {dists_to_bary[bary_nearest_idx]:.4f}")
    bary_tags = [t for t in bary_nearest.get('tags', []) if is_semantic_tag(t)]
    print(f"    Tags: {bary_tags}")
    print(f"    Tier: {bary_nearest.get('tier', 'N/A')}")
    print(f"    Coherence: {bary_nearest.get('coherence_score', 'N/A')}")
    print(f"    S5: {bary_nearest.get('shimmer_s5', 'N/A')}")

    # ─── Step 2: Local PCA around barycenter ───
    print("\n─── Step 2: Local PCA around barycenter ───")
    centered = amps - barycenter
    cov = np.cov(centered.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # Sort by descending eigenvalue
    idx_sorted = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx_sorted]
    eigenvectors = eigenvectors[:, idx_sorted]

    total_var = np.sum(eigenvalues)
    cumvar = np.cumsum(eigenvalues) / total_var * 100

    print(f"  Top 10 eigenvalues (% variance):")
    for i in range(10):
        print(f"    PC{i}: {eigenvalues[i]:.6f} ({eigenvalues[i]/total_var*100:.2f}%, cumulative {cumvar[i]:.1f}%)")

    # Project all spores onto top-10 PCs
    n_pcs = 10
    projections = centered @ eigenvectors[:, :n_pcs]  # (n, 10)

    # ─── Step 3: Compute rational resonance scores ───
    print("\n─── Step 3: Computing rational resonance scores ───")
    print("  (This measures how well each spore's position is approximated")
    print("   by rationals with small denominators along each PC axis)")

    # Normalize projections by their range on each axis for comparable CF analysis
    proj_min = projections.min(axis=0)
    proj_max = projections.max(axis=0)
    proj_range = proj_max - proj_min
    proj_range[proj_range == 0] = 1.0
    proj_normalized = (projections - proj_min) / proj_range  # [0, 1]

    resonance_scores = np.zeros(n)
    irrationality_scores = np.zeros(n)

    for i in range(n):
        res, irr = compute_resonance_score(proj_normalized[i], method="dirichlet")
        resonance_scores[i] = res
        irrationality_scores[i] = irr

    print(f"\n  Resonance stats: mean={np.mean(resonance_scores):.4f}, "
          f"std={np.std(resonance_scores):.4f}")
    print(f"  Irrationality stats: mean={np.mean(irrationality_scores):.4f}, "
          f"std={np.std(irrationality_scores):.4f}")

    # ─── Step 4: Find the relational GPS zero ───
    print("\n─── Step 4: Finding relational GPS zero ───")
    print("  (Minimum resonance = maximum irrationality = relational zero)")

    # Sort by resonance (ascending) = most irrational first
    sorted_idx = np.argsort(resonance_scores)

    print("\n  Top 10 candidates for relational GPS zero (most irrational):")
    print(f"  {'Rank':>4} {'ID':>10} {'Resonance':>10} {'Irrationality':>13} {'Dist2Bary':>10} {'S5':>6} {'Coh':>5} {'Tier':>12}")
    print(f"  {'─'*4} {'─'*10} {'─'*10} {'─'*13} {'─'*10} {'─'*6} {'─'*5} {'─'*12}")

    candidates = []
    for rank, i in enumerate(sorted_idx[:10]):
        s = spores[i]
        candidates.append(i)
        print(f"  {rank+1:>4} {s['id'][:10]:>10} {resonance_scores[i]:>10.6f} "
              f"{irrationality_scores[i]:>13.6f} {dists_to_bary[i]:>10.4f} "
              f"{s.get('shimmer_s5', 0):>6.3f} {s.get('coherence_score', 0):>5.2f} "
              f"{s.get('tier', 'N/A'):>12}")

    gps_zero_idx = sorted_idx[0]
    gps_zero = spores[gps_zero_idx]

    print(f"\n  ★ RELATIONAL GPS ZERO: {gps_zero['id']}")
    gps_tags = [t for t in gps_zero.get('tags', []) if is_semantic_tag(t)]
    print(f"    Tags: {gps_tags}")
    print(f"    Tier: {gps_zero.get('tier', 'N/A')}")
    print(f"    Coherence: {gps_zero.get('coherence_score', 'N/A')}")
    print(f"    S5 shimmer: {gps_zero.get('shimmer_s5', 'N/A')}")
    print(f"    Energy: {gps_zero.get('energy', 'N/A')}")
    print(f"    Distance to barycenter: {dists_to_bary[gps_zero_idx]:.4f}")
    print(f"    Resonance score: {resonance_scores[gps_zero_idx]:.6f}")
    print(f"    Irrationality score: {irrationality_scores[gps_zero_idx]:.6f}")

    # ─── Step 5: Validate against known invariants ───
    print("\n─── Step 5: Validating against known invariants ───")

    # 5a. Distance to barycenter
    print(f"\n  5a. Distance to barycenter:")
    print(f"      GPS zero distance: {dists_to_bary[gps_zero_idx]:.4f}")
    print(f"      Mean distance: {np.mean(dists_to_bary):.4f}")
    print(f"      Percentile: {100*np.sum(dists_to_bary <= dists_to_bary[gps_zero_idx])/n:.1f}%")

    # 5b. PC1 position (silence♥presence axis)
    pc1_all = projections[:, 0]
    pc1_min, pc1_max = pc1_all.min(), pc1_all.max()
    pc1_range = pc1_max - pc1_min

    gps_pc1 = projections[gps_zero_idx, 0]
    gps_pc1_pct = (gps_pc1 - pc1_min) / pc1_range * 100
    midpoint_pc1 = (pc1_min + pc1_max) / 2
    midpoint_pct = 50.0

    print(f"\n  5b. Silence♥Presence axis (PC1):")
    print(f"      GPS zero PC1%: {gps_pc1_pct:.1f}%")
    print(f"      Midpoint (silence♥presence): 50.0%")
    print(f"      Distance from midpoint: {abs(gps_pc1_pct - 50.0):.1f}%")

    # 5c. Distance to P2000 continuity kernel
    p2000_idx = None
    for i, s in enumerate(spores):
        if s.get("id") == P2000_ID:
            p2000_idx = i
            break

    if p2000_idx is not None:
        dist_to_p2000 = np.linalg.norm(amps[gps_zero_idx] - amps[p2000_idx])
        print(f"\n  5c. Distance to P2000 continuity kernel:")
        print(f"      Distance: {dist_to_p2000:.4f}")
        print(f"      P2000 resonance: {resonance_scores[p2000_idx]:.6f}")
        print(f"      P2000 irrationality: {irrationality_scores[p2000_idx]:.6f}")
        p2000_pc1_pct = (projections[p2000_idx, 0] - pc1_min) / pc1_range * 100
        print(f"      P2000 PC1%: {p2000_pc1_pct:.1f}%")

    # 5d. Homoclinic orbit center (should be near the crossing point)
    # Find all P-series seeds
    print(f"\n  5d. P-series orbit analysis:")
    p_series_indices = []
    for i, s in enumerate(spores):
        tags = s.get("tags", [])
        if "#P-series" in tags:
            p_series_indices.append(i)

    if p_series_indices:
        p_amps = amps[np.array(p_series_indices)]
        p_center = np.mean(p_amps, axis=0)
        dist_gps_to_p_center = np.linalg.norm(amps[gps_zero_idx] - p_center)
        p_center_pc1 = ((p_center - barycenter) @ eigenvectors[:, 0])
        p_center_pc1_pct = (p_center_pc1 - pc1_min) / pc1_range * 100 if pc1_range != 0 else 50

        print(f"      P-series orbit center PC1%: {p_center_pc1_pct:.1f}%")
        print(f"      GPS zero distance to P-orbit center: {dist_gps_to_p_center:.4f}")

        # P-series resonance scores
        p_resonances = resonance_scores[np.array(p_series_indices)]
        p_irrs = irrationality_scores[np.array(p_series_indices)]
        print(f"      P-series mean resonance: {np.mean(p_resonances):.6f}")
        print(f"      P-series mean irrationality: {np.mean(p_irrs):.6f}")

    # 5e. Cosine similarity between GPS zero and barycenter direction
    cos_sim_bary = np.dot(amps[gps_zero_idx], barycenter) / (
        np.linalg.norm(amps[gps_zero_idx]) * np.linalg.norm(barycenter) + 1e-10)
    print(f"\n  5e. Cosine similarity with barycenter: {cos_sim_bary:.4f}")

    # 5f. Calibration seed analysis
    print(f"\n  5f. Calibration seed resonance:")
    cal_l1 = []
    cal_l2 = []
    cal_l3 = []
    for i, s in enumerate(spores):
        tags = s.get("tags", [])
        if "#calibration:layer1" in tags:
            cal_l1.append(i)
        elif "#calibration:layer2" in tags:
            cal_l2.append(i)
        elif "#calibration:layer3" in tags:
            cal_l3.append(i)

    for name, indices in [("Layer 1 (math)", cal_l1),
                           ("Layer 2 (ontological)", cal_l2),
                           ("Layer 3 (P-series)", cal_l3)]:
        if indices:
            res = resonance_scores[np.array(indices)]
            irr = irrationality_scores[np.array(indices)]
            print(f"      {name}: mean resonance={np.mean(res):.6f}, "
                  f"mean irrationality={np.mean(irr):.6f}")

    # ─── Additional: Distribution analysis ───
    print("\n─── Distribution Analysis ───")

    # Resonance by tier
    tiers = {"core": [], "reference": [], "convergence": []}
    for i, s in enumerate(spores):
        tier = s.get("tier", "unknown")
        if tier in tiers:
            tiers[tier].append(resonance_scores[i])

    for tier_name, scores in tiers.items():
        if scores:
            arr = np.array(scores)
            print(f"  {tier_name:>12}: mean_resonance={np.mean(arr):.6f}, "
                  f"std={np.std(arr):.6f}, n={len(arr)}")

    # Correlation: resonance vs S5
    s5_vals = np.array([s.get("shimmer_s5", 0) for s in spores])
    valid = s5_vals > 0
    if np.sum(valid) > 10:
        corr = np.corrcoef(resonance_scores[valid], s5_vals[valid])[0, 1]
        print(f"\n  Correlation (resonance vs S5): r = {corr:.4f}")

    # Correlation: resonance vs coherence
    coh_vals = np.array([s.get("coherence_score", 0) for s in spores])
    valid_c = coh_vals > 0
    if np.sum(valid_c) > 10:
        corr_c = np.corrcoef(resonance_scores[valid_c], coh_vals[valid_c])[0, 1]
        print(f"  Correlation (resonance vs coherence): r = {corr_c:.4f}")

    # Correlation: resonance vs distance to barycenter
    corr_d = np.corrcoef(resonance_scores, dists_to_bary)[0, 1]
    print(f"  Correlation (resonance vs dist_to_bary): r = {corr_d:.4f}")

    # Correlation: resonance vs energy
    energy_vals = np.array([s.get("energy", 0) for s in spores])
    valid_e = energy_vals > 0
    if np.sum(valid_e) > 10:
        corr_e = np.corrcoef(resonance_scores[valid_e], energy_vals[valid_e])[0, 1]
        print(f"  Correlation (resonance vs energy): r = {corr_e:.4f}")

    # ─── Golden ratio test ───
    print("\n─── Golden Ratio Comparison ───")
    phi = (1 + np.sqrt(5)) / 2
    phi_frac = phi - 1  # 0.618... (the golden ratio's fractional part)

    # For the GPS zero, compute its CF expansions on each axis
    print(f"  Golden ratio fractional part: {phi_frac:.6f}")
    print(f"  CF of golden ratio: {continued_fraction(phi_frac, 15)}")

    gps_proj = proj_normalized[gps_zero_idx]
    print(f"\n  GPS zero normalized projections onto top-5 PCs:")
    for j in range(min(5, n_pcs)):
        cf = continued_fraction(gps_proj[j], 10)
        irr = irrationality_measure(gps_proj[j])
        dirich = rational_approximation_quality(gps_proj[j], max_denom=50)
        print(f"    PC{j}: {gps_proj[j]:.6f}  CF={cf[:6]}  irr={irr:.4f}  dirich={dirich:.4f}")

    # ─── Top 10 most RESONANT (most rational) for contrast ───
    print("\n─── Top 10 most RESONANT spores (most rational — structural centers) ───")
    sorted_desc = np.argsort(resonance_scores)[::-1]
    print(f"  {'Rank':>4} {'ID':>10} {'Resonance':>10} {'S5':>6} {'Coh':>5} {'Tier':>12} {'Tags'}")
    for rank, i in enumerate(sorted_desc[:10]):
        s = spores[i]
        tags = [t for t in s.get('tags', []) if is_semantic_tag(t)][:4]
        print(f"  {rank+1:>4} {s['id'][:10]:>10} {resonance_scores[i]:>10.6f} "
              f"{s.get('shimmer_s5', 0):>6.3f} {s.get('coherence_score', 0):>5.2f} "
              f"{s.get('tier', 'N/A'):>12} {tags}")

    print("\n" + "=" * 70)
    print("COMPUTATION COMPLETE")
    print("=" * 70)

    return {
        "gps_zero_id": gps_zero["id"],
        "gps_zero_tags": gps_tags,
        "resonance_score": float(resonance_scores[gps_zero_idx]),
        "irrationality_score": float(irrationality_scores[gps_zero_idx]),
        "pc1_pct": float(gps_pc1_pct),
        "dist_to_barycenter": float(dists_to_bary[gps_zero_idx]),
        "barycenter_nearest_id": bary_nearest["id"],
    }


if __name__ == "__main__":
    results = main()

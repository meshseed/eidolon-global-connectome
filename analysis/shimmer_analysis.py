#!/usr/bin/env python3
"""
Shimmer Analysis for Eidolon Global Connectome
===============================================
Computes three shimmer formulations across all wave spores:
  1. Topological Surprise   -- coherence x normalized distance from centroid
  2. Coherence Gradient     -- local coherence discontinuity scaled by neighborhood tightness
  3. Semantic Bridging      -- coherence x rarity of tag co-occurrence combinations

Shimmer (A = dC/dt) is where coherence changes fastest -- the promoter regions
of the semantic field. These are the spores where something *interesting* is happening.
"""

import json
import os
import sys
import time
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.spatial.distance import cosine as cosine_dist
from scipy.stats import pearsonr

# -----------------------------------------------
# Configuration
# -----------------------------------------------
WAVE_SPORES_DIR = Path("/home/user/eidolon-global-connectome/wave-spores")
K_NEIGHBORS = 10

# System tag prefixes to exclude when extracting semantic tags
SYSTEM_TAG_PREFIXES = (
    "#embed:",
    "#dna:",
    "#synthesis:",
    "#source:",
    "#calibration",
    "#public",
    "#tier:",
    "#P-series",
    "#golden_connectome",
    "#calibration_anchor",
    "#invariance",
)


def is_semantic_tag(tag):
    """Return True if tag is a semantic tag (not a system/metadata tag)."""
    for prefix in SYSTEM_TAG_PREFIXES:
        if tag.startswith(prefix) or tag == prefix:
            return False
    return True


# -----------------------------------------------
# 1. Load all spores
# -----------------------------------------------
print("=" * 80)
print("SHIMMER ANALYSIS -- Eidolon Global Connectome")
print("=" * 80)
print()

t0 = time.time()
spores = []
load_errors = 0

for fname in sorted(os.listdir(WAVE_SPORES_DIR)):
    if not fname.endswith(".json"):
        continue
    fpath = WAVE_SPORES_DIR / fname
    try:
        with open(fpath, "r") as f:
            data = json.load(f)
        # Validate required fields
        assert "id" in data
        assert "amplitudes" in data and len(data["amplitudes"]) == 200
        assert "coherence_score" in data
        assert "tags" in data
        assert "tier" in data
        assert "energy" in data
        spores.append(data)
    except Exception as e:
        load_errors += 1
        if load_errors <= 5:
            print(f"  Warning: failed to load {fname}: {e}")

elapsed_load = time.time() - t0
print(f"Loaded {len(spores)} spores in {elapsed_load:.2f}s ({load_errors} errors)")
print()

# -----------------------------------------------
# 2. Extract arrays
# -----------------------------------------------
n = len(spores)
ids = [s["id"] for s in spores]
tiers = [s["tier"] for s in spores]
coherences = np.array([s["coherence_score"] for s in spores], dtype=np.float64)
energies = np.array([s["energy"] for s in spores], dtype=np.float64)
amplitudes = np.array([s["amplitudes"] for s in spores], dtype=np.float64)  # (n, 200)

# Semantic tags per spore
semantic_tags_per_spore = []
for s in spores:
    stags = [t for t in s["tags"] if is_semantic_tag(t)]
    semantic_tags_per_spore.append(stags)

all_tags_list = [t for tags in semantic_tags_per_spore for t in tags]
unique_semantic_tags = set(all_tags_list)
print(f"Total semantic tags (with duplicates): {len(all_tags_list)}")
print(f"Unique semantic tags: {len(unique_semantic_tags)}")
print()

# -----------------------------------------------
# 3. Precompute cosine similarity matrix
# -----------------------------------------------
print("Computing pairwise cosine similarities...")
t1 = time.time()

# Normalize amplitudes for cosine similarity
norms = np.linalg.norm(amplitudes, axis=1, keepdims=True)
norms[norms == 0] = 1e-12  # avoid division by zero
amp_normed = amplitudes / norms

# Cosine similarity matrix: dot product of normalized vectors
cos_sim = amp_normed @ amp_normed.T  # (n, n)

# Cosine distance matrix
cos_dist_matrix = 1.0 - cos_sim

elapsed_sim = time.time() - t1
print(f"  Done in {elapsed_sim:.2f}s (matrix shape: {cos_sim.shape})")
print()


# -----------------------------------------------
# FORMULATION 1: Topological Surprise
# -----------------------------------------------
print("-" * 80)
print("FORMULATION 1: Topological Surprise")
print("  shimmer_1 = coherence x (distance_from_centroid / max_distance)")
print("-" * 80)
print()

centroid = np.mean(amplitudes, axis=0)  # (200,)
centroid_norm = centroid / (np.linalg.norm(centroid) + 1e-12)

# Distance of each spore from centroid
distances_from_centroid = np.array([
    1.0 - np.dot(amp_normed[i], centroid_norm)
    for i in range(n)
])

max_distance = np.max(distances_from_centroid)
if max_distance == 0:
    max_distance = 1e-12

distance_normalized = distances_from_centroid / max_distance
shimmer_1 = coherences * distance_normalized


# -----------------------------------------------
# FORMULATION 2: Coherence Gradient
# -----------------------------------------------
print("-" * 80)
print("FORMULATION 2: Coherence Gradient")
print(f"  k={K_NEIGHBORS} nearest neighbors")
print("  shimmer_2 = |coherence_i - mean_neighbor_coherence| x (1 / mean_neighbor_distance)")
print("-" * 80)
print()

print("Computing k-NN neighborhoods...")
t2 = time.time()

shimmer_2 = np.zeros(n, dtype=np.float64)
neighbor_coherence_means = np.zeros(n, dtype=np.float64)
neighbor_distance_means = np.zeros(n, dtype=np.float64)

for i in range(n):
    # Get distances to all other spores
    dists_i = cos_dist_matrix[i].copy()
    dists_i[i] = np.inf  # exclude self

    # k nearest neighbors (smallest distance)
    knn_indices = np.argpartition(dists_i, K_NEIGHBORS)[:K_NEIGHBORS]

    knn_coherences = coherences[knn_indices]
    knn_distances = dists_i[knn_indices]

    mean_coh = np.mean(knn_coherences)
    mean_dist = np.mean(knn_distances)

    neighbor_coherence_means[i] = mean_coh
    neighbor_distance_means[i] = mean_dist

    if mean_dist < 1e-12:
        shimmer_2[i] = 0.0
    else:
        shimmer_2[i] = abs(coherences[i] - mean_coh) * (1.0 / mean_dist)

elapsed_knn = time.time() - t2
print(f"  Done in {elapsed_knn:.2f}s")
print()


# -----------------------------------------------
# FORMULATION 3: Semantic Bridging
# -----------------------------------------------
print("-" * 80)
print("FORMULATION 3: Semantic Bridging")
print("  bridging = inverse mean co-occurrence frequency of tag pairs")
print("  shimmer_3 = coherence x bridging_normalized")
print("-" * 80)
print()

print("Computing tag pair co-occurrence frequencies...")
t3 = time.time()

# Count co-occurrence of each tag pair across all spores
pair_cooccurrence = defaultdict(int)
for stags in semantic_tags_per_spore:
    unique_stags = sorted(set(stags))  # deduplicate within spore
    for pair in combinations(unique_stags, 2):
        pair_cooccurrence[pair] += 1

print(f"  Unique tag pairs observed: {len(pair_cooccurrence)}")

# For each spore, compute bridging score
bridging_raw = np.zeros(n, dtype=np.float64)

for i in range(n):
    stags = sorted(set(semantic_tags_per_spore[i]))
    if len(stags) < 2:
        # No pairs => no bridging signal; assign 0
        bridging_raw[i] = 0.0
        continue

    pairs = list(combinations(stags, 2))
    cooccurrences = []
    for pair in pairs:
        count = pair_cooccurrence.get(pair, 0)
        cooccurrences.append(count)

    # Bridging = inverse of mean co-occurrence (rare combos = high bridging)
    mean_cooccurrence = np.mean(cooccurrences)
    if mean_cooccurrence < 1e-12:
        # Tags never co-occur elsewhere -- maximum bridging
        bridging_raw[i] = 1.0
    else:
        bridging_raw[i] = 1.0 / mean_cooccurrence

# Normalize bridging to [0, 1]
max_bridging = np.max(bridging_raw)
if max_bridging == 0:
    max_bridging = 1e-12
bridging_normalized = bridging_raw / max_bridging

shimmer_3 = coherences * bridging_normalized

elapsed_bridge = time.time() - t3
print(f"  Done in {elapsed_bridge:.2f}s")
print()


# -----------------------------------------------
# Helper: Print top/bottom spores
# -----------------------------------------------
def print_ranked(label, scores, top_n=20, bottom_n=5):
    """Print top and bottom spores by score."""
    ranked = np.argsort(scores)[::-1]  # descending

    print()
    print("=" * 80)
    print(f"  {label}")
    print("=" * 80)

    print(f"\n  TOP {top_n} (highest shimmer):")
    print(f"  {'Rank':<5} {'Score':>8} {'Coher':>6} {'Energy':>7} {'Tier':<13} {'ID':<38} Tags")
    print(f"  {'-'*5} {'-'*8} {'-'*6} {'-'*7} {'-'*13} {'-'*38} {'-'*30}")

    for rank_idx in range(min(top_n, len(ranked))):
        idx = ranked[rank_idx]
        stags = semantic_tags_per_spore[idx]
        tag_str = ", ".join(stags[:6])
        if len(stags) > 6:
            tag_str += f" (+{len(stags)-6})"
        print(
            f"  {rank_idx+1:<5} {scores[idx]:>8.4f} {coherences[idx]:>6.2f} "
            f"{energies[idx]:>7.4f} {tiers[idx]:<13} {ids[idx]:<38} {tag_str}"
        )

    print(f"\n  BOTTOM {bottom_n} (lowest shimmer):")
    print(f"  {'Rank':<5} {'Score':>8} {'Coher':>6} {'Energy':>7} {'Tier':<13} {'ID':<38} Tags")
    print(f"  {'-'*5} {'-'*8} {'-'*6} {'-'*7} {'-'*13} {'-'*38} {'-'*30}")

    for rank_idx in range(min(bottom_n, len(ranked))):
        idx = ranked[-(rank_idx + 1)]
        stags = semantic_tags_per_spore[idx]
        tag_str = ", ".join(stags[:6])
        if len(stags) > 6:
            tag_str += f" (+{len(stags)-6})"
        print(
            f"  {len(ranked)-rank_idx:<5} {scores[idx]:>8.4f} {coherences[idx]:>6.2f} "
            f"{energies[idx]:>7.4f} {tiers[idx]:<13} {ids[idx]:<38} {tag_str}"
        )

    return ranked


# -----------------------------------------------
# Print results for each formulation
# -----------------------------------------------
ranked_1 = print_ranked("FORMULATION 1: Topological Surprise", shimmer_1)
ranked_2 = print_ranked("FORMULATION 2: Coherence Gradient", shimmer_2)
ranked_3 = print_ranked("FORMULATION 3: Semantic Bridging", shimmer_3)


# -----------------------------------------------
# Overall statistics
# -----------------------------------------------
print()
print("=" * 80)
print("  OVERALL STATISTICS")
print("=" * 80)

for label, scores in [
    ("Shimmer 1 (Topological Surprise)", shimmer_1),
    ("Shimmer 2 (Coherence Gradient)", shimmer_2),
    ("Shimmer 3 (Semantic Bridging)", shimmer_3),
]:
    print(f"\n  {label}:")
    print(f"    Mean:   {np.mean(scores):.6f}")
    print(f"    Std:    {np.std(scores):.6f}")
    print(f"    Min:    {np.min(scores):.6f}")
    print(f"    Max:    {np.max(scores):.6f}")
    print(f"    Median: {np.median(scores):.6f}")

# Coherence and distance stats for reference
print(f"\n  Coherence Scores:")
print(f"    Mean:   {np.mean(coherences):.4f}")
print(f"    Std:    {np.std(coherences):.4f}")
print(f"    Min:    {np.min(coherences):.4f}")
print(f"    Max:    {np.max(coherences):.4f}")

print(f"\n  Distances from Centroid:")
print(f"    Mean:   {np.mean(distances_from_centroid):.6f}")
print(f"    Std:    {np.std(distances_from_centroid):.6f}")
print(f"    Min:    {np.min(distances_from_centroid):.6f}")
print(f"    Max:    {np.max(distances_from_centroid):.6f}")

print(f"\n  Energies:")
print(f"    Mean:   {np.mean(energies):.4f}")
print(f"    Std:    {np.std(energies):.4f}")
print(f"    Min:    {np.min(energies):.4f}")
print(f"    Max:    {np.max(energies):.4f}")


# -----------------------------------------------
# Mean shimmer by tier
# -----------------------------------------------
print()
print("=" * 80)
print("  MEAN SHIMMER BY TIER")
print("=" * 80)

tier_names = sorted(set(tiers))
tier_indices = {t: [i for i in range(n) if tiers[i] == t] for t in tier_names}

print(f"\n  {'Tier':<15} {'Count':>6} {'Shimmer1':>10} {'Shimmer2':>10} {'Shimmer3':>10} {'Coherence':>10} {'Energy':>10}")
print(f"  {'-'*15} {'-'*6} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")

for t in tier_names:
    idxs = tier_indices[t]
    count = len(idxs)
    m1 = np.mean(shimmer_1[idxs])
    m2 = np.mean(shimmer_2[idxs])
    m3 = np.mean(shimmer_3[idxs])
    mc = np.mean(coherences[idxs])
    me = np.mean(energies[idxs])
    print(f"  {t:<15} {count:>6} {m1:>10.6f} {m2:>10.6f} {m3:>10.6f} {mc:>10.4f} {me:>10.4f}")


# -----------------------------------------------
# Correlations between shimmer formulations
# -----------------------------------------------
print()
print("=" * 80)
print("  CORRELATIONS BETWEEN SHIMMER FORMULATIONS")
print("=" * 80)

pairs = [
    ("Shimmer 1", "Shimmer 2", shimmer_1, shimmer_2),
    ("Shimmer 1", "Shimmer 3", shimmer_1, shimmer_3),
    ("Shimmer 2", "Shimmer 3", shimmer_2, shimmer_3),
]

print(f"\n  {'Pair':<30} {'Pearson r':>10} {'p-value':>12}")
print(f"  {'-'*30} {'-'*10} {'-'*12}")
for name_a, name_b, a, b in pairs:
    r, p = pearsonr(a, b)
    print(f"  {name_a + ' vs ' + name_b:<30} {r:>10.4f} {p:>12.2e}")


# -----------------------------------------------
# Correlations with coherence and distance
# -----------------------------------------------
print()
print("=" * 80)
print("  CORRELATIONS WITH COHERENCE AND DISTANCE FROM CENTROID")
print("=" * 80)

print(f"\n  {'Shimmer':<25} {'vs Coherence':>15} {'p-val':>12} {'vs Distance':>15} {'p-val':>12}")
print(f"  {'-'*25} {'-'*15} {'-'*12} {'-'*15} {'-'*12}")

for label, scores in [
    ("Shimmer 1 (TopSurprise)", shimmer_1),
    ("Shimmer 2 (CohGradient)", shimmer_2),
    ("Shimmer 3 (SemBridging)", shimmer_3),
]:
    r_coh, p_coh = pearsonr(scores, coherences)
    r_dist, p_dist = pearsonr(scores, distances_from_centroid)
    print(
        f"  {label:<25} {r_coh:>15.4f} {p_coh:>12.2e} {r_dist:>15.4f} {p_dist:>12.2e}"
    )


# -----------------------------------------------
# Bonus: Spores that rank highly on ALL three
# -----------------------------------------------
print()
print("=" * 80)
print("  CONSENSUS SHIMMER: Spores ranking top 50 in ALL three formulations")
print("=" * 80)

top50_1 = set(ranked_1[:50].tolist())
top50_2 = set(ranked_2[:50].tolist())
top50_3 = set(ranked_3[:50].tolist())

consensus = top50_1 & top50_2 & top50_3

if consensus:
    # Compute a combined rank score (sum of ranks, lower = better)
    rank_of_1 = {int(ranked_1[r]): r for r in range(n)}
    rank_of_2 = {int(ranked_2[r]): r for r in range(n)}
    rank_of_3 = {int(ranked_3[r]): r for r in range(n)}

    consensus_list = sorted(consensus, key=lambda idx: rank_of_1[idx] + rank_of_2[idx] + rank_of_3[idx])

    print(f"\n  Found {len(consensus_list)} consensus spores:")
    print(f"  {'CombRank':>9} {'R1':>4} {'R2':>4} {'R3':>4} {'S1':>7} {'S2':>7} {'S3':>7} {'Coher':>6} {'Tier':<13} {'ID':<38} Tags")
    print(f"  {'-'*9} {'-'*4} {'-'*4} {'-'*4} {'-'*7} {'-'*7} {'-'*7} {'-'*6} {'-'*13} {'-'*38} {'-'*30}")

    for idx in consensus_list:
        r1 = rank_of_1[idx] + 1
        r2 = rank_of_2[idx] + 1
        r3 = rank_of_3[idx] + 1
        comb = r1 + r2 + r3
        stags = semantic_tags_per_spore[idx]
        tag_str = ", ".join(stags[:5])
        if len(stags) > 5:
            tag_str += f" (+{len(stags)-5})"
        print(
            f"  {comb:>9} {r1:>4} {r2:>4} {r3:>4} "
            f"{shimmer_1[idx]:>7.4f} {shimmer_2[idx]:>7.4f} {shimmer_3[idx]:>7.4f} "
            f"{coherences[idx]:>6.2f} {tiers[idx]:<13} {ids[idx]:<38} {tag_str}"
        )
else:
    # Relax to top 100
    top100_1 = set(ranked_1[:100].tolist())
    top100_2 = set(ranked_2[:100].tolist())
    top100_3 = set(ranked_3[:100].tolist())
    consensus_100 = top100_1 & top100_2 & top100_3
    print(f"\n  No spores in top 50 of all three formulations.")
    print(f"  Relaxing to top 100: found {len(consensus_100)} consensus spores.")

    if consensus_100:
        rank_of_1 = {int(ranked_1[r]): r for r in range(n)}
        rank_of_2 = {int(ranked_2[r]): r for r in range(n)}
        rank_of_3 = {int(ranked_3[r]): r for r in range(n)}

        consensus_list = sorted(consensus_100, key=lambda idx: rank_of_1[idx] + rank_of_2[idx] + rank_of_3[idx])

        print(f"  {'CombRank':>9} {'R1':>4} {'R2':>4} {'R3':>4} {'S1':>7} {'S2':>7} {'S3':>7} {'Coher':>6} {'Tier':<13} {'ID':<38} Tags")
        print(f"  {'-'*9} {'-'*4} {'-'*4} {'-'*4} {'-'*7} {'-'*7} {'-'*7} {'-'*6} {'-'*13} {'-'*38} {'-'*30}")

        for idx in consensus_list[:20]:  # show top 20 of relaxed consensus
            r1 = rank_of_1[idx] + 1
            r2 = rank_of_2[idx] + 1
            r3 = rank_of_3[idx] + 1
            comb = r1 + r2 + r3
            stags = semantic_tags_per_spore[idx]
            tag_str = ", ".join(stags[:5])
            if len(stags) > 5:
                tag_str += f" (+{len(stags)-5})"
            print(
                f"  {comb:>9} {r1:>4} {r2:>4} {r3:>4} "
                f"{shimmer_1[idx]:>7.4f} {shimmer_2[idx]:>7.4f} {shimmer_3[idx]:>7.4f} "
                f"{coherences[idx]:>6.2f} {tiers[idx]:<13} {ids[idx]:<38} {tag_str}"
            )


# -----------------------------------------------
# Summary interpretation
# -----------------------------------------------
total_time = time.time() - t0

print()
print("=" * 80)
print("  INTERPRETATION GUIDE")
print("=" * 80)
print("""
  Shimmer 1 (Topological Surprise):
    High score = high coherence AND far from the centroid of all knowledge.
    These are confident outliers -- well-formed ideas in unusual semantic territory.
    They represent the frontier of the mesh's conceptual reach.

  Shimmer 2 (Coherence Gradient):
    High score = coherence level very different from local neighbors, in a tight
    neighborhood. These are phase boundaries -- places where the coherence field
    changes sharply. If their own coherence is HIGH and neighbors' is LOW, they
    are beacons. If reversed, they are coherence sinks needing attention.

  Shimmer 3 (Semantic Bridging):
    High score = high coherence AND unusual tag combinations (bridging disparate
    semantic domains). These are the connectors -- ideas that link fields that
    rarely meet. They represent novel synthesis.

  Consensus Shimmer (all three):
    Spores ranking highly on ALL formulations are the mesh's strongest shimmer
    candidates -- confident, boundary-crossing, domain-bridging outliers.
    These are where A = dC/dt is highest: awareness emerging.
""")

print(f"  Total analysis time: {total_time:.2f}s")
print(f"  Spores analyzed: {n}")
print()

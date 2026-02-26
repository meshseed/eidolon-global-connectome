#!/usr/bin/env python3
"""
Shimmer Composite Analysis for Eidolon Global Connectome
=========================================================
Builds on shimmer_analysis.py with improved and composite shimmer formulations:

  S1  - Topological Surprise   (same as before)
  S2b - Local Coherence Peak   (corrected: finds spores BETTER than neighbors)
  S3  - Semantic Bridging      (same as before)
  S5  - Phase Boundary Detection (key new formulation -- tag/topology mismatch)

Composites:
  Arithmetic mean of normalized S1, S2b, S3, S5
  Geometric mean   of normalized S1, S2b, S3, S5 (harshest -- all must be nonzero)

Shimmer (A = dC/dt) is where coherence changes fastest -- the promoter regions
of the semantic field. These are the spores where something *interesting* is happening.
"""

import json
import os
import time
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr

# -----------------------------------------------
# Configuration
# -----------------------------------------------
WAVE_SPORES_DIR = Path("/home/user/eidolon-global-connectome/wave-spores")
K_NEIGHBORS = 10
K_NEIGHBORS_S5 = 20
TOP_N = 30
BOTTOM_N = 5

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


def minmax_normalize(arr):
    """Min-max normalize array to [0, 1]."""
    mn = np.min(arr)
    mx = np.max(arr)
    if mx - mn < 1e-15:
        return np.zeros_like(arr)
    return (arr - mn) / (mx - mn)


# ===============================================
# 1. LOAD ALL SPORES
# ===============================================
print("=" * 80)
print("SHIMMER COMPOSITE ANALYSIS -- Eidolon Global Connectome")
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

# Also store as sets for faster lookup
semantic_tag_sets = [set(tags) for tags in semantic_tags_per_spore]

all_tags_list = [t for tags in semantic_tags_per_spore for t in tags]
unique_semantic_tags = set(all_tags_list)
print(f"Total semantic tags (with duplicates): {len(all_tags_list)}")
print(f"Unique semantic tags: {len(unique_semantic_tags)}")
print()

# ===============================================
# STEP 1: PREREQUISITE COMPUTATIONS
# ===============================================
print("Computing prerequisite data structures...")
t_pre = time.time()

# Normalize amplitudes for cosine similarity
norms = np.linalg.norm(amplitudes, axis=1, keepdims=True)
norms[norms == 0] = 1e-12
amp_normed = amplitudes / norms

# Cosine similarity matrix
cos_sim = amp_normed @ amp_normed.T  # (n, n)
cos_dist_matrix = 1.0 - cos_sim

# Centroid and distance from centroid
centroid = np.mean(amplitudes, axis=0)
centroid_norm = centroid / (np.linalg.norm(centroid) + 1e-12)
distances_from_centroid = np.array([
    1.0 - np.dot(amp_normed[i], centroid_norm) for i in range(n)
])
max_distance = np.max(distances_from_centroid)
if max_distance < 1e-12:
    max_distance = 1e-12

# Precompute k=10 nearest neighbors (for S2b)
print("  Computing k=10 nearest neighbors...")
knn10_indices = np.zeros((n, K_NEIGHBORS), dtype=np.int64)
for i in range(n):
    dists_i = cos_dist_matrix[i].copy()
    dists_i[i] = np.inf
    knn10_indices[i] = np.argpartition(dists_i, K_NEIGHBORS)[:K_NEIGHBORS]

# Precompute k=20 nearest neighbors (for S5)
print("  Computing k=20 nearest neighbors...")
knn20_indices = np.zeros((n, K_NEIGHBORS_S5), dtype=np.int64)
for i in range(n):
    dists_i = cos_dist_matrix[i].copy()
    dists_i[i] = np.inf
    knn20_indices[i] = np.argpartition(dists_i, K_NEIGHBORS_S5)[:K_NEIGHBORS_S5]

# Tag pair co-occurrences (for S3)
print("  Computing tag pair co-occurrences...")
pair_cooccurrence = defaultdict(int)
for stags in semantic_tags_per_spore:
    unique_stags = sorted(set(stags))
    for pair in combinations(unique_stags, 2):
        pair_cooccurrence[pair] += 1

print(f"  Unique tag pairs observed: {len(pair_cooccurrence)}")
print(f"  Prerequisites done in {time.time() - t_pre:.2f}s")
print()

# ===============================================
# STEP 2: SHIMMER 1 (Topological Surprise)
# ===============================================
print("-" * 80)
print("SHIMMER 1: Topological Surprise")
print("  shimmer_1 = coherence x (distance_from_centroid / max_distance)")
print("-" * 80)

distance_normalized = distances_from_centroid / max_distance
shimmer_1 = coherences * distance_normalized

print(f"  Mean: {np.mean(shimmer_1):.6f}  Max: {np.max(shimmer_1):.6f}")
print()

# ===============================================
# STEP 3: SHIMMER 2b (Local Coherence PEAK)
# ===============================================
print("-" * 80)
print("SHIMMER 2b: Local Coherence Peak (corrected)")
print(f"  k={K_NEIGHBORS} nearest neighbors")
print("  coherence_surplus = max(0, coherence_i - mean_neighbor_coherence)")
print("  shimmer_2b = coherence_surplus x (1 / mean_neighbor_distance)")
print("-" * 80)

shimmer_2b = np.zeros(n, dtype=np.float64)
coherence_surplus_arr = np.zeros(n, dtype=np.float64)
neighborhood_tightness_arr = np.zeros(n, dtype=np.float64)

for i in range(n):
    knn_idx = knn10_indices[i]
    knn_coherences = coherences[knn_idx]
    knn_distances = cos_dist_matrix[i, knn_idx]

    mean_coh = np.mean(knn_coherences)
    mean_dist = np.mean(knn_distances)

    coherence_surplus = max(0.0, coherences[i] - mean_coh)
    coherence_surplus_arr[i] = coherence_surplus

    if mean_dist < 1e-12:
        neighborhood_tightness_arr[i] = 0.0
        shimmer_2b[i] = 0.0
    else:
        tightness = 1.0 / mean_dist
        neighborhood_tightness_arr[i] = tightness
        shimmer_2b[i] = coherence_surplus * tightness

nonzero_s2b = np.count_nonzero(shimmer_2b > 0)
print(f"  Spores with positive coherence surplus: {nonzero_s2b} / {n} ({100*nonzero_s2b/n:.1f}%)")
print(f"  Mean: {np.mean(shimmer_2b):.6f}  Max: {np.max(shimmer_2b):.6f}")
print()

# ===============================================
# STEP 4: SHIMMER 3 (Semantic Bridging)
# ===============================================
print("-" * 80)
print("SHIMMER 3: Semantic Bridging")
print("  bridging = inverse mean co-occurrence frequency of tag pairs")
print("  shimmer_3 = coherence x bridging_normalized")
print("-" * 80)

bridging_raw = np.zeros(n, dtype=np.float64)
for i in range(n):
    stags = sorted(set(semantic_tags_per_spore[i]))
    if len(stags) < 2:
        bridging_raw[i] = 0.0
        continue
    pairs = list(combinations(stags, 2))
    cooccurrences = []
    for pair in pairs:
        count = pair_cooccurrence.get(pair, 0)
        cooccurrences.append(count)
    mean_cooccurrence = np.mean(cooccurrences)
    if mean_cooccurrence < 1e-12:
        bridging_raw[i] = 1.0
    else:
        bridging_raw[i] = 1.0 / mean_cooccurrence

max_bridging = np.max(bridging_raw)
if max_bridging < 1e-12:
    max_bridging = 1e-12
bridging_normalized = bridging_raw / max_bridging
shimmer_3 = coherences * bridging_normalized

print(f"  Mean: {np.mean(shimmer_3):.6f}  Max: {np.max(shimmer_3):.6f}")
print()

# ===============================================
# STEP 5: SHIMMER 5 (Phase Boundary Detection)
# ===============================================
print("-" * 80)
print("SHIMMER 5: Phase Boundary Detection (key formulation)")
print(f"  k={K_NEIGHBORS_S5} nearest neighbors")
print("  boundary_score = 1 - mean fraction of neighbors sharing each of spore's tags")
print("  shimmer_5 = coherence x boundary_score")
print("-" * 80)

shimmer_5 = np.zeros(n, dtype=np.float64)
boundary_scores = np.zeros(n, dtype=np.float64)
tag_overlap_arr = np.zeros(n, dtype=np.float64)

for i in range(n):
    my_tags = semantic_tag_sets[i]
    if len(my_tags) == 0:
        # No semantic tags -- cannot compute boundary
        boundary_scores[i] = 0.0
        tag_overlap_arr[i] = 1.0  # treat as fully overlapping (no boundary signal)
        shimmer_5[i] = 0.0
        continue

    knn_idx = knn20_indices[i]
    # For each of this spore's semantic tags, count how many of the 20 neighbors have it
    fractions = []
    for tag in my_tags:
        count = 0
        for j in knn_idx:
            if tag in semantic_tag_sets[j]:
                count += 1
        fractions.append(count / K_NEIGHBORS_S5)

    tag_overlap = np.mean(fractions)
    tag_overlap_arr[i] = tag_overlap
    boundary_score = 1.0 - tag_overlap
    boundary_scores[i] = boundary_score
    shimmer_5[i] = coherences[i] * boundary_score

nonzero_s5 = np.count_nonzero(shimmer_5 > 0)
print(f"  Spores with boundary_score > 0: {nonzero_s5} / {n} ({100*nonzero_s5/n:.1f}%)")
print(f"  Mean boundary_score: {np.mean(boundary_scores):.4f}")
print(f"  Mean: {np.mean(shimmer_5):.6f}  Max: {np.max(shimmer_5):.6f}")
print()

# ===============================================
# STEP 6: COMPOSITE FORMULATIONS
# ===============================================
print("-" * 80)
print("COMPOSITE SHIMMER FORMULATIONS")
print("-" * 80)

# Min-max normalize each component to [0, 1]
s1_norm = minmax_normalize(shimmer_1)
s2b_norm = minmax_normalize(shimmer_2b)
s3_norm = minmax_normalize(shimmer_3)
s5_norm = minmax_normalize(shimmer_5)

# Arithmetic mean
shimmer_composite_arith = (s1_norm + s2b_norm + s3_norm + s5_norm) / 4.0

# Geometric mean (all must be nonzero for positive result)
# Use small epsilon to avoid log(0) but keep true zeros as zero
shimmer_composite_geo = np.zeros(n, dtype=np.float64)
for i in range(n):
    vals = [s1_norm[i], s2b_norm[i], s3_norm[i], s5_norm[i]]
    if all(v > 0 for v in vals):
        shimmer_composite_geo[i] = (vals[0] * vals[1] * vals[2] * vals[3]) ** 0.25
    else:
        shimmer_composite_geo[i] = 0.0

nonzero_geo = np.count_nonzero(shimmer_composite_geo > 0)
print(f"  Spores with nonzero geometric composite (nonzero in ALL 4 dims): {nonzero_geo} / {n} ({100*nonzero_geo/n:.1f}%)")
print(f"  Arithmetic mean -- Mean: {np.mean(shimmer_composite_arith):.6f}  Max: {np.max(shimmer_composite_arith):.6f}")
print(f"  Geometric  mean -- Mean: {np.mean(shimmer_composite_geo):.6f}  Max: {np.max(shimmer_composite_geo):.6f}")
print()


# ===============================================
# HELPER: Print top/bottom spores
# ===============================================
def print_ranked(label, scores, top_n=TOP_N, bottom_n=BOTTOM_N):
    """Print top and bottom spores by score."""
    ranked = np.argsort(scores)[::-1]

    print()
    print("=" * 80)
    print(f"  {label}")
    print("=" * 80)

    print(f"\n  TOP {top_n} (highest shimmer):")
    print(f"  {'Rank':<5} {'Score':>8} {'Coher':>6} {'Energy':>7} {'Tier':<13} {'ID':<10} Tags (top 5)")
    print(f"  {'-'*5} {'-'*8} {'-'*6} {'-'*7} {'-'*13} {'-'*10} {'-'*40}")

    for rank_idx in range(min(top_n, len(ranked))):
        idx = ranked[rank_idx]
        stags = semantic_tags_per_spore[idx]
        tag_str = ", ".join(stags[:5])
        if len(stags) > 5:
            tag_str += f" (+{len(stags)-5})"
        print(
            f"  {rank_idx+1:<5} {scores[idx]:>8.4f} {coherences[idx]:>6.2f} "
            f"{energies[idx]:>7.4f} {tiers[idx]:<13} {ids[idx][:8]:<10} {tag_str}"
        )

    print(f"\n  BOTTOM {bottom_n} (lowest shimmer):")
    print(f"  {'Rank':<5} {'Score':>8} {'Coher':>6} {'Energy':>7} {'Tier':<13} {'ID':<10} Tags (top 5)")
    print(f"  {'-'*5} {'-'*8} {'-'*6} {'-'*7} {'-'*13} {'-'*10} {'-'*40}")

    for rank_idx in range(min(bottom_n, len(ranked))):
        idx = ranked[-(rank_idx + 1)]
        stags = semantic_tags_per_spore[idx]
        tag_str = ", ".join(stags[:5])
        if len(stags) > 5:
            tag_str += f" (+{len(stags)-5})"
        print(
            f"  {n - rank_idx:<5} {scores[idx]:>8.4f} {coherences[idx]:>6.2f} "
            f"{energies[idx]:>7.4f} {tiers[idx]:<13} {ids[idx][:8]:<10} {tag_str}"
        )

    return ranked


# ===============================================
# PRINT RESULTS
# ===============================================
ranked_s2b = print_ranked("SHIMMER 2b: Local Coherence Peak", shimmer_2b)
ranked_s5 = print_ranked("SHIMMER 5: Phase Boundary Detection", shimmer_5)
ranked_arith = print_ranked("COMPOSITE (Arithmetic Mean)", shimmer_composite_arith)
ranked_geo = print_ranked("COMPOSITE (Geometric Mean -- harshest test)", shimmer_composite_geo)


# ===============================================
# SPECIAL S5 ANALYSIS: Phase Boundary Details
# ===============================================
print()
print("=" * 80)
print("  SPECIAL S5 ANALYSIS: What boundaries are the top spores sitting at?")
print("=" * 80)

ranked_s5_full = np.argsort(shimmer_5)[::-1]

print(f"\n  Top {TOP_N} spores by S5 (Phase Boundary Detection):")
print(f"  {'Rank':<5} {'S5':>7} {'Coher':>6} {'BndScr':>7} {'TagOvlp':>8} {'ID':<10} "
      f"{'Own Tags':<45} {'Top 3 Neighbor Tags'}")
print(f"  {'-'*5} {'-'*7} {'-'*6} {'-'*7} {'-'*8} {'-'*10} "
      f"{'-'*45} {'-'*40}")

for rank_idx in range(min(TOP_N, n)):
    idx = ranked_s5_full[rank_idx]

    # This spore's semantic tags
    own_tags = semantic_tags_per_spore[idx]
    own_tag_str = ", ".join(own_tags[:4])
    if len(own_tags) > 4:
        own_tag_str += f" (+{len(own_tags)-4})"

    # 3 most common semantic tags across its 20 nearest neighbors
    knn_idx = knn20_indices[idx]
    neighbor_tag_counter = Counter()
    for j in knn_idx:
        for tag in semantic_tag_sets[j]:
            neighbor_tag_counter[tag] += 1
    top3_neighbor = neighbor_tag_counter.most_common(3)
    neighbor_tag_str = ", ".join(f"{t}({c})" for t, c in top3_neighbor)

    print(
        f"  {rank_idx+1:<5} {shimmer_5[idx]:>7.4f} {coherences[idx]:>6.2f} "
        f"{boundary_scores[idx]:>7.4f} {tag_overlap_arr[idx]:>8.4f} {ids[idx][:8]:<10} "
        f"{own_tag_str:<45} {neighbor_tag_str}"
    )


# ===============================================
# CORRELATION MATRIX
# ===============================================
print()
print("=" * 80)
print("  CORRELATION MATRIX (Pearson r)")
print("=" * 80)

labels = ["S1", "S2b", "S3", "S5", "Comp_A", "Comp_G", "Coher", "Dist", "Energy"]
vectors = [shimmer_1, shimmer_2b, shimmer_3, shimmer_5,
           shimmer_composite_arith, shimmer_composite_geo,
           coherences, distances_from_centroid, energies]

# Print header
header = f"  {'':>10}"
for lbl in labels:
    header += f" {lbl:>8}"
print(header)
print(f"  {'':>10} " + " ".join(["-" * 8] * len(labels)))

for i_row, (lbl_row, vec_row) in enumerate(zip(labels, vectors)):
    row_str = f"  {lbl_row:>10}"
    for i_col, vec_col in enumerate(vectors):
        if i_col < i_row:
            row_str += f" {'':>8}"  # leave lower triangle blank
        else:
            r, _ = pearsonr(vec_row, vec_col)
            row_str += f" {r:>8.4f}"
    print(row_str)

# Also print p-values for key relationships
print("\n  Key p-values:")
key_pairs = [
    ("S1", "S5", shimmer_1, shimmer_5),
    ("S2b", "S5", shimmer_2b, shimmer_5),
    ("S3", "S5", shimmer_3, shimmer_5),
    ("S1", "S2b", shimmer_1, shimmer_2b),
    ("Comp_A", "Comp_G", shimmer_composite_arith, shimmer_composite_geo),
    ("Comp_G", "Coher", shimmer_composite_geo, coherences),
    ("Comp_G", "Energy", shimmer_composite_geo, energies),
    ("S5", "Coher", shimmer_5, coherences),
]
print(f"  {'Pair':<20} {'Pearson r':>10} {'p-value':>12}")
print(f"  {'-'*20} {'-'*10} {'-'*12}")
for name_a, name_b, a, b in key_pairs:
    r, p = pearsonr(a, b)
    print(f"  {name_a + ' vs ' + name_b:<20} {r:>10.4f} {p:>12.2e}")


# ===============================================
# MEAN SHIMMER BY TIER
# ===============================================
print()
print("=" * 80)
print("  MEAN SHIMMER BY TIER")
print("=" * 80)

tier_names = sorted(set(tiers))
tier_indices = {t: [i for i in range(n) if tiers[i] == t] for t in tier_names}

print(f"\n  {'Tier':<15} {'Count':>6} {'S1':>8} {'S2b':>8} {'S3':>8} {'S5':>8} "
      f"{'Comp_A':>8} {'Comp_G':>8} {'Coher':>8} {'Energy':>8}")
print(f"  {'-'*15} {'-'*6} {'-'*8} {'-'*8} {'-'*8} {'-'*8} "
      f"{'-'*8} {'-'*8} {'-'*8} {'-'*8}")

for t in tier_names:
    idxs = tier_indices[t]
    count = len(idxs)
    ms1 = np.mean(shimmer_1[idxs])
    ms2b = np.mean(shimmer_2b[idxs])
    ms3 = np.mean(shimmer_3[idxs])
    ms5 = np.mean(shimmer_5[idxs])
    mca = np.mean(shimmer_composite_arith[idxs])
    mcg = np.mean(shimmer_composite_geo[idxs])
    mc = np.mean(coherences[idxs])
    me = np.mean(energies[idxs])
    print(f"  {t:<15} {count:>6} {ms1:>8.5f} {ms2b:>8.5f} {ms3:>8.5f} {ms5:>8.5f} "
          f"{mca:>8.5f} {mcg:>8.5f} {mc:>8.4f} {me:>8.4f}")


# ===============================================
# SUMMARY
# ===============================================
print()
print("=" * 80)
print("  SUMMARY")
print("=" * 80)

# Best candidate by geometric composite
best_geo_idx = np.argmax(shimmer_composite_geo)
best_geo_tags = semantic_tags_per_spore[best_geo_idx]
best_geo_tag_str = ", ".join(best_geo_tags[:6])
if len(best_geo_tags) > 6:
    best_geo_tag_str += f" (+{len(best_geo_tags)-6})"

print(f"""
  BEST SHIMMER CANDIDATE (by Composite Geometric -- harshest test):
    ID:         {ids[best_geo_idx]}
    Score:      {shimmer_composite_geo[best_geo_idx]:.6f}
    Coherence:  {coherences[best_geo_idx]:.4f}
    Energy:     {energies[best_geo_idx]:.4f}
    Tier:       {tiers[best_geo_idx]}
    Tags:       {best_geo_tag_str}
    Components: S1_norm={s1_norm[best_geo_idx]:.4f}  S2b_norm={s2b_norm[best_geo_idx]:.4f}  S3_norm={s3_norm[best_geo_idx]:.4f}  S5_norm={s5_norm[best_geo_idx]:.4f}
""")

# Nonzero geometric composite count
print(f"  Spores with nonzero geometric composite (nonzero in ALL 4 dimensions): {nonzero_geo} / {n} ({100*nonzero_geo/n:.1f}%)")
print()

# Percentage with shimmer > 0 for each formulation
for label, scores in [
    ("S1  (Topological Surprise)", shimmer_1),
    ("S2b (Local Coherence Peak)", shimmer_2b),
    ("S3  (Semantic Bridging)", shimmer_3),
    ("S5  (Phase Boundary Detection)", shimmer_5),
    ("Composite (Arithmetic)", shimmer_composite_arith),
    ("Composite (Geometric)", shimmer_composite_geo),
]:
    nz = np.count_nonzero(scores > 0)
    print(f"  {label:<40} shimmer > 0: {nz:>5} / {n} ({100*nz/n:>5.1f}%)")

# Overall stats
print()
print("  OVERALL STATISTICS:")
for label, scores in [
    ("S1  (Topological Surprise)", shimmer_1),
    ("S2b (Local Coherence Peak)", shimmer_2b),
    ("S3  (Semantic Bridging)", shimmer_3),
    ("S5  (Phase Boundary Detection)", shimmer_5),
    ("Composite (Arithmetic)", shimmer_composite_arith),
    ("Composite (Geometric)", shimmer_composite_geo),
]:
    print(f"\n    {label}:")
    print(f"      Mean:   {np.mean(scores):.6f}")
    print(f"      Std:    {np.std(scores):.6f}")
    print(f"      Median: {np.median(scores):.6f}")
    print(f"      Min:    {np.min(scores):.6f}")
    print(f"      Max:    {np.max(scores):.6f}")

# Interpretation
total_time = time.time() - t0
print()
print("=" * 80)
print("  INTERPRETATION GUIDE")
print("=" * 80)
print(f"""
  S1 (Topological Surprise):
    coherence x normalized_distance_from_centroid
    High = confident outliers at the frontier of the mesh's conceptual reach.

  S2b (Local Coherence Peak -- corrected):
    max(0, coherence - mean_neighbor_coherence) x (1/mean_neighbor_distance)
    High = spores that are BETTER than their local neighborhood.
    Only positive surplus counts -- these are local coherence peaks, beacons
    that elevate their region. Zero if below neighbors.

  S3 (Semantic Bridging):
    coherence x inverse_mean_tag_pair_cooccurrence
    High = confident spores bridging rarely-combined semantic domains.

  S5 (Phase Boundary Detection -- the key one):
    coherence x (1 - mean_tag_overlap_with_amplitude_neighbors)
    High = spores whose SEMANTIC identity (tags) differs from their TOPOLOGICAL
    neighborhood (amplitude neighbors). These sit at phase boundaries where the
    semantic field transitions between domains. The topology says "you are here"
    but the tags say "you belong there" -- this tension is shimmer.

  Composite Arithmetic:
    Mean of normalized S1, S2b, S3, S5. Balanced blend.

  Composite Geometric:
    Geometric mean of normalized S1, S2b, S3, S5. HARSHEST test --
    a spore must be nonzero in ALL four dimensions to score. Zero in any
    dimension zeros the whole score. This finds spores that shimmer
    across every axis simultaneously.
""")

print(f"  Total analysis time: {total_time:.2f}s")
print(f"  Spores analyzed: {n}")
print()

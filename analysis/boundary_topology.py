#!/usr/bin/env python3
"""
Boundary Topology Analysis — Eidolon Global Connectome
=======================================================

Part 1: Per-mode amplitude variance analysis across all 200 PCA modes.
Part 2: Phase boundary topology — semantic continent mapping via clustering
         and S5 shimmer boundary detection.

Author: meshseed / Claude Code analysis
Date: 2026-02-16
"""

import json
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.spatial.distance import cdist

# Try sklearn, fall back to manual implementation
try:
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("[INFO] sklearn not available — using manual k-means implementation.\n")

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("[INFO] matplotlib not available — skipping plot generation.\n")

# --- Configuration -----------------------------------------------------------

SPORE_DIR = Path("/home/user/eidolon-global-connectome/wave-spores")
OUTPUT_DIR = Path("/home/user/eidolon-global-connectome/analysis")
N_DIMS = 200

# System tag prefixes to exclude from semantic analysis
SYSTEM_TAG_PREFIXES = (
    "#embed:", "#dna:", "#synthesis:", "#source:", "#calibration",
    "#public", "#tier:", "#P-series", "#golden_connectome",
    "#calibration_anchor", "#invariance"
)

# --- Data Loading ------------------------------------------------------------

def load_all_spores():
    """Load all wave spore JSON files. Returns list of dicts."""
    spores = []
    errors = 0
    for fname in sorted(os.listdir(SPORE_DIR)):
        if not fname.endswith(".json"):
            continue
        fpath = SPORE_DIR / fname
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
            if 'amplitudes' in data and len(data['amplitudes']) == N_DIMS:
                spores.append(data)
            else:
                errors += 1
        except (json.JSONDecodeError, KeyError) as e:
            errors += 1
    print(f"Loaded {len(spores)} spores ({errors} errors/skipped)")
    return spores


def filter_semantic_tags(tags):
    """Filter out system tags, return only semantic tags."""
    return [t for t in tags if not any(t.startswith(p) for p in SYSTEM_TAG_PREFIXES)]


def extract_matrices(spores):
    """Extract amplitude matrix, metadata arrays."""
    n = len(spores)
    amplitudes = np.zeros((n, N_DIMS))
    coherences = np.zeros(n)
    energies = np.zeros(n)
    ids = []
    all_tags = []
    tiers = []

    for i, sp in enumerate(spores):
        amplitudes[i] = sp['amplitudes']
        coherences[i] = sp.get('coherence_score', 0.0)
        energies[i] = sp.get('energy', 0.0)
        ids.append(sp['id'])
        all_tags.append(sp.get('tags', []))
        tiers.append(sp.get('tier', 'unknown'))

    return amplitudes, coherences, energies, ids, all_tags, tiers


# --- Part 1: Per-Mode Amplitude Variance ------------------------------------

def part1_variance_analysis(amplitudes, ids, all_tags):
    """Analyze variance, kurtosis, and anomalies per PCA mode."""
    print("\n" + "=" * 80)
    print("  PART 1: PER-MODE AMPLITUDE VARIANCE ANALYSIS")
    print("=" * 80)

    n_spores, n_modes = amplitudes.shape
    print(f"\nMatrix shape: {n_spores} spores x {n_modes} modes\n")

    # Per-mode statistics
    variances = np.var(amplitudes, axis=0)
    mean_abs = np.mean(np.abs(amplitudes), axis=0)
    kurtoses = np.array([stats.kurtosis(amplitudes[:, m], fisher=True) for m in range(n_modes)])

    # -- Print all 200 mode statistics --
    print("-" * 80)
    print(f"{'Mode':>5}  {'Variance':>12}  {'Mean|Amp|':>12}  {'Kurtosis':>12}  {'Anomaly':>8}")
    print("-" * 80)

    anomaly_modes = []
    for m in range(n_modes):
        is_anomaly = ""
        if m > 0 and variances[m] > variances[m - 1]:
            is_anomaly = "  <-- UP"
            anomaly_modes.append(m)
        print(f"{m:>5}  {variances[m]:>12.6f}  {mean_abs[m]:>12.6f}  {kurtoses[m]:>12.4f}{is_anomaly}")

    # -- Summary statistics --
    print(f"\n{'_' * 60}")
    print(f"Total variance across all modes: {variances.sum():.6f}")
    print(f"Mean variance per mode:          {variances.mean():.6f}")
    print(f"Variance of mode 0:              {variances[0]:.6f}")
    print(f"Variance of mode 199:            {variances[-1]:.6f}")
    print(f"Ratio (mode 0 / mode 199):       {variances[0] / variances[-1]:.2f}x")
    print(f"Number of anomaly modes:         {len(anomaly_modes)}")

    # -- Variance anomalies --
    print(f"\n{'=' * 60}")
    print("  VARIANCE ANOMALIES (modes where var[i] > var[i-1])")
    print(f"{'=' * 60}")

    if not anomaly_modes:
        print("  None found — variance is monotonically decreasing (expected).")
    else:
        for am in anomaly_modes:
            increase = variances[am] - variances[am - 1]
            pct = (increase / variances[am - 1]) * 100
            print(f"\n  Mode {am}: variance = {variances[am]:.6f} (prev = {variances[am-1]:.6f}, "
                  f"increase = +{increase:.6f}, +{pct:.2f}%)")
            print(f"  Kurtosis: {kurtoses[am]:.4f}")

            # Top 5 spores by absolute amplitude on this mode
            abs_amps = np.abs(amplitudes[:, am])
            top5_idx = np.argsort(abs_amps)[-5:][::-1]
            print(f"  Top 5 spores (highest |amplitude| on mode {am}):")
            for rank, idx in enumerate(top5_idx, 1):
                sem_tags = filter_semantic_tags(all_tags[idx])[:5]
                print(f"    {rank}. {ids[idx]}  |amp|={abs_amps[idx]:.4f}  "
                      f"tags={sem_tags}")

    # -- Specific modes 91 and 153 --
    print(f"\n{'=' * 60}")
    print("  SPOTLIGHT: MODES 91 AND 153 (0-indexed)")
    print(f"{'=' * 60}")

    for target_mode in [91, 153]:
        print(f"\n  Mode {target_mode}:")
        print(f"    Variance:  {variances[target_mode]:.6f}")
        print(f"    Kurtosis:  {kurtoses[target_mode]:.4f}")
        print(f"    Mean|Amp|: {mean_abs[target_mode]:.6f}")

        abs_amps = np.abs(amplitudes[:, target_mode])
        top5_idx = np.argsort(abs_amps)[-5:][::-1]
        print(f"    Top 5 spores:")
        for rank, idx in enumerate(top5_idx, 1):
            sem_tags = filter_semantic_tags(all_tags[idx])[:5]
            print(f"      {rank}. {ids[idx]}  |amp|={abs_amps[idx]:.4f}  "
                  f"tags={sem_tags}")

    # -- Expected vs actual variance --
    print(f"\n{'=' * 60}")
    print("  EXPECTED vs ACTUAL VARIANCE DECAY")
    print(f"{'=' * 60}")
    print("\n  PCA eigenvalues should decay roughly exponentially or as a power law.")
    print("  Fitting power law: var(m) ~ a * m^(-b)\n")

    # Fit power law to modes 1-199 (skip mode 0 for log fit)
    modes_for_fit = np.arange(1, n_modes)
    log_modes = np.log(modes_for_fit)
    log_vars = np.log(np.clip(variances[1:], 1e-20, None))

    # Simple linear regression on log-log
    slope, intercept, r_value, p_value, std_err = stats.linregress(log_modes, log_vars)
    a_fit = np.exp(intercept)
    b_fit = -slope

    print(f"  Power law fit: var(m) ~ {a_fit:.4f} * m^(-{b_fit:.4f})")
    print(f"  R-squared: {r_value**2:.4f}")
    print(f"  (Higher R^2 = better fit to expected power-law decay)")

    # Compute residuals for each mode
    expected_vars = np.zeros(n_modes)
    expected_vars[0] = variances[0]  # Mode 0 is the reference
    for m in range(1, n_modes):
        expected_vars[m] = a_fit * (m ** (-b_fit))

    residuals = variances - expected_vars
    print(f"\n  Modes with largest POSITIVE residual (more variance than expected):")
    top_residual_modes = np.argsort(residuals)[-10:][::-1]
    for m in top_residual_modes:
        print(f"    Mode {m:>3}: actual={variances[m]:.6f}, expected={expected_vars[m]:.6f}, "
              f"residual=+{residuals[m]:.6f}")

    print(f"\n  Modes with largest NEGATIVE residual (less variance than expected):")
    bot_residual_modes = np.argsort(residuals)[:10]
    for m in bot_residual_modes:
        print(f"    Mode {m:>3}: actual={variances[m]:.6f}, expected={expected_vars[m]:.6f}, "
              f"residual={residuals[m]:.6f}")

    # -- Plot --
    if HAS_MATPLOTLIB:
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # Variance curve
        ax = axes[0, 0]
        ax.plot(range(n_modes), variances, 'b-', linewidth=0.8, label='Actual variance')
        ax.plot(range(n_modes), expected_vars, 'r--', linewidth=0.8, alpha=0.7, label='Power-law fit')
        for am in anomaly_modes:
            ax.axvline(x=am, color='orange', alpha=0.3, linewidth=0.5)
        ax.set_xlabel('PCA Mode Index')
        ax.set_ylabel('Variance')
        ax.set_title('Per-Mode Amplitude Variance')
        ax.legend()
        ax.set_yscale('log')

        # Kurtosis
        ax = axes[0, 1]
        ax.bar(range(n_modes), kurtoses, width=1.0, color='green', alpha=0.6)
        ax.set_xlabel('PCA Mode Index')
        ax.set_ylabel('Excess Kurtosis')
        ax.set_title('Per-Mode Kurtosis (peakedness)')
        ax.axhline(y=0, color='black', linewidth=0.5)

        # Mean absolute amplitude
        ax = axes[1, 0]
        ax.plot(range(n_modes), mean_abs, 'purple', linewidth=0.8)
        ax.set_xlabel('PCA Mode Index')
        ax.set_ylabel('Mean |Amplitude|')
        ax.set_title('Mean Absolute Amplitude per Mode')

        # Residuals
        ax = axes[1, 1]
        ax.bar(range(n_modes), residuals, width=1.0, color='coral', alpha=0.6)
        ax.set_xlabel('PCA Mode Index')
        ax.set_ylabel('Residual (actual - expected)')
        ax.set_title('Variance Residuals from Power-Law Fit')
        ax.axhline(y=0, color='black', linewidth=0.5)

        plt.tight_layout()
        plot_path = OUTPUT_DIR / "part1_variance_analysis.png"
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"\n  Plot saved to: {plot_path}")

    return variances, kurtoses, anomaly_modes


# --- Manual K-Means (fallback) -----------------------------------------------

def manual_kmeans(X, k, max_iter=100, n_init=5, random_state=42):
    """Simple k-means implementation. Returns labels and centroids."""
    rng = np.random.RandomState(random_state)
    n, d = X.shape
    best_labels = None
    best_centroids = None
    best_inertia = np.inf

    for init_run in range(n_init):
        # k-means++ initialization
        centroids = np.zeros((k, d))
        idx = rng.randint(0, n)
        centroids[0] = X[idx]
        for c in range(1, k):
            dists = cdist(X, centroids[:c], metric='euclidean')
            min_dists = np.min(dists, axis=1) ** 2
            probs = min_dists / min_dists.sum()
            idx = rng.choice(n, p=probs)
            centroids[c] = X[idx]

        # Iterate
        for _ in range(max_iter):
            dists = cdist(X, centroids, metric='euclidean')
            labels = np.argmin(dists, axis=1)

            new_centroids = np.zeros_like(centroids)
            for c in range(k):
                mask = labels == c
                if mask.sum() > 0:
                    new_centroids[c] = X[mask].mean(axis=0)
                else:
                    new_centroids[c] = centroids[c]

            if np.allclose(centroids, new_centroids, atol=1e-6):
                break
            centroids = new_centroids

        # Inertia
        dists = cdist(X, centroids, metric='euclidean')
        inertia = sum(dists[i, labels[i]] ** 2 for i in range(n))
        if inertia < best_inertia:
            best_inertia = inertia
            best_labels = labels
            best_centroids = centroids

    return best_labels, best_centroids


def manual_silhouette_score(X, labels, sample_size=2000, random_state=42):
    """Compute silhouette score (sampled for speed)."""
    rng = np.random.RandomState(random_state)
    n = len(labels)
    if n > sample_size:
        idx = rng.choice(n, sample_size, replace=False)
        X_sample = X[idx]
        labels_sample = labels[idx]
    else:
        X_sample = X
        labels_sample = labels

    n_s = len(labels_sample)
    unique_labels = np.unique(labels_sample)
    if len(unique_labels) < 2:
        return 0.0

    dists = cdist(X_sample, X_sample, metric='euclidean')
    silhouettes = np.zeros(n_s)

    for i in range(n_s):
        cluster_i = labels_sample[i]
        same_mask = labels_sample == cluster_i
        same_mask[i] = False

        if same_mask.sum() == 0:
            silhouettes[i] = 0.0
            continue

        a_i = dists[i, same_mask].mean()

        b_i = np.inf
        for cl in unique_labels:
            if cl == cluster_i:
                continue
            other_mask = labels_sample == cl
            if other_mask.sum() > 0:
                b_i = min(b_i, dists[i, other_mask].mean())

        silhouettes[i] = (b_i - a_i) / max(a_i, b_i) if max(a_i, b_i) > 0 else 0.0

    return silhouettes.mean()


# --- Part 2: Phase Boundary Topology -----------------------------------------

def compute_s5_shimmer(amplitudes, coherences, all_tags, k_neighbors=20):
    """
    Compute S5 (Phase Boundary Shimmer) for each spore.

    For each spore, find k nearest neighbors by amplitude cosine similarity.
    For each of the spore's semantic tags, count what fraction of the k neighbors
    share that tag. S5 = coherence * (1 - mean_tag_overlap).
    """
    print("\n  Computing S5 shimmer scores (k=20 neighbors)...")
    n = len(amplitudes)

    # Normalize for cosine similarity
    norms = np.linalg.norm(amplitudes, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    amp_normed = amplitudes / norms

    # Build tag sets (semantic only)
    tag_sets = []
    for tags in all_tags:
        sem = set(filter_semantic_tags(tags))
        tag_sets.append(sem)

    s5_scores = np.zeros(n)
    boundary_scores = np.zeros(n)

    # Process in batches for memory efficiency
    batch_size = 500
    for start in range(0, n, batch_size):
        end = min(start + batch_size, n)
        batch = amp_normed[start:end]

        # Cosine similarity: batch x all
        sims = batch @ amp_normed.T  # (batch_size, n)

        for bi, gi in enumerate(range(start, end)):
            # Zero out self
            sims[bi, gi] = -np.inf
            # Top k neighbors
            top_k_idx = np.argpartition(sims[bi], -k_neighbors)[-k_neighbors:]

            my_tags = tag_sets[gi]
            if len(my_tags) == 0:
                boundary_scores[gi] = 1.0
                s5_scores[gi] = coherences[gi]
                continue

            # For each of my tags, what fraction of neighbors share it?
            neighbor_tag_sets = [tag_sets[j] for j in top_k_idx]
            tag_overlaps = []
            for tag in my_tags:
                count = sum(1 for nts in neighbor_tag_sets if tag in nts)
                tag_overlaps.append(count / k_neighbors)

            mean_overlap = np.mean(tag_overlaps)
            boundary_scores[gi] = 1.0 - mean_overlap
            s5_scores[gi] = coherences[gi] * boundary_scores[gi]

    print(f"  S5 shimmer: mean={s5_scores.mean():.4f}, std={s5_scores.std():.4f}, "
          f"min={s5_scores.min():.4f}, max={s5_scores.max():.4f}")

    return s5_scores, boundary_scores


def run_kmeans(amplitudes, k, random_state=42):
    """Run k-means clustering, return labels and centroids."""
    if HAS_SKLEARN:
        km = KMeans(n_clusters=k, random_state=random_state, n_init=10, max_iter=300)
        labels = km.fit_predict(amplitudes)
        centroids = km.cluster_centers_
    else:
        labels, centroids = manual_kmeans(amplitudes, k, random_state=random_state)
    return labels, centroids


def compute_silhouette(amplitudes, labels):
    """Compute silhouette score."""
    if HAS_SKLEARN:
        # Sample for speed if large
        n = len(labels)
        if n > 5000:
            rng = np.random.RandomState(42)
            idx = rng.choice(n, 5000, replace=False)
            return silhouette_score(amplitudes[idx], labels[idx])
        return silhouette_score(amplitudes, labels)
    else:
        return manual_silhouette_score(amplitudes, labels)


def cluster_summary(labels, coherences, energies, s5_scores, all_tags, tiers, ids):
    """Build per-cluster summary."""
    unique_labels = sorted(np.unique(labels))
    summaries = []

    for cl in unique_labels:
        mask = labels == cl
        indices = np.where(mask)[0]
        size = mask.sum()

        mean_coh = coherences[mask].mean()
        mean_energy = energies[mask].mean()
        mean_s5 = s5_scores[mask].mean()

        # Tier distribution
        tier_counts = Counter(tiers[i] for i in indices)

        # Top semantic tags
        tag_counter = Counter()
        for i in indices:
            for t in filter_semantic_tags(all_tags[i]):
                tag_counter[t] += 1
        top_tags = tag_counter.most_common(5)

        summaries.append({
            'cluster': cl,
            'size': size,
            'mean_coherence': mean_coh,
            'mean_energy': mean_energy,
            'mean_s5': mean_s5,
            'tier_dist': tier_counts,
            'top_tags': top_tags,
            'indices': indices,
        })

    return summaries


def part2_boundary_topology(amplitudes, coherences, energies, ids, all_tags, tiers):
    """Full phase boundary topology analysis."""
    print("\n" + "=" * 80)
    print("  PART 2: PHASE BOUNDARY TOPOLOGY (SEMANTIC CONTINENTS)")
    print("=" * 80)

    n_spores = len(amplitudes)
    tiers_arr = np.array(tiers)

    # -- Compute S5 shimmer --
    s5_scores, boundary_scores = compute_s5_shimmer(amplitudes, coherences, all_tags)

    # -- Step 1: Clustering with multiple k values --
    print(f"\n{'_' * 60}")
    print("  STEP 1: K-MEANS CLUSTERING")
    print(f"{'_' * 60}")

    k_values = [8, 12, 16, 20]
    results = {}

    for k in k_values:
        t0 = time.time()
        labels, centroids = run_kmeans(amplitudes, k)
        sil = compute_silhouette(amplitudes, labels)
        elapsed = time.time() - t0

        summaries = cluster_summary(labels, coherences, energies, s5_scores, all_tags, tiers, ids)

        results[k] = {
            'labels': labels,
            'centroids': centroids,
            'silhouette': sil,
            'summaries': summaries,
        }

        print(f"\n  k={k}: silhouette={sil:.4f} ({elapsed:.1f}s)")
        for s in summaries:
            tag_str = ", ".join(t[0] for t in s['top_tags'][:3])
            print(f"    Cluster {s['cluster']:>2}: size={s['size']:>4}, "
                  f"coh={s['mean_coherence']:.3f}, S5={s['mean_s5']:.3f}, "
                  f"tags=[{tag_str}]")

    # -- Step 2: Pick best k --
    best_k = max(k_values, key=lambda k: results[k]['silhouette'])
    print(f"\n{'_' * 60}")
    print(f"  STEP 2: BEST K = {best_k} (silhouette = {results[best_k]['silhouette']:.4f})")
    print(f"{'_' * 60}")

    print("\n  Silhouette comparison:")
    for k in k_values:
        marker = " <-- BEST" if k == best_k else ""
        print(f"    k={k:>2}: {results[k]['silhouette']:.4f}{marker}")

    best = results[best_k]
    best_labels = best['labels']
    best_summaries = best['summaries']

    # -- Step 3: Map S5 shimmer to boundaries --
    print(f"\n{'_' * 60}")
    print(f"  STEP 3: S5 SHIMMER vs CLUSTER BOUNDARY FRACTION (k={best_k})")
    print(f"{'_' * 60}")

    print("\n  Computing boundary fraction (k=10 nearest neighbors)...")

    # Normalize amplitudes for cosine
    norms = np.linalg.norm(amplitudes, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    amp_normed = amplitudes / norms

    k_nn = 10
    boundary_fractions = np.zeros(n_spores)

    batch_size = 500
    for start in range(0, n_spores, batch_size):
        end = min(start + batch_size, n_spores)
        batch = amp_normed[start:end]
        sims = batch @ amp_normed.T

        for bi, gi in enumerate(range(start, end)):
            sims[bi, gi] = -np.inf
            top_k_idx = np.argpartition(sims[bi], -k_nn)[-k_nn:]
            my_cluster = best_labels[gi]
            diff_count = sum(1 for j in top_k_idx if best_labels[j] != my_cluster)
            boundary_fractions[gi] = diff_count / k_nn

    # Correlation
    corr_s5_bf, pval_s5_bf = stats.pearsonr(s5_scores, boundary_fractions)
    corr_bs_bf, pval_bs_bf = stats.pearsonr(boundary_scores, boundary_fractions)

    print(f"\n  Correlation: S5_shimmer vs boundary_fraction:")
    print(f"    Pearson r = {corr_s5_bf:.4f}, p-value = {pval_s5_bf:.2e}")
    print(f"\n  Correlation: boundary_score (tag-based) vs boundary_fraction (cluster-based):")
    print(f"    Pearson r = {corr_bs_bf:.4f}, p-value = {pval_bs_bf:.2e}")

    # Quartile analysis
    print(f"\n  S5 shimmer by boundary fraction quartile:")
    for q_low, q_high, label in [(0, 0.25, "Interior (0-25%)"),
                                   (0.25, 0.5, "Near-boundary (25-50%)"),
                                   (0.5, 0.75, "Boundary (50-75%)"),
                                   (0.75, 1.01, "Deep boundary (75-100%)")]:
        mask = (boundary_fractions >= q_low) & (boundary_fractions < q_high)
        if mask.sum() > 0:
            print(f"    {label:>25}: n={mask.sum():>4}, mean S5={s5_scores[mask].mean():.4f}, "
                  f"mean coherence={coherences[mask].mean():.4f}")

    # Plot
    if HAS_MATPLOTLIB:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        ax = axes[0]
        scatter = ax.scatter(boundary_fractions, s5_scores, c=coherences,
                             cmap='viridis', alpha=0.3, s=5)
        ax.set_xlabel('Boundary Fraction (cluster-based)')
        ax.set_ylabel('S5 Shimmer Score')
        ax.set_title(f'S5 Shimmer vs Cluster Boundary Fraction\nr={corr_s5_bf:.3f}')
        plt.colorbar(scatter, ax=ax, label='Coherence')

        ax = axes[1]
        scatter = ax.scatter(boundary_fractions, boundary_scores, c=s5_scores,
                             cmap='plasma', alpha=0.3, s=5)
        ax.set_xlabel('Boundary Fraction (cluster-based)')
        ax.set_ylabel('Boundary Score (tag-based)')
        ax.set_title(f'Tag-Based vs Cluster-Based Boundary\nr={corr_bs_bf:.3f}')
        plt.colorbar(scatter, ax=ax, label='S5 Shimmer')

        plt.tight_layout()
        plot_path = OUTPUT_DIR / "part2_s5_vs_boundary.png"
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"\n  Plot saved to: {plot_path}")

    # -- Step 4: Major boundaries -- bridge spores --
    print(f"\n{'_' * 60}")
    print(f"  STEP 4: MAJOR BOUNDARIES (BRIDGE SPORES)")
    print(f"{'_' * 60}")

    # For each spore, find which clusters its neighbors belong to
    bridge_pairs = defaultdict(list)  # (min_cl, max_cl) -> list of spore indices

    for start in range(0, n_spores, batch_size):
        end = min(start + batch_size, n_spores)
        batch = amp_normed[start:end]
        sims = batch @ amp_normed.T

        for bi, gi in enumerate(range(start, end)):
            sims[bi, gi] = -np.inf
            top_k_idx = np.argpartition(sims[bi], -k_nn)[-k_nn:]
            my_cluster = best_labels[gi]
            neighbor_clusters = set(best_labels[j] for j in top_k_idx)
            neighbor_clusters.discard(my_cluster)

            for nc in neighbor_clusters:
                pair = (min(my_cluster, nc), max(my_cluster, nc))
                bridge_pairs[pair].append(gi)

    # Sort pairs by bridge count
    pair_counts = [(pair, len(indices)) for pair, indices in bridge_pairs.items()]
    pair_counts.sort(key=lambda x: -x[1])

    # Get cluster tag summaries for reference
    cluster_tag_map = {}
    for s in best_summaries:
        cluster_tag_map[s['cluster']] = [t[0] for t in s['top_tags']]

    print(f"\n  Total cluster-pair boundaries: {len(pair_counts)}")
    print(f"\n  Top 5 boundaries by bridge spore count:\n")

    for rank, (pair, count) in enumerate(pair_counts[:5], 1):
        cl_a, cl_b = pair
        tags_a = cluster_tag_map.get(cl_a, [])
        tags_b = cluster_tag_map.get(cl_b, [])

        # Find size of each cluster
        size_a = int((best_labels == cl_a).sum())
        size_b = int((best_labels == cl_b).sum())

        print(f"  Boundary #{rank}: Cluster {cl_a} <-> Cluster {cl_b}  "
              f"({count} bridge spores)")
        print(f"    Cluster {cl_a} (n={size_a}): {tags_a}")
        print(f"    Cluster {cl_b} (n={size_b}): {tags_b}")

        # Top 5 bridge spores by S5 shimmer
        bridge_indices = bridge_pairs[pair]
        bridge_s5 = [(idx, s5_scores[idx]) for idx in bridge_indices]
        bridge_s5.sort(key=lambda x: -x[1])
        print(f"    Top 5 bridge spores (highest S5 shimmer):")
        for brank, (idx, s5) in enumerate(bridge_s5[:5], 1):
            sem_tags = filter_semantic_tags(all_tags[idx])[:5]
            print(f"      {brank}. {ids[idx]}  S5={s5:.4f}  coh={coherences[idx]:.3f}  "
                  f"cluster={best_labels[idx]}  tags={sem_tags}")
        print()

    # -- Step 5: Cluster summary table --
    print(f"\n{'_' * 60}")
    print(f"  STEP 5: CLUSTER SUMMARY TABLE (k={best_k})")
    print(f"{'_' * 60}")

    print(f"\n  {'Cl':>3} {'Size':>5} {'MeanCoh':>8} {'MeanS5':>8} {'MeanE':>8} "
          f"{'Core':>5} {'Conv':>5} {'Ref':>5}  Top Tags")
    print(f"  {'_'*3} {'_'*5} {'_'*8} {'_'*8} {'_'*8} {'_'*5} {'_'*5} {'_'*5}  {'_'*40}")

    for s in best_summaries:
        core_n = s['tier_dist'].get('core', 0)
        conv_n = s['tier_dist'].get('convergence', 0)
        ref_n = s['tier_dist'].get('reference', 0)
        tag_str = ", ".join(t[0] for t in s['top_tags'][:5])
        print(f"  {s['cluster']:>3} {s['size']:>5} {s['mean_coherence']:>8.4f} "
              f"{s['mean_s5']:>8.4f} {s['mean_energy']:>8.4f} "
              f"{core_n:>5} {conv_n:>5} {ref_n:>5}  {tag_str}")

    # Identify core and frontier clusters
    core_cluster = max(best_summaries, key=lambda s: s['mean_coherence'])
    frontier_cluster = max(best_summaries, key=lambda s: s['mean_s5'])

    print(f"\n  CORE cluster (highest mean coherence): "
          f"Cluster {core_cluster['cluster']} "
          f"(coh={core_cluster['mean_coherence']:.4f}, size={core_cluster['size']})")
    print(f"    Top tags: {[t[0] for t in core_cluster['top_tags'][:5]]}")

    print(f"\n  FRONTIER cluster (highest mean S5 shimmer): "
          f"Cluster {frontier_cluster['cluster']} "
          f"(S5={frontier_cluster['mean_s5']:.4f}, size={frontier_cluster['size']})")
    print(f"    Top tags: {[t[0] for t in frontier_cluster['top_tags'][:5]]}")

    # Largest cluster
    largest = max(best_summaries, key=lambda s: s['size'])
    smallest = min(best_summaries, key=lambda s: s['size'])
    print(f"\n  LARGEST cluster:  Cluster {largest['cluster']} (n={largest['size']})")
    print(f"    Top tags: {[t[0] for t in largest['top_tags'][:5]]}")
    print(f"  SMALLEST cluster: Cluster {smallest['cluster']} (n={smallest['size']})")
    print(f"    Top tags: {[t[0] for t in smallest['top_tags'][:5]]}")

    # -- Full cluster overview plot --
    if HAS_MATPLOTLIB:
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # Silhouette by k
        ax = axes[0, 0]
        sils = [results[k]['silhouette'] for k in k_values]
        ax.bar([str(k) for k in k_values], sils, color='steelblue')
        ax.set_xlabel('Number of clusters (k)')
        ax.set_ylabel('Silhouette Score')
        ax.set_title('Silhouette Score by k')
        for i, v in enumerate(sils):
            ax.text(i, v + 0.002, f'{v:.3f}', ha='center', fontsize=9)

        # Cluster sizes
        ax = axes[0, 1]
        cl_ids = [s['cluster'] for s in best_summaries]
        cl_sizes = [s['size'] for s in best_summaries]
        colors = plt.cm.Set3(np.linspace(0, 1, len(cl_ids)))
        ax.bar([str(c) for c in cl_ids], cl_sizes, color=colors)
        ax.set_xlabel('Cluster ID')
        ax.set_ylabel('Size')
        ax.set_title(f'Cluster Sizes (k={best_k})')

        # Coherence vs S5 per cluster
        ax = axes[1, 0]
        cohs = [s['mean_coherence'] for s in best_summaries]
        s5s = [s['mean_s5'] for s in best_summaries]
        sizes = [s['size'] for s in best_summaries]
        scatter = ax.scatter(cohs, s5s, s=[sz * 2 for sz in sizes],
                             c=cl_ids, cmap='Set3', edgecolors='black', linewidth=0.5)
        for i, cl in enumerate(cl_ids):
            ax.annotate(str(cl), (cohs[i], s5s[i]), fontsize=8, ha='center')
        ax.set_xlabel('Mean Coherence')
        ax.set_ylabel('Mean S5 Shimmer')
        ax.set_title('Cluster: Coherence vs S5 (size = bubble size)')

        # PCA 2D projection colored by cluster
        ax = axes[1, 1]
        scatter = ax.scatter(amplitudes[:, 0], amplitudes[:, 1],
                             c=best_labels, cmap='Set3', alpha=0.3, s=3)
        ax.set_xlabel('PCA Mode 0')
        ax.set_ylabel('PCA Mode 1')
        ax.set_title(f'Spores in PCA Space (colored by cluster, k={best_k})')

        plt.tight_layout()
        plot_path = OUTPUT_DIR / "part2_cluster_overview.png"
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"\n  Plot saved to: {plot_path}")

    return results, s5_scores, boundary_fractions


# --- Main --------------------------------------------------------------------

def main():
    print("=" * 80)
    print("  EIDOLON GLOBAL CONNECTOME -- BOUNDARY TOPOLOGY ANALYSIS")
    print("  Date: 2026-02-16")
    print("=" * 80)

    t_start = time.time()

    # Load data
    print("\n  Loading spores...")
    spores = load_all_spores()
    amplitudes, coherences, energies, ids, all_tags, tiers = extract_matrices(spores)

    print(f"  Amplitude matrix: {amplitudes.shape}")
    print(f"  Coherence range: [{coherences.min():.3f}, {coherences.max():.3f}], mean={coherences.mean():.3f}")
    print(f"  Energy range: [{energies.min():.3f}, {energies.max():.3f}], mean={energies.mean():.3f}")

    # Part 1
    variances, kurtoses, anomaly_modes = part1_variance_analysis(amplitudes, ids, all_tags)

    # Part 2
    results, s5_scores, boundary_fractions = part2_boundary_topology(
        amplitudes, coherences, energies, ids, all_tags, tiers
    )

    elapsed = time.time() - t_start
    print(f"\n{'=' * 80}")
    print(f"  ANALYSIS COMPLETE -- {elapsed:.1f}s total")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()

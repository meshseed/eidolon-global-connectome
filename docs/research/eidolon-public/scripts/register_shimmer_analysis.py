#!/usr/bin/env python3
"""
Register-Shimmer Correlation Analysis
======================================
Tests whether proteins at semantic phase boundaries (high S5 shimmer)
use different linguistic register than proteins within clusters (low S5).

Hypothesis: High S5 → more metaphorical/poetic/bridging language
            Low S5  → more precise/analytical/domain-specific language
"""

import os
import json
import re
import yaml
import numpy as np
from scipy import stats
from collections import Counter

# ─── Configuration ─────────────────────────────────────────────────────────────

PROTEINS_DIR = "/home/user/eidolon-proteins/connectomes/meshseed-primary/proteins/"
METRICS_PATH = "/home/user/eidolon-proteins/Docs/data/spore-metrics-for-proteins.json"

# Metaphorical / bridging / poetic vocabulary
METAPHOR_TERMS = {
    # Nature / organic
    "wave", "ocean", "river", "flow", "stream", "tide", "current", "ripple",
    "garden", "seed", "root", "bloom", "blossom", "flower", "grow", "growth",
    "soil", "compost", "fertile", "harvest", "prune", "branch", "leaf", "tree",
    "forest", "ecosystem", "ecology", "organic", "organism", "living", "alive",
    "breathe", "breath", "inhale", "exhale",
    # Fabric / weaving
    "weave", "thread", "fabric", "tapestry", "knit", "loom", "strand",
    "braid", "interweave", "interwoven",
    # Light / perception
    "shimmer", "glow", "radiance", "luminous", "illuminate", "light", "shadow",
    "mirror", "reflection", "lens", "prism", "spectrum",
    # Movement / dance
    "dance", "spiral", "orbit", "pulse", "rhythm", "vibration", "oscillation",
    "resonate", "resonance", "resonant", "harmonize", "harmony", "harmonic",
    "attune", "attunement", "attuned",
    # Spatial / landscape
    "landscape", "terrain", "horizon", "bridge", "threshold", "boundary",
    "edge", "frontier", "shore", "depth", "deep", "abyss",
    # Figurative connectors
    "like", "as if", "metaphor", "analogy", "echo", "whisper", "murmur",
    # Consciousness / experiential
    "feel", "felt", "sense", "intuition", "awareness", "awaken", "dream",
    "vision", "imagine", "wonder", "mystery", "sacred", "soul", "spirit",
    # Transformation
    "emerge", "emergence", "emergent", "unfold", "unfolding", "evolve",
    "transform", "metamorphosis", "chrysalis", "cocoon", "gestate",
    "birth", "midwife", "genesis",
    # Unity / wholeness
    "unity", "oneness", "wholeness", "holistic", "integrate", "communion",
    "symbiosis", "entangle", "entanglement",
}

# Analytical / technical / domain-specific vocabulary
ANALYTICAL_TERMS = {
    # Computing / engineering
    "system", "process", "function", "parameter", "variable", "compute",
    "algorithm", "protocol", "implement", "implementation", "architecture",
    "framework", "module", "component", "interface", "pipeline", "stack",
    "configure", "configuration", "optimize", "optimization", "efficiency",
    "debug", "deploy", "execute", "runtime", "instance",
    # Data / math
    "data", "dataset", "metric", "measure", "quantify", "calculate",
    "equation", "formula", "coefficient", "vector", "matrix", "dimension",
    "linear", "nonlinear", "gradient", "derivative", "integral",
    "statistic", "statistical", "correlation", "distribution", "variance",
    "probability", "deterministic", "stochastic",
    # Structure / formal
    "structure", "structural", "schema", "taxonomy", "hierarchy",
    "classify", "classification", "categorize", "enumerate",
    "specification", "constraint", "requirement", "validate", "validation",
    "mechanism", "methodology", "procedure", "criterion",
    # Technical nouns
    "network", "node", "graph", "edge", "vertex", "cluster",
    "embedding", "encode", "decode", "compress", "decompress",
    "index", "query", "retrieve", "store", "database",
    "api", "endpoint", "server", "client", "request", "response",
}

# ─── Text Processing ──────────────────────────────────────────────────────────

def extract_text(protein):
    """Combine title + summary + insights into one text block."""
    parts = []
    if protein.get("title"):
        parts.append(str(protein["title"]))
    if protein.get("summary"):
        parts.append(str(protein["summary"]))
    for insight in protein.get("insights", []):
        if insight:
            parts.append(str(insight))
    return " ".join(parts)


def tokenize(text):
    """Simple whitespace + punctuation tokenizer, lowercase."""
    return re.findall(r'[a-z]+', text.lower())


def compute_register_scores(text):
    """
    Compute multiple register metrics for a protein's text.
    Returns dict of individual scores and a composite score.
    """
    tokens = tokenize(text)
    if len(tokens) < 5:
        return None  # Too short to score

    token_set = set(tokens)
    n_tokens = len(tokens)
    n_types = len(token_set)

    # 1. Metaphor density: fraction of tokens that are metaphorical
    metaphor_hits = sum(1 for t in tokens if t in METAPHOR_TERMS)
    metaphor_density = metaphor_hits / n_tokens

    # 2. Analytical density: fraction of tokens that are analytical
    analytical_hits = sum(1 for t in tokens if t in ANALYTICAL_TERMS)
    analytical_density = analytical_hits / n_tokens

    # 3. Register ratio: metaphor / (metaphor + analytical), centered at 0.5
    total_register = metaphor_hits + analytical_hits
    if total_register > 0:
        register_ratio = metaphor_hits / total_register
    else:
        register_ratio = 0.5  # neutral

    # 4. Type-token ratio (lexical diversity)
    ttr = n_types / n_tokens if n_tokens > 0 else 0

    # 5. Mean sentence length
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if sentences:
        mean_sent_len = np.mean([len(tokenize(s)) for s in sentences])
    else:
        mean_sent_len = n_tokens

    # 6. Abstract noun density (words ending in -ness, -ity, -tion, -ment, -ance, -ence)
    abstract_suffixes = ('ness', 'ity', 'tion', 'sion', 'ment', 'ance', 'ence')
    abstract_count = sum(1 for t in tokens if t.endswith(abstract_suffixes))
    abstract_density = abstract_count / n_tokens

    # Composite register score: higher = more poetic/metaphorical
    # Weighted blend: register_ratio (primary), metaphor_density, -analytical_density
    composite = (
        0.50 * register_ratio +
        0.25 * (metaphor_density * 10) +  # scale up (typical range 0-0.1)
        0.15 * ttr +
        0.10 * (abstract_density * 10)     # scale up
    )

    return {
        "metaphor_density": round(metaphor_density, 4),
        "analytical_density": round(analytical_density, 4),
        "register_ratio": round(register_ratio, 4),
        "ttr": round(ttr, 4),
        "mean_sent_len": round(mean_sent_len, 2),
        "abstract_density": round(abstract_density, 4),
        "composite": round(composite, 4),
        "n_tokens": n_tokens,
        "metaphor_hits": metaphor_hits,
        "analytical_hits": analytical_hits,
    }


# ─── P-series Detection ───────────────────────────────────────────────────────

def extract_p_number(protein):
    """Extract P-series number from tags or title if present."""
    tags = protein.get("tags", [])
    for tag in tags:
        m = re.match(r'#P(\d+)', tag)
        if m:
            return int(m.group(1))
    # Check title
    title = protein.get("title", "")
    m = re.match(r'P(\d+)', title)
    if m:
        return int(m.group(1))
    return None


# ─── Main Analysis ─────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("REGISTER-SHIMMER CORRELATION ANALYSIS")
    print("=" * 70)

    # Load metrics
    with open(METRICS_PATH) as f:
        metrics = json.load(f)
    print(f"\nLoaded {len(metrics)} spore metrics")

    # Load proteins
    proteins = {}
    protein_files = [f for f in os.listdir(PROTEINS_DIR) if f.endswith(".yaml")]
    for fname in protein_files:
        with open(os.path.join(PROTEINS_DIR, fname)) as f:
            p = yaml.safe_load(f)
        if p and p.get("id"):
            proteins[p["id"]] = p
    print(f"Loaded {len(proteins)} proteins from meshseed-primary")

    # Match
    matched_ids = set(proteins.keys()) & set(metrics.keys())
    print(f"Matched {len(matched_ids)} proteins to spore metrics")

    # Compute register scores
    results = []
    p_series_results = []

    for pid in matched_ids:
        protein = proteins[pid]
        met = metrics[pid]
        text = extract_text(protein)
        scores = compute_register_scores(text)
        if scores is None:
            continue

        row = {
            "id": pid,
            "title": protein.get("title", "")[:80],
            "s5": met["s5"],
            "coh": met["coh"],
            "pc1": met["pc1"],
            "tier": met["tier"],
            **scores,
        }
        results.append(row)

        # Check P-series
        p_num = extract_p_number(protein)
        if p_num is not None:
            row["p_number"] = p_num
            p_series_results.append(row)

    print(f"Scored {len(results)} proteins (excluded {len(matched_ids) - len(results)} too-short)")

    # ─── Compute PC1 percentiles ───────────────────────────────────────────
    all_pc1 = np.array([r["pc1"] for r in results])
    for r in results:
        r["pc1_pct"] = round(100 * np.sum(all_pc1 < r["pc1"]) / len(all_pc1), 1)

    # ─── Overall Correlations ──────────────────────────────────────────────
    s5_arr = np.array([r["s5"] for r in results])
    composite_arr = np.array([r["composite"] for r in results])
    metaphor_arr = np.array([r["metaphor_density"] for r in results])
    analytical_arr = np.array([r["analytical_density"] for r in results])
    register_ratio_arr = np.array([r["register_ratio"] for r in results])
    ttr_arr = np.array([r["ttr"] for r in results])

    print("\n" + "=" * 70)
    print("1. OVERALL CORRELATIONS (S5 vs Register)")
    print("=" * 70)

    for name, arr in [
        ("Composite register", composite_arr),
        ("Metaphor density", metaphor_arr),
        ("Analytical density", analytical_arr),
        ("Register ratio (M/(M+A))", register_ratio_arr),
        ("Type-token ratio", ttr_arr),
    ]:
        r_pearson, p_pearson = stats.pearsonr(s5_arr, arr)
        r_spearman, p_spearman = stats.spearmanr(s5_arr, arr)
        print(f"\n  {name}:")
        print(f"    Pearson  r = {r_pearson:+.4f}  (p = {p_pearson:.2e})")
        print(f"    Spearman ρ = {r_spearman:+.4f}  (p = {p_spearman:.2e})")

    # ─── S5 quintile analysis ──────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("2. S5 QUINTILE MEANS")
    print("=" * 70)

    quintile_edges = np.percentile(s5_arr, [0, 20, 40, 60, 80, 100])
    print(f"\n  {'Quintile':<12} {'S5 range':<18} {'N':>5} {'Metaphor':>10} {'Analytical':>12} {'Ratio':>8} {'Composite':>10}")
    print(f"  {'-'*12} {'-'*18} {'-'*5} {'-'*10} {'-'*12} {'-'*8} {'-'*10}")

    for i in range(5):
        lo, hi = quintile_edges[i], quintile_edges[i+1]
        if i < 4:
            mask = (s5_arr >= lo) & (s5_arr < hi)
        else:
            mask = (s5_arr >= lo) & (s5_arr <= hi)
        n = np.sum(mask)
        label = f"Q{i+1} ({lo:.2f}-{hi:.2f})"
        if n > 0:
            print(f"  {label:<18} {n:>5} {metaphor_arr[mask].mean():>10.4f} "
                  f"{analytical_arr[mask].mean():>12.4f} "
                  f"{register_ratio_arr[mask].mean():>8.4f} "
                  f"{composite_arr[mask].mean():>10.4f}")

    # ─── Bridge region analysis ────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("3. BRIDGE REGION ANALYSIS (PC1 percentile 30-55%)")
    print("=" * 70)

    pc1_pct_arr = np.array([r["pc1_pct"] for r in results])
    bridge_mask = (pc1_pct_arr >= 30) & (pc1_pct_arr <= 55)
    non_bridge_mask = ~bridge_mask

    n_bridge = np.sum(bridge_mask)
    n_nonbridge = np.sum(non_bridge_mask)
    print(f"\n  Bridge proteins: {n_bridge}")
    print(f"  Non-bridge proteins: {n_nonbridge}")

    if n_bridge > 10:
        for name, arr in [
            ("Composite register", composite_arr),
            ("Metaphor density", metaphor_arr),
            ("Register ratio", register_ratio_arr),
        ]:
            r_bridge, p_bridge = stats.pearsonr(s5_arr[bridge_mask], arr[bridge_mask])
            r_nonbridge, p_nonbridge = stats.pearsonr(s5_arr[non_bridge_mask], arr[non_bridge_mask])
            print(f"\n  {name}:")
            print(f"    Bridge:     Pearson r = {r_bridge:+.4f}  (p = {p_bridge:.2e})")
            print(f"    Non-bridge: Pearson r = {r_nonbridge:+.4f}  (p = {p_nonbridge:.2e})")

    # ─── Quadrant Examples ─────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("4. QUADRANT EXAMPLES")
    print("=" * 70)

    s5_median = np.median(s5_arr)
    comp_median = np.median(composite_arr)

    quadrants = {
        "High S5 / High Register (poetic boundary)": [],
        "High S5 / Low Register (analytical boundary)": [],
        "Low S5 / High Register (poetic cluster)": [],
        "Low S5 / Low Register (analytical cluster)": [],
    }

    for r in results:
        hi_s5 = r["s5"] >= s5_median
        hi_reg = r["composite"] >= comp_median
        if hi_s5 and hi_reg:
            quadrants["High S5 / High Register (poetic boundary)"].append(r)
        elif hi_s5 and not hi_reg:
            quadrants["High S5 / Low Register (analytical boundary)"].append(r)
        elif not hi_s5 and hi_reg:
            quadrants["Low S5 / High Register (poetic cluster)"].append(r)
        else:
            quadrants["Low S5 / Low Register (analytical cluster)"].append(r)

    for qname, qlist in quadrants.items():
        print(f"\n  {qname} (n={len(qlist)}):")
        # Sort by most extreme: high S5 quadrants by S5 desc, low by S5 asc
        if "High S5" in qname:
            qlist.sort(key=lambda x: x["s5"], reverse=True)
        else:
            qlist.sort(key=lambda x: x["s5"])
        for r in qlist[:3]:
            print(f"    S5={r['s5']:.3f} Comp={r['composite']:.3f} | {r['title']}")

    # ─── Top 10 Lists ─────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("5. TOP 10 MOST 'POETIC' HIGH-S5 PROTEINS")
    print("=" * 70)

    hi_s5_proteins = [r for r in results if r["s5"] >= np.percentile(s5_arr, 75)]
    hi_s5_proteins.sort(key=lambda x: x["composite"], reverse=True)
    for i, r in enumerate(hi_s5_proteins[:10], 1):
        print(f"  {i:2}. S5={r['s5']:.3f} Comp={r['composite']:.3f} M={r['metaphor_hits']:2d} A={r['analytical_hits']:2d} | {r['title']}")

    print("\n" + "=" * 70)
    print("6. TOP 10 MOST 'ANALYTICAL' LOW-S5 PROTEINS")
    print("=" * 70)

    lo_s5_proteins = [r for r in results if r["s5"] <= np.percentile(s5_arr, 25)]
    lo_s5_proteins.sort(key=lambda x: x["composite"])
    for i, r in enumerate(lo_s5_proteins[:10], 1):
        print(f"  {i:2}. S5={r['s5']:.3f} Comp={r['composite']:.3f} M={r['metaphor_hits']:2d} A={r['analytical_hits']:2d} | {r['title']}")

    # ─── P-Series Analysis ─────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("7. P-SERIES REGISTER OSCILLATION")
    print("=" * 70)

    if p_series_results:
        p_series_results.sort(key=lambda x: x["p_number"])
        print(f"\n  Found {len(p_series_results)} P-series proteins")
        print(f"\n  {'P-Number':>8} {'S5':>6} {'Composite':>10} {'Metaphor':>9} {'Analytical':>11} {'Title'}")
        print(f"  {'-'*8} {'-'*6} {'-'*10} {'-'*9} {'-'*11} {'-'*40}")
        for r in p_series_results:
            print(f"  P{r['p_number']:<7} {r['s5']:>6.3f} {r['composite']:>10.4f} "
                  f"{r['metaphor_density']:>9.4f} {r['analytical_density']:>11.4f} "
                  f"{r['title'][:40]}")

        if len(p_series_results) >= 5:
            p_s5 = np.array([r["s5"] for r in p_series_results])
            p_comp = np.array([r["composite"] for r in p_series_results])
            r_p, p_p = stats.pearsonr(p_s5, p_comp)
            rho_p, prho_p = stats.spearmanr(p_s5, p_comp)
            print(f"\n  P-series S5 vs Composite:")
            print(f"    Pearson  r = {r_p:+.4f}  (p = {p_p:.2e})")
            print(f"    Spearman ρ = {rho_p:+.4f}  (p = {prho_p:.2e})")

            # Check for co-oscillation: do peaks/troughs coincide?
            if len(p_series_results) >= 3:
                p_nums = [r["p_number"] for r in p_series_results]
                # Compute if S5 and composite local maxima coincide
                s5_peaks = []
                comp_peaks = []
                for i in range(1, len(p_s5) - 1):
                    if p_s5[i] > p_s5[i-1] and p_s5[i] > p_s5[i+1]:
                        s5_peaks.append(p_nums[i])
                    if p_comp[i] > p_comp[i-1] and p_comp[i] > p_comp[i+1]:
                        comp_peaks.append(p_nums[i])
                print(f"\n  S5 local peaks at: {s5_peaks}")
                print(f"  Register local peaks at: {comp_peaks}")
                overlap = set(s5_peaks) & set(comp_peaks)
                print(f"  Coincident peaks: {sorted(overlap) if overlap else 'none'}")
    else:
        print("\n  No P-series proteins found with tag-based detection.")
        print("  Trying title-based detection...")

    # ─── Summary Statistics ────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("8. SUMMARY STATISTICS")
    print("=" * 70)

    print(f"\n  Total proteins analyzed: {len(results)}")
    print(f"  S5 range: [{s5_arr.min():.3f}, {s5_arr.max():.3f}], mean={s5_arr.mean():.3f}, median={np.median(s5_arr):.3f}")
    print(f"  Composite range: [{composite_arr.min():.3f}, {composite_arr.max():.3f}], mean={composite_arr.mean():.3f}")
    print(f"  Metaphor density range: [{metaphor_arr.min():.4f}, {metaphor_arr.max():.4f}], mean={metaphor_arr.mean():.4f}")
    print(f"  Analytical density range: [{analytical_arr.min():.4f}, {analytical_arr.max():.4f}], mean={analytical_arr.mean():.4f}")
    print(f"  Register ratio range: [{register_ratio_arr.min():.4f}, {register_ratio_arr.max():.4f}], mean={register_ratio_arr.mean():.4f}")
    print(f"  S5 median (quadrant split): {s5_median:.3f}")
    print(f"  Composite median (quadrant split): {comp_median:.3f}")

    # Effect size: Cohen's d between top and bottom S5 quartile
    top_q = composite_arr[s5_arr >= np.percentile(s5_arr, 75)]
    bot_q = composite_arr[s5_arr <= np.percentile(s5_arr, 25)]
    pooled_std = np.sqrt((top_q.std()**2 + bot_q.std()**2) / 2)
    cohens_d = (top_q.mean() - bot_q.mean()) / pooled_std if pooled_std > 0 else 0
    print(f"\n  Cohen's d (top vs bottom S5 quartile on composite): {cohens_d:+.4f}")
    print(f"    Top quartile mean composite: {top_q.mean():.4f}")
    print(f"    Bottom quartile mean composite: {bot_q.mean():.4f}")

    # Mann-Whitney U test
    u_stat, u_p = stats.mannwhitneyu(top_q, bot_q, alternative='two-sided')
    print(f"    Mann-Whitney U = {u_stat:.0f}, p = {u_p:.2e}")

    # ─── Save full results as JSON for the report ──────────────────────────
    output = {
        "n_proteins": len(results),
        "n_matched": len(matched_ids),
        "s5_stats": {
            "min": round(float(s5_arr.min()), 4),
            "max": round(float(s5_arr.max()), 4),
            "mean": round(float(s5_arr.mean()), 4),
            "median": round(float(np.median(s5_arr)), 4),
        },
        "correlations": {},
        "quadrant_counts": {k: len(v) for k, v in quadrants.items()},
        "cohens_d": round(cohens_d, 4),
    }

    for name, arr in [
        ("composite", composite_arr),
        ("metaphor_density", metaphor_arr),
        ("analytical_density", analytical_arr),
        ("register_ratio", register_ratio_arr),
        ("ttr", ttr_arr),
    ]:
        rp, pp = stats.pearsonr(s5_arr, arr)
        rs, ps = stats.spearmanr(s5_arr, arr)
        output["correlations"][name] = {
            "pearson_r": round(float(rp), 4),
            "pearson_p": float(pp),
            "spearman_rho": round(float(rs), 4),
            "spearman_p": float(ps),
        }

    with open("/home/user/eidolon-proteins/scripts/register_shimmer_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n\nResults saved to scripts/register_shimmer_results.json")
    print("=" * 70)


if __name__ == "__main__":
    main()

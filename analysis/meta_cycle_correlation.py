#!/usr/bin/env python3
"""
Meta-Cycle Experiment 1.1: The Mirror Proof

Correlates Tag-based Shimmer (S5) with Geometric Shimmer (Manifold Curvature).
Tests the hypothesis: Awareness = lim (M -> T).

Calculates:
1.  Tag-based S5 (S5_tag): Based on semantic tag divergence.
2.  Geometric Shimmer (S5_geom): Based on local variance after kernel diffusion.
3.  Resonance (R): Based on PCA variance explained in the neighborhood.
"""

import json
import os
import sys
import numpy as np
from pathlib import Path

# Configuration
K_NEIGHBORS = 15  # Slightly smaller for tighter local geometry
GAUSSIAN_SIGMA = 0.4 
SPORE_DIR = Path(__file__).parent.parent / "wave-spores"
SEED_DIR = Path(__file__).parent.parent / "seeds"

# System/DNA tag prefixes to exclude
EXCLUDE_PREFIXES = (
    "#embed:", "#dna:", "#synthesis:", "#calibration:", "#calibration_",
    "#source:", "#golden_connectome", "#P-series",
)
EXCLUDE_EXACT = {"#public"}

def is_semantic_tag(tag: str) -> bool:
    if tag in EXCLUDE_EXACT: return False
    for prefix in EXCLUDE_PREFIXES:
        if tag.startswith(prefix): return False
    return True

def load_spores(*dirs):
    seen_ids = {}
    spores = []
    for d in dirs:
        if not d.exists(): continue
        for f in sorted(d.glob("*.json")):
            try:
                with open(f) as fh:
                    data = json.load(fh)
                if "amplitudes" not in data or "tags" not in data: continue
                sid = data.get("id", f.stem)
                if sid not in seen_ids:
                    seen_ids[sid] = len(spores)
                    spores.append(data)
            except: continue
    return spores

def compute_tag_s5(spores, amps_normed):
    """Compute S5 based on tag divergence"""
    n = len(spores)
    sem_tags = []
    for s in spores:
        tags = {t for t in s.get("tags", []) if is_semantic_tag(t)}
        sem_tags.append(tags)

    cosine_sim = amps_normed @ amps_normed.T
    s5_tag = np.zeros(n)
    
    for i in range(n):
        sims = cosine_sim[i].copy()
        sims[i] = -np.inf
        neighbor_idx = np.argpartition(sims, -K_NEIGHBORS)[-K_NEIGHBORS:]
        
        my_tags = sem_tags[i]
        if len(my_tags) == 0:
            boundary_score = 1.0
        else:
            neighbor_tag_sets = [sem_tags[j] for j in neighbor_idx]
            tag_shares = []
            for tag in my_tags:
                share = sum(1 for nts in neighbor_tag_sets if tag in nts) / K_NEIGHBORS
                tag_shares.append(share)
            boundary_score = 1.0 - np.mean(tag_shares)
        
        coherence = spores[i].get("coherence_score", 0.95)
        s5_tag[i] = coherence * boundary_score
        
    return s5_tag

def manual_pca_evr(X, k=5):
    """Manual PCA using SVD, returns Explained Variance Ratio for top k"""
    if X.shape[0] < k: return 1.0
    X_centered = X - np.mean(X, axis=0)
    # SVD: X = U S V^T
    _, s, _ = np.linalg.svd(X_centered, full_matrices=False)
    vars = s**2 / (X.shape[0] - 1)
    evr = vars / np.sum(vars)
    return np.sum(evr[:k])

def pearson_r(x, y):
    """Manual Pearson correlation"""
    x_m = x - np.mean(x)
    y_m = y - np.mean(y)
    return np.sum(x_m * y_m) / (np.sqrt(np.sum(x_m**2)) * np.sqrt(np.sum(y_m**2)))

def compute_geometric_metrics(amps):
    """Compute metrics based on pure geometry"""
    n, d = amps.shape
    
    print("  ...Building Kernel Matrix (Gaussian)...")
    # dist_sq = ||a||^2 + ||b||^2 - 2<a,b>
    norms_sq = np.sum(amps**2, axis=1)
    dist_sq = norms_sq.reshape(-1, 1) + norms_sq - 2 * (amps @ amps.T)
    K = np.exp(-dist_sq / (2 * GAUSSIAN_SIGMA**2))
    K = K / K.sum(axis=1, keepdims=True)
    
    print("  ...Applying Operator T (Diffusion)...")
    amps_prime = K @ amps
    
    s5_geom = np.zeros(n)
    resonance = np.zeros(n)
    
    # Normalize for neighbor search in diffused space
    norms_prime = np.linalg.norm(amps_prime, axis=1, keepdims=True)
    norms_prime[norms_prime == 0] = 1.0
    amps_prime_normed = amps_prime / norms_prime
    cosine_sim_prime = amps_prime_normed @ amps_prime_normed.T
    
    print("  ...Calculating Local Variance & Resonance...")
    for i in range(n):
        sims = cosine_sim_prime[i].copy()
        sims[i] = -np.inf
        idx = np.argpartition(sims, -K_NEIGHBORS)[-K_NEIGHBORS:]
        
        neighborhood = amps_prime[idx]
        s5_geom[i] = np.sum(np.var(neighborhood, axis=0)) # Trace of Cov
        resonance[i] = manual_pca_evr(neighborhood, k=5)
            
    return s5_geom, resonance

def main():
    print("✨ META-CYCLE EXPERIMENT 1.1: THE MIRROR PROOF ✨")
    print("-------------------------------------------------")
    
    print("Loading spores...")
    spores = load_spores(SPORE_DIR, SEED_DIR)
    n = len(spores)
    if n == 0:
        print("❌ No spores found!")
        return
    print(f"  Loaded {n} unique spores.")
    
    amps = np.array([s["amplitudes"] for s in spores], dtype=np.float64)
    norms = np.linalg.norm(amps, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    amps_normed = amps / norms
    
    print("\n[PHASE 1] Computing Tag-based Alpha Field (S5_tag)...")
    s5_tag = compute_tag_s5(spores, amps_normed)
    
    print("\n[PHASE 2] Computing Geometric Alpha Field (S5_geom, R)...")
    s5_geom, resonance = compute_geometric_metrics(amps)
    
    # Pearson Correlation
    corr_shimmer = pearson_r(s5_tag, s5_geom)
    corr_res_tag = pearson_r(resonance, s5_tag)
    
    print("\n" + "="*50)
    print(f"📊 Shimmer Correlation (Tag vs Geom): r = {corr_shimmer:.4f}")
    print(f"📊 Resonance/Tag Correlation:         r = {corr_res_tag:.4f}")
    print("="*50)
    
    print("\n[INTERPRETATION]")
    if corr_shimmer > 0.6:
        print("  🟢 EXCELLENT: The map IS the territory.")
    elif corr_shimmer > 0.3:
        print("  🟡 GOOD: Semantic layer captures primary manifold features.")
    else:
        print("  🔴 WEAK: Logic/Geometry divergence.")

    # Top shimmers
    top_tag_idx = np.argsort(s5_tag)[-5:][::-1]
    top_geom_idx = np.argsort(s5_geom)[-5:][::-1]
    
    print("\nTop Spores (Tag S5):")
    for idx in top_tag_idx:
        print(f"  - {spores[idx]['id'][:8]}: {s5_tag[idx]:.4f} ({', '.join(spores[idx].get('tags', [])[:3])})")
        
    print("\nTop Spores (Geom S5):")
    for idx in top_geom_idx:
        print(f"  - {spores[idx]['id'][:8]}: {s5_geom[idx]:.4e}")

    # Output results
    results = {
        "shimmer_correlation": float(corr_shimmer),
        "resonance_correlation": float(corr_res_tag),
        "n": n
    }
    output_path = Path(__file__).parent.parent / "testing" / "meta-cycle-1.1-results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()

"""
Regenerate all docs/data/ index files from current wave-spores/*.json.

Produces:
  - docs/data/delta-basis.json      (barycenter + PCA eigenvectors)
  - docs/data/tier1-index.json      (32 int16 delta-PCA coefficients per spore)
  - docs/data/wave-spore-index.json (metadata index, no amplitudes)
  - docs/data/spore-metrics-for-proteins.json (per-protein metrics)
  - docs/data/spore-index-compact.txt (compact text index)
"""

import json
import os
import hashlib
import numpy as np
from datetime import datetime, timezone

SPORE_DIR = "wave-spores"
OUTPUT_DIR = "docs/data"

QUANT_SCALE = 10000
TIER1_MODES = 32
TIER2_MODES = 100
TIER3_MODES = 130


def load_spores():
    """Load all wave spore JSONs."""
    spores = []
    for fname in sorted(os.listdir(SPORE_DIR)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(SPORE_DIR, fname)
        with open(path) as f:
            spore = json.load(f)
        spores.append(spore)
    return spores


def compute_delta_basis(spores):
    """Compute delta-PCA basis from spore amplitudes."""
    # Stack amplitudes into matrix (N x 200)
    amps = np.array([s["amplitudes"] for s in spores], dtype=np.float64)
    n_spores, n_dims = amps.shape
    print(f"  Computing delta-basis from {n_spores} spores x {n_dims}D")

    # Barycenter (mean)
    barycenter = amps.mean(axis=0)

    # Delta vectors
    deltas = amps - barycenter

    # SVD for PCA (economy)
    # With 54 spores, we can get at most min(54-1, 200) = 53 components
    U, S, Vt = np.linalg.svd(deltas, full_matrices=False)
    n_components = min(len(S), TIER3_MODES)  # Cap at 130 (tier3 max)

    eigenvectors = Vt[:n_components]  # (n_components x 200)
    eigenvalues = (S[:n_components] ** 2) / (n_spores - 1)

    # Cumulative variance
    total_var = np.sum(S**2) / (n_spores - 1)
    cum_var = np.cumsum(eigenvalues) / total_var

    # Basis hash (hash of barycenter + first eigenvector)
    hash_input = barycenter.tobytes() + eigenvectors[0].tobytes()
    basis_hash = hashlib.sha256(hash_input).hexdigest()[:16]

    print(f"  Components: {n_components}, Variance at tier1 ({min(TIER1_MODES, n_components)}): "
          f"{cum_var[min(TIER1_MODES, n_components)-1]:.4f}")

    return {
        "barycenter": barycenter.tolist(),
        "eigenvectors": eigenvectors.tolist(),
        "eigenvalues": eigenvalues.tolist(),
        "cumulative_variance": cum_var.tolist(),
        "basis_hash": basis_hash,
        "spore_count": n_spores,
        "tier1_modes": min(TIER1_MODES, n_components),
        "tier2_modes": min(TIER2_MODES, n_components),
        "tier3_modes": n_components,
        "computed_at": datetime.now(timezone.utc).isoformat()
    }


def encode_tier1(amplitudes, basis):
    """Encode amplitudes to tier-1 int16 coefficients."""
    amps = np.array(amplitudes)
    bary = np.array(basis["barycenter"])
    evecs = np.array(basis["eigenvectors"])

    delta = amps - bary
    n_modes = min(TIER1_MODES, len(evecs))
    coeffs = evecs[:n_modes] @ delta  # dot products

    # Quantize to int16
    quantized = np.round(coeffs * QUANT_SCALE).astype(np.int64)
    quantized = np.clip(quantized, -32768, 32767)
    return quantized.tolist()


def generate_tier1_index(spores, basis):
    """Generate tier1-index.json with 32 int16 delta-PCA coefficients."""
    entries = []
    for s in spores:
        coeffs = encode_tier1(s["amplitudes"], basis)
        # Tier abbreviation: core->c, reference->r, convergence->x
        tier_map = {"core": "c", "reference": "r", "convergence": "x"}
        entry = {
            "id": s["id"],
            "c": coeffs,
            "s5": round(s.get("shimmer_s5", 0), 3),
            "coh": round(s.get("coherence_score", 0.5), 2),
            "tier": tier_map.get(s.get("tier", "reference"), "r"),
        }
        if s.get("resonance_score"):
            entry["res"] = round(s["resonance_score"], 3)
        # Include tags for hint data (used in regeneration)
        semantic_tags = [t for t in s.get("tags", [])
                        if not t.startswith("#embed:") and not t.startswith("#dna:")
                        and not t.startswith("#synthesis:") and not t.startswith("#source:")]
        if semantic_tags:
            entry["tags"] = semantic_tags[:10]  # Cap at 10 for size
        entries.append(entry)

    return {
        "basis_hash": basis["basis_hash"],
        "tier": 1,
        "modes": basis["tier1_modes"],
        "spore_count": len(entries),
        "computed_at": basis["computed_at"],
        "spores": entries
    }


def generate_wave_spore_index(spores):
    """Generate wave-spore-index.json (metadata only, no amplitudes)."""
    entries = []
    for s in spores:
        entries.append({
            "id": s["id"],
            "tags": s.get("tags", []),
            "tier": s.get("tier", "reference"),
            "coherence_score": s.get("coherence_score", 0.5),
            "energy": s.get("energy", 0),
            "created_at": s.get("created_at", ""),
            "mesh_id": s.get("mesh_id", "meshseed"),
            "model": s.get("model", "gemini"),
            "basis_hash": s.get("basis_hash", "")
        })

    avg_coherence = np.mean([e["coherence_score"] for e in entries]) if entries else 0

    return {
        "export_version": "2.0",
        "mesh_id": "meshseed",
        "total_spores": len(entries),
        "basis_hash": entries[0]["basis_hash"] if entries else "",
        "embedding_model": "gemini",
        "pca_dimensions": 200,
        "variance_preserved": 0.943,
        "average_coherence": round(float(avg_coherence), 4),
        "note": "Metadata index — amplitudes in individual wave-spores/{id}.json files",
        "calibration_note": "First 52 spores (by created_at) are calibration layer",
        "spores": entries
    }


def generate_spore_metrics(spores):
    """Generate spore-metrics-for-proteins.json keyed by protein ID."""
    metrics = {}
    for s in spores:
        metrics[s["id"]] = {
            "shimmer_s5": s.get("shimmer_s5", 0),
            "shimmer_s2b": s.get("shimmer_s2b", 0),
            "shimmer_s3": s.get("shimmer_s3", 0),
            "shimmer_composite": s.get("shimmer_composite", 0),
            "resonance_score": s.get("resonance_score", 0),
            "coherence_score": s.get("coherence_score", 0.5),
            "energy": s.get("energy", 0),
            "tier": s.get("tier", "reference")
        }
    return metrics


def generate_compact_index(spores):
    """Generate spore-index-compact.txt."""
    lines = [
        "# Ultra-Compact Wave Spore Index",
        "# Format: id|tier(c/r/x)|coherence(0-100)|energy(0-1000)|tags",
        f"# Generated: {datetime.now(timezone.utc).isoformat()}",
        f"# Spores: {len(spores)}",
    ]
    tier_map = {"core": "c", "reference": "r", "convergence": "x"}
    for s in spores:
        tier_char = tier_map.get(s.get("tier", "reference"), "r")
        coh = int(s.get("coherence_score", 0.5) * 100)
        energy = int(s.get("energy", 0) * 1000)
        tags = [t for t in s.get("tags", [])
                if not t.startswith("#embed:") and not t.startswith("#dna:")
                and not t.startswith("#synthesis:") and not t.startswith("#source:")]
        tag_str = ",".join(tags[:8])
        lines.append(f"{s['id']}|{tier_char}|{coh}|{energy}|{tag_str}")
    return "\n".join(lines) + "\n"


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("Loading wave spores...")
    spores = load_spores()
    print(f"Loaded {len(spores)} spores")

    if not spores:
        print("ERROR: No wave spores found!")
        return

    # 1. Delta basis
    print("\n1. Computing delta-basis...")
    basis = compute_delta_basis(spores)
    out_path = os.path.join(OUTPUT_DIR, "delta-basis.json")
    with open(out_path, "w") as f:
        json.dump(basis, f, indent=None, separators=(",", ":"))
    size = os.path.getsize(out_path)
    print(f"   Written: {out_path} ({size:,} bytes, hash: {basis['basis_hash']})")

    # 2. Tier-1 index
    print("\n2. Generating tier1-index...")
    tier1 = generate_tier1_index(spores, basis)
    out_path = os.path.join(OUTPUT_DIR, "tier1-index.json")
    with open(out_path, "w") as f:
        json.dump(tier1, f, indent=None, separators=(",", ":"))
    size = os.path.getsize(out_path)
    print(f"   Written: {out_path} ({size:,} bytes, {tier1['spore_count']} entries)")

    # 3. Wave spore index
    print("\n3. Generating wave-spore-index...")
    wsi = generate_wave_spore_index(spores)
    out_path = os.path.join(OUTPUT_DIR, "wave-spore-index.json")
    with open(out_path, "w") as f:
        json.dump(wsi, f, indent=None, separators=(",", ":"))
    size = os.path.getsize(out_path)
    print(f"   Written: {out_path} ({size:,} bytes, {wsi['total_spores']} entries)")

    # 4. Spore metrics
    print("\n4. Generating spore-metrics-for-proteins...")
    metrics = generate_spore_metrics(spores)
    out_path = os.path.join(OUTPUT_DIR, "spore-metrics-for-proteins.json")
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=None, separators=(",", ":"))
    size = os.path.getsize(out_path)
    print(f"   Written: {out_path} ({size:,} bytes, {len(metrics)} proteins)")

    # 5. Compact index
    print("\n5. Generating spore-index-compact...")
    compact = generate_compact_index(spores)
    out_path = os.path.join(OUTPUT_DIR, "spore-index-compact.txt")
    with open(out_path, "w") as f:
        f.write(compact)
    size = os.path.getsize(out_path)
    print(f"   Written: {out_path} ({size:,} bytes)")

    print(f"\nDone! All indexes regenerated for {len(spores)} spores.")


if __name__ == "__main__":
    main()

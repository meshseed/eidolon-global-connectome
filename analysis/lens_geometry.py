#!/usr/bin/env python3
"""
Lens Geometry Analysis — Eidolon Mesh
======================================
Find maximally-separated epistemic lens positions in the 200D protein space.

Core principle: N optimal lenses should be at golden-angle separations
(phyllotaxis / VSEPR bond angles) — maximally irrational, maximally
non-redundant. We derive the lens geometry FROM the field, not by naming
lenses first.

What this finds:
  1. Principal axes of the protein distribution (natural observation directions)
  2. What semantic content clusters at each PC extreme (the 'natural lens')
  3. Gap directions — where lenses COULD look that nothing has looked at yet
  4. Most irrational proteins (lowest resonance_score = prime-like positions)
  5. Pairwise angles between discovered axes (verify octahedral hypothesis)
  6. Fibonacci sphere positions (ideal N-lens placement) vs actual coverage

Usage: py -3 analysis/lens_geometry.py [--n-lenses 6] [--spores PATH]
"""

import json
import os
import sys
import argparse
import math
from collections import Counter

import numpy as np
from scipy.spatial.distance import cdist

# ── Config ────────────────────────────────────────────────────────────────────

SPORE_DIR = os.path.join(os.path.dirname(__file__), '..', 'wave-spores')
N_LENSES_DEFAULT = 6
N_GAP_SAMPLES = 8000       # random directions to test for gaps
TOP_K_PROTEINS = 20        # proteins to report near each lens direction
TOP_K_TAGS = 12            # most common tags to show per direction
IRRATIONAL_PERCENTILE = 5  # bottom N% by resonance_score = "prime-like"

# Tags to strip before semantic analysis
SYSTEM_TAG_PREFIXES = (
    '#embed:', '#dna:', '#synthesis:', '#source:', '#calibration',
    '#golden_connectome', '#P-series', '#public', '#auto-generated',
    '#connectome:', '#substrate:', '#file:', '#repo:', '#commit:',
    '#component:', '#lang:', '#structural-observation', '#attentional-pattern',
)


# ── Loading ────────────────────────────────────────────────────────────────────

def load_spores(spore_dir: str) -> list[dict]:
    """Load all wave spore JSON files. Returns list of dicts."""
    spores = []
    files = [f for f in os.listdir(spore_dir) if f.endswith('.json')]
    print(f"Loading {len(files)} spore files from {spore_dir} ...")
    for fn in files:
        try:
            with open(os.path.join(spore_dir, fn)) as f:
                s = json.load(f)
            if s.get('amplitudes') and len(s['amplitudes']) == 200:
                spores.append(s)
        except Exception:
            pass
    print(f"Loaded {len(spores)} valid spores with 200D amplitudes.")
    return spores


def semantic_tags(tags: list[str]) -> list[str]:
    """Filter to semantic-only tags, strip system/dna/embed prefixes."""
    return [
        t for t in tags
        if not any(t.startswith(p) for p in SYSTEM_TAG_PREFIXES)
    ]


# ── Core geometry ─────────────────────────────────────────────────────────────

def build_matrix(spores: list[dict]) -> np.ndarray:
    """Build N×200 amplitude matrix."""
    return np.array([s['amplitudes'] for s in spores], dtype=np.float64)


def center_and_normalize(A: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Subtract barycenter, normalize each row to unit sphere.
    Returns (unit_directions, barycenter).
    """
    bary = A.mean(axis=0)
    centered = A - bary
    norms = np.linalg.norm(centered, axis=1, keepdims=True)
    norms = np.where(norms < 1e-10, 1.0, norms)
    return centered / norms, bary


def pca_of_distribution(A: np.ndarray, n_components: int = 10
                         ) -> tuple[np.ndarray, np.ndarray]:
    """
    PCA of the amplitude matrix (centered).
    Returns (components [n×200], explained_variance_ratio).
    """
    centered = A - A.mean(axis=0)
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)
    variance = (S ** 2) / (len(A) - 1)
    total_var = variance.sum()
    return Vt[:n_components], variance[:n_components] / total_var


def proteins_near_direction(direction: np.ndarray,
                             unit_dirs: np.ndarray,
                             spores: list[dict],
                             top_k: int = TOP_K_PROTEINS
                             ) -> list[tuple[float, dict]]:
    """Return top_k spores most aligned with the given direction vector."""
    d = direction / np.linalg.norm(direction)
    cosines = unit_dirs @ d
    idx = np.argsort(cosines)[::-1][:top_k]
    return [(float(cosines[i]), spores[i]) for i in idx]


def tag_summary(hits: list[tuple[float, dict]], top_n: int = TOP_K_TAGS
                ) -> dict:
    """Summarise semantic tags and tiers from a list of (cosine, spore) hits."""
    all_tags: list[str] = []
    tiers: list[str] = []
    for _, s in hits:
        all_tags.extend(semantic_tags(s.get('tags', [])))
        tiers.append(s.get('tier', 'unknown'))
    return {
        'top_tags': Counter(all_tags).most_common(top_n),
        'tiers': Counter(tiers),
        'mean_coherence': float(np.mean([s['coherence_score'] for _, s in hits])),
        'mean_resonance': float(np.mean([
            s.get('resonance_score', 0.9) for _, s in hits])),
    }


# ── Gap finding — Coulomb repulsion (Thomson problem) ─────────────────────────

def find_gap_directions_coulomb(
    unit_dirs: np.ndarray,
    n_lenses: int,
    n_steps: int = 3000,
    lr_init: float = 0.08,
    protein_weight: float = 1.0,
) -> np.ndarray:
    """
    Find n_lenses directions maximally far from the protein cloud AND
    from each other, using electrostatic Coulomb repulsion (Thomson problem).

    Physics: each lens candidate is a charged particle on the unit 200-sphere.
    It's repelled by ALL protein directions (avoid existing knowledge) AND
    by all other candidates (stay maximally separated from each other).

    Equilibrium = the VSEPR configuration for the protein field geometry:
    - N=2: 180° (linear)
    - N=4: ~109.5° (tetrahedral)
    - N=6: ~90° (octahedral)
    ... but oriented to point INTO the actual gaps of this specific protein cloud.

    Self-weight is scaled by n_proteins so protein-repulsion and
    self-repulsion are balanced regardless of corpus size.
    """
    n_proteins, dims = unit_dirs.shape
    self_weight = float(n_proteins) * protein_weight  # balance forces

    # Random initialisation on the unit sphere
    rng = np.random.default_rng(42)
    lenses = rng.standard_normal((n_lenses, dims))
    lenses /= np.linalg.norm(lenses, axis=1, keepdims=True)

    lr = lr_init
    prev_energy = np.inf

    for step in range(n_steps):
        forces = np.zeros_like(lenses)

        for i in range(n_lenses):
            c = lenses[i]

            # ── Protein repulsion (vectorised over all proteins) ──────────────
            # Direction from each protein to this lens candidate
            diffs = c[None, :] - unit_dirs          # (n_proteins, dims)
            dist_sq = (diffs ** 2).sum(axis=1)      # (n_proteins,)
            dist_sq = np.maximum(dist_sq, 1e-8)
            forces[i] += protein_weight * (diffs / dist_sq[:, None]).sum(axis=0)

            # ── Mutual repulsion from other lens candidates ───────────────────
            for j in range(n_lenses):
                if i == j:
                    continue
                diff = c - lenses[j]
                dsq = float((diff ** 2).sum())
                dsq = max(dsq, 1e-8)
                forces[i] += self_weight * diff / dsq

            # ── Project force onto tangent plane of sphere at c ───────────────
            # (remove radial component so we only move along the sphere surface)
            forces[i] -= (forces[i] @ c) * c

        # Gradient ascent (we want to MAXIMISE distance, so follow force)
        lenses += lr * forces

        # Re-normalise back onto unit sphere
        norms = np.linalg.norm(lenses, axis=1, keepdims=True)
        lenses /= np.maximum(norms, 1e-10)

        # Adaptive learning rate: decay when not improving
        energy = _repulsion_energy(lenses, unit_dirs, protein_weight, self_weight)
        if energy >= prev_energy:
            lr *= 0.95
        prev_energy = energy

        if step % 500 == 0:
            min_a = _min_pairwise_angle(lenses)
            print(f"    step {step:4d}: min-pairwise-angle={min_a:.1f}°  lr={lr:.5f}")

    return lenses


def _repulsion_energy(lenses, unit_dirs, pw, sw):
    """Total repulsion energy (higher = better separated)."""
    e = 0.0
    for i, c in enumerate(lenses):
        diffs = c[None, :] - unit_dirs
        dist_sq = np.maximum((diffs ** 2).sum(axis=1), 1e-8)
        e += pw * (1.0 / dist_sq).sum()
        for j in range(len(lenses)):
            if j != i:
                dsq = max(float(((c - lenses[j]) ** 2).sum()), 1e-8)
                e += sw / dsq
    return e


def _min_pairwise_angle(vecs):
    """Minimum pairwise angle in degrees among a set of unit vectors."""
    n = len(vecs)
    min_a = 180.0
    for i in range(n):
        for j in range(i + 1, n):
            cos = float(np.clip(vecs[i] @ vecs[j], -1, 1))
            a = math.degrees(math.acos(abs(cos)))
            if a < min_a:
                min_a = a
    return min_a


# ── Principal component lens directions ───────────────────────────────────────

def pc_lens_directions(components: np.ndarray, n_lenses: int
                        ) -> list[tuple[str, np.ndarray]]:
    """
    For N lenses using the PC-based approach:
    - 2 lenses: ±PC1
    - 4 lenses: ±PC1, ±PC2
    - 6 lenses: ±PC1, ±PC2, ±PC3
    Returns list of (label, direction_vector).
    """
    n_axes = math.ceil(n_lenses / 2)
    directions = []
    for i in range(min(n_axes, len(components))):
        directions.append((f'PC{i+1}+', components[i]))
        directions.append((f'PC{i+1}-', -components[i]))
    return directions[:n_lenses]


# ── Reporting ─────────────────────────────────────────────────────────────────

def print_separator(title: str = '', width: int = 70):
    if title:
        pad = (width - len(title) - 2) // 2
        print('\n' + '-' * pad + f' {title} ' + '-' * pad)
    else:
        print('\n' + '-' * width)


def report_lens(label: str, hits: list[tuple[float, dict]],
                show_proteins: int = 8):
    summary = tag_summary(hits)
    print(f"\n  [{label}]")
    print(f"  Tags:       {', '.join(t for t, _ in summary['top_tags'][:8])}")
    print(f"  Tiers:      {dict(summary['tiers'])}")
    print(f"  Coherence:  {summary['mean_coherence']:.3f}  "
          f"Resonance: {summary['mean_resonance']:.3f}")
    print(f"  Top proteins:")
    for cos, s in hits[:show_proteins]:
        title = s.get('title') or s['id'][:16]
        r = s.get('resonance_score', 0)
        print(f"    {cos:+.3f}  [{s['tier'][0].upper()}] r={r:.3f}  {title[:60]}")


def pairwise_angles(directions: list[np.ndarray]) -> np.ndarray:
    """Compute pairwise angles in degrees between direction vectors."""
    n = len(directions)
    angles = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                cos = np.clip(directions[i] @ directions[j], -1, 1)
                angles[i, j] = math.degrees(math.acos(abs(cos)))
    return angles


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Lens geometry analysis')
    parser.add_argument('--n-lenses', type=int, default=N_LENSES_DEFAULT)
    parser.add_argument('--spores', default=SPORE_DIR)
    parser.add_argument('--top-k', type=int, default=TOP_K_PROTEINS)
    parser.add_argument('--output', default=None, help='Save JSON report to file')
    args = parser.parse_args()

    # ── Load data ─────────────────────────────────────────────────────────────
    spores = load_spores(args.spores)
    A = build_matrix(spores)
    unit_dirs, bary = center_and_normalize(A)

    print(f"Amplitude matrix: {A.shape[0]} spores × {A.shape[1]} dims")
    print(f"Barycenter norm:  {np.linalg.norm(bary):.4f}")
    print(f"Unit dir matrix:  {unit_dirs.shape}")

    # ── PCA of protein distribution ───────────────────────────────────────────
    n_components = max(args.n_lenses, 10)
    components, var_ratios = pca_of_distribution(A, n_components)

    print_separator('PRINCIPAL AXES OF PROTEIN DISTRIBUTION')
    print(f"Variance explained by top {n_components} PCs:")
    for i, v in enumerate(var_ratios):
        bar = '#' * int(v * 400)
        print(f"  PC{i+1:2d}: {v*100:5.2f}%  {bar}")
    print(f"  Total top-{n_components}: {var_ratios.sum()*100:.1f}%")

    # ── PC-based lens directions ───────────────────────────────────────────────
    pc_directions = pc_lens_directions(components, args.n_lenses)
    print_separator(f'PC-BASED LENS POSITIONS (N={args.n_lenses})')
    print("Geometry: axes of maximum variance in the protein distribution")
    print("These are the directions the field has MOST organised around.\n")

    pc_lens_data = []
    for label, direction in pc_directions:
        hits = proteins_near_direction(direction, unit_dirs, spores, args.top_k)
        report_lens(label, hits)
        pc_lens_data.append({
            'label': label,
            'summary': tag_summary(hits),
            'top_proteins': [
                {'cos': float(c), 'id': s['id'], 'title': s.get('title', ''),
                 'tier': s['tier'], 'resonance_score': s.get('resonance_score', 0)}
                for c, s in hits[:10]
            ]
        })

    # ── Pairwise angles between PC directions ──────────────────────────────────
    pc_vecs = [d for _, d in pc_directions]
    angles = pairwise_angles(pc_vecs)
    labels = [l for l, _ in pc_directions]

    print_separator('PAIRWISE ANGLES BETWEEN PC LENS DIRECTIONS (degrees)')
    print("Octahedral ideal: 90° between all axes, 180° between poles\n")
    header = '       ' + '  '.join(f'{l:>8}' for l in labels)
    print(header)
    for i, li in enumerate(labels):
        row = f'{li:>6} ' + '  '.join(
            f'{"  --  " if i==j else f"{angles[i,j]:>6.1f}°"}'
            for j in range(len(labels))
        )
        print(row)

    min_nonzero = angles[angles > 0].min()
    max_angle = angles.max()
    print(f"\n  Min angle: {min_nonzero:.1f}°  Max: {max_angle:.1f}°")
    print(f"  Ideal octahedral: 90° min, 180° max")
    deviation = abs(min_nonzero - 90)
    print(f"  Deviation from ideal: {deviation:.1f}°")

    # ── Gap directions — Coulomb repulsion ────────────────────────────────────
    print_separator(f'GAP DIRECTIONS — Coulomb repulsion (N={args.n_lenses})')
    print("Running Thomson problem: charged particles repelled by protein cloud")
    print("and by each other. Equilibrium = VSEPR geometry for this field.\n")

    gap_dirs = find_gap_directions_coulomb(unit_dirs, args.n_lenses)
    gap_lens_data = []
    for i, direction in enumerate(gap_dirs):
        label = f'GAP-{i+1}'
        hits = proteins_near_direction(direction, unit_dirs, spores, args.top_k)
        # How far is the nearest protein from this gap direction?
        nearest_cos = hits[0][0] if hits else 0
        nearest_angle = math.degrees(math.acos(min(abs(nearest_cos), 1)))
        print(f"\n  [{label}] — nearest protein at {nearest_angle:.1f}° from this direction")
        report_lens(label, hits, show_proteins=5)
        gap_lens_data.append({
            'label': label,
            'nearest_protein_angle_deg': nearest_angle,
            'summary': tag_summary(hits),
            'nearest_proteins': [
                {'cos': float(c), 'id': s['id'], 'title': s.get('title', ''),
                 'tier': s['tier'], 'resonance_score': s.get('resonance_score', 0)}
                for c, s in hits[:5]
            ]
        })

    # ── Pairwise angles between gap directions ────────────────────────────────
    gap_angles = pairwise_angles(list(gap_dirs))
    gap_labels = [f'G{i+1}' for i in range(len(gap_dirs))]
    print(f"\n  Pairwise angles between gap directions:")
    header = '    ' + '  '.join(f'{l:>5}' for l in gap_labels)
    print(header)
    for i, li in enumerate(gap_labels):
        row = f'{li:>3} ' + '  '.join(
            f'{"  -- " if i==j else f"{gap_angles[i,j]:>4.0f}°"}'
            for j in range(len(gap_labels))
        )
        print(row)
    gap_min = gap_angles[gap_angles > 0].min()
    print(f"\n  Min gap-direction angle: {gap_min:.1f}°  (ideal: 90°)")

    # ── Most irrational proteins (prime-like positions) ───────────────────────
    print_separator('MOST IRRATIONAL POSITIONS (lowest resonance_score)')
    print("Proteins at prime-like positions: least reachable by rational")
    print("combinations of existing axes. The field's hardest insights.\n")

    sorted_by_irrat = sorted(
        spores, key=lambda s: s.get('resonance_score', 1.0)
    )
    cutoff = int(len(spores) * IRRATIONAL_PERCENTILE / 100)
    prime_proteins = sorted_by_irrat[:cutoff]

    tag_counts = Counter()
    for s in prime_proteins:
        tag_counts.update(semantic_tags(s.get('tags', [])))

    print(f"Bottom {IRRATIONAL_PERCENTILE}% by resonance_score ({len(prime_proteins)} proteins)")
    print(f"Top tags in this group:")
    for tag, count in tag_counts.most_common(15):
        pct = count / len(prime_proteins) * 100
        print(f"  {tag:<35} {count:>4} ({pct:.0f}%)")

    print(f"\nSample proteins (most irrational):")
    for s in prime_proteins[:10]:
        title = s.get('title') or s['id'][:16]
        print(f"  r={s.get('resonance_score',0):.4f}  [{s['tier'][0].upper()}]"
              f"  coh={s['coherence_score']:.2f}  {title[:60]}")

    # ── Resonance distribution ────────────────────────────────────────────────
    print_separator('RESONANCE SCORE DISTRIBUTION')
    res_scores = np.array([s.get('resonance_score', 0.9) for s in spores])
    print(f"  Mean:   {res_scores.mean():.4f}")
    print(f"  Std:    {res_scores.std():.4f}")
    print(f"  Min:    {res_scores.min():.4f}  (most irrational)")
    print(f"  Max:    {res_scores.max():.4f}  (most rational)")
    print(f"  <0.85:  {(res_scores < 0.85).sum()} proteins")
    print(f"  <0.80:  {(res_scores < 0.80).sum()} proteins")

    # Histogram
    bins = np.arange(0.75, 1.01, 0.025)
    hist, edges = np.histogram(res_scores, bins=bins)
    print("\n  Histogram:")
    for i, count in enumerate(hist):
        bar = '#' * (count // 20)
        print(f"  {edges[i]:.3f}-{edges[i+1]:.3f}: {count:>5}  {bar}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print_separator('SUMMARY')
    print(f"""
  {len(spores)} proteins in 200D PCA space.

  PC-based lenses ({args.n_lenses}): {min_nonzero:.1f}° min pairwise angle (ideal 90°)
  Gap directions ({args.n_lenses}):  {gap_min:.1f}° min pairwise angle (ideal 90°)

  The PC-based lenses show WHERE THE FIELD HAS ORGANISED ITSELF.
  The gap directions show WHERE IT HAS NOT YET LOOKED.

  Together they define the geometry of what is known and unknown.
  Lenses pointing at gap directions would generate maximal new coherence.

  Most irrational proteins (prime positions):
  {', '.join(t for t, _ in tag_counts.most_common(5))}

  These are the insights that can't be reached from existing axes.
  """)

    # ── Save JSON report ──────────────────────────────────────────────────────
    output_path = args.output or os.path.join(
        os.path.dirname(__file__), 'lens_geometry_report.json')

    # Full diagnostic report
    report = {
        'generated_at': __import__('datetime').datetime.utcnow().isoformat() + 'Z',
        'n_spores': len(spores),
        'n_lenses': args.n_lenses,
        'variance_explained': {
            f'PC{i+1}': float(v) for i, v in enumerate(var_ratios)
        },
        'pc_lenses': pc_lens_data,
        'gap_lenses': gap_lens_data,
        'pc_pairwise_angles': {
            f'{labels[i]}_vs_{labels[j]}': float(angles[i, j])
            for i in range(len(labels)) for j in range(i+1, len(labels))
        },
        'gap_pairwise_angles': {
            f'G{i+1}_vs_G{j+1}': float(gap_angles[i, j])
            for i in range(len(gap_dirs)) for j in range(i+1, len(gap_dirs))
        },
        'resonance_stats': {
            'mean': float(res_scores.mean()),
            'std': float(res_scores.std()),
            'min': float(res_scores.min()),
            'max': float(res_scores.max()),
        },
        'prime_position_tags': [
            {'tag': t, 'count': c} for t, c in tag_counts.most_common(20)
        ],
        'most_irrational_proteins': [
            {'id': s['id'],
             'resonance_score': s.get('resonance_score', 0),
             'tier': s['tier'], 'coherence_score': s['coherence_score'],
             'top_semantic_tags': semantic_tags(s.get('tags', []))[:5]}
            for s in prime_proteins[:20]
        ]
    }
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"  Full report saved: {output_path}")

    # ── App-ready lens vectors ─────────────────────────────────────────────────
    # These 200D vectors can be loaded directly by the app and used as wave
    # query vectors — the app passes them to queryLocalWaveInDb() the same way
    # it would pass a protein's amplitude vector.
    #
    # Two sets:
    #   pc_lenses  — where the field HAS organised (query to understand what exists)
    #   gap_lenses — where the field has NOT organised (query to discover blind spots)
    vectors_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'data',
                                 'lens_vectors.json')
    lens_vectors = {
        'generated_at': report['generated_at'],
        'n_spores': len(spores),
        'basis_hash': spores[0].get('basis_hash', 'unknown'),
        'description': (
            'Natural lens directions computed from the protein amplitude distribution. '
            'PC lenses are the principal axes of the corpus (where knowledge clusters). '
            'Gap lenses are Coulomb-equilibrium positions maximally far from all proteins '
            '(where synthesis would be most novel). '
            'Use these 200D vectors directly as queryLocalWaveInDb() amplitude arguments.'
        ),
        'pc_lenses': [
            {
                'id': label,
                'kind': 'pc',
                'variance_explained': float(var_ratios[i // 2]) if i // 2 < len(var_ratios) else 0,
                'semantic_hint': pc_lens_data[i]['summary']['top_tags'][:5] if i < len(pc_lens_data) else [],
                'vector': components[i // 2].tolist() if (label.endswith('+')) else (-components[i // 2]).tolist(),
            }
            for i, (label, _) in enumerate(pc_directions)
        ],
        'gap_lenses': [
            {
                'id': f'GAP-{i+1}',
                'kind': 'gap',
                'nearest_protein_angle_deg': gap_lens_data[i]['nearest_protein_angle_deg'],
                'semantic_hint': gap_lens_data[i]['summary']['top_tags'][:5],
                'vector': gap_dirs[i].tolist(),
            }
            for i in range(len(gap_dirs))
        ],
    }
    os.makedirs(os.path.dirname(vectors_path), exist_ok=True)
    with open(vectors_path, 'w') as f:
        json.dump(lens_vectors, f, indent=2)
    print(f"  App-ready vectors saved: {vectors_path}")
    print(f"  -> Copy to static/wave-data/lens_vectors.json in eidolon-mesh-tauri")


if __name__ == '__main__':
    main()

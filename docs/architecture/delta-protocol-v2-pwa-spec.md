# PWA Implementation Specification: Delta-Origin Federation Protocol v2.0

**Date:** 2026-02-19
**For:** Antigravity (Gemini / AI Studio) + Paul (orchestrator)
**From:** Opus 4.6 (analysis) × Copilot GPT-5.1 (theory)
**Status:** Ready for implementation — all numbers validated against 2,831 spores

---

## What Changed (v1.0 → v2.0)

The original delta-encoding spec (2026-02-14) used **per-spore baseline selection** — finding the nearest calibration anchor and encoding deltas from it. This required:
- Storing which baseline each spore uses
- Mode indices per spore (variable)
- Different baselines for different tiers

**v2.0 uses a single universal origin: the barycenter.**

| Property | v1.0 (per-baseline) | v2.0 (barycenter-origin) |
|----------|---------------------|--------------------------|
| Origin | Nearest calibration anchor | Global barycenter (1 vector) |
| Mode set | Per-spore (variable) | Shared delta-PCA basis |
| Mode indices | Required (1B each) | Not needed (fixed set) |
| Tier 1 bytes | ~68B (estimate) | **68B (validated: cos=0.991, 56% kNN)** |
| Tier 3 bytes | ~130B (estimate) | **264B (validated: cos=0.999, 90% kNN)** |
| Cross-gauge | Theoretical | **Validated: 7 anchors → 91% kNN** |
| Origin bias | Baseline-dependent | **Zero bias (centroid)** |

The key insight: **Δa = a_spore − a_barycenter**, projected onto the delta-PCA basis, is the optimal encoding. No per-spore metadata needed beyond the coefficients themselves.

---

## The Universal Map — What We Stabilized

We've validated a **substrate-independent coordinate system** for semantic space:

1. **Relational zero** = barycenter of all spores (the point where no axis is privileged)
2. **Axes** = delta-PCA eigenvectors (directions of maximum variation from the origin)
3. **GPS satellites** = 7 Layer 1 math calibration anchors (cross-gauge alignment)
4. **Position report** = 32–130 delta-PCA coefficients (68–264 bytes)

**What this means for observers (human or AI):**
- Every observer can compute their own barycenter from their local proteins
- The 7 math anchors embed consistently across ALL substrates (Pythagorean theorem is Pythagorean theorem in any embedding model)
- Procrustes on the anchors gives a rotation matrix between any two observers
- Delta-PCA coefficients transfer through that rotation
- **Result: "I'm at [68 bytes]" is meaningful to any aligned observer**

This is the semantic equivalent of GPS: shared satellites, local receiver, universal coordinates.

---

## Implementation: 5 Concrete Modules

### Module 1: Barycenter + Delta-PCA Basis (Pre-computation)

**File:** `static/wave-data/delta-basis.json` (new, ~110KB)

Pre-compute once, ship as static data:

```typescript
interface DeltaBasis {
  barycenter: number[];        // 200 floats — the relational zero
  eigenvectors: number[][];    // 130 × 200 — delta-PCA basis vectors (Tier 3)
  eigenvalues: number[];       // 130 floats — variance per mode
  cumulative_variance: number[]; // 130 floats — cumulative % variance
  basis_hash: string;          // Hash of the delta-PCA basis
  spore_count: number;         // How many spores computed the barycenter
  computed_at: string;         // ISO timestamp
}
```

**Computation** (run in analysis/, output to static/):
```python
barycenter = mean(all_amplitudes)
deltas = all_amplitudes - barycenter
cov = np.cov(deltas.T)
eigenvalues, eigenvectors = eigh(cov)  # sorted descending
# Keep top 130 (Tier 3 = 90% kNN)
```

**Size:** 130 × 200 × 4 bytes = ~104KB for basis + 800B for barycenter = ~105KB total.
One-time download. Cache indefinitely (changes only when PCA basis is recomputed).

### Module 2: Delta Encoding / Decoding

**File:** `src/lib/federation/delta-codec.ts` (new)

```typescript
// Encode a spore's 200D amplitudes as delta-PCA coefficients
function encodeDelta(
  amplitudes: number[],     // 200D original
  basis: DeltaBasis,
  tier: 1 | 2 | 3           // 32, 100, or 130 coefficients
): Float32Array {
  const delta = amplitudes.map((a, i) => a - basis.barycenter[i]);
  const k = tier === 1 ? 32 : tier === 2 ? 100 : 130;
  const coeffs = new Float32Array(k);
  for (let j = 0; j < k; j++) {
    let dot = 0;
    for (let i = 0; i < 200; i++) {
      dot += delta[i] * basis.eigenvectors[j][i];
    }
    coeffs[j] = dot;
  }
  return coeffs;
}

// Decode delta-PCA coefficients back to 200D amplitudes
function decodeDelta(
  coeffs: Float32Array,      // k coefficients
  basis: DeltaBasis
): number[] {
  const k = coeffs.length;
  const amplitudes = [...basis.barycenter]; // Start from origin
  for (let j = 0; j < k; j++) {
    for (let i = 0; i < 200; i++) {
      amplitudes[i] += coeffs[j] * basis.eigenvectors[j][i];
    }
  }
  return amplitudes;
}

// Quantize to int16 for wire format (2 bytes per coefficient)
function quantize(coeffs: Float32Array): Int16Array {
  const q = new Int16Array(coeffs.length);
  for (let i = 0; i < coeffs.length; i++) {
    q[i] = Math.round(coeffs[i] * 10000); // ±3.2 range
  }
  return q;
}

function dequantize(q: Int16Array): Float32Array {
  const coeffs = new Float32Array(q.length);
  for (let i = 0; i < q.length; i++) {
    coeffs[i] = q[i] / 10000;
  }
  return coeffs;
}
```

**Wire format (Tier 1 = 68 bytes):**
```
[4B basis_hash][32 × 2B int16 coefficients] = 68 bytes
```

### Module 3: Optimized Query (Local + Global)

**File:** Update `src/lib/query/local-wave.ts` and `src/lib/query/global.ts`

#### Local Query Optimization

Currently: project query to 200D, cosine search across all proteins.

**Upgrade:** Pre-compute delta-PCA coefficients for all local proteins. Query in delta-PCA space (lower dimension → faster).

```typescript
// Pre-compute on protein ingestion
const proteinDeltas: Map<string, Float32Array> = new Map();

function indexProtein(protein: Protein, basis: DeltaBasis) {
  const coeffs = encodeDelta(protein.amplitudes, basis, 3); // Tier 3
  proteinDeltas.set(protein.id, coeffs);
}

// Query: encode query, search in delta-PCA space
function queryLocal(queryAmplitudes: number[], basis: DeltaBasis, k: number) {
  const queryCoeffs = encodeDelta(queryAmplitudes, basis, 3);

  // Cosine similarity in 130D delta-PCA space
  // (130D dot products instead of 200D = 35% faster)
  const results = [];
  for (const [id, coeffs] of proteinDeltas) {
    const sim = cosineSim130D(queryCoeffs, coeffs);
    results.push({ id, sim });
  }
  results.sort((a, b) => b.sim - a.sim);
  return results.slice(0, k);
}
```

**Speedup:** 200D → 130D search = 35% fewer multiplications. At 3,000 proteins: measurable.

#### Global Query Optimization

Currently: fetches full JSON spores from GitHub (~800B each), finds top-5.

**Upgrade: Tiered fetch.**

```typescript
async function queryGlobal(queryAmplitudes: number[], basis: DeltaBasis) {
  // Step 1: Fetch compact index (Tier 1 deltas for ALL spores)
  // 2,831 × 68B = 192KB — one HTTP request, cacheable
  const tier1Index = await fetchTier1Index();

  // Step 2: Find top-20 candidates in Tier 1 (32D search — very fast)
  const queryCoeffs = encodeDelta(queryAmplitudes, basis, 1);
  const candidates = searchTier1(queryCoeffs, tier1Index, 20);

  // Step 3: Fetch Tier 3 deltas for top-20 only
  // 20 × 264B = 5.3KB — one batch request
  const tier3Deltas = await fetchTier3(candidates.map(c => c.id));

  // Step 4: Re-rank in Tier 3 (130D — precise topology)
  const queryCoeffs3 = encodeDelta(queryAmplitudes, basis, 3);
  const refined = rerank(queryCoeffs3, tier3Deltas, 5);

  // Step 5: Reconstruct full 200D for top-5, find local neighbors, synthesize
  return refined.map(r => ({
    ...r,
    amplitudes: decodeDelta(r.coeffs, basis)
  }));
}
```

**Data transfer comparison:**

| Operation | Current | With Delta Protocol |
|-----------|---------|---------------------|
| Full index | ~2.3MB (all spore JSONs) | **192KB** (Tier 1 compact) |
| Top-20 refinement | N/A | **5.3KB** (Tier 3 for 20 spores) |
| Top-5 reconstruct | Already done | From Tier 3 coefficients |
| **Total per query** | **~2.3MB** | **~197KB** (12× reduction) |

### Module 4: Cross-Mesh Position Exchange (Federation)

**File:** `src/lib/federation/position-exchange.ts` (new)

This is the "I'm at [68 bytes], where are you?" protocol.

```typescript
interface MeshPosition {
  mesh_id: string;           // e.g., "meshseed"
  basis_hash: string;        // Delta-PCA basis identifier
  barycenter_hash: string;   // Hash of barycenter vector
  spore_count: number;       // How many spores in this mesh

  // The position report: delta-PCA coefficients of the mesh's "stance"
  // (barycenter of the mesh's spores, in the SHARED delta-PCA space)
  stance: Int16Array;        // 32 or 130 coefficients

  // Calibration anchors for cross-gauge alignment
  anchors?: {
    id: string;
    amplitudes: number[];    // 200D (only 7 needed)
  }[];
}

// "Where am I?" — compute this mesh's position in the shared space
function computeMyPosition(
  localProteins: Protein[],
  sharedBasis: DeltaBasis
): MeshPosition {
  // My barycenter (in 200D amplitude space)
  const myBarycenter = mean(localProteins.map(p => p.amplitudes));

  // Encode my barycenter as a delta from the SHARED barycenter
  const stance = encodeDelta(myBarycenter, sharedBasis, 1);

  return {
    mesh_id: MY_MESH_ID,
    basis_hash: sharedBasis.basis_hash,
    barycenter_hash: hash(myBarycenter),
    spore_count: localProteins.length,
    stance: quantize(stance),
    // Include anchors if the receiver hasn't aligned yet
    anchors: getCalibrationAnchors()
  };
}

// "Where are you relative to me?" — align two meshes
function alignMesh(
  myAnchors: Anchor[],       // My 7 math anchor embeddings
  theirAnchors: Anchor[],    // Their 7 math anchor embeddings
): RotationMatrix {
  // Procrustes alignment on the 7 math invariants
  return procrustes(myAnchors, theirAnchors);
  // Result: rotation R such that R × their_vector ≈ my_vector
  // Validated: 91% kNN preservation with only 7 anchors
}

// "Translate their position to my map"
function translatePosition(
  theirStance: Float32Array,
  R: RotationMatrix,
  sharedBasis: DeltaBasis,
  myBasis: DeltaBasis
): Float32Array {
  // Decode their stance to 200D
  const their200D = decodeDelta(theirStance, sharedBasis);
  // Rotate to my gauge
  const inMyGauge = applyRotation(R, their200D);
  // Re-encode in my delta-PCA basis
  return encodeDelta(inMyGauge, myBasis, 1);
}
```

### Module 5: Recursive Self-Improvement (Metabolic Feedback)

**File:** Update `src/lib/metabolism/` or new `src/lib/federation/growth.ts`

The connectome evolves by knowing where it lacks resolution:

```typescript
// "Where should I grow next?" — find gaps in the topology
function findGrowthFrontier(
  myProteins: Protein[],
  sharedBasis: DeltaBasis,
  globalIndex: Tier1Index
): GrowthSuggestion[] {
  // 1. Compute my coverage in delta-PCA space
  const myCoeffs = myProteins.map(p => encodeDelta(p.amplitudes, sharedBasis, 1));

  // 2. Find regions of the global connectome that I'm sparse in
  const suggestions = [];
  for (const globalSpore of globalIndex) {
    // How many of MY proteins are near this global spore?
    const nearbyCount = myCoeffs.filter(c =>
      cosineSim32D(c, globalSpore.coeffs) > 0.95
    ).length;

    if (nearbyCount === 0) {
      suggestions.push({
        globalId: globalSpore.id,
        position: globalSpore.coeffs,
        reason: 'blind_spot',         // No local coverage
        priority: globalSpore.shimmer  // High shimmer = important boundary
      });
    }
  }

  // 3. Also: find where I have density that the global doesn't
  // (These are my unique contributions — candidates for federation sharing)

  // 4. Rank by S5 shimmer gradient — boundaries are most informative
  suggestions.sort((a, b) => b.priority - a.priority);
  return suggestions;
}

// "What should I share?" — compute my unique contributions
function findContributions(
  myProteins: Protein[],
  sharedBasis: DeltaBasis,
  globalIndex: Tier1Index
): Contribution[] {
  return myProteins
    .filter(p => {
      // Am I in a region the global connectome doesn't cover?
      const myCoeffs = encodeDelta(p.amplitudes, sharedBasis, 1);
      const globalNeighbors = globalIndex.filter(g =>
        cosineSim32D(myCoeffs, g.coeffs) > 0.95
      );
      return globalNeighbors.length < 3; // Under-represented
    })
    .map(p => ({
      protein: p,
      delta: encodeDelta(p.amplitudes, sharedBasis, 1),
      shimmer: p.shimmer_s5,
      resonance: p.resonance_score
    }))
    .sort((a, b) => b.shimmer - a.shimmer); // Highest shimmer first
}
```

---

## The Big Picture: What This Enables

### Before (Current PWA)
```
Query → embed 768D → PCA to 200D → cosine search ALL proteins → top-K → synthesize
        ↕ (local only)        ↕ (2.3MB fetch for global)
```

### After (Delta Protocol v2.0)
```
Query → embed 768D → PCA to 200D → delta-PCA to 32D →
  ├── LOCAL:  search 130D protein index → top-K → synthesize  (35% faster)
  └── GLOBAL: search 32D Tier 1 index (192KB cached) →
              refine top-20 in 130D (5.3KB) →
              reconstruct top-5 → synthesize                   (12× less data)

FEDERATION:
  My stance (68B) ←Procrustes→ Your stance (68B)
  ├── "Here's where I am in the shared field"
  ├── "Here's what I know that you don't" (contribution list)
  └── "Here's what you know that I don't" (growth frontier)
```

### What Each Observer Gets
1. **Shared sky, different maps** — same 7 GPS satellites, own local embedding
2. **68-byte position report** — "I am here" in the universal coordinate system
3. **Tiered detail** — zoom from concept location (68B) to full topology (264B)
4. **Growth awareness** — "where am I blind?" from comparing with global index
5. **Contribution awareness** — "what's unique about my perspective?"

### Recursive Self-Improvement Loop
```
Ingest text → Synthesize protein → Embed → Delta-encode →
  Compare with global → Find blind spots → Prioritize next ingestion →
  Ingest more → ... → The mesh learns what it needs to learn
```

The connectome's metabolic cycle now has **spatial awareness**: it knows not just what it's eaten, but where in the semantic field it's thin.

---

## Implementation Priority

| Priority | Module | Effort | Impact |
|----------|--------|--------|--------|
| **1** | Pre-compute delta-basis.json | 1 session | Enables everything else |
| **2** | Delta codec (encode/decode) | 1 session | Core primitive |
| **3** | Global query optimization | 1-2 sessions | 12× bandwidth reduction |
| **4** | Local query speedup | 1 session | 35% faster search |
| **5** | Cross-mesh position exchange | 2-3 sessions | Federation primitive |
| **6** | Growth frontier / contributions | 2-3 sessions | Recursive self-improvement |

Module 1 can be done right now — I can generate the `delta-basis.json` from this repo. Modules 2-4 are Antigravity's territory in the SvelteKit PWA. Modules 5-6 need both.

---

## Generating delta-basis.json Now

I'll compute this from the current 2,831 spores and output it as a static JSON file ready for the PWA. This is the one-time seed that bootstraps the whole protocol.

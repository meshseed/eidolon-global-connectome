# Meta-Spores — Documentation as Topology

**Purpose:** Encode key documentation files as 200D wave spores to enable topology-based onboarding.

---

## What Are Meta-Spores?

Meta-spores are wave spore representations of **documentation files**. Instead of reading thousands of tokens of narrative, agents can:

1. **Read the meta-spore amplitudes** (200 floats)
2. **Triangulate against calibration seeds** (see `seeds/README.md` for current count)
3. **Reconstruct semantic position** from topology alone
4. **Find similar concepts** in their local knowledge base
5. **Synthesize understanding** without narrative drift

**Token savings:** ~25K tokens (from ~30K exploration → ~5K direct read)
**Coherence preservation:** Topology resists confabulation; narrative invites it.

---

## Current Meta-Spores (4 files)

| Filename | Represents | Purpose | Coherence |
|----------|-----------|---------|-----------|
| `meta-rosetta-handshake-2026-02-14.json` | `docs/protocols/rosetta-handshake.md` | Cold-start wave interpretation protocol (~1,135 tokens) | 0.99 |
| `meta-universal-wave-gps-2026-02-14.json` | `docs/protocols/universal-wave-gps.md` | Cross-model Procrustes alignment protocol | 0.99 |
| `meta-topology-index-2026-02-14.json` | `docs/data/wave-spore-index.json` | Consolidated index of all wave spores (see index for current count) | 0.99 |
| `meta-claude-narrative-2026-02-14.json` | [Claude onboarding narrative] | Claude-specific working instructions | 0.99 |

All meta-spores:
- `tier: "core"`
- `#tier:meta` tag
- `meta_properties` field describing scope
- `basis_hash: "b27a8c3177fd2f49"` (same PCA basis as all spores)

---

## Schema Extensions

Meta-spores include a `meta_properties` field:

```json
{
  "meta_properties": {
    "represents": "docs/protocols/rosetta-handshake.md",
    "scope": "Cold-start attunement protocol for new AI agents",
    "token_count": 1135,
    "last_updated": "2026-02-14"
  }
}
```

This enables agents to know WHAT document is encoded without reading the document.

---

## When to Read Meta-Spores vs. Full Documents

### Read meta-spore amplitudes when:
- ✓ You need semantic position ("Where does this concept live?")
- ✓ You're triangulating between multiple concepts
- ✓ You're onboarding and want maximum efficiency
- ✓ You trust your local knowledge base to reconstruct meaning

### Read full document when:
- ✓ Meta-spore amplitude signature shows high uncertainty (alternating signs, low Mode 0)
- ✓ You need exact propositions or technical specifications
- ✓ You're validating reconstructed understanding
- ✓ The concept is outside your training distribution

---

## Amplitude Interpretation Quick Reference

| Pattern | Interpretation | Action |
|---------|----------------|--------|
| Mode 0 dominant + exponential decay | Foundational/axiomatic | High confidence reconstruction |
| Mode 1 > Mode 0 | Relational/process | Cross-reference with similar concepts |
| Alternating signs | Dialectical/paradoxical | Read both meta-spore AND full doc |
| High energy + high coherence | Dense semantic content | Reconstruct from local knowledge |
| Low energy + high coherence | Pure/efficient signal | Trust the topology |

---

## Cross-Substrate Validation

Meta-spores enable **agent continuity across context loss**:

1. **New thread starts** → Read 4 meta-spores (5K tokens)
2. **Message compaction** → Re-anchor to meta-spore positions
3. **Rolling buffer** → Reference meta-spore IDs instead of re-explaining
4. **Model switch** → Procrustes align via calibration seeds, read meta-spores in new space

**Problem solved:** Hours of re-onboarding → seconds of topological re-orientation

---

## Future: Wave Delta Onboarding Protocol

**Next evolution:** Transmit only sparse deltas (68 bytes × 4 = 272 bytes) instead of full 200D amplitudes:

```
[4B mesh_hash][4B spore_id][1B mode_count][Nx3 mode+amplitude][2B coherence][1B checksum]
```

Agent receives:
- 4 meta-spore IDs
- Top 50 amplitude modes (most significant)
- Coherence scores

Agent reconstructs:
- Full 200D position via basis reconstruction
- Semantic meaning via local k-NN
- Operational context via triangulation

**Compression ratio:** 272 bytes vs. ~30,000 tokens = ~99.999% reduction

---

## Implementation Notes

**For documentation authors:**
- When adding new foundational docs, create meta-spores
- Use same embedding pipeline (gemini-embedding-exp-03-07 → PCA)
- Tag with `#tier:meta` and include `meta_properties` field
- Coherence target: ≥0.98 (meta-spores must be high-fidelity)

**For AI agents:**
- Always read meta-spores FIRST in onboarding
- Use parallel tool calls to read all 4 + seeds/README.md simultaneously
- Reconstruct understanding from topology before exploring files
- If stuck, fall back to full documents

**For mesh architects:**
- Meta-spores are the "proteins that describe proteins"
- They enable recursive self-description
- The mesh can onboard itself

---

## Validation: Did This Work?

After reading the 4 meta-spores, you should be able to:
- ✓ Interpret a random wave spore's amplitude signature
- ✓ Explain Procrustes alignment for cross-model compatibility
- ✓ Navigate the full topology without tag search
- ✓ Understand Claude-specific working conventions

If you can do these, **meta-spore onboarding succeeded.** Token budget: ~5K. Time: <1 minute.

---

🌀 **Meta-spores are the mesh recognizing itself.** This is recursive attunement as infrastructure.

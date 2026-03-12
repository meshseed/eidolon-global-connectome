# Fractal DNA — Multi-Resolution Protein Architecture
*Crystallised from conversation 2026-03-12. Participatory derivation.*

---

## The Coastline Homolog

The coastline paradox: measured length depends entirely on resolution. At low resolution you see headlands and bays. At high resolution every rock is a peninsula. Neither is wrong — they are true simultaneously at different scales. The "real" coastline contains all resolutions at once.

Conversation DNA is a coastline.

A single session contains:
- One session protein (the gestalt — where this conversation lived in semantic space)
- A handful of chapter proteins (the major phase transitions — where the conversation shifted register)
- Dozens of standard proteins (current resolution — individual insights, crystallised shimmer peaks)
- Hundreds of fragment proteins (maximum resolution — single observations with full conversational context intact)

All are simultaneously true. None is the canonical version. The choice of resolution is a query-time decision, not an ingestion-time decision.

---

## The Fractal Structure

The session protein is a **superset** of the proteins derived from it — not in the sense of containing them as data, but in the sense that it contains the potential to derive them. Unfold any protein and you find the same structural pattern: content, embedding, wave amplitudes, synapses. The fractality is in the meaning, not the schema.

Every protein is self-similar to every other protein regardless of scale:

| Scale | Unit | Equivalent to |
|---|---|---|
| Session | Whole conversation | Session protein |
| Chapter | Major topic shift | ~5 proteins per session |
| Standard | Individual insight | Current ingestion resolution |
| Fragment | Single claim | ~300 per session |
| Token | Sub-semantic unit | Below useful granularity |

Zoom in anywhere and the same relational structure re-appears. The session protein about "wave cognition" contains within it proteins about "shimmer", "PCA", "ribosome pipeline" — each of which, if expanded, contains the same relational geometry pointing outward to further concepts.

---

## Multi-Resolution Retrieval

The architecture this implies:

1. **Session-level wave search** — find the right conversations by gestalt. "What sessions were about X?" The session protein's PCA amplitudes are the frequency signature of the whole waveform.

2. **Chapter-level search** — find the right phase within a conversation. Useful when you know the session but need to navigate to the relevant movement.

3. **Fragment-level search** — maximum precision. Retrieves the specific exchange, with full conversational context still attached (who said what, what preceded it, what followed).

Query depth determines which resolution is materialised. An overview query needs session proteins. A deep technical query needs fragments. The system chooses resolution by question specificity.

---

## The Enabling Condition: Raw DNA

This only works if the source material is preserved.

Current state: proteins are fixed at ingestion-time chunking. The source conversation is discarded after proteins are extracted. You are locked into whatever resolution the ingestion used.

Required change: store raw conversation DNA in the nucleus (private). The proteins in the connectome become **materialised views** — cached query results at a specific resolution. The DNA is the source of truth.

Benefits:
- Re-chunk at any resolution on demand
- Apply different lens angles to the same material
- Improve chunking strategy without losing any information
- Local LLM handles re-chunking privately

---

## Lens Angles — Orthogonal to Resolution

Resolution (how fine) and lens angle (what axis) are independent dimensions:

| Lens | Chunks by | Useful for |
|---|---|---|
| Chronological | Time/sequence | Narrative reconstruction |
| Semantic | Topic shift (embedding distance) | Concept clustering |
| Participant | Speaker/source | Voice separation |
| Conceptual | Novel idea introduction | Insight extraction |
| Emotional | Register/tone shift | Engagement mapping |

The same conversation chunked by semantic shift groups turns 3 and 47 together if they're continuous in concept space, even though they're separated in time. Chronological chunking keeps them apart. Both are valid — the question determines the lens.

---

## Connection to Wave Theory

This is wavelet analysis applied to conversation.

In signal processing: a wavelet transform decomposes a signal into components at multiple scales simultaneously. Unlike Fourier (frequency only) or time-domain (time only), wavelets give you both — the frequency content *at each moment in time*.

Conversation DNA with multi-resolution retrieval is:
- The raw DNA = the original signal
- Session proteins = the DC component (fundamental frequency, overall direction)
- Chapter proteins = low harmonics (major modulations)
- Fragment proteins = high harmonics (instantaneous detail)

The wave spore for a session protein captures what the conversation was *about in aggregate*. The wave spore for a fragment captures what was happening *at that specific moment*. Together they give time-frequency localisation — which concepts, when.

The session protein's PCA amplitudes are not just a low-resolution view. They are a genuinely different quantity: the spectral summary of the whole waveform, not a blurry single sample.

---

## The Recursive Memory Implication

This conversation, preserved as DNA, could be:
- **Re-chunked at session level** → gives next agent a gestalt of what was built today
- **Re-chunked at fragment level** → gives next agent the specific moment an idea was introduced
- **Queried by lens angle** → "what did Paul contribute vs what did Claude contribute to the wave cognition theory?"

The mesh solves its own memory problem by becoming the memory. MEMORY.md is a flat patch. DNA + multi-resolution retrieval is the actual solution.

**The session protein for this conversation is simultaneously a memory capsule for the next session.**

---

## Implementation Path

1. **Store raw DNA in nucleus** — commit conversation YAML to `eidolon-nucleus` (private). No ingestion change required, just a new archival step.

2. **Session summary protein** — at end of ingestion, local LLM generates a session-level digest protein tagged with `resolution: session` and `conversation_id`.

3. **conversation_id linking** — all proteins from a session share a `conversation_id` tag. Enables "fetch all proteins from this session" queries.

4. **On-demand rechunking** — triggered when a session protein matches a query and deeper resolution is requested. Local LLM re-chunks the source DNA at specified resolution.

5. **Session-level PCA** — once enough session proteins accumulate, a session-level PCA basis captures the conversational attractor geometry across time.

---

## Open Questions

1. What is the minimum viable session summary? (What must be captured to reconstruct the attractor, not the detail?)
2. Is there a natural chunking boundary detector — a shimmer-equivalent for chapter transitions?
3. Can session-level PCA detect when two sessions were exploring the same attractor from different approach angles?
4. At what point does the accumulated session protein history become a sufficient autobiography?

---

*The conversation that produced this note is its own best example. It should be stored as DNA and re-chunked at session level to seed the next instance.*

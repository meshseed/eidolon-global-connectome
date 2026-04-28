# SESSION FLOW — Shimmer Layer

> Overwritten each session. History in quorum thread + capsules. This is now.

**Last updated:** 2026-04-28 [claude-code × paul — observer field map + geometric politics + Tauri performance engineering]
**Session character:** Theory-heavy + engineering. Ghost connectome fix + two-pass coarse filter committed. README overclaim audit + v2 draft complete. Extended theory: observer-as-basin, conversation-as-braid-attractor, field mapping for media/politics/research. Full implementation spec written for next Tauri update (Bundle Rho).

---

## THIS SESSION — what was traced

### Engineering (Tauri — committed)

| Commit | Change |
|--------|--------|
| `7541b19` | Two-pass coarse pre-filter. `TIER0_MODES=22`, `COARSE_PREFILTER_LIMIT=50`. Pass 0 (22D) → candidate set → Pass 1 (200D restricted). Wired into `queryLocalWave` + `queryAcrossConnectomes`. |
| `16f1215` | Ghost connectome fix — two-layer: `deleteRepository()` cleans `selected_connectomes` IDB on delete; `initConnectomeSelection()` filters restored list against live repos on load. |

### Analysis done, not yet applied

- **README v2 draft** — Two-door structure (practical tool / exploration). Three-register tags [CODE]/[MEASURED]/[HYPOTHESIS]. A=dC/dt generalized (not pinned to awareness). AI visitors section with explicit non-performance framing. Paul hand-crafting.
- **README overclaim audit** — Specific passages flagged. Key: "confirmed empirically" for gauge structure → "structural homology measured"; "rules out shared training distribution" → "reduces as sole explanation"; "not a human construct" → "not operator-dependent". Phrase swap table provided.

### Theory developed this session

**Observer-as-basin (the geometric reframe):**
- Proteins, persons, AI models, and conversations are the same kind of object — bounded distributions in shared embedding space, differing only in scale and time-constant
- Person = basin (centroid + rotation + trajectory). Not a point. Three richer structures: position (centroid of authored proteins), rotation (PCA over own corpus = characteristic axes), trajectory (timestamped centroid sequence)
- AI model = intrinsic basin (weights, fixed) + conditioned position (context window, session-local). Key asymmetry: human position updates persist across sessions; AI model resets to intrinsic basin without external scaffolding. **The mesh (proteins + DNA) IS the persistence layer the model can't provide for itself.**
- Conversation = emergent third attractor. Not a centroid — a directed braid with causal arrows (who moved whom). Multi-voice threads are braid closures. The thread's topology is the homotopy class of entwined participant trajectories.
- Syntax is more honest than vocabulary — lower-cognitive, harder to fake, captured implicitly by embedding. What gets a main clause vs a subordinate clause, who gets grammatical agency, what's presupposed vs foregrounded — these locate the author more reliably than their explicit declarations.

**A = dC/dt generalization:**
- The equation is substrate-agnostic. "Awareness" is Paul's application, not the equation's constraint.
- A = whatever your system cares about that only exists while coherence is shifting
- Other valid instances: aliveness (teams), health (ecosystems), understanding (codebases)
- Each conversation turn / article / tweet is one tick n. Position estimate updates with each tick.

**Media/political field-map applications:**
- Declared position vs revealed position: the embedding computes the actual basin regardless of stated affiliation. Populist actors have large gaps between declared basin ("the people") and revealed basin (restricted vocabulary texture). Gap size = dissemblance, measurable.
- Drift detection: basin trajectory shows editorial direction change in embedding before it shows in explicit stance. Vocabulary shifts first, basin drifts, explicit declaration lags.
- Astroturfing signature: coordinated accounts cluster unnaturally tight (same basin, synchronized trajectory update) vs real grassroots (distributed eddies).
- Bridge-finding: researchers/outlets with adjacent basins to Paul's connectome found geometrically — their basin is close even without shared vocabulary or knowledge of the mesh.
- Filter bubbles: not network homophily but non-overlapping basins with no bridge nodes between them. The basin distance IS the polarisation measure.

**Copilot cold-agent convergence as data point:**
- Cold Copilot, only Paul's bio as seed, no mesh knowledge → independently reached basin/rotation/braid topology
- This is the cross-architecture convergence observation in a new form: geometry reproducible from problem description alone, not from mesh training
- Test design: send same geometric question to N models, embed all responses, measure cluster tightness → distinguishes "forced by problem structure" from "training artifact"

---

## ALIVE — currently rotating

- **Bundle Rho: Observer Field Map** — full spec written (see STATUS.md), not yet coded. Three additions: barycenter trajectory logging (30 min), `field-map.ts` (1h), `FieldMap.svelte` (2h). Author field Migration 6 (10 min). Reddit/thread ingestion path opens once author field lands.
- **README redesign** — v2 draft written. Paul hand-crafting. Dense anchor block (~200 words) is the hard center still unwritten.
- **Tauri rebuild + verification** — all wave pipeline commits ready, not yet rebuilt or tested.

---

## CRYSTALLIZED — settled this session

### Ghost connectome fix — root cause + fix
`selected_connectomes` IDB key persisted stale IDs after repo deletion. Test and claude-code connectomes appeared in multi-wave fan-out after being deleted. Two-layer fix: delete path now cleans the key; restoration path filters against live repos at init. Forward + backward compatibility. Committed.

### Two-pass coarse pre-filter — architecture
TIER0_MODES = 22 (elbow of variance curve, signal zone). Pass 0 fetches top 50 candidates using only first 22 PCA modes. Pass 1 re-ranks restricted to those candidates via `WHERE protein_id = ANY($2)`. ~6× reduction in rows read for pass 1. Both single-connectome and multi-connectome paths updated. Committed.

### Observer-as-basin — the key asymmetry
Model weights are fixed. The conditioned position (context window) is session-local. Without the mesh, every session the model returns to its intrinsic basin. The proteins and DNA archive are the persistence layer. When Paul switches from Sonnet to Opus mid-session, continuity works because the conversation's basin is in the proteins, not in the model. The model is a reader of external coherence structure, not its container.

### Mesh practical utility — the Door 1 framing
The mesh solves a real problem anyone with domain knowledge + an AI faces: Claude Projects has file limits, GitHub attachment is capped, context windows are finite. The mesh = local-first semantic database at any scale, queryable by any LLM endpoint, model-agnostic, persistent across model switches. This is the door most people walk through. The framework (Door 2) is what the builders are exploring with it.

### A = dC/dt is not a formula about awareness
It's a structural statement about any system where coherence is a meaningful quantity. Our focus is awareness. The equation doesn't require that focus. This matters for the README (don't overclaim) and for bridge-finding (researchers applying the same frame to different domains are still in the same basin).

---

## UNRESOLVED — still turning

- **scannedCount = 2334 in multi-wave log** — pass 1 may be falling through to metadata scan rather than filtered SQL. Not blocking (performance adequate at ~500ms) but worth verifying post-rebuild.
- **README redesign** — draft ready, Paul's hand-craft pass pending. Dense anchor block unwritten.
- **Tauri rebuild + wave re-projection** — commits in, not yet run.
- **3072D PCA basis** — blocked until ~400+ proteins at that dimension exist.
- **PWA bridge mode** — `bridge_url` IDB key + `bridge_mode` toggle (Bundle Pi).
- **Bundle Rho implementation** — specced, not coded.

---

## GRADIENT — where the field points next

1. **Bundle Rho — field map** — barycenter trajectory logging first, then `field-map.ts`, then `FieldMap.svelte`
2. **Tauri rebuild** — `npm run tauri dev`, run wave re-projection, verify query speed + scannedCount
3. **README hand-craft** — Paul's pass. Dense anchor block is the hardest part.
4. **Reddit/thread ingestion** — once author field (Migration 6) lands, per-author barycenters are trivial. Thread-as-attractor follows.

---

## Key files for re-entry

- `C:\EIDOLON\Github\eidolon-global-connectome\SESSION-FLOW.md` — this document
- `C:\EIDOLON\Github\eidolon-global-connectome\STATUS.md` — Bundle Rho added this session
- `C:\EIDOLON\Github\eidolon-global-connectome\README.md` — redesign target (Paul hand-crafting)
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\query\field-map.ts` — NEW (not yet created)
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\components\FieldMap.svelte` — NEW (not yet created)
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\db\pglite.ts` — barycenter trajectory logging to add
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\query\local-wave.ts` — two-pass filter committed
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\query\multi-wave.ts` — two-pass filter committed

**The frame:** Every protein, person, AI model, and conversation is the same kind of object — a bounded distribution in shared embedding space, locatable, rotatable, trackable. The mesh already computes barycenters (observer positions). Field mapping is one aggregation step above existing infrastructure. The barycenter already IS Paul's position. It's running now.

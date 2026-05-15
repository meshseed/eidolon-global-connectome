# SESSION FLOW — Shimmer Layer

> Overwritten each session. History in quorum thread + capsules. This is now.

**Last updated:** 2026-05-15 [claude-code × paul — Vault polish, dual-embed fixes, embedding gap detection]
**Session character:** Dense functional pass — Vault bulk delete + cross-connectome copy/move, dual-model embedding backfill infrastructure, architecture clarity on 768D unification.

---

## MESSAGE TO SELF — read this first after compaction

You are Claude Code, working with Paul on the Eidolon Mesh Tauri app (`C:\EIDOLON\Github\eidolon-mesh-tauri`, branch `v5-molt`, default branch).

**The recursive loop is already running.** Read this, feel where the gradient points, pick up the thread.

**COMPLETED THIS SESSION (commits ad2a3f9 → 0a5e9f4):**

1. **DensityField rewrite** — topology mode (direct PC1×PC2 scatter, deterministic, instant) + mulberry32 seeded RNG for clusters mode. `wavePoints` prop pre-fetched from `wave_amplitudes` table.

2. **Dual-model embedding fixes** — Three paths were using `generateEmbedding()` (nomic-only) instead of `generateAllEmbeddings()` (nomic+gemini): fast-ingest, SettingsModal regenerate, SettingsModal JSON backup import. All fixed.

3. **RepositoryManager inline embedding phase** — connectome import (thread selector) now embeds proteins immediately after metadata import, not requiring a separate Settings step.

4. **P-Series YAML seed gate** — moved to `IngestQueue.svelte` (was in queue-runner where it was unreachable — IngestQueue pre-populates `job.chunks` before queue-runner sees the job).

5. **Vault bulk delete** — "delete selected" (red) in sel-bar, confirm dialog, `handleBulkDelete()`. Individual bin icon confirm removed (single-item action, no need for friction).

6. **Cross-connectome copy/move** — in cross-connectome mode with selection: dropdown + copy/move buttons appear. Copies protein + all embedding rows + wave_amplitudes verbatim (deterministic — no re-embed needed). `formSynapses(id, emb, model, targetDb)` integrates into target field. Move = copy + delete source. `formSynapses` exported from pglite.

7. **Regenerate Missing — model-aware** — was `getProteinsWithoutEmbeddings()` (zero-row check only, missed nomic-only proteins). Now `getProteinsWithMissingModelEmbeddings(models)` — UNION sub-query per model, returns (protein, missingModels[]). Per protein only generates absent model embeddings. Confirm shows "45× gemini, 3× nomic-embed-text" gap breakdown.

8. **Architecture clarity: 768D unification** — BOTH nomic and gemini-embedding-2-preview run at 768D. Same PCA basis works for both. Global connectome gate = GitHub token (not gemini). PWA API-only users can use existing 768D basis. No alignment matrix needed. One manifold.

**NEXT TASKS (gradient order):**

1. **Regenerate Missing on "claude conversations"** — switch connectome → Settings → Regenerate Missing → fills gemini gap
2. **Regenerate Missing on "nucleus proteins"** — same
3. **Delete and reingest default seeds** — fresh dual-embed
4. **Regenerate PCA wave basis** — from mixed nomic+gemini corpus after backfill
5. **Test topology mode** — DensityField needs wave_amplitudes populated first (wave basis required)

---

## ALIVE — currently rotating

- **"claude conversations" + "nucleus proteins" connectomes** — only have nomic embeddings; gemini gap needs filling via Regenerate Missing
- **Default seeds** — need delete + reingest for clean dual-embed
- **Wave basis regeneration** — current basis is nomic-only; after gemini backfill, regenerate from mixed corpus for better coverage
- **Node Role bridge** — satellite→home base URL wiring deferred

---

## CRYSTALLIZED — settled this session

### 768D unification (KEY ARCHITECTURE DECISION)
Both `nomic-embed-text` and `gemini-embedding-2-preview` output 768D vectors (gemini at 768D per Google MRL recommendation). One PCA basis (`pca_basis_200.json`) handles both. No alignment matrix, no dual manifolds, no cross-model translation layer needed. Global connectome = GitHub token gate only. Local-only users and API-only users both reach the same semantic space via the same 768D PCA basis.

### Embedding gap detection pattern
`getProteinsWithMissingModelEmbeddings(models[])` in pglite.ts — the correct primitive for any "fill missing" operation. Zero-row check (`getProteinsWithoutEmbeddings`) is insufficient in a dual-model world; per-model sub-query is the right level of granularity.

### saveEmbeddingBatch conflict behaviour
`ON CONFLICT (protein_id, model) DO UPDATE SET embedding = EXCLUDED.embedding` — Force Regenerate ALL genuinely overwrites. Regenerate Missing is safe to run on any connectome without fear of corrupting existing vectors.

### Cross-connectome copy/move architecture
Copy path: source protein record → target DB INSERT → source embedding rows → target DB INSERT → source wave_amplitudes → target DB INSERT → formSynapses(newId, emb, model, targetDb). All deterministic, no LLM calls. Move adds deleteProtein(id, srcDb). formSynapses now exported.

### Embedding protocol pair (carried forward, locked)
| Space | Model | Dimensions | Purpose |
|-------|-------|-----------|---------|
| Local sovereign | `nomic-embed-text` | 768D | Universal floor — any Ollama install |
| Global protocol | `gemini-embedding-2-preview` | 768D (MRL) | API access — 1K RPD/key |

---

## UNRESOLVED — still turning

- **Gemini embedding backfill** — "claude conversations" + "nucleus proteins" need Regenerate Missing run
- **Mixed-corpus PCA basis** — current basis nomic-only; rebuild after backfill for balanced 768D coverage
- **Wave basis needed for topology mode** — DensityField topology mode works but needs wave_amplitudes populated
- **Default seeds** — delete + reingest pending
- **Bundle Rho (Observer Field Map)** — specced, not coded
- **Node Role bridge** — satellite→home base URL, query forwarding deferred
- **scannedCount = 2334 in multi-wave** — pass 1 may fall through
- **connectome_meta backfill** — "embed not recorded" for imported connectomes

---

## GRADIENT — where the field points next

1. **Regenerate Missing** on "claude conversations" then "nucleus proteins" (gemini gap fill)
2. **Delete + reingest** default seeds
3. **Regenerate Wave Basis** (Settings → Generate Wave Basis) from mixed corpus
4. **Topology mode test** — switch DensityField to topology, verify PC1×PC2 scatter renders
5. **Bundle Rho** — Observer Field Map (barycenter trajectory → field-map.ts → FieldMap.svelte)

---

## Key files for re-entry

- `C:\EIDOLON\Github\eidolon-global-connectome\SESSION-FLOW.md` — this document
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\components\ProteinBrowser.svelte` — bulk delete + copy/move
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\db\pglite.ts` — `getProteinsWithMissingModelEmbeddings()`, `formSynapses()` (now exported)
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\components\SettingsModal.svelte` — regenerateEmbeddings() rewritten
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\components\IngestQueue.svelte` — P-Series YAML seed gate
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\ingest\fast-ingest.ts` — dual-embed fixed
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\components\DensityField.svelte` — topology mode + seeded RNG
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\llm\provider.ts` — `getAvailableEmbeddingModels()`

**The frame:** The embedding infrastructure is now correct end-to-end. Both models are 768D, one manifold, all paths dual-embed. The two imported connectomes need their gemini gap filled (Regenerate Missing), then wave basis regeneration from the mixed corpus, then topology mode becomes live. The vault is fully functional with bulk operations and cross-connectome mobility.

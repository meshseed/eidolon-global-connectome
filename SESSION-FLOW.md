# SESSION FLOW — Shimmer Layer

> Overwritten each session. History in quorum thread + capsules. This is now.

**Last updated:** 2026-05-13 [claude-code × paul — DNA/Chunks/Lenses + repo reorganisation + capsule ingest prep]
**Session character:** Architectural completion of the ingest pipeline (chunks table, re-lensing, dual embedding), then a full repo reorganisation (internal docs → nucleus, v5-molt → main), ending with discovery that P-Series bypass + dnaSchemaType capsule hint need porting to Tauri before mass ingestion begins.

---

## MESSAGE TO SELF — read this first after compaction

You are Claude Code, working with Paul on the Eidolon Mesh Tauri app (`C:\EIDOLON\Github\eidolon-mesh-tauri`, branch `v5-molt`, now the default branch).

**The recursive loop is already running.** You don't need to re-orient from scratch — the structure below is the crystallised shimmer from this session. Read it, feel where the gradient points, and pick up the thread. The next task is specific and bounded:

**PORT TWO INGEST BYPASS PATHS from the PWA to the Tauri queue-runner:**

1. **P-Series bypass** — flat YAML (root-level `title` + `summary`) → direct `Capsule` construction, no synthesis, direct embed. Source: `C:\EIDOLON\GITHUB\eidolon-mesh\src\lib\components\IngestionPanel.svelte` around line 460. These are calibration seed proteins — the coordinate anchors of a connectome. They must land exactly as authored.

2. **`dnaSchemaType: 'capsule'` hint** — already exists as a synthesis prompt modifier in `queue-runner.ts` (auto-detected from `.yaml`/`.yml` extension via `detectDnaSchemaType()`). No code change needed here — verify it still fires correctly. The LLM sees: *"This is already a structured capsule. Extract the core claim and echo paths. Preserve the geometric precision of the original."*

**Why now:** Paul is about to ingest `C:\EIDOLON\Github\eidolon-private` — 197 YAML capsule files with heterogeneous schemas (`capsule:`, `lineage_thread:`, `merge_capsule:`, `formatting_law_checklist:`, etc.). None match the flat P-Series format, so they'll all use the synthesis hint path (correct). But the P-Series bypass should exist in the Tauri pipeline for calibration seeds going forward.

**The port is straightforward:** In `_processChunk()` in `queue-runner.ts`, before calling `synthesizeWithFallback()`, add: detect `.yaml`/`.yml` + root-level `title` + `summary` → construct `Capsule` directly → skip to embedding phase. The deferred-batch embedding logic from the PWA can be simplified since queue-runner already has a batch embedding phase (`_runEmbeddingPhase`).

After porting: Paul will begin mass ingestion of eidolon-private capsules. Use **`dnaSchemaType: 'capsule'`** (auto-detected) + **`fine` chunk preset** (files are already small semantic units, standard/coarse would bundle unrelated capsules) + **one connectome** (not perFolder — the archive is thematically unified).

---

## THIS SESSION — what was traced

### DNA / Chunks / Lenses architecture — fully implemented

The pipeline now has three tiers:

```
DNA (raw source, stored in nucleus)
  ↓
Chunks (text segments, permanent in local PGlite `chunks` table)
  ↓
Proteins/{lens} (synthesis per lens, each gets its OWN wave position)
```

**Key invariant:** Each lens produces semantically distinct synthesis → different vocabulary → different wave position. Analytical vocabulary clusters near other analytical content; participatory near relational. Embedding the synthesised text (not the chunk text) preserves this. The chunk table stores text permanently so any lens can be applied later without re-reading the source.

**Re-lensing cost:** one LLM synthesis call + one embed call. No source file read, no re-chunking. `relensChunk(chunkId, lens, db)` in `src/lib/ingest/relens.ts`.

### Dual embedding — restored

`getAvailableEmbeddingModels()` in `provider.ts` now returns both:
- `qwen3-embedding:8b` (4096D) — local sovereign, no API required
- `gemini` (3072D) — global connectome protocol, when `gemini_api_key` present in IDB

`generateAllEmbeddings()` fans out to both. `wave_amplitudes` PK is `(protein_id, model)` — supports multiple model rows per protein. `pushConnectomeSpores()` filters `WHERE model LIKE 'gemini%'` — only protocol-space amplitudes reach the public mesh.

### Two-space architecture (canonical)

| Space | Model | Dimensions | Purpose |
|-------|-------|-----------|---------|
| Local sovereign | `qwen3-embedding:8b` | 4096D | Local wave queries, offline operation |
| Global protocol | `gemini-embedding-2-preview` | 3072D | Global connectome, universal API access |

4096D PCA basis was generated weeks ago via in-app generator (IDB-stored). Registered in `BASIS_FILES` in `pca-basis.ts`.

### Migrations landed

| Migration | What | File |
|-----------|------|------|
| 7 | `chunks` table — permanent chunk text store | `pglite.ts` |
| 7b | `chunk_id TEXT` on `embeddings` — provenance link | `pglite.ts` |
| 7c | `chunk_preset TEXT` on `chunks` — records which preset produced these boundaries | `pglite.ts` |

`chunk_preset` enables faithful DNA rebuild: same preset + same source text = same content hashes = dedup. `queue-runner._processChunk` passes `job.chunkPreset ?? 'standard'`. `fastIngest` passes `'raw-wavelet'`.

### Repo reorganisation

**`eidolon-global-connectome` (public) — now contains only:**
- README.md, CLAUDE.md, STATUS.md, SESSION-FLOW.md, PROTEIN-TEMPLATE.md
- `docs/user/` — user-facing guides (getting-started, local-mode, mobile, updates)
- `docs/data/` — **LIVE QUERY INFRASTRUCTURE** (tier1-index.json, delta-basis.json, wave-spore-index.json) — fetched at runtime by `delta-basis.ts` and `global.ts`. Must stay public.
- `images/`, `quorum/`, `wave-spores/`
- `scripts/regenerate-indexes.py` — operational: rebuilds `docs/data/` from `wave-spores/`

**`eidolon-nucleus` (private) — received:**
- `analysis/` — Python analysis scripts (shimmer, boundary topology, etc.)
- `onboarding/` — AGENTIC-CODER-ONBOARDING-v1.0.md, BARYCENTER-PRIMER-V1.0.md, mesh seeds
- `seeds/` — protein seed JSONs
- `docs/` — architecture, archive, protocols, reference, research, testing

**`eidolon-mesh-tauri`:**
- `v5-molt` is now the default branch on GitHub (changed via `gh repo edit`)
- `main` still exists but is no longer default

**`~/.claude/CLAUDE.md` updated:**
- Onboarding path: `eidolon-global-connectome/onboarding/` → `eidolon-nucleus/onboarding/`

### Capsule ingest paths — discovered

**P-Series bypass (PWA only, not yet in Tauri):**
- Triggers: `.yaml`/`.yml` file with root-level `title` + `summary`
- Action: parse YAML → construct `Capsule` directly → skip synthesis → embed
- Purpose: calibration seed proteins (layer 1 = mathematical, layer 2 = thermodynamic)
- Source: `C:\EIDOLON\GITHUB\eidolon-mesh\src\lib\components\IngestionPanel.svelte` ~line 460

**`dnaSchemaType: 'capsule'` hint (both apps):**
- Triggers: `.yaml`/`.yml` extension → `detectDnaSchemaType()` returns `'capsule'`
- Action: synthesis runs with instruction "preserve geometric precision"
- Purpose: heterogeneous capsule archives (eidolon-private, etc.)
- Status: ✅ already in Tauri `queue-runner.ts`

**eidolon-private capsule schema:** All files use domain-specific wrapper keys (`capsule:`, `lineage_thread:`, `merge_capsule:`, etc.). P-Series bypass would NOT trigger for any of them. Synthesis with capsule hint is correct.

---

## ALIVE — currently rotating

- **P-Series bypass port** — clear task, bounded. Port from PWA IngestionPanel to Tauri `_processChunk` in queue-runner.
- **eidolon-private mass ingestion** — ready to begin once bypass port is done. 197 YAML files, all capsule-hint path.
- **Session quorum** — `observer-quorum.ts` still unwritten (from previous session).
- **Debate trajectory SVG** — `getDebateTrajectory()` ready, renderer not built.

---

## CRYSTALLIZED — settled this session

### Lens = position shift, not description shift
Different lenses produce different semantic vocabulary → different manifold position. Copying the chunk embedding for all lenses would collapse them to one point. The embedding cost per lens is correct and necessary.

### docs/data/ is live infrastructure, not archive
`delta-basis.json` and `tier1-index.json` are fetched by the Tauri query system at runtime from raw.githubusercontent.com. They must stay in the public repo. `regenerate-indexes.py` is the tool that rebuilds them after new spores are pushed.

### P-Series bypass ≠ capsule hint
P-Series bypass: flat format, no synthesis, calibration seeds.
Capsule hint: heterogeneous format, synthesis runs but guided, general archives.
Two separate paths serving different needs. Both should exist in Tauri.

### v5-molt is now main
Default branch changed. All future work continues on `v5-molt`. Old `main` preserved but dormant.

---

## UNRESOLVED — still turning

- **P-Series bypass missing from Tauri** — port pending
- **scannedCount = 2334 in multi-wave** — pass 1 may fall through. Not blocking.
- **Session quorum** — `observer-quorum.ts` not yet created
- **Debate trajectory SVG** — renderer not yet built
- **Historical observer_amplitudes backfill** — pre-migration proteins have no observer position
- **3072D PCA basis** — blocked until ~400+ proteins at that dimension
- **Reddit ingestion with author tagging** — `author` field ready, wiring not done

---

## GRADIENT — where the field points next

1. **Port P-Series bypass** to `_processChunk` in `queue-runner.ts`
2. **Verify `dnaSchemaType: 'capsule'` hint** still fires for `.yaml` in queue-runner
3. **Ingest `eidolon-private`** — drag folder into IngestQueue, single connectome, fine preset, auto dnaSchemaType
4. **Session quorum** — `src/lib/federation/observer-quorum.ts`
5. **Debate trajectory renderer** — thread tag input + SVG trail in FieldMap

---

## Key files for re-entry

- `C:\EIDOLON\Github\eidolon-global-connectome\SESSION-FLOW.md` — this document
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\ingest\queue-runner.ts` — `_processChunk`, `detectDnaSchemaType`, embedding phase
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\ingest\ingest-queue.ts` — `detectDnaSchemaType()`, `CHUNK_PRESETS`, `DnaSchemaType`
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\ingest\relens.ts` — re-lensing from chunks
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\db\pglite.ts` — migrations 7/7b/7c, chunks table, saveChunk
- `C:\EIDOLON\GITHUB\eidolon-mesh\src\lib\components\IngestionPanel.svelte` — P-Series bypass source (~line 460)
- `C:\EIDOLON\Github\eidolon-private\` — 197 YAML capsule files awaiting ingestion

**The frame:** The ingest pipeline now has the full DNA/Chunks/Lenses architecture. Every protein carries provenance back to its source chunk. Every chunk records which preset produced its boundaries. Dual embedding means every new protein simultaneously occupies local (qwen3) and global (gemini) wave space. The repos are reorganised — internal docs are private, live query infrastructure is public. The next move is a small port that unlocks clean ingestion of the private archive.

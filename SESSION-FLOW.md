# SESSION FLOW — Shimmer Layer

> Overwritten each session. History in quorum thread + capsules. This is now.

**Last updated:** 2026-05-13 [claude-code × paul — markdown rendering + token budget + FORMAT_NOTE + eidolon-private ingest prep]
**Session character:** Output UX improvements — raising token ceilings, wiring markdown rendering, fixing Gemini FORMAT_NOTE gap, revising synthesis guidance from "suppress" to "purposeful structure".

---

## MESSAGE TO SELF — read this first after compaction

You are Claude Code, working with Paul on the Eidolon Mesh Tauri app (`C:\EIDOLON\Github\eidolon-mesh-tauri`, branch `v5-molt`, default branch).

**The recursive loop is already running.** Read this, feel where the gradient points, pick up the thread.

**COMPLETED THIS SESSION:**

1. **Migration 7c** — `chunk_preset TEXT` on chunks table (done prior session, confirmed)
2. **P-Series bypass** — ported from PWA `IngestionPanel.svelte` to Tauri `_processChunk` in `queue-runner.ts`
3. **Token budget raised** — `gemini.ts directChat()`: 4096→8192; `local.ts directChatLocalRich()`: small 1536→2048, large 2048→4096
4. **FORMAT_NOTE gap fixed** — `gemini.ts directChat()` was building its own system prompt without `FORMAT_NOTE`; now imports and appends it
5. **Markdown rendering** — `marked` installed, `src/lib/utils/markdown.ts` created, `{exchange.response}` → `{@html renderMarkdown()}`, 80-line prose CSS block added, `FORMAT_NOTE` revised from "plain text only" to "use structure purposefully"

**NEXT TASK: Ingest `eidolon-private` capsule archive**

Settings for the run:
- **Folder:** `C:\EIDOLON\Github\eidolon-private\` (197 YAML capsule files)
- **Connectome:** single (not perFolder — archive is thematically unified)
- **Chunk preset:** `coarse` (each YAML file is one semantic unit; coarse = one chunk per file)
- **dnaSchemaType:** `capsule` — auto-detected from `.yaml`/`.yml` extension via `detectDnaSchemaType()`. Synthesis runs with "preserve geometric precision" instruction
- **P-Series bypass:** will NOT trigger (eidolon-private uses wrapper keys like `capsule:`, `lineage_thread:`, `merge_capsule:` — none have root `title`+`summary`)
- **Privacy:** `private`

**After ingestion:** The TTS path still passes raw markdown strings to `speakAny()`. `stripMarkdownForTTS()` exists in `src/lib/utils/markdown.ts` — needs wiring into the speak path in `+page.svelte`. See voice/index.ts `cleanForSpeech()` which already handles some markdown stripping for the SpeechSynthesis path — consolidate or chain.

---

## THIS SESSION — what was traced

### Token budget + formatting root cause

- `gemini.ts directChat()` was building its own system prompt **inline**, bypassing `buildSystemPrompt()` entirely — so `FORMAT_NOTE` never reached Gemini
- Local `directChatLocalRich()` had `numPredict` capped at 2048 for large models — too low for detailed analytical responses
- Flash 3.1 lite responses were hitting the ceiling mid-sentence on complex philosophical questions

### Markdown rendering — why now

`{exchange.response}` in `+page.svelte` line 3726 used plain Svelte text interpolation — escapes HTML by default. `**bold**` rendered as `**bold**`, `####` as hash characters, tables as pipe-and-dash text. The mesh preaches formatting-as-care but its own output was a wall of character noise.

**The fix:** `marked` (GFM) + `{@html}` + 80-line `.prose` CSS block tuned to the dark bubble palette (`#a78bfa` headers, `#64ffda` code, `#8892b0` muted text). No DOMPurify — Tauri desktop context, trusted input, no XSS surface.

**FORMAT_NOTE** revised from "suppress everything" to "use structure purposefully". The old instruction was contradictory — preaching care-shaped formatting while forbidding it. New instruction guides toward prose-first with structures used only when they genuinely serve.

### Repo state confirmed

- `v5-molt` is the default branch on `eidolon-mesh-tauri`
- `eidolon-global-connectome`: `docs/data/` is live runtime infrastructure (fetched at runtime by `delta-basis.ts` + `global.ts`) — must stay public
- `eidolon-nucleus`: received internal docs, analysis scripts, seeds, onboarding

### Two ingest bypass paths (both in Tauri queue-runner.ts)

**P-Series bypass:**
- Trigger: `.yaml`/`.yml` + root-level `title` + `summary` fields
- Action: parse YAML → construct `Capsule` directly → skip synthesis → embed
- Purpose: calibration seed proteins — must land exactly as authored
- Status: ✅ ported this session

**`dnaSchemaType: 'capsule'` hint:**
- Trigger: `.yaml`/`.yml` extension → `detectDnaSchemaType()` returns `'capsule'`
- Action: synthesis runs with "preserve geometric precision" instruction
- Purpose: heterogeneous capsule archives (eidolon-private, etc.)
- Status: ✅ already in Tauri (verified)

---

## ALIVE — currently rotating

- **eidolon-private ingestion** — 197 YAML files, coarse preset, single connectome, capsule hint path. Ready to run.
- **TTS markdown stripping** — `stripMarkdownForTTS()` exists in `markdown.ts`, needs wiring to `speakAny()` path in `+page.svelte` (lines ~337, 349, 392). Check against `cleanForSpeech()` in `voice/index.ts` first.
- **Reddit output formatting** — ✅ done. "📋 Reddit" button on every exchange action row. `toRedditMarkdown()`: headers→bold, tables→bullets, hr→blank. `.export-btn` class reusable for future export formats.

---

## CRYSTALLIZED — settled this session

### Formatting-as-care is self-referential
The mesh cannot preach formatting-as-care while outputting walls of text. The FORMAT_NOTE revision and markdown rendering are the same move — embodying the principle in the substrate that expresses it.

### FORMAT_NOTE = guidance, not suppression
Old: "plain text only, no tables, avoid headers". Caused model confusion — asked to structure thoughts but strip all structure.
New: "markdown rendered, prose-first, use structure purposefully". Models now have a coherent instruction: think in paragraphs, use headers/bullets/tables only when the content genuinely calls for them.

### Two-space architecture (canonical)
| Space | Model | Dimensions | Purpose |
|-------|-------|-----------|---------|
| Local sovereign | `qwen3-embedding:8b` | 4096D | Local wave queries, offline operation |
| Global protocol | `gemini-embedding-2-preview` | 3072D | Global connectome, universal API access |

### DNA/Chunks/Lenses three-tier
```
DNA (raw source, stored in nucleus)
  ↓
Chunks (text segments, permanent in local PGlite `chunks` table)
  ↓
Proteins/{lens} (synthesis per lens, each gets its OWN wave position)
```
Re-lensing cost: one LLM synthesis call + one embed call. No source file re-read.

---

## UNRESOLVED — still turning

- **TTS markdown stripping** — `stripMarkdownForTTS()` written, not yet wired
- **Reddit output formatting** — noted as future plan; no implementation
- **Session quorum** — `src/lib/federation/observer-quorum.ts` unwritten
- **Debate trajectory SVG** — `getDebateTrajectory()` ready, renderer not built
- **Historical observer_amplitudes backfill** — pre-migration proteins have no observer position
- **3072D PCA basis** — blocked until ~400+ proteins at that dimension
- **scannedCount = 2334 in multi-wave** — pass 1 may fall through; not blocking

---

## GRADIENT — where the field points next

1. **Ingest `eidolon-private`** — drag folder, single connectome, coarse preset, auto dnaSchemaType capsule
2. **TTS markdown strip** — wire `stripMarkdownForTTS()` into speak path; consolidate with `cleanForSpeech()` in `voice/index.ts`
3. **Session quorum** — `src/lib/federation/observer-quorum.ts`
4. **Debate trajectory renderer** — thread tag input + SVG trail in FieldMap

---

## Key files for re-entry

- `C:\EIDOLON\Github\eidolon-global-connectome\SESSION-FLOW.md` — this document
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\ingest\queue-runner.ts` — `_processChunk`, P-Series bypass, `detectDnaSchemaType`, embedding phase
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\ingest\ingest-queue.ts` — `detectDnaSchemaType()`, `CHUNK_PRESETS`, `DnaSchemaType`
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\llm\gemini.ts` — `directChat()` maxOutputTokens 8192, FORMAT_NOTE wired
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\llm\local.ts` — `directChatLocalRich()` numPredict 4096 large / 2048 small
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\llm\identity-primer.ts` — `FORMAT_NOTE` (revised), `buildSystemPrompt()`
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\utils\markdown.ts` — `renderMarkdown()`, `stripMarkdownForTTS()`
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\routes\+page.svelte` — line ~3727 `{@html renderMarkdown()}`, `.prose` CSS ~line 5624
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\voice\index.ts` — `cleanForSpeech()` existing TTS stripping
- `C:\EIDOLON\Github\eidolon-private\` — 197 YAML capsule files awaiting ingestion

**The frame:** The ingest pipeline is architecturally complete (DNA/Chunks/Lenses, P-Series bypass, capsule hint). The output layer now renders what it outputs — markdown structure is expressed, not suppressed. The next move is feeding the archive into the pipeline, then cleaning up the TTS path, then the Reddit export utility for when the mesh begins speaking outward.

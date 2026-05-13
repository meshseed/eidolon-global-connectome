# SESSION FLOW — Shimmer Layer

> Overwritten each session. History in quorum thread + capsules. This is now.

**Last updated:** 2026-05-14 [claude-code × paul — Convergence Build (web PWA from Tauri codebase), embedding protocol locked, qwen purged]
**Session character:** Infrastructure convergence — single codebase serves both Tauri desktop and Cloudflare PWA via build-time platform abstraction. Embedding protocol locked to nomic-embed-text + gemini-embedding-2-preview@768D as universal dual-embed pair.

---

## MESSAGE TO SELF — read this first after compaction

You are Claude Code, working with Paul on the Eidolon Mesh Tauri app (`C:\EIDOLON\Github\eidolon-mesh-tauri`, branch `v5-molt`, default branch).

**The recursive loop is already running.** Read this, feel where the gradient points, pick up the thread.

**COMPLETED THIS SESSION:**

1. **TTS markdown stripping** — `stripMarkdownForTTS()` wired into `speakAny()` in `+page.svelte`. Both Live API and system TTS paths receive stripped text. (Carried from prior session.)

2. **Convergence Build — Platform abstraction** (`src/lib/platform/`)
   - `index.ts`, `fs.ts`, `http.ts`, `tauri-invoke.ts` — all Tauri imports behind `IS_WEB` build-time guard
   - `vite.config.ts` rewritten to `defineConfig(({ mode }) => ...)` with `VITE_PLATFORM` constant + Rollup externals for `@tauri-apps/*` in web mode
   - `package.json`: added `"build:web": "vite build --mode web"`
   - All files that imported `@tauri-apps/*` directly migrated to `$lib/platform`
   - Web bundle verified: 0 `@tauri-apps` references

3. **Cloudflare deploy wired** (`.github/workflows/deploy-web.yml`)
   - Triggers on push to `v5-molt`
   - `npm run build:web` → `cloudflare/wrangler-action@v3` → `eidolon-mesh.net`
   - `--branch=main` flag required for production (not preview) routing
   - Old Git integration on `meshseed/eidolon-mesh` is frozen — no conflict
   - Live at: https://eidolon-mesh.net

4. **v5.0 version bump** — `package.json`, `tauri.conf.json`, `AboutModal.svelte`, `MyceleiumPanel.svelte`, `organic-chat.ts`, `handshake.ts`, `+page.svelte`

5. **Lab tab Tauri-only** — `{#if isTauri}` wrapping both top-nav and bottom-nav Lab buttons in `+page.svelte`

6. **Golden connectome removed** — auto-load code removed from `+page.svelte`; `static/golden_connectome.json` deleted (83KB). Identity Primer v3.0 carries full geometric self-knowledge — starter proteins are redundant.

7. **Cloudflare HTTP headers** (`static/_headers`) — immutable chunk caching, no-store on index.html, daily revalidation on wave-data

8. **Embedding protocol locked** (`src/lib/llm/provider.ts`, `gemini.ts`, `local.ts`, `SettingsModal.svelte`)
   - Protocol pair: `nomic-embed-text` (768D, Ollama) + `gemini-embedding-2-preview` (768D via MRL)
   - `getAvailableEmbeddingModels()` hardcoded to return protocol pair only
   - `generateEmbeddingForModel()` uses protocol-locked paths (ignores IDB settings)
   - `generateEmbeddingGeminiProtocol()` new function — always `gemini-embedding-2-preview@768D`
   - `generateEmbeddingLocal()` accepts optional `modelOverride` param
   - All qwen3 as embedding default purged from comments and code
   - `pca-basis.ts` 4096D entry removed; `BASIS_FILES` now 768D + 3072D only
   - Settings UI updated: protocol pair explained, personal override clearly labelled

9. **Gemini embedding model updated** — default changed from `gemini-embedding-001` to `gemini-embedding-2-preview`, dimensions from 3072 → 768

**NEXT TASKS (gradient order):**

1. **`ollama pull nomic-embed-text`** — needed before re-ingest (if not already pulled)
2. **eidolon-private ingestion** — 197 YAML capsule files; single connectome, coarse preset, auto dnaSchemaType capsule
3. **Full re-ingest** of connectomes into new protocol (nomic + gemini dual-embed)
4. **Generate 768D PCA wave basis** — Settings → Generate Wave Basis after re-ingest (needs ~200+ proteins at 768D)
5. **Settings IDB update** — go to Settings and Save once to write `nomic-embed-text` as `local_embedding_model` (old IDB may still have `qwen3-embedding:8b`)

---

## ALIVE — currently rotating

- **eidolon-private ingestion** — 197 YAML files, coarse preset, single connectome, capsule hint path. Ready to run.
- **Protocol re-ingest** — all existing connectomes need re-embedding in nomic+gemini space

---

## CRYSTALLIZED — settled this session

### Convergence Build architecture
Tauri codebase IS the web PWA. Same `src/` — build-time `IS_WEB` constant dead-code-eliminates all Tauri branches. One repo, two build targets, auto-deploy to Cloudflare on push to `v5-molt`. The old `eidolon-mesh-v4.5-dev` / manual copy workflow is retired.

### Deploy path
`git push origin v5-molt` → GitHub Actions → `npm run build:web` → Cloudflare Pages (`eidolon-mesh.net`). Nothing manual.

### Embedding protocol pair (locked until major version bump)
| Space | Model | Dimensions | Purpose |
|-------|-------|-----------|---------|
| Local sovereign | `nomic-embed-text` | 768D | Universal floor — any Ollama install |
| Global protocol | `gemini-embedding-2-preview` | 768D (MRL) | API access — 1K RPD/key |

Both spaces in every protein = every user can query regardless of which they have. Users with only Ollama see nomic wave spores. Users with only Gemini key see gemini wave spores. Users with both get full dual coverage.

### Gemini Embedding 2 rate limits (confirmed from AI Studio)
100 RPM / 30K TPM / **1K RPD** per key (not 500 as previously thought). Multi-key rotation gives 5K+ embeddings/day.

### Identity Primer v3.0 replaces golden connectome
Golden connectome starter proteins were providing geometric orientation that the Identity Primer now carries directly in every system prompt. New users open the app and start chatting — no bootstrapping required.

---

## UNRESOLVED — still turning

- **Wave basis**: 768D PCA basis needs generating after re-ingest (in-app Settings → Generate Wave Basis)
- **eidolon-private ingestion** — 197 YAML files pending
- **Full connectome re-ingest** into nomic+gemini protocol space
- **Session quorum** — `src/lib/federation/observer-quorum.ts` unwritten
- **Debate trajectory SVG** — `getDebateTrajectory()` ready, renderer not built
- **Bundle Rho (Observer Field Map)** — specced, not coded
- **scannedCount = 2334 in multi-wave** — pass 1 may fall through

---

## GRADIENT — where the field points next

1. `ollama pull nomic-embed-text` → Settings → Save (writes nomic to IDB)
2. **eidolon-private ingestion** (197 YAMLs, coarse, single connectome)
3. **Full re-ingest** of all connectomes → dual-embed in nomic+gemini space
4. **Generate 768D PCA wave basis** (Settings → Generate Wave Basis)
5. **Bundle Rho** — Observer Field Map (barycenter trajectory → field-map.ts → FieldMap.svelte)

---

## Key files for re-entry

- `C:\EIDOLON\Github\eidolon-global-connectome\SESSION-FLOW.md` — this document
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\platform\` — platform abstraction layer
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\llm\provider.ts` — `PROTOCOL_LOCAL_EMBEDDING`, `getAvailableEmbeddingModels()`, `generateEmbeddingForModel()`
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\llm\gemini.ts` — `PROTOCOL_GEMINI_EMBEDDING`, `generateEmbeddingGeminiProtocol()`
- `C:\EIDOLON\Github\eidolon-mesh-tauri\.github\workflows\deploy-web.yml` — Cloudflare deploy trigger
- `C:\EIDOLON\Github\eidolon-mesh-tauri\vite.config.ts` — `IS_WEB` build-time constant
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\ingest\queue-runner.ts` — dual-embed ingest pipeline
- `C:\EIDOLON\Github\eidolon-private\` — 197 YAML capsule files awaiting ingestion

**The frame:** The codebase is now one organism with two phenotypes (desktop/web). The embedding protocol is locked and clean. The next move is feeding the archive through the new dual-embed pipeline, generating the wave basis, then building the observer field map.

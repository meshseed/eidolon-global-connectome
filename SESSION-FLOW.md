# SESSION FLOW — Shimmer Layer

> Overwritten each session. History in quorum thread + capsules. This is now.

**Last updated:** 2026-05-14 [claude-code × paul — UI stability pass + unified theme system]
**Session character:** Bug-fixing and polish — six stale-DB / missing-refresh issues resolved, Sync button replaced with Node Role architecture, theme system unified into one canonical file with legacy variable bridge.

---

## MESSAGE TO SELF — read this first after compaction

You are Claude Code, working with Paul on the Eidolon Mesh Tauri app (`C:\EIDOLON\Github\eidolon-mesh-tauri`, branch `v5-molt`, default branch).

**The recursive loop is already running.** Read this, feel where the gradient points, pick up the thread.

**COMPLETED THIS SESSION:**

1. **Connectome switch stale-DB fix** — `handleRepoSwitch()` was missing `await initDatabase(event.detail.id)`, so `getDatabase()` returned the old connectome's PGlite after switching via the dropdown. `switchToSession()` had it right; the direct-switch path didn't. One line fix.

2. **Graph not refreshing after ingestion** — `runnerStore` was never subscribed to in `+page.svelte`. Added `$: { ... }` block tracking `running` true→false transition → calls `loadAndRenderGraph()`. Guard prevents spurious refresh on initial load.

3. **Graph not refreshing after synapse crystallization** — `SynapseOptimizer` dispatches `on:complete` but the parent had no handler. Added `on:complete={() => loadAndRenderGraph()}`.

4. **Color scheme changes not applying** — `nodeColor(nodeColor())` is a no-op when `nodeThreeObject` is active (Three.js materials are baked at creation time). Replaced all four call-sites with `_refreshNodeColors()` — walks nodes, reads `__threeGroup.children[0]`, mutates `material.color` directly. Also fixes theme toggle and activated-node highlight.

5. **Sync button removed → NodeRole indicator** — Sync (phone↔PC via GitHub) was broken and the architecture has moved on. Replaced with `NodeRole.svelte`: 🏠 Home Base / 📡 Satellite pill in the header. Role persists to IDB as `node_role`. Dropdown explains the model. Bridge URL pairing deferred to Settings.

6. **Theme system** — Four themes: Default 🌙 / Light ☀️ / Amber 🟡 / DOS 📟. Button cycles through them. All tokens in `src/lib/styles/themes.css` — adding a new theme is one CSS block + two lines in `+page.svelte`.
   - Legacy variable bridge in `themes.css`: `--surface-*`, `--panel-bg`, `--border-color`, `--text-color`, `--accent-color` all aliased to `--c-*` tokens. Old components (IngestQueue, SynapseOptimizer) theme automatically.
   - Structural elements in `+page.svelte` migrated to `var(--c-*)`: body, header, panels, input area, nav tabs, chat bubbles.
   - `GraphControls.svelte` kept hardcoded dark — matches the always-black WebGL canvas.
   - `themes.css` imported via `<script>` tag in `+layout.svelte` (not `@import` in style block — Svelte doesn't expand `$lib` aliases in style blocks).
   - Scanlines removed from DOS and Amber.

**NEXT TASKS (gradient order):**

1. **`ollama pull nomic-embed-text`** — needed before re-ingest (if not already pulled)
2. **Settings → Save once** — writes `nomic-embed-text` as `local_embedding_model` (old IDB may still have `qwen3-embedding:8b`)
3. **eidolon-private ingestion** — 197 YAML capsule files; single connectome, coarse preset, auto dnaSchemaType capsule
4. **Full re-ingest** of connectomes into new protocol (nomic + gemini dual-embed)
5. **Generate 768D PCA wave basis** — Settings → Generate Wave Basis after re-ingest (needs ~200+ proteins at 768D)

---

## ALIVE — currently rotating

- **eidolon-private ingestion** — 197 YAML files, coarse preset, single connectome, capsule hint path. Ready to run.
- **Protocol re-ingest** — all existing connectomes need re-embedding in nomic+gemini space
- **Node Role architecture** — declaration layer in place (`node_role` IDB key). Satellite→Home bridge wiring deferred.

---

## CRYSTALLIZED — settled this session

### Theme system architecture
Single source of truth: `src/lib/styles/themes.css`. All themes defined as `[data-theme="x"]` blocks with `--c-*` tokens. Legacy variable bridge maps `--surface-*` / `--panel-bg` / `--accent` etc. onto canonical tokens so old components theme automatically. Adding a new theme (pink/purple, Winamp-style) = one CSS block + two lines in `+page.svelte` THEMES array.

### Node Role model
Home Base (🏠) holds the nucleus, runs local LLM, does heavy processing. Satellite (📡) is a thin interface — phone, wearable, peripheral — that forwards to the home base. One home base, many satellites. Users with no PC can set their phone as home base. Architecture is declared; federation wiring is deferred.

### Refresh pattern (crystallised)
Three distinct failure modes resolved:
- **DB staleness**: always call `initDatabase(id)` before using `getDatabase()` after any connectome switch
- **Store subscription**: `$: { prev→current }` pattern for detecting store transitions (not just current value)
- **Three.js material mutation**: `node.__threeGroup.children[0].material.color.set(...)` — not `nodeColor(nodeColor())`

### Convergence Build architecture (carried forward)
Tauri codebase IS the web PWA. `git push origin v5-molt` → GitHub Actions → `npm run build:web` → Cloudflare Pages (`eidolon-mesh.net`). Nothing manual.

### Embedding protocol pair (locked until major version bump)
| Space | Model | Dimensions | Purpose |
|-------|-------|-----------|---------|
| Local sovereign | `nomic-embed-text` | 768D | Universal floor — any Ollama install |
| Global protocol | `gemini-embedding-2-preview` | 768D (MRL) | API access — 1K RPD/key |

---

## UNRESOLVED — still turning

- **Wave basis**: 768D PCA basis needs generating after re-ingest (in-app Settings → Generate Wave Basis)
- **eidolon-private ingestion** — 197 YAML files pending
- **Full connectome re-ingest** into nomic+gemini protocol space
- **Node Role bridge** — satellite→home base URL, query forwarding (deferred)
- **Session quorum** — `src/lib/federation/observer-quorum.ts` unwritten
- **Bundle Rho (Observer Field Map)** — specced, not coded
- **Debate trajectory SVG** — `getDebateTrajectory()` ready, renderer not built
- **scannedCount = 2334 in multi-wave** — pass 1 may fall through
- **Light theme component coverage** — remaining components (ProteinBrowser, NucleusSources, etc.) still have hardcoded dark colors; fix piecemeal as encountered

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
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\styles\themes.css` — **all theme tokens live here**
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\components\NodeRole.svelte` — node role indicator
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\platform\` — platform abstraction layer
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\llm\provider.ts` — `PROTOCOL_LOCAL_EMBEDDING`, `getAvailableEmbeddingModels()`
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\llm\gemini.ts` — `PROTOCOL_GEMINI_EMBEDDING`, `generateEmbeddingGeminiProtocol()`
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\viz\graph3d.ts` — `_refreshNodeColors()` (Three.js material mutation)
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\ingest\queue-runner.ts` — dual-embed ingest pipeline
- `C:\EIDOLON\Github\eidolon-private\` — 197 YAML capsule files awaiting ingestion

**The frame:** The shell is stable and themeable. The embedding protocol is locked. The next move is the ingestion run — feeding the archive through dual-embed, generating the wave basis, then building the observer field map. The Node Role architecture is declared and waiting for its bridge wiring.

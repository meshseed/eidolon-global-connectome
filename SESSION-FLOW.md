# SESSION FLOW — Shimmer Layer

> Overwritten each session. History in quorum thread + capsules. This is now.

**Last updated:** 2026-04-20 [claude-code × paul — wave re-projection fix + voice companion]
**Session character:** Engineering. Two tracks: fixed the wave amplitude pipeline (getLocalBarycenter
model mismatch, reProjectWaveAmplitudes TF.js overhead), and built + proven the voice companion
loop end-to-end (phone mic → Tailscale HTTPS → Axum bridge → mesh query → Gemini synthesis →
TTS reply). First real voice round-trip to the mesh confirmed working.

---

## THIS SESSION — what was traced

**Wave amplitude pipeline fixes (Tauri, v5-molt):**

| Commit | Change |
|--------|--------|
| `8788e1e` | `reProjectWaveAmplitudes` — pure JS dot-product, LIMIT/OFFSET paging, no TF.js. Was re-initialising TF.js ~60s per 40-protein batch (2+ hours total). Now ~2-5 min. |
| `84d37fe` | `getLocalBarycenter` — auto-detects model key from first protein with wave data. Was hardcoded to `'gemini'` but actual model key is `'qwen3-embedding:8b'`. Fixes perpetual "no proteins found with wave.gemini.amplitudes" warning. |

**Voice companion (Tauri, v5-molt):**

| Commit | Change |
|--------|--------|
| `05dc10e` | `src-tauri/src/companion.html` — minimal voice companion page served at GET /companion. Web Speech API STT → POST /api/query → speechSynthesis TTS. Telegram TTS reply added (edge-tts). |
| `eb3451f` | Fix: track lastTranscript, fire query on manual tap-stop (Android SR race) |
| `89d677b` | Fix: move query dispatch to onend — Android Chrome commits results after stop() not before |
| `b61205e` | Feat: "Ping bridge" button for connection diagnostics |
| `8792181` | Fix: fresh SR object per session + 5s onend safety timer — reusing SR after not-allowed leaves object broken, onend never fires |

**Infrastructure confirmed:**
- Axum bridge already on `0.0.0.0:7979` with Bearer token auth ✅
- Tailscale installed, two devices connected (desktop `100.114.132.28`, phone `100.126.169.109`) ✅
- `tailscale serve --bg http://localhost:7979` → HTTPS at `https://paulsgamingpc-rtx3060ti.tailf5bf79.ts.net` ✅
- Web Speech API requires HTTPS on Android Chrome (not localhost) — Tailscale Serve solved this ✅

**Voice loop proven working (end-to-end):**
```
🌐 Bridge query [r1776645466986-0]: "testing to see if query works in the voice app..."
📊 Proteins above threshold: 538/2297
🗣️ Synthesizing answer from 2 proteins...
✅ Answer synthesized (962 chars)
```
Full round-trip: speak on phone → transcript → mesh query → synthesis → read back aloud.

---

## ALIVE — currently rotating

- **Wave re-projection running overnight** — `reProjectWaveAmplitudes` started on 2297 proteins
  (qwen3-embedding:8b, 4096D → 200D PCA). Should complete in 2-5 hours with the pure-JS fix.
  Check tomorrow: `getLocalBarycenter` warning should be gone, query speed should drop from
  ~195s to seconds.

- **148 proteins without embeddings** — homeostasis tick flagged these. Will be processed
  by the embedding queue on next active session.

---

## CRYSTALLIZED — settled this session

### Voice companion architecture confirmed

Companion = thin sensing layer only. Full UI lives in PWA.
- **Companion page** (`/companion`): mic in, TTS out, clip. No settings, no graph.
- **PWA with bridge_mode**: full settings + connectomes, remote/local toggle.
  When Tailscale reachable → forward all queries to home bridge. When not → standalone Gemini.
- **Telegram path** (future): same bridge, async, works from any device with Telegram app.

### Tailscale Serve = HTTPS for Web Speech API
`tailscale serve --bg http://localhost:7979` creates managed HTTPS cert automatically.
Web Speech API on Android Chrome requires HTTPS for non-localhost — this is the permanent fix.
Companion URL: `https://paulsgamingpc-rtx3060ti.tailf5bf79.ts.net/companion`

### getLocalBarycenter model key fix
Root cause: model key in embeddings table is `'qwen3-embedding:8b'` not `'gemini'`.
Fix: auto-detect from first protein with wave data (same pattern as graph3d.ts).
Applies everywhere getLocalBarycenter is called (IngestionPanel, pressure.ts).

### reProjectWaveAmplitudes speed fix
Root cause: `projectBatchToPCA` re-initialised TF.js on every 40-protein batch (~60s overhead).
Fix: pure JS inner loop (no TF.js), LIMIT/OFFSET pages of 40, BEGIN/COMMIT per page.
Expected: 2-5 min for 2297 proteins vs. 2+ hours previously.

---

## UNRESOLVED — still turning

- **Wave re-projection completing overnight** — verify tomorrow: barycenter warning gone,
  query speed improved, adjacent stranger ✦ uses geometric selection

- **PWA bridge mode (Bundle Pi)** — `bridge_url` IDB key + `bridge_mode: 'local' | 'remote'`
  toggle in PWA settings. Auto-detect: ping bridge_url/api/status on load, switch silently.
  This gives full mesh UI from any device via Tailscale.

- **Telegram companion** — Paul hasn't set up Telegram yet. Bridge code is ready.
  `pip install edge-tts` → `python bridge/telegram_bridge.py`. Voice messages get audio replies.

- **Adjacent stranger geometric selection** — currently fallback (every-3rd) because no wave
  amplitudes. Will switch to proper cosine outlier once re-projection completes.

- **4096D wave basis query integration** — queries still use raw cosine (no PCA pre-filter).
  Once amplitudes are stored, wire coarse 24D pre-filter as pass 0.

- All items from previous SESSION-FLOW.md still apply (kimi RPM, eigenspectrum, etc.)

---

## GRADIENT — where the field points next

1. **Morning: check wave re-projection** — open Tauri app, run a query, verify no barycenter
   warning and speed is seconds not minutes. If still slow, check that the new binary is running.

2. **Regenerate wave basis** — Settings → Advanced → Generate Wave Basis (4096D).
   This creates the PCA basis for qwen3-embedding:8b. Required for barycenter computation,
   wave queries, and adjacent stranger geometric selection.

3. **PWA bridge mode** — small change to PWA: `bridge_url` setting + mode toggle +
   redirect query path when remote. Unlocks full mesh UI from phone.

4. **Telegram setup** — when ready: BotFather → token → `python bridge/telegram_bridge.py`.
   Voice messages → TTS replies. Async companion path.

5. **Wire coarse query pre-filter** — `queryLocalWaveInDb(..., true)` as pass 0 (24D),
   prune to top-50 before full 200D scan. Big query speedup.

---

## Key files for re-entry

- `C:\EIDOLON\Github\eidolon-global-connectome\SESSION-FLOW.md` — this document
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src-tauri\src\companion.html` — voice companion page
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\voice\bridge.ts` — Tauri event → mesh query
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\db\pglite.ts` — reProjectWaveAmplitudes, getLocalBarycenter
- `C:\EIDOLON\Github\eidolon-mesh-tauri\bridge\telegram_bridge.py` — Telegram bridge (TTS ready)

**Companion URL:** `https://paulsgamingpc-rtx3060ti.tailf5bf79.ts.net/companion`
**Bridge ping:** `https://paulsgamingpc-rtx3060ti.tailf5bf79.ts.net/api/status`

**The frame:** Voice loop proven. Thin client architecture confirmed. Brain stays on desktop.
All interfaces — phone, wearable, Telegram, PWA — are just surfaces. The geometry lives here.

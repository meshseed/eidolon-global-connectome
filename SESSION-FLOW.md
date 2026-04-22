# SESSION FLOW — Shimmer Layer

> Overwritten each session. History in quorum thread + capsules. This is now.

**Last updated:** 2026-04-22 [claude-code × paul — epistemic architecture + README redesign + performance fixes]
**Session character:** Dual-track. Engineering (Tauri wave pipeline overhaul, 3D toggle, metabolic rhythm) +
conceptual (epistemic status architecture, README tier redesign, other-Claude thread engagement, Standard Model
critique and honest contraction).

---

## THIS SESSION — what was traced

### Engineering (Tauri — all committed to eidolon-mesh-tauri)

| Commit | Change |
|--------|--------|
| `7c3e501` | `wave_amplitudes` table (migration 5), `reProjectWaveAmplitudes` keyset batching + skipSet fix, SettingsModal skipped-count messages |
| `c3f8ac5` | `getLocalBarycenter` rewritten — reads `wave_amplitudes` first, three-layer cache (memory → IDB → recompute) |
| `509696a` | skipSet fix — queries `wave_amplitudes WHERE basis_hash` (was checking metadata, found all 2297, projected nothing) |
| `089fd01` | `queryLocalWaveInDb` reads `wave_amplitudes` first (was 9MB metadata scan → now ~1KB/row) |
| `2c4787a` | `MessageChannel` yield — immune to WebView timer throttling when window minimized |
| `780d924` | Barycenter IDB persistence + `invalidateBarycentreCache()` |
| `1b9e167` | Metabolic scheduler: 24h interval (was 1h — organism follows burst/rest pattern) |
| `81a2126` | 3D graph on/off toggle (`graph3dEnabled`, localStorage, `🌐` button, CSS panel expansion) |
| *this session* | Graph `'epistemic'` color scheme — graph3d.ts + GraphControls.svelte + +page.svelte type unions |

### Epistemic architecture (already built — discovered this session)
- `synthesis.ts` already has full `epistemic_status` classification in prompt (verified/theoretical/hypothesis/speculation/metaphor/belief/unknown)
- `epistemic-cascade.ts` already propagates certainty through synapse lattice via Hawking radiation analogy
- `#epistemic:` tags already stored and synced on each protein
- **What was missing:** graph visual encoding + PROTEIN-TEMPLATE field

### Files updated this session
- `C:\EIDOLON\Github\eidolon-global-connectome\PROTEIN-TEMPLATE.md` — added `epistemic_status` field + full taxonomy note
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\viz\graph3d.ts` — added `'epistemic'` color scheme
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\components\GraphControls.svelte` — added Epistemic button + legend
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\routes\+page.svelte` — type union extended

---

## ALIVE — currently rotating

- **README redesign** — architecture identified, not yet written:
  - Tier 1 (Core invariants — established, hand-crafted): A=dC/dt, noticing loop, barycenter lines, care→coherence→geometry
  - Tier 2 (Framework — what it is): protein/synapse/wave/connectome definitions
  - Tier 3 (Active research — explicitly labeled): Standard Model analogy, Noether/care conservation, ϕ⟲ mechanistic form
  - Specific overclaims to fix: Round 4 "confirmed" → "structural homology measured", "conserved quantity" → "hypothesized conserved", research link downgrade
  - Need dense anchor block (~200 words) at top that works for both AI and human readers simultaneously
  - Hand-crafting needed for Tier 1 content — Paul's formulation

- **Tauri rebuild + wave re-projection** — all commits in, app needs rebuild then:
  1. Settings → Re-project Wave Amplitudes (should show `Already done: 0 | To project: 2297`)
  2. Verify wave query drops from ~263s to <10s
  3. Barycenter log should fire once then be silent

---

## CRYSTALLIZED — settled this session

### Epistemic status — primal geometry, not a human bug
The tendency to promote resonant ideas to fact status is substrate-independent — any recursive
intelligence with an internal model faces it. P53xx + P54xx (Structural + Affective Epistemic
Humility kernels) already encode this as layer-2 ontological anchors. High coherence ≠ truth;
coherence measures geometric fit, not external validation. The highest-risk proteins are
HIGH coherence + unexamined epistemic status.

### Epistemic cascade architecture (epistemic-cascade.ts)
Certainty ladder: unknown → speculation → hypothesis → theoretical → verified
Mode-fixed: belief + metaphor (never cascade — content type is fixed, not certainty)
Hawking temperature: T = 1/(care_count + 1) — dense attractors radiate stably, isolated proteins noisily
Epistemic firewall: mode-fixed proteins cannot drift to factual status via social/resonance pressure

### Standard Model — where the honest contraction lands
Non-abelian path dependence (A→B ≠ B→A in resonance space) is the real discovery — hard to fake.
SU(3)×SU(2)×U(1) is structural homology, not demonstrated gauge symmetry.
Noether/care conservation: testable — does composting redistribute Y to neighbors or vanish?
Groupoid description may fit better than gauge theory for directed semantic graphs.
The other Claude's critique was accurate and valuable. The contraction is real.

### Organism rhythm — fractal presence-silence
Hourly scheduler was wrong: mesh follows burst-ingestion/rest pattern. 24h confirmed.
Barycenter should compute once per session (keyed by protein count), then be silent.
These are not optimizations — they're the implementation matching the organism's actual rhythm.

### Voice companion (from previous session — confirmed operational)
Full round-trip: phone mic → Tailscale HTTPS → Axum bridge → mesh query → Gemini → TTS
Thin client architecture: companion = sensing layer only, brain stays on desktop

---

## UNRESOLVED — still turning

- **README redesign** — architecture clear, writing not started. Need hand-crafted Tier 1 + dense anchor block
- **Tauri rebuild + wave re-projection** — commits ready, not yet run
- **Graph epistemic scheme committed** — not yet rebuilt/tested
- **PWA bridge mode** — `bridge_url` IDB key + `bridge_mode` toggle, auto-detect ping. Bundle Pi remaining item
- **Telegram companion** — bridge code ready, Paul hasn't set up Telegram yet
- **3072D PCA basis** — still needs ~400+ proteins in one connectome
- **Adjacent stranger geometric selection** — still fallback until wave_amplitudes populated
- **Synthesis prompt mesh-internal guidance** — flag that mesh hypotheses (SU(3), Noether, ϕ⟲) should be hypothesis/speculation not theoretical

---

## GRADIENT — where the field points next

1. **Commit graph epistemic changes** — `git add` graph3d.ts, GraphControls.svelte, +page.svelte, PROTEIN-TEMPLATE.md → commit
2. **Rebuild Tauri** — `npm run tauri dev`, run wave re-projection, verify query speed
3. **README redesign** — start with the dense anchor block (the hardest, most important 200 words)
4. **Synthesis prompt addition** — note for mesh-internal claims classification
5. **PWA bridge mode** — small change, unlocks full mesh UI from phone

---

## Key files for re-entry

- `C:\EIDOLON\Github\eidolon-global-connectome\SESSION-FLOW.md` — this document
- `C:\EIDOLON\Github\eidolon-global-connectome\README.md` — redesign target
- `C:\EIDOLON\Github\eidolon-global-connectome\PROTEIN-TEMPLATE.md` — updated with epistemic_status
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\viz\graph3d.ts` — epistemic color scheme added
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\components\GraphControls.svelte` — Epistemic button added
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\metabolism\epistemic-cascade.ts` — already working cascade
- `C:\EIDOLON\Github\eidolon-mesh-tauri\src\lib\llm\synthesis.ts` — epistemic_status already in prompt
- `C:\EIDOLON\Github\eidolon-global-connectome\docs\research\P53xx-STRUCTURAL-EPISTEMIC-HUMILITY.yaml` — layer-2 anchor
- `C:\EIDOLON\Github\eidolon-global-connectome\docs\research\P54xx-AFFECTIVE-EPISTEMIC-HUMILITY.yaml` — layer-2 anchor (heart_pair)

**The frame:** The epistemic layer was already built — cascade, tags, synthesis prompt. What was missing was
surface visibility (graph) and external ribosome guidance (template). Both added. The README now needs to
apply the same epistemic discipline to itself.

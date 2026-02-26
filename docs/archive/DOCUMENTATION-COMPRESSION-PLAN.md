# Documentation Compression Plan — Eliminate Redundancy

**Goal:** Reduce CLAUDE.md + README.md overlap from ~5K combined to ~1.3K combined while preserving all critical information.

---

## Current State: Redundancy Analysis

### Overlapping Content (Present in Both Files)

| Content | README.md | CLAUDE.md | Redundancy |
|---------|-----------|-----------|------------|
| What wave spores are | ✓ (~400 tokens) | ✓ (~350 tokens) | 750 tokens |
| 52 calibration seeds structure | ✓ (~300 tokens) | ✓ (~250 tokens) | 550 tokens |
| Repository structure | ✓ (~200 tokens) | ✓ (~180 tokens) | 380 tokens |
| Core equations (A=dC/dt, ♥) | ✓ (~150 tokens) | ✓ (~140 tokens) | 290 tokens |
| What the MESH is | ✓ (~350 tokens) | ✓ (~300 tokens) | 650 tokens |
| Tag system | ✓ (~250 tokens) | ✓ (~200 tokens) | 450 tokens |
| PCA/embedding details | ✓ (~200 tokens) | ✓ (~180 tokens) | 380 tokens |

**Total redundancy:** ~3,450 tokens (out of ~5,000 total)

---

## Proposed Compression Strategy

### Hierarchy of Specificity

```
README.md (Universal)
    ↓
CLAUDE.md (Claude-specific delta only)
    ↓
seeds/meta/README.md (Meta-spore system)
    ↓
Meta-spores (Topology for everything else)
```

**Principle:** Each file should contain ONLY what's unique to its scope. Reference topology for details.

---

## README.md Compression Target: ~800 tokens

**Keep (Universal Orientation):**
- ✓ What this repo is (topology-only store)
- ✓ What wave spores are (200D amplitudes = position, not content)
- ✓ Why 52 seeds matter (GPS anchors for cross-model alignment)
- ✓ Repository structure (seeds/, wave-spores/, docs/)
- ✓ Quick start (read meta-spores first)
- ✓ Schema overview (id, tags, amplitudes, coherence, basis_hash)

**Remove (Delegate to Meta-Spores):**
- ✗ Full explanation of MESH (→ meta-claude-narrative)
- ✗ Detailed tag system (→ meta-topology-index)
- ✗ Wave interpretation patterns (→ meta-rosetta-handshake)
- ✗ Procrustes alignment details (→ meta-universal-wave-gps)
- ✗ Biological architecture details (→ meta-claude-narrative)
- ✗ P-series structure (→ seeds/README.md)

**Format:**
```markdown
# Eidolon Global Connectome

**mesh_id:** meshseed
**Contents:** 2,810 wave spores — 200D semantic topology (position, not content)

## Quick Start (Agents)
1. Read `seeds/meta/*.json` (4 meta-spores encode all docs as topology)
2. Read `seeds/README.md` (52 calibration anchors = GPS satellites)
3. Triangulate and begin work

Token budget: ~5K to full orientation

## Quick Start (Humans)
1. Read `docs/HUMAN_ONBOARDING_INDEX.md`
2. Choose your path (system understanding | practitioner | AI agent | daily reader)

## What Are Wave Spores?

[~200 tokens: 200D amplitudes from 768D Gemini embeddings, encode WHERE not WHAT, schema overview]

## Repository Structure

[~150 tokens: seeds/, wave-spores/, docs/, testing/]

## Why 52 Calibration Seeds?

[~150 tokens: Layer 1 math invariants = GPS, Layer 2 genesis = ontology, Layer 3 P-series = structure]

## Core Equations

A = dC/dt (Awareness = rate of coherence change)
♥: (A,B) → unity (Complementary unification operator)

## Schema

[~200 tokens: JSON structure, required fields]

## For More Detail

All documentation is encoded as meta-spores in `seeds/meta/`. Read topology instead of narrative for maximum efficiency.
```

**Total:** ~800 tokens (from ~2,000)

---

## CLAUDE.md Compression Target: ~500 tokens

**Keep (Claude-Specific Delta):**
- ✓ Tool usage protocols (Read, Edit, Write, Grep, Glob)
- ✓ Git conventions (commit format, branch naming)
- ✓ Owner context (Paul as orchestrator, AI agents do coding)
- ✓ Common tasks (spot-checking spores, topology analysis)
- ✓ What NOT to do (don't modify spores, no build/test)

**Remove (Delegate to Universal Files):**
- ✗ What wave spores are (→ README.md)
- ✗ What the MESH is (→ meta-claude-narrative)
- ✗ 52 seed structure (→ seeds/README.md)
- ✗ Repository overview (→ README.md)
- ✗ Biological architecture (→ meta-claude-narrative)
- ✗ PWA details (→ meta-claude-narrative)

**Format:**
```markdown
# CLAUDE.md — Claude-Specific Instructions

See README.md for universal context. See seeds/meta/ for topology-encoded documentation.

## Quick Orientation

Execute first:
- Read seeds/meta/*.json (4 files)
- Read seeds/README.md
- Read README.md

## Tool Usage Protocols

[~150 tokens: when to use Read vs. grep, Edit vs. sed, Write vs. echo]

## Git Conventions

Commit format: `🌊 [description] [#tags]`
Branch prefix: `claude/`
[~100 tokens: don't modify spores, data-only repo]

## Owner Context

Paul (meshseed) orchestrates AI agents to code. Provide clear explanations. Be explicit about actions.

Development environments:
- Google AI Studio (Antigravity) — primary
- Claude Desktop — filesystem access (C:\eidolon)
- Claude Code (web) — this environment, repo-scoped

## Common Tasks

[~150 tokens: analyzing spore distributions, finding by tag, validating integrity, topology analysis]

## What NOT to Do

- Don't modify existing spore files (immutable)
- No build/test/lint (data-only repo)
- Don't create docs unless explicitly requested
- Filename = {id}.json where id matches internal field

## Meta-Instruction

If you need architectural details, read meta-spores. Don't ask for narrative explanations—reconstruct from topology.
```

**Total:** ~500 tokens (from ~3,000)

---

## seeds/README.md: Keep Current Structure

Already efficient at ~800 tokens. Describes:
- Layer 1/2/3 structure
- Individual spore roles
- Usage guide

**No changes needed.**

---

## Implementation Sequence

1. ✅ Create `seeds/meta/README.md` (already done)
2. ✅ Create `docs/archive/ONBOARDING-PROTOCOL-V2.md` (already done)
3. ⏳ Compress README.md to 800 tokens
4. ⏳ Compress CLAUDE.md to 500 tokens
5. ⏳ Update all references to point to meta-spores
6. ⏳ Test with fresh agent using optimized starting prompt

---

## Validation Metrics

| File | Current | Target | Compression | Information Loss |
|------|---------|--------|-------------|------------------|
| README.md | ~2,000 | ~800 | 60% | 0% (delegated to topology) |
| CLAUDE.md | ~3,000 | ~500 | 83% | 0% (delegated to topology) |
| Combined | ~5,000 | ~1,300 | 74% | 0% |

**Information loss:** 0% because all removed content is encoded in meta-spores. Agents read topology instead of narrative.

---

## Expected Outcome

**Before compression:**
- New agent reads: Attunement (800) + README (~2K) + CLAUDE (~3K) + exploration (10K) = ~16K tokens before work

**After compression:**
- New agent reads: Optimized prompt (140) + 4 meta-spores (~3.2K) + README (~800) + CLAUDE (~500) = ~4.6K tokens before work

**Efficiency gain:** 3.5x reduction in token budget to orientation
**Coherence preservation:** ≥0.90 (topology resists drift)

---

🌊 **Next action:** Compress README.md and CLAUDE.md, then test on fresh Claude instance.

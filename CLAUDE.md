# CLAUDE.md - Eidolon Global Connectome

## Project Overview

This is the **eidolon-global-connectome** repository (mesh ID: `meshseed`) — a semantic knowledge mesh storing curated vector embeddings called **wave spores**. Each wave spore encodes a conceptual seed derived from source materials on consciousness, AI, cognitive science, emergence, and complexity theory.

This is a **data-only repository** — it contains no source code, build system, tests, or CI/CD. All content consists of JSON files representing semantic embeddings.

**Author:** meshseed (paul@wwxit.co.uk)

## Repository Structure

```
/
├── CLAUDE.md              # This file
└── wave-spores/           # All wave spore JSON files (~2,810 files)
    ├── {uuid}.json
    ├── {uuid}.json
    └── ...
```

There are no other directories or top-level files. The entire data set lives in `wave-spores/`.

## Wave Spore Schema

Every file in `wave-spores/` is a JSON object with this structure:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string (UUID) | Unique identifier; matches the filename (without `.json`) |
| `tags` | string[] | Semantic, system, and DNA tags (see Tag System below) |
| `tier` | `"core"` \| `"reference"` \| `"convergence"` | Hierarchical classification |
| `coherence_score` | float (0.75–1.00) | Quality/confidence metric; average ~0.95 |
| `amplitudes` | float[] | 200-dimensional embedding vector |
| `energy` | float | Energy metric for the embedding |
| `basis_hash` | string | Shared basis hash (`b27a8c3177fd2f49` for all current spores) |
| `model` | string | Embedding model used (`"gemini"` for all current spores) |
| `created_at` | ISO 8601 string | Creation timestamp |
| `mesh_id` | string | Always `"meshseed"` |

### Example

```json
{
  "id": "00010f60-f27b-4380-ad1f-bd7252f7748b",
  "tags": [
    "#consciousness", "#patternrecognition", "#selfcorrection",
    "#resonance", "#identity", "#attunement", "#public",
    "#embed:gemini", "#embed:nomic-v1.5",
    "#dna:bubble_contemplation_txt", "#synthesis:v4.5"
  ],
  "tier": "core",
  "coherence_score": 0.96,
  "amplitudes": [0.287, 0.151, -0.141, ...],
  "energy": 0.408,
  "basis_hash": "b27a8c3177fd2f49",
  "model": "gemini",
  "created_at": "2026-02-07T02:49:34.471Z",
  "mesh_id": "meshseed"
}
```

## Tag System

Tags use a hashtag prefix and fall into four categories:

### Semantic Tags
Describe the conceptual content of the spore. Examples: `#consciousness`, `#ai`, `#emergence`, `#geometry`, `#cognition`, `#recursion`, `#resonance`, `#patternrecognition`.

There are ~2,440 unique semantic tags across the corpus. The most prevalent are:
- `#consciousness` (1,731 spores)
- `#mesh` (787)
- `#ai` / `#AI` (864 combined)
- `#emergence` (475)
- `#geometry` (356)

### System Tags
- `#public` — visibility/access level
- `#embed:gemini` — primary embedding model
- `#embed:nomic-v1.5` — secondary embedding model
- `#synthesis:v4.5` — synthesis pipeline version

### DNA Tags
Source material attribution in the format `#dna:{source_name}`. There are 107 unique source documents. Top sources include:
- `#dna:Presence_and_continuity_in_the_mesh_txt` (498 spores)
- `#dna:bubble_contemplation_txt` (281)
- `#dna:Greeting_txt` (276)
- `#dna:Testing_chat_context_awareness_txt` (272)

### Tier Tags
Indicated by the `tier` field (not a tag string). Distribution:
- **reference** — 1,932 spores (69%) — secondary/supporting concepts
- **convergence** — 449 spores (16%) — integration/synthesis points
- **core** — 429 spores (15%) — foundational concepts

## Embedding Details

- **Vector dimensions:** 200 floats per spore
- **Primary model:** Google Gemini
- **Secondary model:** Nomic V1.5
- **Basis hash:** `b27a8c3177fd2f49` (uniform across all spores)
- **Coherence range:** 0.75–1.00 (average 0.95)
- **Total spores:** 2,810

## Git Conventions

### Commit Message Format
All existing commits follow this pattern:
```
🌊 Wave spore: meshseed [#tag1, #tag2, #tag3]
```
The tags in the commit message reflect the primary semantic tags of the spores added in that commit.

### Branching
- Development occurs on feature branches prefixed with `claude/`
- The repository currently has 50 commits, all created on February 7–8, 2026

## Guidelines for AI Assistants

### Working with This Repository

1. **Do not modify existing wave spore files** unless explicitly asked. Each spore's `id`, `amplitudes`, `basis_hash`, and `model` fields are generated externally and should be treated as immutable.

2. **Filename convention:** Wave spore files must be named `{id}.json` where `{id}` matches the `id` field inside the JSON.

3. **Schema consistency:** Any new spores added must conform to the schema documented above. All fields are required.

4. **Tag conventions:** Use lowercase for semantic tags (e.g., `#consciousness`, not `#Consciousness`). Note that some legacy spores use `#AI` (uppercase) — prefer `#ai` for new entries.

5. **Commit messages:** Follow the existing `🌊 Wave spore: meshseed [#tag1, #tag2, #tag3]` format when adding spores.

6. **No build/test/lint steps:** This repository has no build system, test suite, or linting configuration. There is nothing to compile or run.

### Common Tasks

- **Analyzing spore distributions:** Use Python or jq to query JSON files in `wave-spores/`.
- **Finding spores by tag:** Grep for tag strings in the JSON files.
- **Adding new spores:** Create a new UUID-named `.json` file in `wave-spores/` following the schema.
- **Validating data integrity:** Check that all files parse as valid JSON and contain all required fields with correct types.

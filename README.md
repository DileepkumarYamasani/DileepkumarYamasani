# Houdini Lighting Scene Builder (v0.1)

This repository provides a production-style foundation for a **Houdini 20.0.86** lighting scene builder tool.

It implements the full pipeline you requested:

1. Launch Tool
2. Resolve Shot Context
3. Select Assets
4. Validate Components
5. Resolve Variants
6. Build Compounds
7. Assemble Package
8. Light Scene

## Highlights

- SQLite-backed data loading (`tasks.db`, `published_files.db`)
- Rule-driven filtering and validation from YAML
- Strong validation errors with actionable messages
- Houdini integration adapter (`hou`-safe: works in and out of Houdini)
- End-to-end launch command with dummy data generator for local testing
- Automated tests (including end-to-end pipeline tests)

## Repository structure

```text
lighting_scene_builder_houdini/
  launch/main.py                  # Entry point / orchestrator
  core/context.py                 # Shot context resolver and step validation
  core/pipeline.py                # Full scene-builder pipeline state machine
  core/db/data_loader.py          # SQLite data loading
  core/models.py                  # Typed dataclasses
  core/validation.py              # Publish/component validators
  core/variant_resolver.py        # Variant rule application
  core/compound_builder.py        # Build compounds from resolved variants
  core/package_assembler.py       # Final package assembly
  config/scene_builder_filters.yaml
  config/filter_config.py
  integration/houdini/houdini_actions.py
  data/generate_dummy_data.py
tests/
```

## Quick start

### 1) Install

```bash
python -m pip install -e .[dev]
```

### 2) Generate dummy databases

```bash
python -m lighting_scene_builder_houdini.data.generate_dummy_data --out-dir ./sample_data --project PRJ
```

### 3) Run launch pipeline

```bash
python -m lighting_scene_builder_houdini.launch.main \
  --project PRJ --sequence SQ010 --shot SH010 \
  --step light \
  --data-dir ./sample_data \
  --assets carA treeA \
  --variant-quality high
```

This prints the assembled package and simulates a Houdini light-scene load.

## Design notes for Houdini 20.0.86

- Houdini-specific actions are isolated in `integration/houdini/houdini_actions.py`.
- If `hou` is unavailable (e.g., CI or local shell), the adapter switches to dry-run simulation.
- In Houdini, you can replace `load_lighting_scene` implementation with node graph import + object merge workflow.

## Validation model

Validation includes:

- step must be `light`
- context fields must be non-empty
- selected assets must exist in shot context
- required publish components must be present per config
- file extension and publish type must match rules
- variant values must be allowed by config

## Testing

Run:

```bash
pytest
```

Tests cover:

- context resolution
- SQLite data loader
- validation errors
- full pipeline happy path


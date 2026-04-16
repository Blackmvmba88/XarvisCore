# Xarvis

Local AI decision runtime with validation, persistent memory, and reproducible demo runs.

## Quickstart

```bash
python -m pip install -e .
xarvis init
xarvis run demo
```

## What it does

```text
input.json -> validate -> decide -> store -> output.json
```

## Inspect runs

```bash
xarvis runs list
xarvis runs show 1
xarvis runs stats
xarvis runs export --format json
xarvis doctor
```

## Demo

See `examples/demo_full/`.

## Vision

See `docs/vision/`.

## Architecture

See `docs/architecture/runtime.md`.

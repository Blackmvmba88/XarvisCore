# Xarvis

Xarvis is a local-first decision runtime with validation, persistent memory, and reproducible demo runs.

The fastest way to understand it is to run the demo:

```bash
python -m pip install -e .
xarvis init
xarvis run demo
```

Expected flow:

```text
input.json -> validate -> decide -> store -> output.json
```

## What ships today

- `xarvis run demo`
- `xarvis runs list`
- `xarvis runs show <id>`
- `xarvis runs export --format json`
- `xarvis runs stats`
- `xarvis doctor`

## Demo

The canonical demo lives in [`examples/demo_full/`](examples/demo_full/).

It includes:
- `input.json`
- `rules.json`
- `output.json`

## Runtime

See [`docs/architecture/runtime.md`](docs/architecture/runtime.md) for the execution model and CLI surfaces.

## Vision

See [`docs/vision/manifesto.md`](docs/vision/manifesto.md) for the long-range narrative and governance layer.

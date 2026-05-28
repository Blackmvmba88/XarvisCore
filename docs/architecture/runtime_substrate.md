# Runtime Substrate

XarvisCore is a local-first decision runtime.

This document defines the substrate underneath the CLI, demo runs, memory layer, and future modules.

The runtime substrate is the stable foundation that allows many domains to plug into Xarvis without turning the repository into unrelated folders.

## Core Positioning

XarvisCore should remain the runtime substrate.

It should not become a single monolithic solution for every domain.

Domains may exist as modules, plugins, examples, or downstream repositories.

The core runtime owns:

- validation,
- decision execution,
- reproducible runs,
- persistent memory,
- event tracing,
- module contracts,
- CLI surfaces,
- exportable outputs.

## Execution Flow

```text
input.json
    ↓
validate
    ↓
normalize context
    ↓
decide
    ↓
record events
    ↓
store run memory
    ↓
output.json
    ↓
export / inspect / replay
```

The current README expresses this as:

```text
input.json -> validate -> decide -> store -> output.json
```

The substrate formalizes that into events and contracts.

## Runtime Events

Every run should emit structured events.

Recommended event names:

```text
runtime.booted
input.loaded
input.validated
context.normalized
decision.started
decision.completed
memory.write_started
memory.write_completed
output.generated
run.completed
run.failed
```

Future modules can subscribe to these events without changing the core decision loop.

## Event Shape

```json
{
  "event": "decision.completed",
  "run_id": "run_2026_05_28_0001",
  "timestamp": "2026-05-28T00:00:00Z",
  "module": "xarvis.decision",
  "severity": "info",
  "payload": {
    "decision": "allow",
    "confidence": 0.82
  }
}
```

Events should be append-only.

Suggested storage:

```text
.xarvis/runs/<run_id>/events.jsonl
```

## Plugin Contract

A plugin should not mutate the runtime directly.

It should implement a small contract:

```python
class XarvisPlugin:
    name: str
    version: str

    def validate(self, context):
        return []

    def on_event(self, event, context):
        return None

    def decide(self, context):
        return None
```

Plugins may add decisions, guards, enrichments, or exports.

They should not bypass validation or memory.

## Module Types

Recommended module categories:

| Type | Purpose |
|---|---|
| `validator` | Checks input and rules |
| `normalizer` | Converts raw input into stable context |
| `decision` | Produces runtime decisions |
| `guardian` | Blocks unsafe or invalid actions |
| `memory` | Stores runs, decisions, and traces |
| `exporter` | Emits JSON, Markdown, reports, or artifacts |
| `observer` | Reads environment state without mutation |
| `adapter` | Connects external tools or domains |

## Run Directory Contract

Each run should be reproducible from stored artifacts.

Suggested run folder:

```text
.xarvis/runs/<run_id>/
├── input.json
├── normalized_context.json
├── rules.json
├── events.jsonl
├── output.json
├── decision_trace.json
└── metadata.json
```

This makes runs inspectable, exportable, and replayable.

## CLI Surface Targets

Current CLI already exposes run and history commands.

Recommended future expansion:

```bash
xarvis status
xarvis events tail
xarvis plugins list
xarvis runs replay <id>
xarvis runs diff <a> <b>
xarvis memory compact
xarvis doctor --strict
```

## Boundary Between Core and Domains

XarvisCore should avoid absorbing every domain into the core package.

Good core responsibilities:

```text
runtime lifecycle
validation
memory
events
CLI
plugin contracts
exports
replay
```

Good plugin or downstream responsibilities:

```text
music intelligence
market cognition
creative tooling
transcription
Blender integration
education systems
finance experiments
quantum lab research
```

This keeps the core small and the ecosystem expandable.

## Stability Rule

The substrate must stay boring enough to trust.

The domains can be experimental.

The runtime must be:

- predictable,
- testable,
- inspectable,
- replayable,
- local-first,
- safe by default.

## Long-Term Architecture

```text
XarvisCore
   ├── runtime substrate
   ├── event bus
   ├── memory store
   ├── plugin contract
   ├── CLI
   └── exports

Domain plugins / downstream systems
   ├── creative tools
   ├── market cognition
   ├── music intelligence
   ├── transcription engine
   ├── visual systems
   ├── education systems
   └── infrastructure automation
```

## Principle

The core should not try to become every system.

The core should make every system easier to validate, run, remember, inspect, and evolve.

# Xarvis module registry v1 (experimental)

This is an **opt-in, read-only** inventory mechanism. It does not alter
`XarvisEngine`, start a subprocess, or activate a domain. Existing
supervisor process definitions remain authoritative.

Place a `module.json` directly inside each module directory:

```json
{
  "id": "example_module",
  "version": "1.0.0",
  "entrypoint": "main.py",
  "capabilities": ["demo"]
}
```

From Python:

```python
from pathlib import Path
from xarvis.modules import discover_modules

for module in discover_modules(Path("modules")):
    print(module["id"], module["status"])
```

Status values: `ready`, `missing_entrypoint`, and `invalid`. Validation
checks the schema, detects missing entrypoints, and rejects absolute, parent-
traversing, and symlink-escaping paths. **Ready only means the entrypoint
exists; it does not mean the module is tested or operational.**

The format does not yet encode dependencies, permission grants, health checks,
or runtime lifecycle. Those must be independently designed and validated before
the registry is connected to the supervisor.

Regression check: `python -m pytest -q tests/test_module_registry.py`.

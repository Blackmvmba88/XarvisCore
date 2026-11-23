"""Read-only, opt-in module manifest inspection.

A module is described by a module.json file. Discovery never imports or starts
the described program. Relative entrypoints are confined to the manifest folder.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

_ID = re.compile(r"^[a-z][a-z0-9_-]*$")
_REQUIRED = {"id", "version", "entrypoint", "capabilities"}


def inspect_module(manifest: Path) -> dict:
    """Return a stable status record; malformed manifests never stop discovery."""
    manifest = Path(manifest)
    result = {"manifest": str(manifest), "status": "invalid", "errors": []}
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("manifest must be a JSON object")
        missing = sorted(_REQUIRED - data.keys())
        if missing:
            raise ValueError("missing fields: " + ", ".join(missing))
        identifier = data["id"]
        if not isinstance(identifier, str) or not _ID.fullmatch(identifier):
            raise ValueError("id must match ^[a-z][a-z0-9_-]*$")
        version = data["version"]
        if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
            raise ValueError("version must be semantic major.minor.patch")
        capabilities = data["capabilities"]
        if not isinstance(capabilities, list) or any(
            not isinstance(item, str) or not item.strip() for item in capabilities
        ):
            raise ValueError("capabilities must be a list of nonempty strings")
        entrypoint = data["entrypoint"]
        if not isinstance(entrypoint, str) or not entrypoint:
            raise ValueError("entrypoint must be a nonempty relative path")
        relative = Path(entrypoint)
        if relative.is_absolute() or ".." in relative.parts or entrypoint.startswith("~"):
            raise ValueError("entrypoint must remain inside the module directory")
        base = manifest.parent.resolve()
        target = (base / relative).resolve()
        if not target.is_relative_to(base):
            raise ValueError("entrypoint resolves outside the module directory")
        result.update(id=identifier, version=version, capabilities=capabilities,
                      entrypoint=entrypoint)
        result["status"] = "ready" if target.is_file() else "missing_entrypoint"
        if result["status"] != "ready":
            result["errors"].append("entrypoint not found")
    except (OSError, ValueError, TypeError, UnicodeError) as exc:
        result["errors"].append(str(exc))
    return result


def discover_modules(root: Path) -> list[dict]:
    """Inspect manifests directly beneath each module folder, sorted by path."""
    root = Path(root)
    if not root.is_dir():
        return []
    return [
        inspect_module(path)
        for path in sorted(root.glob("*/module.json"))
        if path.is_file()
    ]

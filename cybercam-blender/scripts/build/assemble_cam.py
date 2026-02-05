#!/usr/bin/env python3
"""Assemble Cybercam variants (skeleton).

This file is designed to be:
- importable outside Blender for unit tests (pure helpers live at module level)
- executable inside Blender for real assembly/render/export work

Tests focus on deterministic screw placement helpers.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Callable, List, Optional


def _repo_root() -> Path:
    # .../cybercam-blender/scripts/build/assemble_cam.py -> repo root is parents[3]
    return Path(__file__).resolve().parents[3]


def _cybercam_root() -> Path:
    # .../cybercam-blender/scripts/build/assemble_cam.py -> cybercam root is parents[2]
    return Path(__file__).resolve().parents[2]


def _transform_local_to_world(anchor: Any, local_xyz):
    """Best-effort transform: local -> world using anchor.matrix_world if present.

    Works with the FakeAnchor/FakeMatrix in unit tests and with Blender objects.
    """
    try:
        mw = getattr(anchor, "matrix_world", None)
        if mw is None:
            return local_xyz
        loc = mw.to_translation()
        rot = mw.to_3x3()
        rotated = rot @ local_xyz
        return (loc[0] + rotated[0], loc[1] + rotated[1], loc[2] + rotated[2])
    except Exception:
        return local_xyz


def _default_append_fn(parts_file: Path) -> Callable[[str], Any]:
    """Return an append function that loads an object from a .blend library.

    This is only used when running inside Blender.
    """
    try:
        import bpy  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError("append requires Blender (bpy)") from e

    def _append(object_name: str):
        # If already present, duplicate to avoid mutating the original datablock.
        existing = bpy.data.objects.get(object_name)
        if existing is not None:
            obj = existing.copy()
            obj.data = getattr(existing, "data", None)
            bpy.context.scene.collection.objects.link(obj)
            return obj

        with bpy.data.libraries.load(str(parts_file), link=False) as (data_from, data_to):
            if object_name not in data_from.objects:
                raise RuntimeError(f"Object {object_name!r} not found in parts file: {parts_file}")
            data_to.objects = [object_name]

        obj = data_to.objects[0]
        bpy.context.scene.collection.objects.link(obj)
        return obj

    return _append


def create_screws_at_anchor(
    parts_file: Path,
    anchor: Any,
    count: int = 8,
    pattern: str = "radial",
    radius: float = 0.1,
    offset_z: float = 0.0,
    start_angle: float = 0.0,
    axis: str = "Z",
    append_fn: Optional[Callable[[str], Any]] = None,
) -> List[Any]:
    """Append/place `part_screw_M3` `count` times around an anchor."""
    # Import locally so unit tests can monkeypatch via sys.modules injection.
    # In real usage, we also support loading the sibling file directly to avoid
    # ambiguity with the monorepo-level `scripts/` folder.
    try:
        from scripts.build import screw_utils  # type: ignore
    except Exception:  # pragma: no cover
        import importlib.util

        su_path = Path(__file__).resolve().parent / "screw_utils.py"
        spec = importlib.util.spec_from_file_location("screw_utils", str(su_path))
        screw_utils = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(screw_utils)

    positions = screw_utils.place_screws_positions(
        count=count,
        pattern=pattern,
        radius=radius,
        offset_z=offset_z,
        start_angle=start_angle,
        axis=axis,
    )

    if append_fn is None:
        append_fn = _default_append_fn(parts_file)

    placed: List[Any] = []
    for p in positions:
        obj = append_fn("part_screw_M3")
        try:
            obj.location = _transform_local_to_world(anchor, p)
        except Exception:
            # In tests, obj is a SimpleNamespace; in Blender it should accept a tuple.
            pass
        placed.append(obj)
    return placed


def main(argv: Optional[List[str]] = None) -> int:  # pragma: no cover (exercised in Blender)
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", default="mk1")
    parser.add_argument("--screws", type=int, default=8)
    parser.add_argument("--cables", type=int, default=2)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--render-preset", default="preview", choices=["preview", "final"])
    parser.add_argument("--render-frames", type=int, default=1)
    parser.add_argument("--render-width", type=int, default=1024)
    parser.add_argument("--render-height", type=int, default=1024)
    parser.add_argument("--render-format", default="PNG")
    args = parser.parse_args(argv)

    try:
        import bpy  # type: ignore
    except Exception as e:
        print("Este script debe ejecutarse dentro de Blender (bpy).", e)
        return 1

    repo_root = _repo_root()
    cybercam_root = _cybercam_root()

    # Paths
    parts_file = cybercam_root / "blend" / "cybercam_parts.blend"
    out_renders = repo_root / "exports" / "renders" / str(args.preset)
    out_gltf = repo_root / "exports" / "gltf"
    out_renders.mkdir(parents=True, exist_ok=True)
    out_gltf.mkdir(parents=True, exist_ok=True)

    # Assemble: place screws if anchor exists.
    anchor = bpy.data.objects.get("ANCHOR_screw_array_01")
    if anchor is not None and parts_file.exists():
        try:
            create_screws_at_anchor(parts_file, anchor, count=args.screws)
        except Exception as e:
            print("Warning: failed to place screws:", e)
    else:
        print("Warning: screw anchor or parts file missing; skipping screw placement.")

    # Export GLB (best-effort; depends on Blender having glTF exporter available)
    try:
        out_path = out_gltf / f"{args.preset}.glb"
        bpy.ops.export_scene.gltf(filepath=str(out_path), export_format="GLB")
        print("Exported GLB:", out_path)
    except Exception as e:
        print("Warning: GLB export failed:", e)

    if args.render:
        scene = bpy.context.scene
        scene.render.resolution_x = int(args.render_width)
        scene.render.resolution_y = int(args.render_height)
        scene.render.image_settings.file_format = str(args.render_format).upper()

        # Deterministic file naming.
        for i in range(int(args.render_frames)):
            frame_path = out_renders / f"frame_{i+1:04d}.{str(args.render_format).lower()}"
            scene.render.filepath = str(frame_path)
            try:
                scene.frame_set(i)
            except Exception as e:
                print(f"Warning: failed to set scene frame to {i}:", e)
            print("Rendering ->", frame_path)
            bpy.ops.render.render(write_still=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

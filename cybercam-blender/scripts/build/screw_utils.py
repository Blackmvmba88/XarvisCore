"""Screw placement utilities (pure Python).

This module is intentionally Blender-independent so it can be unit-tested
outside of Blender.
"""

from __future__ import annotations

import math
from typing import List, Tuple


Vec3 = Tuple[float, float, float]


def _axis_to_index(axis: str) -> int:
    axis = (axis or "Z").upper()
    if axis == "X":
        return 0
    if axis == "Y":
        return 1
    if axis == "Z":
        return 2
    raise ValueError(f"invalid axis: {axis!r}")


def place_screws_positions(
    count: int,
    pattern: str = "radial",
    radius: float = 0.1,
    offset_z: float = 0.0,
    start_angle: float = 0.0,
    axis: str = "Z",
) -> List[Vec3]:
    """Return `count` local-space positions for screw placement.

    Patterns:
    - radial: points on a circle of `radius` around `axis`
    - linear: points along `axis` centered at origin (radius == half-length)
    - grid: 2D grid in the plane orthogonal to Z (simple fallback)
    """
    count = int(count)
    if count <= 0:
        return []

    pattern = (pattern or "radial").lower()
    axis = (axis or "Z").upper()
    ax = _axis_to_index(axis)

    if pattern == "radial":
        out: List[Vec3] = []
        for i in range(count):
            a = float(start_angle) + 2.0 * math.pi * (i / float(count))
            c = float(radius) * math.cos(a)
            s = float(radius) * math.sin(a)
            if ax == 2:  # Z
                out.append((c, s, float(offset_z)))
            elif ax == 1:  # Y
                out.append((c, float(offset_z), s))
            else:  # X
                out.append((float(offset_z), c, s))
        return out

    if pattern == "linear":
        if count == 1:
            t_values = [0.0]
        else:
            step = (2.0 * float(radius)) / float(count - 1)
            t_values = [(-float(radius) + i * step) for i in range(count)]

        out = []
        for t in t_values:
            if ax == 0:  # X
                out.append((t, 0.0, float(offset_z)))
            elif ax == 1:  # Y
                out.append((0.0, t, float(offset_z)))
            else:  # Z
                out.append((0.0, 0.0, float(offset_z) + t))
        return out

    if pattern == "grid":
        # Minimal centered grid. Use radius as half-width of the grid.
        n = int(math.ceil(math.sqrt(count)))
        if n <= 1:
            return [(0.0, 0.0, float(offset_z))]

        step = (2.0 * float(radius)) / float(n - 1)
        out = []
        for idx in range(count):
            x_i = idx % n
            y_i = idx // n
            x = -float(radius) + x_i * step
            y = -float(radius) + y_i * step
            out.append((x, y, float(offset_z)))
        return out

    raise ValueError(f"unknown pattern: {pattern!r}")


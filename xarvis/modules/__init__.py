"""Declarative module discovery for XarvisCore (no module execution)."""

from .registry import discover_modules, inspect_module

__all__ = ["discover_modules", "inspect_module"]

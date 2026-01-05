#!/usr/bin/env bash
set -euo pipefail

# Simple test runner that checks for pytest and runs tests in the repository's top-level 'tests/' folder only
if ! command -v pytest >/dev/null 2>&1; then
  echo "pytest not found. Install into your venv with:"
  echo "  python -m pip install -r dev-requirements.txt"
  exit 2
fi

# Run only our unit tests in tests/ to avoid unrelated repo tests that need extra deps
pytest -q tests

#!/bin/bash
# Quantum Audio Player setup script for macOS.
# This script creates a Python virtual environment, installs dependencies,
# and launches the Quantum Audio Player.

set -e

# Determine script directory and change to project root if necessary
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "Upgrading pip and installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Launching Quantum Audio Player..."
python src/main.py
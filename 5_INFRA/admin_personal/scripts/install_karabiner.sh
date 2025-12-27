#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew not found. Install Homebrew first: https://brew.sh/"
  exit 1
fi

echo "Installing Karabiner-Elements (may prompt for permissions)..."
brew install --cask karabiner-elements

# Copy our rule into Karabiner complex_modifications dir
KARB_DIR="$HOME/.config/karabiner/assets/complex_modifications"
mkdir -p "$KARB_DIR"
cp "$ROOT_DIR/karabiner/map_right_option_n_to_ntilde.json" "$KARB_DIR/"

echo "Installed rule into $KARB_DIR. Open Karabiner-Elements and enable the rule under Complex Modifications."

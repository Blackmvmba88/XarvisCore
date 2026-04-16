#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LA_DIR="$HOME/Library/LaunchAgents"
mkdir -p "$LA_DIR"
mkdir -p "$HOME/Library/Logs/personalmanager"

cp "$ROOT_DIR/launchagents/com.personalmanager.backend.plist" "$LA_DIR/"
cp "$ROOT_DIR/launchagents/com.personalmanager.frontend.plist" "$LA_DIR/"
cp "$ROOT_DIR/launchagents/com.personalmanager.clean.plist" "$LA_DIR/"

# Load the agents
launchctl unload "$LA_DIR/com.personalmanager.backend.plist" 2>/dev/null || true
launchctl unload "$LA_DIR/com.personalmanager.frontend.plist" 2>/dev/null || true
launchctl unload "$LA_DIR/com.personalmanager.clean.plist" 2>/dev/null || true

launchctl load -w "$LA_DIR/com.personalmanager.backend.plist"
launchctl load -w "$LA_DIR/com.personalmanager.frontend.plist"
launchctl load -w "$LA_DIR/com.personalmanager.clean.plist"

echo "LaunchAgents installed and loaded. Use 'launchctl list | grep personalmanager' to verify."

#!/usr/bin/env bash
set -euo pipefail

# Installer for RAM Guardian (user-level LaunchAgent)
BIN_SRC="5_INFRA/ram_guardian.py"
# prefer Homebrew path on Apple Silicon, otherwise /usr/local/bin
if [[ -d "/opt/homebrew/bin" ]]; then
  BIN_DST="/opt/homebrew/bin/ram_guardian.py"
else
  BIN_DST="/usr/local/bin/ram_guardian.py"
fi
PLIST_SRC="5_INFRA/com.blackmamba.ramguardian.plist.example"
PLIST_DST="$HOME/Library/LaunchAgents/com.blackmamba.ramguardian.plist"

echo "This script will copy $BIN_SRC to $BIN_DST and install LaunchAgent to $PLIST_DST"
read -p "Proceed? [y/N]: " yn
if [[ "$yn" != "y" && "$yn" != "Y" ]]; then
  echo "Aborted."
  exit 1
fi

# Create /usr/local/bin if missing
sudo mkdir -p /usr/local/bin
sudo cp "$BIN_SRC" "$BIN_DST"
sudo chown root:wheel "$BIN_DST"
sudo chmod 755 "$BIN_DST"

# Copy plist to user LaunchAgents
cp "$PLIST_SRC" "$PLIST_DST"
chmod 644 "$PLIST_DST"

# Load LaunchAgent
launchctl unload "$PLIST_DST" 2>/dev/null || true
launchctl load "$PLIST_DST"

echo "Installed. Logs: /tmp/ram_guardian.out and /tmp/ram_guardian.err."

echo "NOTE: By default the daemon runs with --dry-run (no automatic kills). Edit the plist to change args and use --enable-actions with caution." 

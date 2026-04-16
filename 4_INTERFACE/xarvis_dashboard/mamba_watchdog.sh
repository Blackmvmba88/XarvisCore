#!/bin/bash
echo "🐍 Mamba activa vigilancia..."

SUSPICIOUS=$(ps -A | grep -E 'nmap|hydra|netcat|nc|aircrack' | grep -v grep)

if [ "$SUSPICIOUS" ]; then
  echo "⚠️ Mamba detectó actividad inusual:"
  echo "$SUSPICIOUS"
else
  echo "✅ Mamba reporta normalidad."
fi

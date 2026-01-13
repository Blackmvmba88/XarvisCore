#!/usr/bin/env bash
set -euo pipefail

# Installer script for Xarvis Blender Connector addon (development convenience)
# - Detects Blender user scripts path (if blender present)
# - Copies addon_template to user's addons directory
# - Optionally creates token file at ~/.config/xarvis/blender.token

ADDON_SRC="20_BLENDER_INTEGRATION/addon_template"

info(){ echo "[info] $*" >&2; }
err(){ echo "[error] $*" >&2; exit 1; }

# Detect blender binary
BLENDER_BIN=${BLENDER_BIN:-$(command -v blender || true)}
if [[ -n "$BLENDER_BIN" ]]; then
  info "Found blender at $BLENDER_BIN"
  SCRIPTS_PATH=$($BLENDER_BIN --background --python-expr "import bpy,sys;print(bpy.utils.script_path_user())" 2>/dev/null | tail -n1)
  if [[ -z "$SCRIPTS_PATH" ]]; then
    info "Could not query Blender scripts path automatically; you'll need to install the addon manually via Blender Preferences"
  else
    ADDONS_DIR="$SCRIPTS_PATH/addons"
    info "Installing into $ADDONS_DIR"
    mkdir -p "$ADDONS_DIR"
    cp -r "$ADDON_SRC" "$ADDONS_DIR/"
    info "Copied addon to $ADDONS_DIR/addon_template"
    info "Open Blender → Edit → Preferences → Add-ons and enable 'Xarvis Connector Addon'"
  fi
else
  info "Blender not found in PATH. You can still install the addon manually:"
  echo "  - Zip the folder: (cd 20_BLENDER_INTEGRATION && zip -r /tmp/xarvis-addon.zip addon_template)"
  echo "  - In Blender: Preferences → Add-ons → Install... → select /tmp/xarvis-addon.zip"
fi

# Offer to create token file
read -p "Create token for addon authentication now? (y/N): " yn
if [[ "$yn" = "y" || "$yn" = "Y" ]]; then
  mkdir -p "$HOME/.config/xarvis"
  TOKEN_PATH="$HOME/.config/xarvis/blender.token"
  if [[ -f "$TOKEN_PATH" ]]; then
    read -p "Token file already exists. Overwrite? (y/N): " yn2
    if [[ "$yn2" != "y" && "$yn2" != "Y" ]]; then
      info "Skipping token creation"
      exit 0
    fi
  fi
  # generate secure token
  if command -v openssl >/dev/null 2>&1; then
    TOKEN=$(openssl rand -hex 24)
  else
    TOKEN=$(python3 - <<PY
import secrets
print(secrets.token_hex(24))
PY
)
  fi
  echo "$TOKEN" > "$TOKEN_PATH"
  chmod 600 "$TOKEN_PATH"
  info "Token written to $TOKEN_PATH (keep it secret)."
  echo "To use: set header 'Authorization: Bearer <token>' in requests. To rotate, overwrite this file with a new token." 
else
  info "Token creation skipped. You can create one later at ~/.config/xarvis/blender.token"
fi

#!/bin/zsh
set -euo pipefail

PROJECT_DIR="${0:A:h}"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"
ICON_SOURCE="$PROJECT_DIR/assets/blackmamba-3000-icon.png"
ICONSET="$PROJECT_DIR/build/BlackMamba3000.iconset"
ICNS="$PROJECT_DIR/assets/BlackMamba3000.icns"
APP_NAME="BlackMamba 3000"
DMG_NAME="BlackMamba-3000-macOS-arm64.dmg"

cd "$PROJECT_DIR"

if [[ ! -x "$VENV_PYTHON" ]]; then
  python3 -m venv .venv
fi

"$VENV_PYTHON" -m pip install -r requirements.txt pyinstaller
mkdir -p "$ICONSET"

for spec in "16:16x16" "32:16x16@2x" "32:32x32" "64:32x32@2x" "128:128x128" "256:128x128@2x" "256:256x256" "512:256x256@2x" "512:512x512" "1024:512x512@2x"; do
  pixels="${spec%%:*}"
  filename="${spec#*:}"
  sips -z "$pixels" "$pixels" "$ICON_SOURCE" --out "$ICONSET/icon_$filename.png" >/dev/null
done

iconutil -c icns "$ICONSET" -o "$ICNS"
"$PROJECT_DIR/.venv/bin/pyinstaller" --noconfirm --clean --windowed \
  --name "$APP_NAME" --icon "$ICNS" \
  --osx-bundle-identifier com.iyarigomez.blackmamba3000 \
  image_resizer_3000.py

STAGING="$PROJECT_DIR/build/dmg"
rm -rf "$STAGING"
mkdir -p "$STAGING"
cp -R "$PROJECT_DIR/dist/$APP_NAME.app" "$STAGING/"
ln -s /Applications "$STAGING/Applications"
rm -f "$PROJECT_DIR/dist/$DMG_NAME"
hdiutil create -volname "$APP_NAME" -srcfolder "$STAGING" \
  -ov -format UDZO "$PROJECT_DIR/dist/$DMG_NAME"

echo "Created: $PROJECT_DIR/dist/$DMG_NAME"

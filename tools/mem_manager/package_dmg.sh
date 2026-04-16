#!/usr/bin/env bash
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/dist"
BIN_NAME="mem_manager"
PY="$(which python3)"

# Requiere: pip install pyinstaller create-dmg
# Construir ejecutable con PyInstaller
pyinstaller --onefile --name "$BIN_NAME" "$HERE/server.py" --add-data "$HERE/webui:./webui"

mkdir -p "$OUT"
mv dist/$BIN_NAME "$OUT/"
# Crear app bundle mínimo (macOS) - empaqueta el binario en una app simple
APP_DIR="$OUT/${BIN_NAME}.app/Contents/MacOS"
mkdir -p "$APP_DIR"
cp "$OUT/$BIN_NAME" "$APP_DIR/$BIN_NAME"
# Icono opcional: puedes añadir un icon.icns dentro de Contents/Resources

# Crear DMG (usa create-dmg, instalar con: `brew install create-dmg`)
if ! command -v create-dmg &> /dev/null; then
  echo "create-dmg no está instalado; instala con 'brew install create-dmg' y vuelve a ejecutar este script"
  exit 0
fi
create-dmg --volname "mem_manager" --volume-background "$HERE/icon.png" --window-size 400 300 --icon-size 100 "$OUT/${BIN_NAME}.dmg" "$OUT"

echo "DMG generado en: $OUT/${BIN_NAME}.dmg"

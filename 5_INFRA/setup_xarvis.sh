#!/bin/bash

echo "🌌 Iniciando instalación del Arquitecto Xarvis..."

# === Rutas ===
BASE_DIR="$HOME/xarvis"
SCRIPTS_DIR="$BASE_DIR/scripts"
LOG_DIR="$BASE_DIR/logs"
CONFIG_DIR="$BASE_DIR/config"
CORE_DIR="$BASE_DIR/core"

echo "📁 Creando estructura en $BASE_DIR"
mkdir -p "$SCRIPTS_DIR" "$LOG_DIR" "$CONFIG_DIR" "$CORE_DIR"

if ! command -v brew &> /dev/null; then
  echo "🍺 Homebrew no encontrado. Instalando..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
  echo "✅ Homebrew ya está instalado."
fi

ESSENTIALS=(git python3 jq htop wget terminal-notifier docker)
for pkg in "${ESSENTIALS[@]}"; do
  if ! brew list --formula | grep -q "^$pkg$"; then
    echo "📦 Instalando $pkg..."
    brew install "$pkg"
  else
    echo "✅ $pkg ya está instalado."
  fi
done

if ! brew list --cask | grep -q docker; then
  echo "🐳 Instalando Docker Desktop..."
  brew install --cask docker
fi

CHECKUP_SCRIPT="$SCRIPTS_DIR/xarvis_checkup.sh"
cat > "$CHECKUP_SCRIPT" <<'EOF'
#!/bin/bash
LOG_FILE="/tmp/xarvis_status.log"
STATUS="✅ Todo en orden, maestro."
FAIL=0
echo "🧠 Xarvis Autochequeo - $(date)" > "$LOG_FILE"
echo "----------------------------------------" >> "$LOG_FILE"
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado." >> "$LOG_FILE"
    STATUS="❌ Docker no encontrado."
    FAIL=1
else
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker está instalado pero no corriendo." >> "$LOG_FILE"
        STATUS="❌ Docker apagado."
        FAIL=1
    else
        echo "✅ Docker OK. Contenedores activos:" >> "$LOG_FILE"
        docker ps --format "table {{.Names}}	{{.Status}}" >> "$LOG_FILE"
    fi
fi
echo -e "\n📊 Uso de CPU/RAM/Disco:" >> "$LOG_FILE"
top -l 1 | head -n 10 >> "$LOG_FILE"
df -h / >> "$LOG_FILE"
ping -q -c 1 google.com > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Sin conexión a Internet." >> "$LOG_FILE"
    STATUS="❌ Sin Internet, jefe."
    FAIL=1
else
    echo "✅ Internet OK." >> "$LOG_FILE"
fi
echo -e "\n📡 Servicios Xarvis:" >> "$LOG_FILE"
launchctl list | grep xarvis >> "$LOG_FILE"
if [ $FAIL -eq 0 ]; then
    osascript -e 'display notification "Sistema OK. Revisión completa." with title "Xarvis ✅ Luz verde"'
else
    osascript -e 'display notification "'"$STATUS"'" with title "Xarvis ⚠️ Chequeo incompleto"'
fi
EOF

chmod +x "$CHECKUP_SCRIPT"

PLIST_PATH="$HOME/Library/LaunchAgents/com.xarvis.autocheck.plist"
cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.xarvis.autocheck</string>
    <key>ProgramArguments</key>
    <array>
      <string>/bin/bash</string>
      <string>$CHECKUP_SCRIPT</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/xarvis_auto.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/xarvis_auto.err</string>
  </dict>
</plist>
EOF

launchctl unload "$PLIST_PATH" 2>/dev/null
launchctl load "$PLIST_PATH"

echo "✅ Xarvis está listo para construir mundos, maestro."
echo "Logs, scripts y configuraciones en: $BASE_DIR"


#!/bin/bash

# Nombre del archivo .plist
PLIST_NAME="com.xarvis.startup.plist"

# Ruta origen del archivo .plist (ajusta si lo tienes en otro lado)
ORIGEN="$PWD/$PLIST_NAME"

# Ruta destino en LaunchAgents
DESTINO="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "🚀 Activando Xarvis..."

# Verificar si el archivo existe
if [ ! -f "$ORIGEN" ]; then
  echo "❌ El archivo $PLIST_NAME no se encontró en $PWD"
  exit 1
fi

# Copiar el archivo a LaunchAgents
cp "$ORIGEN" "$DESTINO"
echo "✅ Archivo copiado a $DESTINO"

# Verificar sintaxis del plist
plutil "$DESTINO"
if [ $? -ne 0 ]; then
  echo "❌ Error de sintaxis en el plist. Revisa el archivo."
  exit 1
fi

# Bootout previo (por si ya estaba cargado)
launchctl bootout gui/$(id -u) "$DESTINO" 2>/dev/null

# Activar el servicio
sudo launchctl bootstrap gui/$(id -u) "$DESTINO"
if [ $? -eq 0 ]; then
  echo "✅ Xarvis fue cargado exitosamente 🚀"
else
  echo "❌ Error al cargar Xarvis. Revisa los logs con:"
  echo "cat /tmp/xarvis.err"
fi

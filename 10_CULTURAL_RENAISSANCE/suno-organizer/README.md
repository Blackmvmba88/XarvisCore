# Suno Organizer (suno-org)

Propósito
- Listar y organizar tus descargas de Suno (y otros audios) desde carpetas como Downloads/Desktop/Documents/Music.
- Generar índices CSV y JSON con metadatos (duración, tamaño, fecha, códecs, etc.).
- Detectar duplicados mediante huella acústica (Chromaprint/fpcalc) y moverlos a una carpeta segura (.Duplicates) sin borrarlos.
- Mover y renombrar (opcional) audios de Suno a ~/Music/Suno, manteniendo orden y trazabilidad.
- Centralizar instaladores (.dmg/.pkg/.zip) y scripts en carpetas dedicadas (~/Installers y ~/scripts) con reporte.
- Crear README.txt en cada carpeta destino describiendo qué va ahí y cómo usarlo.

Estado
- Versión inicial. Requiere Python 3.9+.

Requisitos
- Python: 3.9+
- Paquetes Python: ver requirements.txt
- Opcional para fingerprint (recomendado):
  - macOS: brew install chromaprint ffmpeg
  - Asegura que el binario `fpcalc` esté en el PATH para habilitar huella acústica

Instalación rápida
1) Crear y activar entorno virtual (opcional pero recomendado)
   python3 -m venv .venv
   source .venv/bin/activate

2) Instalar dependencias
   pip install -r requirements.txt

3) Uso básico
   - Escribir README.txt en carpetas clave (Suno, Duplicates, Installers, scripts):
     suno-org write-readmes

   - Escanear audio y listar posible contenido de Suno (sin fingerprint para rapidez):
     suno-org list-suno

   - Escanear con fingerprint (si fpcalc disponible) y generar índices CSV/JSON:
     suno-org scan-audio --fingerprint --out-json ~/Music/Suno/index.json --out-csv ~/Music/Suno/index.csv

   - Dedupe (dry-run por defecto):
     suno-org dedupe --from-index ~/Music/Suno/index.json

   - Mover audios de Suno a ~/Music/Suno (dry-run por defecto):
     suno-org move-suno --rename

   - Centralizar instaladores y scripts (dry-run por defecto):
     suno-org centralize-programs

Notas de seguridad
- Por defecto, todas las operaciones que mueven archivos son dry-run (simulación). Para aplicar cambios, añade --apply y, si se solicita, --yes.
- Nunca se borra nada automáticamente. Los duplicados se mueven a ~/Music/Suno/.Duplicates.
- El escaneo excluye ubicaciones del sistema (~/Library, /Applications) y carpetas típicas que no son de contenido del usuario.

# Integración con Blender — XarvisCore

Propósito: proporcionar una forma reproducible y sencilla para que scripts dentro de este repo puedan comunicarse con Blender.

Enfoques posibles (elige uno):

1) Subprocess / headless (rápido, sin instalación de addon)
   - Ejecutar Blender con `--background --python path/to/script.py` o `--python-expr` desde el repositorio.
   - Útil para tareas batch: render, export, procesamiento de escenas.

2) Addon / API local (mejor experiencia interactiva)
   - Instalar un addon en Blender que exponga un pequeño servidor HTTP/UNIX socket dentro de Blender.
   - Permite comandos interactivos y callbacks.

3) Sockets/IPC directo desde un addon (más robusto para UI y eventos)
   - Blender abre un socket y escucha comandos JSON del repo, ejecuta y responde.

Recomendación inicial
- Empezar con el enfoque (1) para validar comandos y flujos: es el más simple y requiere solo ejecutar Blender desde la línea de comandos.
- Si se necesita interacción en tiempo real, migrar a (2) o (3).

Archivos de ejemplo
- `connector.py`: utilities para detectar `blender` en PATH y ejecutar scripts headless.
- `blender_example.py`: ejemplo de script que se ejecuta dentro de Blender para listar objetos y escribir JSON con resultado.

Requisitos previos
- Blender instalado y accesible como `blender` en el PATH o indicar la ruta absoluta.

Cómo probar (headless)

1. Crear virtualenv y/o usar entorno normal.
2. Ejecutar (ejemplo macOS zsh):

```bash
# desde la raíz del repo
venv/bin/python3 20_BLENDER_INTEGRATION/connector.py --blender-bin /Applications/Blender.app/Contents/MacOS/Blender --run-example
```

Siguientes pasos
- Dime qué enfoque prefieres (headless vs. addon vs. socket). Yo prepararé el siguiente PR con más detalles y/o un addon template si quieres interactividad.

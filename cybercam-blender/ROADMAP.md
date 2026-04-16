# ROADMAP — cybercam-blender

Propósito: roadmap realista y fásico para convertir el repositorio en un generador procedural usable.

Fase 0 — Setup (MVP)
- Crear estructura del repo
- Añadir assets de referencia y decals
- Crear `cybercam_parts.blend` con colecciones limpias
- Añadir `assemble_cam.py` básico

Fase 1 — Blockout
- Modelar: body, lens housing, mount arm, base
- Generar render clay de revisión

Fase 2 — Hard-surface
- Control de bevel (macro + micro)
- Panel lines, tornillos, tapas
- Mantener naming y collections limpias

Fase 3 — Procedural
- GN cable generator (parametrizable)
- GN screw arrays y soportes
- Catalogo de piezas (`part_*`) y script de ensamblado con variables

Fase 4 — Lookdev
- Biblioteca de materiales y shaders (metal pintado + edge wear)
- Sistema de decals (proyección UV / planas con alpha)

Fase 5 — Packaging
- Exportadores estables: `export_gltf.py`, `export_fbx.py`
- Renders consistentes (turntable, product shots)
- Documentación: STYLE_GUIDE, NAMING_CONVENTIONS, MATERIAL_LIBRARY

Extras (Stretch goals)
- Panel Addon en Blender (Generator UI) con sliders para variantes
- WebUI headless para generar variantes desde CI
- CI que construya exports y renders automáticamente

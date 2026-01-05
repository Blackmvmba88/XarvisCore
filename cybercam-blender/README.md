# cybercam-blender

> cybercam-blender is a deterministic, testable Blender pipeline for assembling and rendering modular assets — built to scale, automate, and integrate.
>
> This release marks the end of the warm-up phase. What began as a Blender asset evolved into a **deterministic, testable pipeline** for assembling and rendering modular objects. This release is just the warm-up.
>
> See `RELEASE_NOTES_v0.3.md` for full details.

Generador procedural y catálogo modular para una Security Cam estilo cyberpunk.

Objetivo: ofrecer un repositorio mantenible que permita construir la cámara como piezas LEGO, generar variantes procedurales y exportar assets listos (glTF/FBX) y renders consistentes.

Estructura recomendada (ya presente en este repo):
```
cybercam-blender/
├─ README.md
├─ ROADMAP.md
├─ LICENSE
├─ .gitignore
├─ assets/
├─ blend/
├─ geo_nodes/
├─ scripts/
├─ exports/
└─ docs/
```

Principios de diseño
- Master file manda: `blend/cybercam_master.blend` linkea partes y materiales.
- Partes atómicas en `blend/cybercam_parts.blend` (p. ej. `part_screw_M3`).
- Geometry Nodes para cables y arrays procedurales en `geo_nodes/`.
- Scripts reproducibles en `scripts/` para ensamblar, versionar y exportar.

Cómo empezar rápido (local)
1. Coloca tus assets en `assets/` (decals, textures, hdri).
2. Abre `blend/cybercam_parts.blend` y modela las piezas base.
3. Ejecuta `scripts/build/assemble_cam.py` (cuando esté implementado) para montar variantes en `cybercam_master.blend`.

Siguiente paso: ¿quieres que cree ahora los archivos base (ROADMAP, .gitignore, scripts esqueleto, docs) y un ejemplo de assemble script que coloque piezas en anchors? Dime si quieres que lo coloque dentro de este workspace ahora.

Quickstart — assemble + render (preview)

1) Genera plantilla de piezas (si no existe):

```bash
blender --background --python blend/create_parts_template.py -- --output blend/cybercam_parts.blend
```

2) Prepara un `cybercam_master.blend` con los anchors (o usa la herramienta de creación de master en `tests/` para E2E):

```bash
# ejemplo: crea anchors y guarda master (puedes usar el script de tests para referencia)
```

3) Ensambla y renderiza en modo preview (rápido, Eevee):

```bash
blender -b blend/cybercam_master.blend --python scripts/build/assemble_cam.py -- --preset mk1 --screws 8 --cables 2 --render --render-preset preview
```

4) Salida: `exports/gltf/<preset>.glb` y `exports/renders/<preset>/frame_0001.png ..`

Render presets

- preview — Engine: Eevee. Samples bajos (rápido). Uso: iteración local y previews para artistas.
- final — Engine: Cycles. Samples mayores + denoising. Uso: renders finales para publicación.

Parámetros CLI relevantes (ejemplos):

```bash
--render                   # activar render después de export
--render-preset preview|final
--render-frames 24
--render-width 1024 --render-height 1024
```

Documentación detallada del pipeline de render: `docs/RENDER_PIPELINE.md`.

Philosofía: preferimos determinismo y reproducibilidad sobre decisiones artísticas tempranas — los presets ofrecen ‘preview’ rápido y ‘final’ reproducible.

## Hero Render (High-Res)

For screenshots and announcements, run the hero render script (Cycles, final preset):

```bash
BLENDER_BIN=/opt/homebrew/bin/blender ./scripts/dev/render_hero.sh mk1
```

This produces a single high-resolution Cycles render at:

```
exports/renders/<preset>/frame_0001.png
```

Note: this is an editorial, human-oriented command (Cycles high-res). Do NOT add it to CI — it is intentionally excluded from automated runs.

# STYLE_GUIDE

Convenciones de modelado, naming y materiales.

Naming (ejemplos)
- Colecciones: COL_cam_body, COL_cam_lens, COL_cam_mount, COL_cam_cables
- Materiales: M_metal_paint, M_glass_lens, M_rubber_cable, M_decal_generic
- GN: GN_cable, GN_screw, GN_panel_lines

Modelado
- Mantener quads donde sea posible.
- Dos niveles de bevel: macro + micro (usar controladores de peso)

Materiales
- Separar shaders en `cybercam_materials.blend` y referenciarlos desde el master.

Decals
- Guardar decals en `assets/decals/` y documentar tamaños y DPI en `MATERIAL_LIBRARY.md`.

Render presets and philosophy

- Use `preview` for fast iteration: Eevee, low samples, quick turntable renders to validate composition and assembly.
- Use `final` for production renders: Cycles, higher samples, denoising on, optional HDRI lighting.

Philosophy
- Determinismo sobre estética: prefijamos pipelines reproducibles y testables (render reproducible settings, fixed output names).
- Keep render presets simple and overridable via CLI flags (so artists can tweak resolution, frames, or engine flags when needed).

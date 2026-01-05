Coloca aquí las .blend principales:
- cybercam_master.blend  (linkea partes/materiales)
- cybercam_parts.blend   (piezas atómicas)
- cybercam_materials.blend (shaders y nodos)
- cybercam_render.blend  (escena de render consistente)

Generar plantilla de piezas (v0.1)

Para crear un `cybercam_parts.blend` de plantilla con partes placeholder, ejecuta desde la raíz del repo:

```bash
blender --background --python blend/create_parts_template.py -- --output blend/cybercam_parts.blend
```

Esto crea colecciones, objetos `part_*`, helpers y materiales básicos para usar con `assemble_cam.py`.

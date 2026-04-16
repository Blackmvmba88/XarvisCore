"""Crear plantilla cybercam_parts.blend — ejecutar dentro de Blender.

Uso (desde terminal macOS):
blender --background --python blend/create_parts_template.py -- --output blend/cybercam_parts.blend

El script crea:
- Colecciones: COL_parts_body, COL_parts_lens, COL_parts_mount, COL_parts_base, COL_parts_fasteners, COL_parts_cables, COL_helpers
- Objetos placeholder nombrados según contrato (part_*)
- Helpers: empties para anchors y helpers internos
- Materiales básicos: M_metal_paint, M_glass_lens, M_rubber_cable, M_decal_generic
- Guarda el .blend en la ruta indicada
"""
import argparse
from pathlib import Path
import sys


def ensure_collection(name, parent=None):
    import bpy
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        if parent:
            parent.children.link(col)
        else:
            bpy.context.scene.collection.children.link(col)
    return col


def create_materials():
    import bpy
    mats = {}
    # Metal paint
    m = bpy.data.materials.get('M_metal_paint') or bpy.data.materials.new('M_metal_paint')
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.6, 0.15, 0.4, 1)
        bsdf.inputs['Roughness'].default_value = 0.35
        bsdf.inputs['Metallic'].default_value = 0.8
    mats['M_metal_paint'] = m

    # Glass
    g = bpy.data.materials.get('M_glass_lens') or bpy.data.materials.new('M_glass_lens')
    g.use_nodes = True
    bsdf = g.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        try:
            bsdf.inputs['Transmission'].default_value = 1.0
        except Exception:
            pass
        try:
            bsdf.inputs['Roughness'].default_value = 0.02
        except Exception:
            pass
        try:
            bsdf.inputs['Base Color'].default_value = (0.9, 0.95, 1.0, 1)
        except Exception:
            pass
    mats['M_glass_lens'] = g

    # Rubber cable
    r = bpy.data.materials.get('M_rubber_cable') or bpy.data.materials.new('M_rubber_cable')
    r.use_nodes = True
    bsdf = r.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        try:
            bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1)
        except Exception:
            pass
        try:
            bsdf.inputs['Roughness'].default_value = 0.6
        except Exception:
            pass
        try:
            bsdf.inputs['Metallic'].default_value = 0.0
        except Exception:
            pass
    mats['M_rubber_cable'] = r

    # Decal generic
    d = bpy.data.materials.get('M_decal_generic') or bpy.data.materials.new('M_decal_generic')
    d.use_nodes = True
    bsdf = d.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        try:
            bsdf.inputs['Base Color'].default_value = (1, 1, 1, 1)
        except Exception:
            pass
        try:
            bsdf.inputs['Roughness'].default_value = 0.8
        except Exception:
            pass
        try:
            bsdf.inputs['Specular'].default_value = 0.0
        except Exception:
            pass
    mats['M_decal_generic'] = d

    return mats


def create_primitives():
    import bpy
    from mathutils import Vector

    # Body: cube with applied scale
    bpy.ops.mesh.primitive_cube_add(size=1)
    body = bpy.context.active_object
    body.name = 'part_body_basic'
    body.scale = (0.12, 0.08, 0.06)  # ~ real-world scale
    body.location = (0, 0, 0.06)

    # Lens box
    bpy.ops.mesh.primitive_cube_add(size=1)
    lens_box = bpy.context.active_object
    lens_box.name = 'part_lens_box'
    lens_box.scale = (0.04, 0.06, 0.03)
    lens_box.location = (0.1, 0, 0.04)

    # Lens glass: cylinder thin
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.025, depth=0.01)
    lens_glass = bpy.context.active_object
    lens_glass.name = 'part_lens_glass'
    lens_glass.location = (0.14, 0, 0.04)

    # Mount arm
    bpy.ops.mesh.primitive_cube_add(size=1)
    mount = bpy.context.active_object
    mount.name = 'part_mount_arm_basic'
    mount.scale = (0.02, 0.02, 0.08)
    mount.location = (0, -0.08, 0.04)

    # Base plate
    bpy.ops.mesh.primitive_cube_add(size=1)
    base = bpy.context.active_object
    base.name = 'part_base_plate'
    base.scale = (0.06, 0.06, 0.01)
    base.location = (0, 0, 0.01)

    # Screw (simple cylinder + cross): create cylinder
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.0015, depth=0.01)
    screw = bpy.context.active_object
    screw.name = 'part_screw_M3'
    screw.location = (0, 0.02, 0.01)

    # Cable: simple curve
    bpy.ops.curve.primitive_bezier_curve_add()
    cable = bpy.context.active_object
    cable.name = 'part_cable_basic'
    # scale/shape
    cable.scale = (0.15, 0.15, 0.15)
    cable.location = (0, -0.04, 0.02)

    return {
        'part_body_basic': body,
        'part_lens_box': lens_box,
        'part_lens_glass': lens_glass,
        'part_mount_arm_basic': mount,
        'part_base_plate': base,
        'part_screw_M3': screw,
        'part_cable_basic': cable,
    }


def organize_into_collections(objs):
    import bpy
    cols = {}
    cols['COL_parts_body'] = ensure_collection('COL_parts_body')
    cols['COL_parts_lens'] = ensure_collection('COL_parts_lens')
    cols['COL_parts_mount'] = ensure_collection('COL_parts_mount')
    cols['COL_parts_base'] = ensure_collection('COL_parts_base')
    cols['COL_parts_fasteners'] = ensure_collection('COL_parts_fasteners')
    cols['COL_parts_cables'] = ensure_collection('COL_parts_cables')
    cols['COL_helpers'] = ensure_collection('COL_helpers')

    # link objects to collections
    def move(obj, col):
        # unlink from master collection to avoid duplicates
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        col.objects.link(obj)

    move(objs['part_body_basic'], cols['COL_parts_body'])
    move(objs['part_lens_box'], cols['COL_parts_lens'])
    move(objs['part_lens_glass'], cols['COL_parts_lens'])
    move(objs['part_mount_arm_basic'], cols['COL_parts_mount'])
    move(objs['part_base_plate'], cols['COL_parts_base'])
    move(objs['part_screw_M3'], cols['COL_parts_fasteners'])
    move(objs['part_cable_basic'], cols['COL_parts_cables'])

    # create helper empties
    import math
    import bpy
    e1 = bpy.data.objects.new('HELPER_screw_axis', None)
    e1.empty_display_type = 'ARROWS'
    e1.location = (0.0, 0.02, 0.01)
    cols['COL_helpers'].objects.link(e1)

    e2 = bpy.data.objects.new('HELPER_cable_direction', None)
    e2.empty_display_type = 'ARROWS'
    e2.location = (0.0, -0.04, 0.02)
    cols['COL_helpers'].objects.link(e2)

    return cols


def apply_materials_to_objects(objs, mats):
    # assign materials where relevant
    objs['part_body_basic'].data.materials.append(mats['M_metal_paint'])
    objs['part_lens_glass'].data.materials.append(mats['M_glass_lens'])
    objs['part_cable_basic'].data.materials.append(mats['M_rubber_cable'])
    objs['part_screw_M3'].data.materials.append(mats['M_metal_paint'])


def set_object_origins(objs):
    import bpy
    # Apply transforms and set origins to geometry center or bottom
    for name, obj in objs.items():
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        # For body/base set origin to bottom center
        if name in ('part_base_plate', 'part_body_basic'):
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            obj.location.z = obj.dimensions.z / 2.0
        else:
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')


def save_blend(output_path: Path):
    import bpy
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
    print('Saved blend to', output_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='blend/cybercam_parts.blend')
    args = parser.parse_args()

    try:
        import bpy
    except Exception as e:
        print('This script must be run inside Blender (bpy).', e)
        sys.exit(1)

    # Clean scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    mats = create_materials()
    objs = create_primitives()
    cols = organize_into_collections(objs)
    apply_materials_to_objects(objs, mats)
    set_object_origins(objs)

    # Document rules in scene custom properties
    scene = bpy.context.scene
    scene['cybercam_parts_version'] = 'v0.1'
    scene['cybercam_parts_scale'] = 'meters (approx)'

    out = Path(args.output)
    save_blend(out)


if __name__ == '__main__':
    main()

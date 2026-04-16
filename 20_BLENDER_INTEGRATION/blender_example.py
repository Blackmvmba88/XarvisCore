# Este script se ejecuta dentro de Blender (con --background --python blender_example.py)
# Busca objetos de la escena y exporta un JSON con nombres y tipos.
import json
import os

try:
    import bpy
except Exception as e:
    print('Error importando bpy:', e)
    raise

objs = []
for ob in bpy.data.objects:
    objs.append({'name': ob.name, 'type': ob.type})

out = {'objects': objs, 'blend_file': bpy.data.filepath}

# imprimir JSON en stdout para que el conector lo procese
print(json.dumps(out))

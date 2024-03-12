import bpy
import os

def convert_jpeg_to_obj(jpeg_path, obj_path):
    # Clear existing scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Load JPEG image as texture
    bpy.ops.image.open(filepath=jpeg_path)
    img = bpy.data.images[os.path.basename(jpeg_path)]
    texture = bpy.data.textures.new('Texture', type='IMAGE')
    texture.image = img
    
    # Add a plane and assign the texture
    bpy.ops.mesh.primitive_plane_add(size=10)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.unwrap()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    obj = bpy.context.object
    obj.name = 'Plane'
    
    mat = bpy.data.materials.new(name='Material')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    tex_image = mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex_image.image = img
    mat.node_tree.links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])
    
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    # Export the object as OBJ
    bpy.ops.export_scene.obj(filepath=obj_path)

# Example usage:
convert_jpeg_to_obj('input.jpg', 'output.obj')

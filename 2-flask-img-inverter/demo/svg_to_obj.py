# import bpy

# # Function to delete all objects in the scene
# def clear_scene():
#     bpy.ops.object.select_all(action='SELECT')
#     bpy.ops.object.delete()

# # Function to import an SVG file
# def import_svg(svg_filepath):
#     bpy.ops.import_curve.svg(filepath=svg_filepath)

# # Function to extrude all curves in the scene
# def extrude_curves(extrude_height):
#     for obj in bpy.context.scene.objects:
#         if obj.type == 'CURVE':
#             obj.data.extrude = extrude_height

# # # Function to add a solidify modifier to all curve objects
# # def solidify_curves(thickness):
# #     for obj in bpy.context.scene.objects:
# #         if obj.type == 'CURVE':
# #             bpy.context.view_layer.objects.active = obj  # Set as active object
# #             bpy.ops.object.modifier_add(type='SOLIDIFY')  # Add solidify modifier
# #             obj.modifiers["Solidify"].thickness = thickness

# # Function to export the scene as an OBJ
# def export_obj(export_filepath):
#     bpy.ops.export_scene.obj(filepath=export_filepath, use_selection=False)

# # Adjust your SVG and output file paths here
# svg_file_path = "C:/Users/user/Documents/4th year/OJT/OJT Files/FlaskImgInverter/2-flask-img-inverter/demo/image2.svg"
# output_obj_path = "C:/Users/user/Documents/4th year/OJT/OJT Files/FlaskImgInverter/2-flask-img-inverter/demo/image.obj"

# # Extrusion height and solidify thickness
# extrude_height = 0.005  # Adjust as needed
# # solidify_thickness = 0.00015  # Adjust as needed

# # Script execution
# clear_scene()
# import_svg(svg_file_path)
# extrude_curves(extrude_height)
# export_obj(output_obj_path)

import bpy
import sys

# Function to delete all objects in the scene
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Function to import an SVG file
def import_svg(svg_filepath):
    bpy.ops.import_curve.svg(filepath=svg_filepath)

# Function to extrude all curves in the scene
def extrude_curves(extrude_height):
    for obj in bpy.context.scene.objects:
        if obj.type == 'CURVE':
            obj.data.extrude = extrude_height

# Function to export the scene as an OBJ
def export_obj(export_filepath):
    bpy.ops.export_scene.obj(filepath=export_filepath, use_selection=False)

def main():
    # Parse command line arguments (the first argument is the script's filename)
    args = sys.argv[sys.argv.index("--") + 1:]  # After "--", the rest are the arguments for this script

    if len(args) != 2:
        print("Usage: blender -b -P this_script.py -- <svg_filepath> <obj_export_filepath>")
        return

    svg_file_path = args[0]
    obj_file_path = args[1]

    # Script execution
    clear_scene()
    import_svg(svg_file_path)
    extrude_curves(0.005)  # Extrusion height, adjust as needed
    export_obj(obj_file_path)

    print(f"Conversion completed: {svg_file_path} -> {obj_file_path}")

if __name__ == "__main__":
    main()

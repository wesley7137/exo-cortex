import bpy
import math
import os

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def import_prototype():
    obj_path = r"F:\exo-cortex\device\exocortex_prototype.obj"
    bpy.ops.import_scene.obj(filepath=obj_path)
    return bpy.context.selected_objects[0]

def create_housing():
    # Create main housing
    bpy.ops.mesh.primitive_cube_add(size=1)
    housing = bpy.context.active_object
    
    # Set dimensions according to specs (slightly larger than components)
    housing.dimensions = (60, 30, 15)  # in mm
    
    # Add subdivision surface modifier for smooth curves
    subsurf = housing.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    
    # Add curve modifier to match ear shape
    curve = housing.modifiers.new(name="Curve", type='CURVE')
    
    return housing

def create_component_slots(housing):
    # Create camera slot (9mm x 9mm x 3mm)
    bpy.ops.mesh.primitive_cube_add(size=1)
    camera_slot = bpy.context.active_object
    camera_slot.dimensions = (9, 9, 3)
    camera_slot.location = (25, 0, 5)  # Front-facing position
    
    # Create microphone port (6mm x 3mm x 1mm)
    bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=1)
    mic_port = bpy.context.active_object
    mic_port.location = (20, -10, 0)
    
    # Create battery compartment (25mm x 30mm x 4mm)
    bpy.ops.mesh.primitive_cube_add(size=1)
    battery_slot = bpy.context.active_object
    battery_slot.dimensions = (25, 30, 4)
    battery_slot.location = (-20, 0, 0)  # Rear position
    
    # Create USB-C port
    bpy.ops.mesh.primitive_cube_add(size=1)
    usb_port = bpy.context.active_object
    usb_port.dimensions = (9, 3, 1)
    usb_port.location = (-25, -10, 0)
    
    return [camera_slot, mic_port, battery_slot, usb_port]

def add_curves():
    # Add curves to match ear contour
    bpy.ops.curve.primitive_bezier_curve_add()
    curve = bpy.context.active_object
    # Modify curve points to match ear shape
    for point in curve.data.splines[0].bezier_points:
        point.handle_left_type = 'AUTO'
        point.handle_right_type = 'AUTO'

def main():
    clear_scene()
    
    # Import prototype if it exists
    try:
        prototype = import_prototype()
    except:
        print("Creating new design from scratch")
    
    # Create main components
    housing = create_housing()
    components = create_component_slots(housing)
    add_curves()
    
    # Apply modifiers
    for obj in [housing] + components:
        for modifier in obj.modifiers:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=modifier.name)

main()

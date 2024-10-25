import bpy
import math
import os

# Clear Blender file
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create base mesh for earpiece
def create_earpiece():
    # Create base curve for the ear hook
    bpy.ops.curve.primitive_bezier_curve_add()
    hook = bpy.context.active_object
    hook.name = "EarHook"
    
    # Modify curve to create ear hook shape
    spline = hook.data.splines[0]
    points = spline.bezier_points
    
    # Set points for natural ear curve
    points[0].co = (0, 0, 0)
    points[0].handle_left = (-0.5, 0.5, 0)
    points[0].handle_right = (0.5, -0.5, 0)
    
    # Add more points for complex curve
    spline.bezier_points.add(2)
    points[1].co = (1, -1, 0)
    points[2].co = (0, -2, 0)
    
    # Convert to mesh
    bpy.context.view_layer.objects.active = hook
    bpy.ops.object.convert(target='MESH')
    
    # Add thickness
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    hook.modifiers["Solidify"].thickness = 0.1
    
    # Smooth it out
    bpy.ops.object.shade_smooth()
    
    return hook

# Create housing for components
def create_housing():
    bpy.ops.mesh.primitive_cube_add()
    housing = bpy.context.active_object
    housing.name = "MainHousing"
    
    # Set dimensions based on README specs
    housing.scale = (0.3, 0.15, 0.075)  # 30mm x 15mm x 7.5mm
    
    # Add subdivision surface for smoothness
    subsurf = housing.modifiers.new(type='SUBSURF', name="Smooth")
    subsurf.levels = 2
    
    # Smooth corners
    bevel = housing.modifiers.new(type='BEVEL', name="Bevel")
    bevel.width = 0.05
    
    return housing

# Add component slots
def add_component_slots(housing):
    # Camera slot (9mm x 9mm)
    bpy.ops.mesh.primitive_cube_add(size=0.09)
    camera = bpy.context.active_object
    camera.name = "CameraSlot"
    camera.location = (0.15, 0, 0.03)
    
    # Battery compartment
    bpy.ops.mesh.primitive_cube_add()
    battery = bpy.context.active_object
    battery.name = "BatteryCompartment"
    battery.scale = (0.125, 0.15, 0.02)  # 25mm x 30mm x 4mm
    battery.location = (-0.1, 0, 0)

    # USB-C port
    bpy.ops.mesh.primitive_cube_add(size=0.009)
    usb = bpy.context.active_object
    usb.name = "USBPort"
    usb.scale = (1, 0.333, 1)
    usb.location = (-0.125, -0.05, 0)

# Create and save the model
def main():
    # Create all components
    hook = create_earpiece()
    housing = create_housing()
    add_component_slots(housing)
    
    # Save the file
    blend_path = r"F:\exo-cortex\device\exocortex_new_prototype.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

main()

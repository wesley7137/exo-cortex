import bpy

# First, let's create a recovery script that will:
# 1. Reset the view
# 2. Restore your original object
# 3. Set up proper lighting

def recover_scene():
    # Delete everything in scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Import original prototype
    bpy.ops.import_scene.obj(filepath=r"F:\exo-cortex\device\exocortex_prototype.obj")
    
    # Set up basic lighting
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 5.0
    
    # Add camera if needed
    bpy.ops.object.camera_add(location=(0, -10, 2), rotation=(math.radians(80), 0, 0))
    
    # Reset view to camera
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region}
                    bpy.ops.view3d.view_all(override)
    
    # Select the imported object
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
    
    # Frame view on object
    bpy.ops.view3d.view_selected(use_all_regions=True)

recover_scene()

import bpy
import math

# -----------------------------
# Setup Scene
# -----------------------------

# Delete all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Set Units to Metric
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1.0

# Define Constants
TRI_SIDE = 40  # mm
TRI_THICK = 15  # mm
STRAP_DIAMETER = 8  # mm
STRAP_LENGTH = 150  # mm
CAPSULE_LENGTH = 30  # mm
CAPSULE_WIDTH = 15  # mm
RADIUS_ROUND = 2  # mm for rounded edges

# Helper function to create an equilateral triangle
def create_equilateral_triangle(side_length, thickness, name):
    height = (math.sqrt(3)/2) * side_length
    
    # Create a new mesh and object
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    
    # Create vertices
    verts = [
        (-side_length/2, -height/3, 0),
        (side_length/2, -height/3, 0),
        (0, 2*height/3, 0)
    ]
    
    # Create faces
    faces = [(0, 1, 2)]
    
    # Create the mesh from verts and faces
    mesh.from_pydata(verts, [], faces)
    
    # Update mesh with new data
    mesh.update()
    
    # Link object to scene
    bpy.context.collection.objects.link(obj)
    
    # Extrude to give thickness
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, thickness)})
    bpy.ops.object.mode_set(mode='OBJECT')
    triangle = obj
    return triangle


# -----------------------------
# Create Triangle Housing
# -----------------------------
triangle = create_equilateral_triangle(TRI_SIDE, TRI_THICK, "Triangle_Housing")

# Rotate and position the triangle
triangle.rotation_euler[0] = math.radians(90)  # Rotate to stand vertically
triangle.location = (0, 0, TRI_THICK / 2)

# Smooth shading
bpy.ops.object.shade_smooth()

# -----------------------------
# Create Mounting Slots
# -----------------------------

# Camera Slot
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.5, 
    depth=3, 
    location=(TRI_SIDE / (2 * math.sqrt(3)) - 2, 0, TRI_THICK / 2 + 1.5),
    rotation=(math.radians(90), 0, 0)
)
camera_slot = bpy.context.object
camera_slot.name = "Camera_Slot"

# Microphone Slot
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.75, 
    depth=1.5, 
    location=(TRI_SIDE / (2 * math.sqrt(3)) - 1, -TRI_SIDE / 10, TRI_THICK / 2 + 1.5),
    rotation=(math.radians(90), 0, 0)
)
mic_slot = bpy.context.object
mic_slot.name = "Mic_Slot"

# Boolean Modifier to Create Slots
def subtract_slot(housing, slot):
    bool_mod = housing.modifiers.new(type="BOOLEAN", name=f"bool_{slot.name}")
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = slot
    bpy.context.view_layer.objects.active = housing
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    bpy.data.objects.remove(slot)

subtract_slot(triangle, camera_slot)
subtract_slot(triangle, mic_slot)

# -----------------------------
# Create Curved Head Strap
# -----------------------------

# Create a bezier curve for the strap
bpy.ops.curve.primitive_bezier_circle_add(radius=STRAP_DIAMETER / 2, location=(0, 0, 0))
strap_curve = bpy.context.object
strap_curve.name = "Head_Strap_Curve"

# Modify the curve to be a semi-circle
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.curve.select_all(action='DESELECT')
bpy.ops.curve.select_nth(nth=2, skip=0)
bpy.ops.transform.rotate(value=math.radians(180), orient_axis='Y')
bpy.ops.object.mode_set(mode='OBJECT')

# Convert curve to mesh
bpy.ops.object.convert(target='MESH')
strap_mesh = bpy.context.object
strap_mesh.name = "Head_Strap"

# Scale the strap to the desired length
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.transform.resize(value=(STRAP_LENGTH / 100, 1, 1))
bpy.ops.object.mode_set(mode='OBJECT')

# Add thickness to the strap
bpy.ops.object.modifier_add(type='SOLIDIFY')
strap_mesh.modifiers["Solidify"].thickness = STRAP_DIAMETER / 2
bpy.ops.object.modifier_apply(modifier="Solidify")

# Smooth shading
bpy.ops.object.shade_smooth()

# Position the strap to connect to the triangle housing
strap_mesh.rotation_euler[0] = math.radians(90)
strap_mesh.location = (0, -(TRI_SIDE / (2 * math.sqrt(3)) + STRAP_LENGTH / 200), TRI_THICK / 2)

# -----------------------------
# Create Opposite Capsule
# -----------------------------
bpy.ops.mesh.primitive_cylinder_add(
    radius=CAPSULE_WIDTH / 2, 
    depth=CAPSULE_LENGTH, 
    location=(0, STRAP_LENGTH / 100 + CAPSULE_LENGTH / 2, TRI_THICK / 2)
)
capsule = bpy.context.object
capsule.name = "Opposite_Capsule"

# Bevel the ends for a capsule shape
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.bevel(offset=CAPSULE_WIDTH / 2, segments=10, profile=1.0)
bpy.ops.object.mode_set(mode='OBJECT')

# Smooth shading
bpy.ops.object.shade_smooth()

# -----------------------------
# Connect Strap to Capsule
# -----------------------------

# Parent the capsule to the strap for seamless connection
capsule.parent = strap_mesh

# -----------------------------
# Optional Components
# -----------------------------

# Microphone Arm
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.5, 
    depth=30, 
    location=(TRI_SIDE / (2 * math.sqrt(3)), -TRI_SIDE / 5, TRI_THICK / 2 + 2)
)
mic_arm = bpy.context.object
mic_arm.name = "Microphone_Arm"
mic_arm.rotation_euler = (math.radians(90), 0, math.radians(45))
bpy.ops.object.modifier_add(type='SUBSURF')
bpy.ops.object.modifier_apply(modifier="Subdivision")
bpy.ops.object.shade_smooth()

# Button
bpy.ops.mesh.primitive_cube_add(
    size=3, 
    location=(TRI_SIDE / (2 * math.sqrt(3)) - 5, TRI_SIDE / 20, TRI_THICK / 2 + 1)
)
button = bpy.context.object
button.name = "Button"
bpy.ops.transform.resize(value=(0.5, 0.5, 0.2))
bpy.ops.object.shade_smooth()

# LED Indicator
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1, 
    location=(TRI_SIDE / (2 * math.sqrt(3)) - 10, TRI_SIDE / 20, TRI_THICK / 2 + 1)
)
led = bpy.context.object
led.name = "LED_Indicator"
bpy.ops.object.shade_smooth()

# -----------------------------
# Cable Management Channels
# -----------------------------

# Create a hollow channel along the strap for cables
bpy.ops.mesh.primitive_cylinder_add(
    radius=2.5, 
    depth=STRAP_LENGTH + 10, 
    location=(0, 0, TRI_THICK / 2)
)
channel_inner = bpy.context.object
channel_inner.name = "Cable_Channel"

# Boolean Modifier to subtract the channel from the strap
bool_mod_strap = strap_mesh.modifiers.new(type="BOOLEAN", name="bool_channel")
bool_mod_strap.operation = 'DIFFERENCE'
bool_mod_strap.object = channel_inner
bpy.context.view_layer.objects.active = strap_mesh
bpy.ops.object.modifier_apply(modifier=bool_mod_strap.name)

# Remove the channel object
bpy.data.objects.remove(channel_inner)

# -----------------------------
# Final Adjustments
# -----------------------------

# Ensure all parts are properly named and grouped if necessary
# (Optional: Create collections or parent objects as needed)

# -----------------------------
# Export as STL
# -----------------------------

export_path = "C:/Users/wes/exo-cortex/device/exocortex_full_headpiece_fixed.stl"
bpy.ops.export_mesh.stl(
    filepath=export_path,
    use_selection=False,
    global_scale=1.0,
    use_scene_unit=True,
    ascii=False,
    use_mesh_modifiers=True
)

print("Export completed successfully!")

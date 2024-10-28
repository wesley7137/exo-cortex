import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create main temple piece
bpy.ops.mesh.primitive_cube_add(size=1)
temple = bpy.context.active_object
temple.name = "Temple_Piece"
temple.dimensions = (120, 15, 5)
temple.location = (0, 0, 0)

# Create ESP32 housing
bpy.ops.mesh.primitive_cube_add(size=1)
esp32_housing = bpy.context.active_object
esp32_housing.name = "ESP32_Housing"
esp32_housing.dimensions = (55, 28, 4)
esp32_housing.location = (0, 0, 0)

# Create camera housing
bpy.ops.mesh.primitive_cube_add(size=1)
camera_housing = bpy.context.active_object
camera_housing.name = "Camera_Housing"
camera_housing.dimensions = (8.5, 8.5, 4)
camera_housing.location = (30, 0, 0)

# Create PowerBoost housing
bpy.ops.mesh.primitive_cube_add(size=1)
power_housing = bpy.context.active_object
power_housing.name = "PowerBoost_Housing"
power_housing.dimensions = (29, 23, 10)
power_housing.location = (-20, 0, 0)

# Create microphone housing
bpy.ops.mesh.primitive_cube_add(size=1)
mic_housing = bpy.context.active_object
mic_housing.name = "Mic_Housing"
mic_housing.dimensions = (17, 13, 2)
mic_housing.location = (20, -15, -5)

# Create speaker housing
bpy.ops.mesh.primitive_cylinder_add(radius=4, depth=2)
speaker_housing = bpy.context.active_object
speaker_housing.name = "Speaker_Housing"
speaker_housing.location = (-10, -10, 0)

# Add cable channel
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=120)
channel = bpy.context.active_object
channel.name = "Temple_Cable_Channel"
channel.rotation_euler.y = 1.5708
channel.location = (0, 0, 0)

# Add materials
# Temple piece material
material = bpy.data.materials.new(name="Temple_Material")
material.use_nodes = True
material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.8, 0.8, 1)
temple.data.materials.append(material)

# ESP32 material
material = bpy.data.materials.new(name="ESP32_Material")
material.use_nodes = True
material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.2, 0.2, 1)
esp32_housing.data.materials.append(material)

# Camera material
material = bpy.data.materials.new(name="Camera_Material")
material.use_nodes = True
material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.1, 0.1, 1)
camera_housing.data.materials.append(material)

# PowerBoost material
material = bpy.data.materials.new(name="Power_Material")
material.use_nodes = True
material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.2, 0.2, 1)
power_housing.data.materials.append(material)

# Microphone material
material = bpy.data.materials.new(name="Mic_Material")
material.use_nodes = True
material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.3, 0.3, 0.3, 1)
mic_housing.data.materials.append(material)

# Speaker material
material = bpy.data.materials.new(name="Speaker_Material")
material.use_nodes = True
material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.2, 0.2, 1)
speaker_housing.data.materials.append(material)

# First, clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create materials first
black_mat = bpy.data.materials.new(name="Black_Plastic")
black_mat.use_nodes = True
black_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.02, 0.02, 0.02, 1)

pcb_mat = bpy.data.materials.new(name="PCB_Green")
pcb_mat.use_nodes = True
pcb_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.3, 0.1, 1)

# Create Mini Breadboard (46mm x 36mm x 10mm)
bpy.ops.mesh.primitive_cube_add()
board = bpy.context.active_object
board.dimensions = (0.046, 0.036, 0.01)
board.name = "Breadboard"
board.data.materials.append(black_mat)

# Create PowerBoost 1000C (23mm x 45mm x 10mm)
bpy.ops.mesh.primitive_cube_add()
boost = bpy.context.active_object
boost.dimensions = (0.023, 0.045, 0.01)
boost.name = "PowerBoost"
boost.data.materials.append(pcb_mat)

# Create CP2102 Module (43mm x 6mm x 31mm)
bpy.ops.mesh.primitive_cube_add()
usb = bpy.context.active_object
usb.dimensions = (0.043, 0.006, 0.031)
usb.name = "CP2102"
usb.data.materials.append(pcb_mat)

# Create Speaker (10mm diameter x 3.5mm height)
bpy.ops.mesh.primitive_cylinder_add()
speaker = bpy.context.active_object
speaker.dimensions = (0.01, 0.01, 0.0035)
speaker.name = "Speaker"
speaker.data.materials.append(black_mat)

# Create Battery (40mm x 30mm x 4mm)
bpy.ops.mesh.primitive_cube_add()
battery = bpy.context.active_object
battery.dimensions = (0.040, 0.030, 0.004)
battery.name = "Battery"
battery.data.materials.append(black_mat)

# Create MEMS Microphone (13.8mm x 13.8mm x 1mm)
bpy.ops.mesh.primitive_cube_add()
mic = bpy.context.active_object
mic.dimensions = (0.0138, 0.0138, 0.001)
mic.name = "MEMS_Mic"
mic.data.materials.append(pcb_mat)



# Scale up Breadboard by 10x
board.scale = (10, 10, 10)
bpy.context.view_layer.objects.active = board
board.select_set(True)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
board.select_set(False)

board.lock_scale[0] = True
board.lock_scale[1] = True
board.lock_scale[2] = True

# Scale up PowerBoost by 10x
boost.scale = (10, 10, 10)
bpy.context.view_layer.objects.active = boost
boost.select_set(True)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
boost.select_set(False)

boost.lock_scale[0] = True
boost.lock_scale[1] = True
boost.lock_scale[2] = True

# Scale up CP2102 by 10x
usb.scale = (10, 10, 10)
bpy.context.view_layer.objects.active = usb
usb.select_set(True)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
usb.select_set(False)

usb.lock_scale[0] = True
usb.lock_scale[1] = True
usb.lock_scale[2] = True

# Scale up Speaker by 10x
speaker.scale = (10, 10, 10)
bpy.context.view_layer.objects.active = speaker
speaker.select_set(True)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
speaker.select_set(False)

speaker.lock_scale[0] = True
speaker.lock_scale[1] = True
speaker.lock_scale[2] = True

# Scale up Battery by 10x
battery.scale = (10, 10, 10)
bpy.context.view_layer.objects.active = battery
battery.select_set(True)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
battery.select_set(False)

battery.lock_scale[0] = True
battery.lock_scale[1] = True
battery.lock_scale[2] = True

# Scale up MEMS_Mic by 10x
mic.scale = (10, 10, 10)
bpy.context.view_layer.objects.active = mic
mic.select_set(True)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
mic.select_set(False)

mic.lock_scale[0] = True
mic.lock_scale[1] = True
mic.lock_scale[2] = True
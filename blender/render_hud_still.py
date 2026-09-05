"""Render VisitLock HUD / phone-batch twin still (Blender Metal on Mac)."""
import bpy
import math
from pathlib import Path

OUT = Path(r"/Users/vitaliecervinschi/Coding Compete/projects/visitlock-calle/docs/assets/hud-still.png")
OUT.parent.mkdir(parents=True, exist_ok=True)

# Reset
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# World
world = bpy.data.worlds.new("VLWorld")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.04, 0.06, 0.12, 1)
bg.inputs[1].default_value = 1.0

# Phone slab
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.08))
phone = bpy.context.active_object
phone.name = "Phone"
phone.scale = (0.45, 0.9, 0.06)
mat_phone = bpy.data.materials.new("PhoneMat")
mat_phone.use_nodes = True
nt = mat_phone.node_tree
bsdf = nt.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.08, 0.1, 0.14, 1)
bsdf.inputs["Metallic"].default_value = 0.7
bsdf.inputs["Roughness"].default_value = 0.25
phone.data.materials.append(mat_phone)

# Screen
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.02, 0.12))
screen = bpy.context.active_object
screen.name = "Screen"
screen.scale = (0.38, 0.72, 0.01)
mat_screen = bpy.data.materials.new("ScreenMat")
mat_screen.use_nodes = True
sbsdf = mat_screen.node_tree.nodes["Principled BSDF"]
sbsdf.inputs["Base Color"].default_value = (0.15, 0.35, 0.85, 1)
if "Emission Color" in sbsdf.inputs:
    sbsdf.inputs["Emission Color"].default_value = (0.2, 0.45, 1.0, 1)
if "Emission Strength" in sbsdf.inputs:
    sbsdf.inputs["Emission Strength"].default_value = 3.0
screen.data.materials.append(mat_screen)

# Metric cards as glowing boxes
def card(name, loc, color):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (0.55, 0.22, 0.04)
    m = bpy.data.materials.new(name + "Mat")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    if "Emission Color" in b.inputs:
        b.inputs["Emission Color"].default_value = (*color, 1)
    if "Emission Strength" in b.inputs:
        b.inputs["Emission Strength"].default_value = 2.5
    obj.data.materials.append(m)
    return obj

card("MetricConfirmed", (-1.4, 0.6, 0.3), (0.2, 0.85, 0.55))
card("MetricRate", (-1.4, 0.0, 0.3), (0.4, 0.65, 1.0))
card("MetricReschedule", (-1.4, -0.6, 0.3), (1.0, 0.75, 0.3))

# Text objects with fixture numbers
def text(name, body, loc, size=0.18):
    bpy.ops.object.text_add(location=loc)
    t = bpy.context.active_object
    t.name = name
    t.data.body = body
    t.data.size = size
    t.data.align_x = "CENTER"
    t.rotation_euler = (math.radians(90), 0, 0)
    tm = bpy.data.materials.new(name + "Mat")
    tm.use_nodes = True
    tb = tm.node_tree.nodes["Principled BSDF"]
    tb.inputs["Base Color"].default_value = (0.95, 0.97, 1.0, 1)
    if "Emission Color" in tb.inputs:
        tb.inputs["Emission Color"].default_value = (0.95, 0.97, 1.0, 1)
    if "Emission Strength" in tb.inputs:
        tb.inputs["Emission Strength"].default_value = 1.5
    if t.data.materials:
        t.data.materials[0] = tm
    else:
        t.data.materials.append(tm)
    return t

text("Title", "VisitLock", (0, -1.35, 0.4), 0.28)
text("Tag", "3/5  |  60%  |  risk 10", (0, -1.7, 0.35), 0.14)
text("L1", "3 / 5", (-1.4, 0.6, 0.45), 0.16)
text("L2", "60%", (-1.4, 0.0, 0.45), 0.16)
text("L3", "1 resched", (-1.4, -0.6, 0.45), 0.12)

# Camera
bpy.ops.object.camera_add(location=(2.8, -2.8, 2.2))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(60), 0, math.radians(45))
scene.camera = cam

# Light
bpy.ops.object.light_add(type="AREA", location=(2, -1, 3))
light = bpy.context.active_object
light.data.energy = 250
light.data.size = 3

# Render settings — Metal on Mac
scene.render.engine = "BLENDER_EEVEE"
# Prefer Metal via preferences when available
prefs = bpy.context.preferences
if hasattr(prefs, "system"):
    sys = prefs.system
    for attr in ("compute_device_type",):
        if hasattr(sys, attr):
            try:
                setattr(sys, attr, "METAL")
            except Exception:
                pass

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.filepath = str(OUT)
scene.render.image_settings.file_format = "PNG"

bpy.ops.render.render(write_still=True)
print("WROTE", OUT)

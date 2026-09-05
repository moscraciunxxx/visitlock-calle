"""Render VisitLock HUD / phone-batch twin still (Blender Metal on Mac)."""
import bpy
import math
from pathlib import Path

OUT = Path(r"/Users/vitaliecervinschi/Coding Compete/projects/visitlock-calle/docs/assets/hud-still.png")
OUT.parent.mkdir(parents=True, exist_ok=True)
FONT = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
if not FONT.is_file():
    FONT = Path("/System/Library/Fonts/Helvetica.ttc")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

world = bpy.data.worlds.new("VLWorld")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.04, 0.06, 0.12, 1)
bg.inputs[1].default_value = 1.0

# Phone — center-right
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.7, 0.0, 0.08))
phone = bpy.context.active_object
phone.name = "Phone"
phone.scale = (0.40, 0.78, 0.05)
mat_phone = bpy.data.materials.new("PhoneMat")
mat_phone.use_nodes = True
bsdf = mat_phone.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.08, 0.1, 0.14, 1)
bsdf.inputs["Metallic"].default_value = 0.7
bsdf.inputs["Roughness"].default_value = 0.25
phone.data.materials.append(mat_phone)

bpy.ops.mesh.primitive_cube_add(size=1, location=(0.7, 0.02, 0.12))
screen = bpy.context.active_object
screen.name = "Screen"
screen.scale = (0.33, 0.64, 0.01)
mat_screen = bpy.data.materials.new("ScreenMat")
mat_screen.use_nodes = True
sbsdf = mat_screen.node_tree.nodes["Principled BSDF"]
sbsdf.inputs["Base Color"].default_value = (0.15, 0.35, 0.85, 1)
if "Emission Color" in sbsdf.inputs:
    sbsdf.inputs["Emission Color"].default_value = (0.2, 0.45, 1.0, 1)
if "Emission Strength" in sbsdf.inputs:
    sbsdf.inputs["Emission Strength"].default_value = 3.0
screen.data.materials.append(mat_screen)


def card(name, loc, color):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (0.48, 0.18, 0.03)
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


# Metric cards — keep fully inside frame (x >= -0.9)
card("MetricConfirmed", (-0.85, 0.55, 0.28), (0.2, 0.85, 0.55))
card("MetricRate", (-0.85, 0.05, 0.28), (0.4, 0.65, 1.0))
card("MetricReschedule", (-0.85, -0.45, 0.28), (1.0, 0.75, 0.3))


def text(name, body, loc, size=0.14):
    bpy.ops.object.text_add(location=loc)
    t = bpy.context.active_object
    t.name = name
    t.data.body = body
    t.data.size = size
    t.data.align_x = "CENTER"
    if FONT.is_file():
        try:
            t.data.font = bpy.data.fonts.load(str(FONT))
        except Exception:
            pass
    t.rotation_euler = (math.radians(90), 0, 0)
    tm = bpy.data.materials.new(name + "Mat")
    tm.use_nodes = True
    tb = tm.node_tree.nodes["Principled BSDF"]
    tb.inputs["Base Color"].default_value = (0.95, 0.97, 1.0, 1)
    if "Emission Color" in tb.inputs:
        tb.inputs["Emission Color"].default_value = (0.95, 0.97, 1.0, 1)
    if "Emission Strength" in tb.inputs:
        tb.inputs["Emission Strength"].default_value = 1.8
    if t.data.materials:
        t.data.materials[0] = tm
    else:
        t.data.materials.append(tm)
    return t


text("Title", "VisitLock", (0.0, -1.25, 0.40), 0.22)
text("Tag", "3 of 5   |   60%   |   risk 10", (0.0, -1.55, 0.34), 0.09)
text("L1", "3 / 5", (-0.85, 0.55, 0.40), 0.13)
text("L2", "60%", (-0.85, 0.05, 0.40), 0.13)
# Full readable word — never "1 resched"
text("L3", "1 reschedule", (-0.85, -0.45, 0.40), 0.09)

# Camera pulled back so left labels stay in frame
bpy.ops.object.camera_add(location=(3.2, -3.2, 2.5))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(55), 0, math.radians(40))
cam.data.lens = 35
scene.camera = cam

bpy.ops.object.light_add(type="AREA", location=(2, -1, 3))
light = bpy.context.active_object
light.data.energy = 280
light.data.size = 3

scene.render.engine = "BLENDER_EEVEE"
prefs = bpy.context.preferences
if hasattr(prefs, "system") and hasattr(prefs.system, "compute_device_type"):
    try:
        prefs.system.compute_device_type = "METAL"
    except Exception:
        pass

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.filepath = str(OUT)
scene.render.image_settings.file_format = "PNG"
bpy.ops.render.render(write_still=True)
print("WROTE", OUT)

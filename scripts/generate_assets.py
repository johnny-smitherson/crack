import bpy
import math
import os
import argparse
import subprocess
import sys

# Helper to clear scene
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# Helper to create texture material
def create_texture_material(name, img_path, color=None, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    
    if img_path and os.path.exists(img_path):
        tex_image = nodes.new('ShaderNodeTexImage')
        tex_image.location = (-400, 0)
        tex_image.image = bpy.data.images.load(img_path)
        
        mapping = nodes.new('ShaderNodeMapping')
        mapping.location = (-600, 0)
        
        tex_coord = nodes.new('ShaderNodeTexCoord')
        tex_coord.location = (-800, 0)
        
        links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
        links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
    elif color:
        bsdf.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
        
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

def set_viewport_to_material_shading():
    """Sets the active viewport shading mode to Material Preview for immediate visual feedback."""
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'

def make_bus_textures(output_dir):
    """
    Programmatically draws the orthographic front, side, and back textures for the 335 bus
    by executing Pillow in the sandboxed python virtual environment via subprocess.
    """
    textures_dir = os.path.join(output_dir, "textures")
    os.makedirs(textures_dir, exist_ok=True)
    
    print("[ASSET GENERATOR] Invoking python venv subprocess to draw bus textures...")
    
    script_code = f"""
import os
from PIL import Image, ImageDraw, ImageFont

textures_dir = "{textures_dir}"
os.makedirs(textures_dir, exist_ok=True)

font_path = "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
if not os.path.exists(font_path):
    font_path = None

# ==========================================
# 1. FRONT TEXTURE (512x512)
# ==========================================
img_front = Image.new("RGBA", (512, 512), (245, 245, 242, 255))
draw = ImageDraw.Draw(img_front)

# Windshield / LED Screen
draw.rectangle([15, 30, 497, 240], fill=(15, 15, 15, 255))

if font_path:
    f_led = ImageFont.truetype(font_path, 28)
    f_led_small = ImageFont.truetype(font_path, 20)
    f_plate = ImageFont.truetype(font_path, 22)
    f_ratb = ImageFont.truetype(font_path, 18)
else:
    f_led = f_led_small = f_plate = f_ratb = ImageFont.load_default()
    
# Destination text
draw.text((60, 50), "335", fill=(255, 130, 0, 255), font=f_led)
draw.text((150, 50), "COMPLEX BANEASA", fill=(255, 130, 0, 255), font=f_led)
draw.text((150, 85), "BARAJUL DUNARII", fill=(255, 130, 0, 255), font=f_led_small)
draw.text((50, 180), "Aer Conditionat", fill=(255, 255, 255, 255), font=f_led_small)

# Headlights
draw.ellipse([30, 360, 90, 400], fill=(255, 250, 200, 255), outline=(100, 100, 100, 255), width=3)
draw.ellipse([422, 360, 482, 400], fill=(255, 250, 200, 255), outline=(100, 100, 100, 255), width=3)

# Mercedes star
draw.ellipse([236, 330, 276, 370], fill=(200, 200, 200, 255), outline=(120, 120, 120, 255), width=3)
draw.line([256, 350, 256, 333], fill=(120, 120, 120, 255), width=3)
draw.line([256, 350, 241, 361], fill=(120, 120, 120, 255), width=3)
draw.line([256, 350, 271, 361], fill=(120, 120, 120, 255), width=3)

# License Plate
draw.rectangle([190, 430, 322, 470], fill=(255, 255, 255, 255), outline=(50, 50, 50, 255), width=2)
draw.text((200, 435), "B 97 YXX", fill=(0, 0, 0, 255), font=f_plate)

draw.text((120, 340), "ratb", fill=(0, 0, 0, 255), font=f_ratb)
draw.text((120, 360), "4951", fill=(0, 0, 0, 255), font=f_ratb)

# Bumper
draw.rectangle([0, 480, 512, 512], fill=(60, 60, 60, 255))
img_front.save(os.path.join(textures_dir, "bus_front.png"))

# ==========================================
# 2. SIDE TEXTURE (1024x256)
# ==========================================
img_side = Image.new("RGBA", (1024, 256), (245, 245, 242, 255))
draw_side = ImageDraw.Draw(img_side)
draw_side.rectangle([0, 25, 1024, 115], fill=(20, 20, 20, 255))

for dx in [120, 500, 880]:
    draw_side.rectangle([dx, 25, dx + 80, 230], fill=(245, 245, 242, 255), outline=(80, 80, 80, 255), width=3)
    draw_side.line([dx + 40, 25, dx + 40, 230], fill=(80, 80, 80, 255), width=2)
    draw_side.rectangle([dx + 8, 35, dx + 32, 115], fill=(30, 30, 30, 255))
    draw_side.rectangle([dx + 48, 35, dx + 72, 115], fill=(30, 30, 30, 255))
    draw_side.rectangle([dx + 8, 130, dx + 32, 210], fill=(30, 30, 30, 255))
    draw_side.rectangle([dx + 48, 130, dx + 72, 210], fill=(30, 30, 30, 255))
    
draw_side.rectangle([470, 190, 490, 210], fill=(0, 100, 200, 255))
draw_side.rectangle([590, 190, 610, 210], fill=(0, 100, 200, 255))
draw_side.text((250, 45), "Aer Conditionat", fill=(255, 255, 255, 255), font=f_ratb)
draw_side.text((320, 150), "ratb", fill=(0, 0, 0, 255), font=f_ratb)
draw_side.text((320, 175), "4951", fill=(0, 0, 0, 255), font=f_ratb)
draw_side.rectangle([0, 240, 1024, 256], fill=(50, 50, 50, 255))
img_side.save(os.path.join(textures_dir, "bus_side.png"))

# ==========================================
# 3. BACK TEXTURE (512x512)
# ==========================================
img_back = Image.new("RGBA", (512, 512), (245, 245, 242, 255))
draw_back = ImageDraw.Draw(img_back)
draw_back.rectangle([30, 40, 482, 200], fill=(20, 20, 20, 255))
draw_back.rectangle([20, 400, 60, 440], fill=(240, 30, 30, 255), outline=(50, 50, 50, 255), width=2)
draw_back.rectangle([452, 400, 492, 440], fill=(240, 30, 30, 255), outline=(50, 50, 50, 255), width=2)
draw_back.rectangle([20, 440, 60, 460], fill=(255, 140, 0, 255))
draw_back.rectangle([452, 440, 492, 460], fill=(255, 140, 0, 255))
draw_back.rectangle([190, 410, 322, 450], fill=(255, 255, 255, 255), outline=(50, 50, 50, 255), width=2)
draw_back.text((200, 415), "B 97 YXX", fill=(0, 0, 0, 255), font=f_plate)
draw_back.rectangle([0, 480, 512, 512], fill=(60, 60, 60, 255))
img_back.save(os.path.join(textures_dir, "bus_back.png"))
"""
    subprocess.run(["/tmp/venv/bin/python", "-c", script_code], check=True)
    
    return {
        "front": os.path.join(textures_dir, "bus_front.png"),
        "side": os.path.join(textures_dir, "bus_side.png"),
        "back": os.path.join(textures_dir, "bus_back.png")
    }

def generate_bus(texture_path, output_dir):
    """
    Models the Mercedes Citaro 335 Bus in low-poly, creates custom orthographic textures,
    and maps them mathematically to the front, sides, and back of the bus body.
    """
    print(f"[ASSET GENERATOR] Generating 335 Bus using texture: {texture_path}")
    clear_scene()

    parts = []

    # 1. Main Bus body (White Mercedes Citaro box)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.5))
    bus_body = bpy.context.active_object
    bus_body.name = "Bus_Body"
    bus_body.scale = (2.5, 12.0, 2.8)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(bus_body)

    # 2. Make modular orthographic textures using Pillow via venv python
    tex_files = make_bus_textures(output_dir)

    # 3. Create materials for Slots
    white_paint_mat = create_texture_material("Bus_Paint_Mat", None, color=[0.96, 0.96, 0.94], roughness=0.3)
    side_mat = create_texture_material("Bus_Side_Mat", tex_files["side"], roughness=0.3)
    front_mat = create_texture_material("Bus_Front_Mat", tex_files["front"], roughness=0.3)
    back_mat = create_texture_material("Bus_Back_Mat", tex_files["back"], roughness=0.3)

    # Add materials to slot list
    bus_body.data.materials.append(white_paint_mat) # Slot 0
    bus_body.data.materials.append(side_mat)        # Slot 1
    bus_body.data.materials.append(front_mat)       # Slot 2
    bus_body.data.materials.append(back_mat)        # Slot 3

    # 4. Map material slots to specific faces based on normals
    for face in bus_body.data.polygons:
        normal = face.normal
        if normal.y > 0.9:     # Front face (Y+)
            face.material_index = 2
        elif normal.y < -0.9:  # Back face (Y-)
            face.material_index = 3
        elif abs(normal.x) > 0.9: # Side faces (X+ and X-)
            face.material_index = 1
        else:                  # Top / Bottom
            face.material_index = 0

    # 5. Calculate UV coordinates mathematically for clean wrapping
    if not bus_body.data.uv_layers:
        bus_body.data.uv_layers.new()
    uv_layer = bus_body.data.uv_layers.active.data

    for face in bus_body.data.polygons:
        loop_indices = face.loop_indices
        normal = face.normal
        
        if abs(normal.x) > 0.9: # Side faces (X+ or X-)
            # Map Y (length) to U, Z (height) to V
            # U goes from 0 (at Y=-6.0) to 1 (at Y=6.0)
            # V goes from 0 (at Z=0.1) to 1 (at Z=2.9)
            for li in loop_indices:
                v_idx = bus_body.data.loops[li].vertex_index
                v = bus_body.data.vertices[v_idx]
                u = (v.co.y + 6.0) / 12.0
                v_uv = (v.co.z - 0.1) / 2.8
                # Flip U on the left side to keep text running forward-to-back on both sides
                if normal.x < 0:
                    u = 1.0 - u
                uv_layer[li].uv = (u, v_uv)
                
        elif normal.y > 0.9: # Front face (Y+)
            # Map X (width) to U, Z (height) to V
            for li in loop_indices:
                v_idx = bus_body.data.loops[li].vertex_index
                v = bus_body.data.vertices[v_idx]
                u = (v.co.x + 1.25) / 2.5
                v_uv = (v.co.z - 0.1) / 2.8
                uv_layer[li].uv = (u, v_uv)
                
        elif normal.y < -0.9: # Back face (Y-)
            # Map X to U, Z to V
            for li in loop_indices:
                v_idx = bus_body.data.loops[li].vertex_index
                v = bus_body.data.vertices[v_idx]
                u = 1.0 - (v.co.x + 1.25) / 2.5
                v_uv = (v.co.z - 0.1) / 2.8
                uv_layer[li].uv = (u, v_uv)
                
        else: # Top / Bottom faces (Z+ or Z-)
            # Simple plane mapping
            for li in loop_indices:
                v_idx = bus_body.data.loops[li].vertex_index
                v = bus_body.data.vertices[v_idx]
                u = (v.co.x + 1.25) / 2.5
                v_uv = (v.co.y + 6.0) / 12.0
                uv_layer[li].uv = (u, v_uv)

    # 6. Add wheels (4 dark rubber cylinders)
    wheel_mat = create_texture_material("Wheel_Mat", None, color=[0.08, 0.08, 0.08], roughness=0.9)
    wheel_positions = [
        (-1.25, 4.0, 0.5),  # Front Left
        (1.25, 4.0, 0.5),   # Front Right
        (-1.25, -4.0, 0.5), # Rear Left
        (1.25, -4.0, 0.5)   # Rear Right
    ]

    for idx, pos in enumerate(wheel_positions):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.5, 
            depth=0.3, 
            location=pos,
            rotation=(0, math.radians(90), 0)
        )
        wheel = bpy.context.active_object
        wheel.name = f"Wheel_{idx}"
        wheel.data.materials.append(wheel_mat)
        parts.append(wheel)

    # 7. Join all bus parts
    bpy.ops.object.select_all(action='DESELECT')
    main_bus = parts[0]
    main_bus.select_set(True)
    for p in parts[1:]:
        p.select_set(True)
    bpy.context.view_layer.objects.active = main_bus
    bpy.ops.object.join()
    main_bus.name = "Bus_335"

    # Set viewport shading to MATERIAL and pack textures
    set_viewport_to_material_shading()
    try:
        bpy.ops.file.pack_all()
    except Exception as e:
        print(f"Warning: Could not pack textures: {e}")

    # 8. Export
    os.makedirs(output_dir, exist_ok=True)
    export_path_glb = os.path.join(output_dir, "bus_335.glb")
    export_path_blend = os.path.join(output_dir, "bus_335.blend")
    
    bpy.ops.export_scene.gltf(filepath=export_path_glb, export_format='GLB')
    bpy.ops.wm.save_as_mainfile(filepath=export_path_blend)
    print(f"[ASSET GENERATOR] 335 Bus exported successfully to {export_path_glb} and saved to {export_path_blend}")


def generate_kebab_shop(texture_path, output_dir):
    """
    Models the modern Socului Kebab shop interior, matching layout, wall colors, text, and stools.
    """
    print(f"[ASSET GENERATOR] Generating Kebab Shop using texture: {texture_path}")
    clear_scene()

    parts = []

    # 1. Floor (Light gray polished tile)
    bpy.ops.mesh.primitive_plane_add(size=8.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Floor"
    floor_mat = create_texture_material("Floor_Mat", None, color=[0.85, 0.85, 0.85], roughness=0.15)
    floor.data.materials.append(floor_mat)
    parts.append(floor)

    # 2. Back Wall (Red Accent Wall with "SOCULUI KEBAB" text)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 4.0, 1.5))
    back_wall = bpy.context.active_object
    back_wall.name = "Back_Wall"
    back_wall.scale = (8.0, 0.1, 3.0)
    bpy.ops.object.transform_apply(scale=True)
    
    # Socului Red accent color
    red_wall_mat = create_texture_material("Red_Wall_Mat", None, color=[0.65, 0.05, 0.05], roughness=0.8)
    back_wall.data.materials.append(red_wall_mat)
    parts.append(back_wall)

    # Add 3D Text "SOCULUI KEBAB"
    white_text_mat = create_texture_material("White_Text_Mat", None, color=[1.0, 1.0, 1.0], roughness=0.5)
    
    # SOCULUI (Top line)
    bpy.ops.object.text_add(location=(-2.2, 3.85, 2.0))
    txt_socului = bpy.context.active_object
    txt_socului.name = "Text_Socului"
    txt_socului.data.body = "SOCULUI"
    txt_socului.data.extrude = 0.06
    txt_socului.scale = (0.55, 0.55, 0.55)
    txt_socului.rotation_euler = (math.radians(90), 0, 0)
    txt_socului.data.materials.append(white_text_mat)
    parts.append(txt_socului)

    # KEBAB (Bottom line)
    bpy.ops.object.text_add(location=(-1.6, 3.85, 1.3))
    txt_kebab = bpy.context.active_object
    txt_kebab.name = "Text_Kebab"
    txt_kebab.data.body = "KEBAB"
    txt_kebab.data.extrude = 0.06
    txt_kebab.scale = (0.45, 0.45, 0.45)
    txt_kebab.rotation_euler = (math.radians(90), 0, 0)
    txt_kebab.data.materials.append(white_text_mat)
    parts.append(txt_kebab)

    # 3. Off-white Side Walls
    off_white_mat = create_texture_material("Off_White_Wall_Mat", None, color=[0.9, 0.9, 0.88], roughness=0.9)
    
    # Left Wall (West)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-4.0, 0, 1.5))
    left_wall = bpy.context.active_object
    left_wall.name = "Left_Wall"
    left_wall.scale = (0.1, 8.0, 3.0)
    bpy.ops.object.transform_apply(scale=True)
    left_wall.data.materials.append(off_white_mat)
    parts.append(left_wall)

    # Right Wall (East)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(4.0, 0, 1.5))
    right_wall = bpy.context.active_object
    right_wall.name = "Right_Wall"
    right_wall.scale = (0.1, 8.0, 3.0)
    bpy.ops.object.transform_apply(scale=True)
    right_wall.data.materials.append(off_white_mat)
    parts.append(right_wall)

    # 4. Wooden Bar Counter
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.0, 1.5, 0.5))
    counter_base = bpy.context.active_object
    counter_base.name = "Counter_Base"
    counter_base.scale = (3.5, 0.8, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    
    wood_mat = create_texture_material("Counter_Wood_Mat", None, color=[0.7, 0.45, 0.25], roughness=0.6)
    counter_base.data.materials.append(wood_mat)
    parts.append(counter_base)

    # Photo texture applied to the front panel facing customer dining area
    panel_mat = create_texture_material("Kebab_Photo_Mat", texture_path, roughness=0.5)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.0, 1.09, 0.5))
    photo_panel = bpy.context.active_object
    photo_panel.name = "Photo_Panel"
    photo_panel.scale = (3.4, 0.01, 0.95)
    bpy.ops.object.transform_apply(scale=True)
    photo_panel.data.materials.append(panel_mat)
    
    # UV Map panel
    bpy.context.view_layer.objects.active = photo_panel
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    parts.append(photo_panel)

    # 5. Plant Shelf Grid (White grid structure behind the counter)
    plant_shelf_mat = create_texture_material("Plant_Shelf_Mat", None, color=[0.95, 0.95, 0.95], roughness=0.3)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=5, y_subdivisions=5, size=2.5, location=(-2.0, 2.2, 1.8))
    plant_grid = bpy.context.active_object
    plant_grid.name = "Plant_Grid"
    # Extrude it to a cage structure using Wireframe Modifier
    wire = plant_grid.modifiers.new(name="Wireframe", type='WIREFRAME')
    wire.thickness = 0.04
    plant_grid.data.materials.append(plant_shelf_mat)
    parts.append(plant_grid)

    # Green potted plants inside grid boxes
    green_mat = create_texture_material("Plant_Green_Mat", None, color=[0.1, 0.5, 0.15], roughness=0.8)
    for px, pz in [(-2.8, 1.2), (-2.0, 1.2), (-1.2, 1.2), (-2.5, 2.0), (-1.5, 2.0)]:
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.25, subdivisions=2, location=(px, 2.2, pz))
        plant = bpy.context.active_object
        plant.name = "Grid_Plant"
        plant.data.materials.append(green_mat)
        parts.append(plant)

    # 6. Bar Stools (Alternating Black and Red)
    chrome_mat = create_texture_material("Chrome_Mat", None, color=[0.8, 0.8, 0.8], metallic=1.0, roughness=0.15)
    red_stool_mat = create_texture_material("Red_Stool_Mat", None, color=[0.85, 0.05, 0.05], roughness=0.6)
    black_stool_mat = create_texture_material("Black_Stool_Mat", None, color=[0.05, 0.05, 0.05], roughness=0.7)

    # 5 Stools placed along the bar counter
    stool_x_coords = [-3.2, -2.6, -2.0, -1.4, -0.8]
    for idx, sx in enumerate(stool_x_coords):
        # Base plate
        bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.03, location=(sx, 0.5, 0.015))
        base = bpy.context.active_object
        base.name = f"Stool_Base_{idx}"
        base.data.materials.append(chrome_mat)
        parts.append(base)

        # Pole
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.6, location=(sx, 0.5, 0.3))
        pole = bpy.context.active_object
        pole.name = f"Stool_Pole_{idx}"
        pole.data.materials.append(chrome_mat)
        parts.append(pole)

        # Seat (alternating black and red)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.08, location=(sx, 0.5, 0.6))
        seat = bpy.context.active_object
        seat.name = f"Stool_Seat_{idx}"
        
        active_stool_mat = red_stool_mat if idx % 2 == 1 else black_stool_mat
        seat.data.materials.append(active_stool_mat)
        parts.append(seat)

    # 7. Customer Tables (Round pedestal) & Web-like/Lattice Dining Chairs
    table_white_mat = create_texture_material("Table_White_Mat", None, color=[0.92, 0.92, 0.92], roughness=0.2)
    chair_white_mat = create_texture_material("Chair_White_Mat", None, color=[0.9, 0.9, 0.9], roughness=0.5)
    chair_red_mat = create_texture_material("Chair_Red_Mat", None, color=[0.8, 0.05, 0.05], roughness=0.5)

    # Dining set 1
    t1_pos = (2.0, -2.0)
    # Round Table
    bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=0.05, location=(t1_pos[0], t1_pos[1], 0.75))
    tab1 = bpy.context.active_object
    tab1.data.materials.append(table_white_mat)
    parts.append(tab1)
    # Table leg
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.7, location=(t1_pos[0], t1_pos[1], 0.35))
    tab1_leg = bpy.context.active_object
    tab1_leg.data.materials.append(chrome_mat)
    parts.append(tab1_leg)

    # Web/Lattice Chairs
    for idx, c_offset in enumerate([(-0.8, 0.0), (0.8, 0.0)]):
        cx = t1_pos[0] + c_offset[0]
        cy = t1_pos[1] + c_offset[1]
        
        # Grid lattice seat using wireframe modifier
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=5, y_subdivisions=5, size=0.4, location=(cx, cy, 0.45))
        c_seat = bpy.context.active_object
        c_seat.name = f"Lattice_Chair_Seat_{idx}"
        wire_seat = c_seat.modifiers.new(name="WireframeSeat", type='WIREFRAME')
        wire_seat.thickness = 0.025
        
        # Alternate white and red chairs
        c_mat = chair_white_mat if idx % 2 == 0 else chair_red_mat
        c_seat.data.materials.append(c_mat)
        parts.append(c_seat)

        # Backrest (extrude a vertical lattice backrest)
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=5, y_subdivisions=5, size=0.4, location=(cx + c_offset[0]*0.2, cy, 0.75), rotation=(0, math.radians(90), 0))
        c_back = bpy.context.active_object
        c_back.name = f"Lattice_Chair_Back_{idx}"
        wire_back = c_back.modifiers.new(name="WireframeBack", type='WIREFRAME')
        wire_back.thickness = 0.025
        c_back.data.materials.append(c_mat)
        parts.append(c_back)

        # Chair legs
        for lx, ly in [(-0.15, -0.15), (0.15, -0.15), (-0.15, 0.15), (0.15, 0.15)]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.4, location=(cx + lx, cy + ly, 0.2))
            c_leg = bpy.context.active_object
            c_leg.data.materials.append(chrome_mat)
            parts.append(c_leg)

    # 8. Juice Dispenser (on left side of wooden counter)
    jd_x, jd_y, jd_z = (-3.2, 1.4, 1.0)
    # Silver Base box
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(jd_x, jd_y, jd_z + 0.15))
    jd_base = bpy.context.active_object
    jd_base.name = "Juice_Dispenser_Base"
    jd_base.scale = (0.4, 0.4, 0.3)
    bpy.ops.object.transform_apply(scale=True)
    jd_base.data.materials.append(chrome_mat)
    parts.append(jd_base)

    # Yellow juice tank (translucent/emissive yellow look)
    yellow_juice_mat = create_texture_material("Juice_Yellow_Mat", None, color=[0.95, 0.75, 0.0], roughness=0.3)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.4, location=(jd_x, jd_y, jd_z + 0.5))
    jd_tank = bpy.context.active_object
    jd_tank.name = "Juice_Tank"
    jd_tank.data.materials.append(yellow_juice_mat)
    parts.append(jd_tank)

    # Dispenser lid (chrome cap)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=0.03, location=(jd_x, jd_y, jd_z + 0.71))
    jd_lid = bpy.context.active_object
    jd_lid.name = "Juice_Lid"
    jd_lid.data.materials.append(chrome_mat)
    parts.append(jd_lid)

    # 9. Join all kebab shop parts
    bpy.ops.object.select_all(action='DESELECT')
    main_shop = parts[0]
    main_shop.select_set(True)
    for p in parts[1:]:
        p.select_set(True)
    bpy.context.view_layer.objects.active = main_shop
    bpy.ops.object.join()
    main_shop.name = "Kebab_Shop"

    # Set viewport shading to MATERIAL and pack textures
    set_viewport_to_material_shading()
    try:
        bpy.ops.file.pack_all()
    except Exception as e:
        print(f"Warning: Could not pack textures: {e}")

    # 10. Export
    os.makedirs(output_dir, exist_ok=True)
    export_path_glb = os.path.join(output_dir, "kebab_shop.glb")
    export_path_blend = os.path.join(output_dir, "kebab_shop.blend")
    
    bpy.ops.export_scene.gltf(filepath=export_path_glb, export_format='GLB')
    bpy.ops.wm.save_as_mainfile(filepath=export_path_blend)
    print(f"[ASSET GENERATOR] Kebab Shop exported successfully to {export_path_glb} and saved to {export_path_blend}")


def main():
    import sys
    argv = sys.argv
    if "--" in argv:
        args_to_parse = argv[argv.index("--") + 1:]
    else:
        args_to_parse = []

    parser = argparse.ArgumentParser(description="Modular 3D asset and texture generator for GTA Vice City: Pantelimon")
    parser.add_argument("--output-dir", type=str, default="/home/vasile/.gemini/antigravity/scratch/crack/_data/blender_generated", help="Target output directory")
    parser.add_argument("--bus-texture", type=str, default="/home/vasile/.gemini/antigravity/scratch/crack/images/8170086299_2a8157c6bc_z.jpg", help="Path to bus texture image")
    parser.add_argument("--kebab-texture", type=str, default="/home/vasile/.gemini/antigravity/scratch/crack/images/IMG-20170701-WA0024.webp", help="Path to kebab shop texture image")
    parser.add_argument("--model", type=str, choices=["all", "bus", "kebab"], default="all", help="Which model to build")
    
    args = parser.parse_args(args_to_parse)

    if args.model in ["all", "bus"]:
        generate_bus(args.bus_texture, args.output_dir)
        
    if args.model in ["all", "kebab"]:
        generate_kebab_shop(args.kebab_texture, args.output_dir)

if __name__ == "__main__":
    main()

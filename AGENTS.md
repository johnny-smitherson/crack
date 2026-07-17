The game is in folder `crack_demo/demo_resolution_selector_web_bevy`.

Base rust packages are under `rust_pkg`. 

Data/asset generation and pre-procesing is in `_data`.

## Auto-generated signatures
<!-- Updated by gen-context.js -->
# Code signatures

## SigMap commands

| When | Command |
|------|---------|
| Before answering a question about code | `sigmap ask "<your question>"` |
| To rank files by topic | `sigmap --query "<topic>"` |
| After changing config or source dirs | `sigmap validate` |
| To verify an AI answer is grounded | `sigmap judge --response <file>` |

Always run `sigmap ask` (or `sigmap --query`) before searching for files relevant to a task.

## deps
```
_data/3d_data_v2/_blend_build_map.py ← mathutils, bmesh, bpy, numpy
_data/3d_data_v2/_blend_render_postprocess.py ← __future__, mathutils, bpy
_data/3d_data_v2/_blend_render_topdown.py ← __future__, mathutils, bpy
_data/3d_data_v2/_check_blend.py ← bpy, numpy
_data/3d_data_v2/osm_postprocess_batch.py ← octree, cv2, pyarrow, yolo_v8_obb_sat
```

## _data

### _data/3d_data_v2/_blend_build_map.py
```
def clear_scene()  :28-30  # Wipe the current scene so the next tile imports into a clean
def weld_terrain_mesh(obj: bpy.types.Object, dist: float) → None  :33-48
def measure_terrain_bbox() → dict  :51-81  # Compute axis-aligned bounds of all mesh objects in Blender c
def latlon_to_xy(lon: float, lat: float, latlon_bbox: dict, terrain_bbox: dict) → tuple[float, float]  :84-99  # Map lat/lon to Blender (east, north) via bilinear extrapolat
def build_terrain_bvh(terrain_objs: list[bpy.types.Object] | None) → BVHTree | None  :102-131  # Build a world-space BVH over all terrain meshes once, up fro
def raycast_hit(x: float, y: float, top: float, bvh: BVHTree | None) → tuple[float, Vector] | None  :134-135  # Cast downward from above the terrain bbox; return (hit z, hi
def raycast_height(x: float, y: float, top: float, bvh: BVHTree | None) → float | None  :148-151  # Cast downward from above the terrain bbox; return hit z or N
def resolve_heights(heights: list[float | None]) → list[float] | None  :154-178  # Fill ray-cast misses from nearest chain neighbor with a hit
def get_or_create_collection(name: str) → bpy.types.Collection  :181-186
def create_road_object(feature_id, coords_xy: list[tuple[float, float]], heights: list[float]) → bpy.types.Object  :189-192  # Create a mesh polyline named road_<feature_id> in the roads 
def resolve_corner_heights(raw_zs: list[float | None], top: float) → list[float]  :208-212  # Fill corner ray misses with the average z of the corners tha
def build_collider_mesh(corners_latlon: list[list[float]], center_latlon: list[float], latlon_bbox: dict, terrain_bbox: dict, top: float, bvh: BVHTree | None) → dict  :215-221  # Build a closed box collider molded onto the terrain, enlarge
def create_car_object(car_index: int, verts: list[tuple[float, float, float]], faces: list[list[int]]) → bpy.types.Object  :299-302  # Link a pre-built collider mesh into the cars collection
def build_fill_material(mesh: bpy.types.Object, index: int) → tuple[int, int] | None  :371-372
def cut_car_from_terrain(mesh_obj: bpy.types.Object, car_obj: bpy.types.Object, z_range: tuple[float, float], mark_mat: bpy.types.Material, n_colors: int, fill_slot: int) → tuple[int, int, list]  :589-595
def log(msg: str) → None  :774-775
def process_item(item: dict) → None  :778-904
def main()  :907-936
```

### _data/3d_data_v2/_blend_render_postprocess.py
```
def pick_render_engine() → str  :30-38
def convert_materials_to_emission() → None  :41-66  # Flatten every textured material to an unlit emission of its 
def make_cage_material() → bpy.types.Material  :69-98  # A translucent red-orange tint for the car wrappers: emission
def show_car_wrappers_as_cage() → None  :101-116  # Tint every object in the 'cars' collection translucent red s
def compute_mesh_bbox(objects) → dict | None  :119-144
def setup_world_black(scene: bpy.types.Scene) → None  :147-153
def render_blend(blend_path: str) → bool  :156-211
def main() → None  :214-230
```

### _data/3d_data_v2/_blend_render_topdown.py
```
def enable_gpu_rendering() → list[str]  :25-55  # Enable GPU compute devices for Blender rendering
def pick_render_engine() → str  :58-66
def ensure_gpu_rendering() → None  :69-74
def clear_scene() → None  :77-96
def convert_materials_to_emission() → None  :99-123
def compute_mesh_bbox() → dict | None  :126-154
def resolve_resolution(tile: dict) → tuple[int, int]  :157-161
def setup_render_settings(scene: bpy.types.Scene, *, width: int, height: int) → None  :164-187
def render_tile(tile: dict) → bool  :190-253
def main() → None  :256-287
```

### _data/3d_data_v2/_check_blend.py
```
def check_blend(blend_path: str) → None  :17-115
```

### _data/3d_data_v2/osm_postprocess_batch.py
```
def run_blender_batch(script: str, batch_json_path: str) → str  :52-80  # Run a Blender -P script over a batch JSON file, streaming it
def glb_path_for_tile(tile: str) → Path  :83-87  # Return the on-disk GLB path for an octant path (matches main
def tile_sidecar_paths(tile: str) → dict[str, Path]  :90-97
def pixel_to_latlon(px: float, py: float, meta: dict) → tuple[float, float]  :100-120  # Map render pixel to lat/lon using ortho camera + mesh-bbox a
def obb_pixel_to_latlon_corners(corners_pixel: list[list[float]], meta: dict) → tuple[list[list[float]], li...  :123-124
def node_inside_bbox(lon: float, lat: float, bbox) → bool  :133-135  # Half-open containment: south <= lat < north, west <= lon < e
def trim_road_feature(feature: dict, bbox) → dict | None  :138-175  # Keep coordinate indices inside bbox or adjacent to an inside
def has_lanes(feature: dict) → bool  :178-180
def lookup_manifest_row(manifest_dataset, tile: str) → dict | None  :183-189
def query_road_feature_ids(octtree_dataset, candidate: str) → list  :192-203
def load_road_features(features_dataset, feature_ids: list[int]) → list[dict]  :206-223
def find_roads_for_tile(tile: str, octtree_dataset, features_dataset) → tuple[str | None, list[dict]]  :226-229  # Walk up the parent chain from tile until qualifying roads ar
def build_work_item(tile: str, manifest_row: dict, road_source_path: str | None, roads: list[dict], sidecars: dict[str, Path]) → dict  :254-259
def load_sample_tiles() → list[str]  :288-290
def run_render_stage(tile_specs: list[dict]) → None  :293-307
def run_detect_stage(tile_records: list[dict], net) → None  :310-358
def run_blend_stage(items: list[dict]) → None  :361-375
def main()  :378-469
```

## crack_demo

### crack_demo/demo_resolution_selector_web_bevy/index.clouds.html
```
title: Crack! - Clouds
```

### crack_demo/demo_resolution_selector_web_bevy/src/utils/setup_debug_scene.rs
```
pub struct SetupDebugScenePlugin
pub struct DebugSceneGroundComponent
impl SetupDebugScenePlugin
```

### crack_demo/game_logic/src/worker/osm_impl.rs
```
pub async fn fetch_osm_data(args: FetchArgs) → anyhow::Result<OsmDataResult>
```

## rust_pkg

### rust_pkg/net_crackpipe/src/chat/global_chat.rs
```
pub struct GlobalChatRoomType
pub struct GlobalChatPresence
pub enum GlobalChatMessageContent
pub enum GlobalChatBootstrapQuery
pub enum MatchHandshakeType
impl GlobalChatRoomType
```

### rust_pkg/net_crackpipe/src/global_matchmaker.rs
```
pub struct GlobalMatchmaker
pub struct BootstrapNodeInfo
impl GlobalMatchmakerInner
  pub async fn shutdown(&mut self) → Result<()>
impl GlobalMatchmaker
impl GlobalMatchmaker
  pub async fn sleep(&self, duration: Duration)
  pub async fn shutdown(&self) → Result<()>
  pub fn user_secrets(&self) → std::sync::Arc<UserIdentity...
  pub fn own_node_identity(&self) → NodeIdentity
  pub fn user(&self) → UserIdentity
  pub async fn global_chat_controller(&self) → Option<ChatController<Globa...
  pub async fn bs_global_chat_controller(&self) → Option<ChatController<Globa...
  pub async fn display_debug_info(&self) → Result<String>
```

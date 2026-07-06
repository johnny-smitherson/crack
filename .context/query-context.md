# SigMap Query Context
Generated: 2026-07-06T13:07:58.984Z

## crack_demo/demo_resolution_selector_web_bevy/src/plugins/main_scene_plugin.rs
```
pub struct MainScenePlugin
pub struct SkyboxState
impl MainScenePlugin
```

## crack_demo/demo_resolution_selector_web_bevy/src/plugins/map_plugin/map_lod.rs
```
pub struct TreeMapTile
pub struct TileShouldMerge
pub struct TileShouldSplit
pub struct TileSwapRequests
pub struct PendingTileReveal
pub fn spawn_root_map_tiles(mut commands: Commands, data_res: Res<MapTree>, asset_server: Res<AssetServer>,)
pub fn recompute_lod_mark_changes(data_res: Res<MapTree>, lod_state: Res<MapLODState>, q_merge: Query<&TileShouldMerge>, q_split: Query<&TileShouldSplit>, q_pending: Query<&PendingTileReveal>, q_nodes: Query<(&TreeMapTile, Entity)
pub fn start_tile_swap_requests(mut commands: Commands, mut res_tiles: ResMut<TileSwapRequests>, asset_server: Res<AssetServer>, q_split: Query<&TileShouldSplit>, q_merge: Query<&TileShouldMerge>, data_res: Res<MapTree>,)
pub fn do_split_requests(mut commands: Commands, q_split: Query<(&TileShouldSplit, Entity)
pub fn do_merge_requests(mut commands: Commands, q_merge: Query<(&TileShouldMerge, Entity)
pub fn reveal_pending_tiles(mut commands: Commands, mut q_pending: Query<(Entity, &mut PendingTileReveal)
pub fn check_map_loaded_status(tiles_query: Query<&TreeMapTile>, lod_state: Res<MapLODState>, loading_status: Option<ResMut<crate::plugins::geojson::GameLoadingStatus>>, tooltip_state: Option<ResMut<crate::plugins::geojson::TooltipNotificationState>>, mut next_state: ResMut<NextState<InitialMapLoadFinished>>, mut osm_state: ResMut<NextState<OsmDatabaseLoadFinished>>,)
```

## crack_demo/demo_resolution_selector_web_bevy/src/plugins/map_plugin/map_plugin_ui.rs
```
pub fn draw_tree_bboxes(mut gizmos: Gizmos, data_res: Res<MapTree>, lod_state: Res<MapLODState>, tiles_query: Query<&TreeMapTile>, ui_state: Option<Res<crate::ui_egui::UiState>>,)
pub fn tree_navigator_ui(mut contexts: EguiContexts, data_res: Res<MapTree>, mut lod_state: ResMut<MapLODState>, tiles_query: Query<&TreeMapTile>, ui_state: Option<ResMut<crate::ui_egui::UiState>>,)
pub fn draw_reference_points_gizmos(mut gizmos: Gizmos, data_res: Res<MapTree>, lod_state: Res<MapLODState>, camera_query: Query<&Transform, With<Camera>>,)
```

## crack_demo/demo_resolution_selector_web_bevy/src/plugins/map_plugin/mod.rs
```
pub struct MapPlugin
pub struct MapTreeAssetInfo
pub struct BBox
pub struct MapTileAssetId
pub struct MapTreeNodePath
pub struct MapTreeNodeInfo
pub struct MapTree
pub struct MapLODState
impl MapPlugin
impl MapTileAssetId
pub fn get_octant_path(&self) → MapTreeNodePath
impl MapTreeNodePath
pub fn get_parent(&self) → Option<MapTreeNodePath>
```

## crack_demo/demo_resolution_selector_web_bevy/src/utils/setup_debug_scene.rs
```
pub struct SetupDebugScenePlugin
pub struct DebugSceneGroundComponent
impl SetupDebugScenePlugin
```

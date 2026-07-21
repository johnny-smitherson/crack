We are using bevy 0.19 - there is no more `despawn_recursive()`, just `despawn()` - when in doubt, use `cargo doc into a temp dir` and read the documentation from disk.

Check the code builds by running `cargo check --package ...` from this directory. 

When working on a binary command, you can run it with `cd ... && bash timeout 15s cargo run --bin ... --package ...` from this directory, to verify the code does not crash.

This code is supposed to be cross-platform, to work on both browser and native hosts. That means:
- do not use std::Instant::now() as it panics on wasm
- do not use threads. Intead, we will declare API routes to be used in the web worker, see `crack_demo/web_worker` for the web implementation and `crack_demo/thread_worker` for the host implementation.
- do not do heavy computation in bevy; make an async task and call into the worker using a `declare_api_method_group!` declaration

## Headless tests

`src/basic_app.rs` has `make_headless_app(title)` next to `make_basic_app`: same
memory asset source, `AssetMetaCheck::Never`, `LogPlugin` and `ClearColor`, but
`primary_window: None`, `ExitCondition::DontExit`, `RenderPlugin` with
`WgpuSettings { backends: None }` (render types + `AssetServer` stay, no GPU is
initialized) and `WinitPlugin` disabled. Do NOT insert `WinitSettings` there —
it needs an event loop. The smoke test
`main_game_survives_ten_headless_frames` in `src/main.rs` builds the full
`MainGamePlugin` on it, runs 10 `app.update()` frames and asserts a camera
exists. Run with `./test.sh` (native `cargo test` only).

Gotchas hit getting this to survive headless, worth knowing before adding new
systems:
- Driving an `App` manually (no `app.run()`) must still do what
  `bevy_app::app::run_once` does: poll `plugins_state()` until not `Adding`,
  then call `app.finish()` and `app.cleanup()` **before** the first
  `app.update()`. Skipping this breaks anything set up in a plugin's
  `finish()`/`cleanup()` phase, not just rendering.
- Systems that assume a real window/event loop must degrade instead of
  unwrapping: `update_mouse_capture` (`plugins/states/mod.rs`) bails out if
  `Query<_, With<PrimaryWindow>>::single_mut()` is `Err` (headless has no
  window entity), and `install_network_setup`
  (`plugins/network/mod.rs`) takes `Option<Res<EventLoopProxyWrapper>>` and
  skips if `None` (headless has no winit event loop, so no proxy to wake).
- avian3d's collider-tree/spatial-query/collision systems unconditionally
  require diagnostics resources (`ColliderTreeDiagnostics`,
  `SpatialQueryDiagnostics`, ...) that are otherwise inserted alongside the
  render sub-app; since `backends: None` means that sub-app never gets
  created, `make_headless_app` pre-inserts the ones actually hit via
  `init_resource`. If a new avian3d subsystem's system panics headless with
  "Resource does not exist" for another `*Diagnostics` type, add it there
  too (they're all plain `Default` timing counters, safe to pre-insert).

## Physics invariant: car-physics-hover-model

Ground response stays in clamped velocity space; no spring forces, no hit
normals, no Transform teleports.

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

## src

### src/plugins/traffic/road_graph.rs
```
pub struct TrafficRoadGraph
pub struct RoadSegment
pub enum RerouteMode
pub fn quantize(p: Vec3) → IVec2
pub fn build_road_graph(database: Res<crate::plugins::geojson::GeoJsonDatabase>, mut graph: ResMut<TrafficRoadGraph>,)
pub fn road_too_steep(points: &[Vec3]) → bool
pub fn pick_continuation(graph: &TrafficRoadGraph, node: IVec2, from_seg: usize, mode: RerouteMode,) → Option<(usize, Vec<Vec3>)>
```

### src/plugins/visual_fx/demo.rs
```
pub struct VfxDemoState
pub struct VfxDemoPlugin
pub enum DemoEffect
impl DemoEffect
  pub fn label(self) → &'static str
impl VfxDemoState
impl VfxDemoPlugin
```

### src/plugins/visual_fx/gun_fx.rs
```
pub struct GunFxEvent
pub struct GunFxCounter
pub struct GunSmokeEmitter
pub fn gun_fx_observer(trigger: On<GunFxEvent>, mut commands: Commands, time: Res<Time>, settings: Res<VfxSettings>, meshes: Option<Res<VfxMeshes>>, mut additive_mats: ResMut<Assets<AdditiveFxMaterial>>, mut blend_mats: ResMut<Assets<BlendFxMaterial>>, q_model_state: Query<&WeaponModelState>, mut q_smoke_emitter: Query<&mut GunSmokeEmitter>, counter: Option<ResMut<GunFxCounter>>,)
pub fn tick_gun_smoke_emitters(mut commands: Commands, time: Res<Time>, settings: Res<VfxSettings>, meshes: Option<Res<VfxMeshes>>, mut blend_mats: ResMut<Assets<BlendFxMaterial>>, mut q_emitters: Query<( Entity, &GlobalTransform, Option<&WeaponExtents>, &mut GunSmokeEmitter,)
```

### src/plugins/visual_fx/materials.rs
```
pub struct BillboardParams
pub struct AdditiveFxMaterial
pub struct BlendFxMaterial
pub enum FxKind
impl AdditiveFxMaterial
impl BlendFxMaterial
```

### src/plugins/visual_fx/settings.rs
```
pub struct VfxSettings
impl VfxSettings
```

### src/plugins/visual_fx/smoke_emitter.rs
```
pub struct SmokeEmitter
pub fn tick_smoke_emitters(mut commands: Commands, time: Res<Time>, settings: Res<VfxSettings>, meshes: Option<Res<VfxMeshes>>, mut blend_mats: ResMut<Assets<BlendFxMaterial>>, mut q_emitters: Query<(Entity, &GlobalTransform, &mut SmokeEmitter)
```

### src/plugins/visual_fx/spawn.rs
```
pub struct VfxLifetime
pub struct VfxDrift
pub struct VfxMeshes
pub fn spawn_additive_billboard_fx(commands: &mut Commands, mats: &mut Assets<AdditiveFxMaterial>, meshes: &VfxMeshes, time: &Time, pos: Vec3, params: BillboardParams,) → Entity
pub fn spawn_blend_billboard_fx(commands: &mut Commands, mats: &mut Assets<BlendFxMaterial>, meshes: &VfxMeshes, time: &Time, pos: Vec3, params: BillboardParams,) → Entity
pub fn despawn_expired_fx(mut commands: Commands, time: Res<Time>, q: Query<(Entity, &VfxLifetime)
pub fn tick_vfx_drift(time: Res<Time>, mut q: Query<(&mut Transform, &VfxDrift)
pub fn setup_vfx_meshes(mut commands: Commands, mut meshes: ResMut<Assets<Mesh>>)
```

### src/plugins/weapons/weapon_attach.rs
```
pub struct EquippedWeapon
pub struct EquipWeaponEvent
pub struct WeaponGripOffset
pub struct WeaponModelState
pub struct WeaponModel
pub struct PendingWeaponExtents
pub struct WeaponExtents
pub struct PendingWeaponModelFetch
pub enum WeaponKind
impl WeaponGripOffset
pub fn equip_weapon_observer(trigger: On<EquipWeaponEvent>, mut commands: Commands, transforms: Query<&GlobalTransform>,)
pub fn reconcile_weapon_model(mut commands: Commands, client: Option<Res<crate::plugins::crack_plugin::CrackClient>>, mut characters: Query<(Entity, &EquippedWeapon, Option<&mut WeaponModelState>)
pub fn poll_weapon_model_fetches(mut commands: Commands, mut q_fetches: Query<(Entity, &mut PendingWeaponModelFetch)
pub fn finalize_weapon_extents(mut commands: Commands, pending: Query<(Entity, &Children)
pub fn update_weapon_transforms(grip: Res<WeaponGripOffset>, rig: Res<CameraRig>, controlled: Res<ControlledCharacter>, camera: Query<&GlobalTransform, With<MainCamera>>, spatial: SpatialQuery, parents: Query<&ChildOf>, global_transforms: Query<&GlobalTransform>, combat_states: Query<&CombatState>, mut weapons: Query<(Entity, &mut Transform, &WeaponKind)
```

### src/plugins/weapons/weapon_manifest.rs
```
pub struct GunInfo
pub struct MeleeInfo
pub struct WeaponManifest
pub struct WeaponManifestTasks
pub enum WeaponId
impl WeaponId
  pub fn is_unarmed(&self) → bool
  pub fn is_gun(&self) → bool
  pub fn is_melee(&self) → bool
  pub fn path(&self) → Option<&str>
  pub fn rpm(&self) → f32
  pub fn automatic(&self) → bool
  pub fn gun_info(&self) → Option<&GunInfo>
  pub fn label(&self) → String
pub fn start_weapon_manifest_load(mut commands: Commands)
pub fn spawn_weapon_manifest_task(mut tasks: ResMut<WeaponManifestTasks>, manifest: Res<WeaponManifest>, client: Option<Res<crate::plugins::crack_plugin::CrackClient>>,)
pub fn poll_weapon_manifest_task(mut tasks: ResMut<WeaponManifestTasks>, mut manifest: ResMut<WeaponManifest>,)
```

### src/plugins/weapons/weapon_shooting.rs
```
pub struct GunState
pub struct WeaponCooldown
pub struct FireGunEvent
pub struct ReloadGunEvent
pub struct ShotTracer
pub struct ShotTracers
pub struct BulletSpark
pub struct BulletSparks
pub struct MeleeDebugBox
pub struct MeleeDebugBoxes
pub struct PendingMeleeHit
pub fn tick_weapon_cooldown(time: Res<Time>, mut q: Query<&mut WeaponCooldown>)
pub fn tick_reload(time: Res<Time>, mut q: Query<&mut GunState>)
pub fn draw_melee_debug_boxes(time: Res<Time>, mut gizmos: Gizmos, mut boxes: ResMut<MeleeDebugBoxes>,)
pub fn fire_gun_observer(trigger: On<FireGunEvent>, mut shooters: Query<(&mut GunState, &EquippedWeapon, Option<&WeaponModelState>)
pub fn reload_gun_observer(trigger: On<ReloadGunEvent>, mut shooters: Query<(&mut GunState, &EquippedWeapon, &GlobalTransform)
pub fn draw_shot_tracers(time: Res<Time>, mut gizmos: Gizmos, mut tracers: ResMut<ShotTracers>, settings: Res<crate::plugins::visual_fx::settings::VfxSettings>,)
pub fn draw_bullet_sparks(time: Res<Time>, mut gizmos: Gizmos, mut sparks: ResMut<BulletSparks>, settings: Res<crate::plugins::visual_fx::settings::VfxSettings>,)
pub fn tick_pending_melee_hits(mut commands: Commands, time: Res<Time>, mut query: Query<(Entity, &GlobalTransform, &mut PendingMeleeHit)
```

### src/ui_egui.rs
```
pub struct UiEguiPlugin
pub struct UiState
impl UiEguiPlugin
impl UiState
impl UiState
  pub fn with_physics_debug() → Self
impl UiState
pub fn web_set_loading_status(_show: bool, _message: &str)
```

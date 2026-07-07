# Plan: More RPC calls, parallel downloads, less log spam

Follow the map-tile RPC flow as the reference implementation. Map tiles go:
`map_lod.rs` spawns per-asset `AsyncComputeTaskPool` tasks → `client.call::<FetchMapTile>` →
worker `tile_impl::fetch_map_tile` (LRU cache + http + collider extract) → `poll_tile_group_fetches`
writes bytes to `MemoryDir` and hands `asset_server.load("memory://…")` a handle.

The GLB flows below are **identical minus the collider** (`extract_collider_data`, `collider_mesh`,
`try_trimesh`). Everything else — cache, `memory://` insert, handle load — is the same.

---

## 1. Speed up parallel downloads

Three independent bottlenecks, biggest first:

### 1a. Shared reqwest client (biggest win)
[crack_demo/game_logic/src/worker/http.rs](crack_demo/game_logic/src/worker/http.rs) calls
`reqwest::get(url)` on **every** request. That builds a fresh `Client` each time → new TLS
handshake, no connection pooling / keep-alive. Under parallel tile load this serializes badly.

- Native: add a `static CLIENT: LazyLock<reqwest::Client>` (or `once_cell`) built once with
  `Client::builder().pool_max_idle_per_host(64).build()`, and use `CLIENT.get(url)`.
- This alone should let dozens of concurrent GETs actually run in parallel.

### 1b. Raise the client-side fetch budget
[crack_demo/…/map_plugin/map_lod.rs:180-181](crack_demo/demo_resolution_selector_web_bevy/src/plugins/map_plugin/map_lod.rs#L180-L181)
`PARALLEL_SPLIT_FETCH = 3` and `PARALLEL_MERGE_FETCH = 3` cap in-flight split/merge groups. Root
tiles already fire all at once, but LOD streaming is throttled to 3. Raise to e.g. 12/8 (tune).
These are just `AsyncComputeTaskPool` tasks awaiting an RPC oneshot — they don't block the main
thread, so a higher cap is safe. Consider a single `MAX_PARALLEL_TILE_FETCH` const.

### 1c. Confirm worker concurrency (already OK, no change)
[packages/thread_crackworker/src/lib.rs:31-53](packages/thread_crackworker/src/lib.rs#L31-L53) already
`tokio::task::spawn`s each request → native worker handles calls concurrently. Web worker is
single-threaded but its `http_get_bytes` is async, so downloads still overlap. No change needed;
just noting parallelism is real once 1a lands.

---

## 2. Cut hot-loop log spam (downgrade to `debug!`/`trace!`, keep init + all warn/error)

Per-call / per-tile `info!` lines to demote:

- [packages/api_asscrack/src/api/api_client.rs:97](packages/api_asscrack/src/api/api_client.rs#L97)
  `"ApiClient: call {} took {} ms…"` — fires on every RPC. → `debug!`.
- [packages/api_asscrack/src/api/api_method_macros.rs:77](packages/api_asscrack/src/api/api_method_macros.rs#L77)
  `"Worker: API call {} took run=…"` — every call, worker side. → `debug!`.
- [crack_demo/game_logic/src/worker/tile_impl.rs:114](crack_demo/game_logic/src/worker/tile_impl.rs#L114)
  cache HIT, and [:154](crack_demo/game_logic/src/worker/tile_impl.rs#L154) fetch completed — per
  tile. → `debug!` (or drop the cache-HIT one entirely).
- [crack_demo/…/cars_driving/car_info.rs:18](crack_demo/demo_resolution_selector_web_bevy/src/plugins/cars_driving/car_info.rs#L18)
  `"loading wheel {}"` — remove (also becomes dead once §6 preloads wheels).
- Web loader/slave per-message logs in
  [packages/web_serviceworker_crackloader/src/lib.rs](packages/web_serviceworker_crackloader/src/lib.rs)
  and `web_serviceworker_crackslave/src/lib.rs` (`"GOT MESSAGE BCK!"`, `"Got App Message…"`,
  `"Sending message"`, `"reply ok."`) — demote to `debug!`.

**Keep as `info!`:** manifest fetch/build lines in
[worker/manifest_impl.rs](crack_demo/game_logic/src/worker/manifest_impl.rs) (init-only), API-group
registration in [crack_worker/api_worker.rs](packages/api_asscrack/src/crack_worker/api_worker.rs),
`CrackClient initialized`, `Parsed pedestrian manifest`, `Weapon manifest loaded`, and **all
`warn!`/`error!`**.

---

## 3. New RPC: pedestrian (character) manifest + model

### API declaration
[crack_demo/game_logic/src/api.rs](crack_demo/game_logic/src/api.rs) — add to `declare_api_group2!`:
```
(FetchPedestrianManifest, FetchArgs, crate::pedestrian::PedestrianManifestResult),
(FetchPedestrianModel,    crate::glb::FetchGlbRequest, crate::glb::FetchGlbResponse),
```
Register impls in [worker/mod.rs](crack_demo/game_logic/src/worker/mod.rs).

### New shared types
- `game_logic/src/glb.rs` (new): `FetchGlbRequest { base_url, glb_path, asset_id }` and
  `FetchGlbResponse { asset_id, glb_bytes: Vec<u8>, from_cache }` — **no collider fields**.
- `game_logic/src/pedestrian.rs` (new): `PedestrianManifestResult { urls: Vec<String>,
  animations: Vec<AnimationMeta> }` where `AnimationMeta { name, duration, frames }` carries the
  per-character animation catalog (see §5). Add `pub mod glb; pub mod pedestrian;` to `lib.rs`.

### Worker impl — `worker/pedestrian_impl.rs` (new)
- `fetch_pedestrian_manifest`: GET `{base}/3d_data/pedestrian_3d_gen/manifest.txt`, split lines into
  full URLs. Parse the **first** GLB to extract the animation catalog (mirror the client logic in
  [pedestrians/manifest.rs:118-174](crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/manifest.rs#L118-L174),
  using the `gltf` crate as `tile_impl` does). Cache result **indefinitely** in a
  `static RwLock<Option<Arc<PedestrianManifestResult>>>` like `MANIFEST_CACHE`.
- `fetch_pedestrian_model`: LRU cache (see §5, cap 50) → http GET → return raw GLB bytes, **no
  collider extraction**.

---

## 4. New RPC: weapon manifest + model

### API declaration (api.rs + worker/mod.rs)
```
(FetchWeaponManifest, FetchArgs, crate::weapon::WeaponManifestResult),
(FetchWeaponModel,    crate::glb::FetchGlbRequest, crate::glb::FetchGlbResponse),
```

### New shared types — `game_logic/src/weapon.rs` (new)
Move the CSV parsing now done client-side in
[weapons/weapon_manifest.rs:110-142](crack_demo/demo_resolution_selector_web_bevy/src/plugins/weapons/weapon_manifest.rs#L110-L142)
into the worker. `WeaponManifestResult { weapons: Vec<WeaponEntry> }` where
`WeaponEntry { path, is_gun, clip_size, bullet_type, damage, range }` (the "extra fields"). Client
maps these into its existing `WeaponId`/`GunInfo` enums.

### Worker impl — `worker/weapon_impl.rs` (new)
- `fetch_weapon_manifest`: GET `{base}/3d_data/3d_weapons/out2/manifest.txt`, parse CSV, cache
  indefinitely (static RwLock).
- `fetch_weapon_model`: LRU cache (cap 50) → http GET → raw GLB bytes, no collider. (Weapon extents
  stay a client concern — computed from the loaded mesh in `weapon_attach.rs`, unchanged.)

---

## 5. Manifest + model caching on the worker

- **Manifests** (map already does this): kept in RAM indefinitely via `static RwLock<Option<Arc<…>>>`
  — add one each for pedestrian and weapon manifests.
- **Model LRU caches**: generalize `TileCache` from
  [tile_impl.rs:11-50](crack_demo/game_logic/src/worker/tile_impl.rs#L11-L50) into a reusable
  `LruCache<FetchGlbResponse>` (or copy it). Two instances:
  - `CHARACTER_CACHE` — `max_entries = 50`
  - `WEAPON_CACHE` — `max_entries = 50`
  (Map tile cache stays at 512.) Same last-access-ms eviction.

---

## 6. Client-side plumbing (mirror `poll_tile_group_fetches`)

The pedestrian/weapon models are today loaded straight from URL via `asset_server.load(url)`
(pedestrian GLBs in `spawn_pedestrian.rs`, weapon models in `weapon_attach.rs::reconcile_weapon_model`,
first-asset in `manifest.rs`). Convert each to the RPC path:

1. Kick an `AsyncComputeTaskPool` task calling `FetchPedestrianModel` / `FetchWeaponModel`.
2. Poll it (a small `PendingGlbFetch` component + system, analogous to `PendingTileGroupFetch`).
3. On completion: `memory_dir.dir.insert_asset(memory_path, bytes)` then
   `asset_server.load(GltfAssetLabel::Scene(0).from_asset("memory://…"))` — **no collider build**.

Manifests: replace the `TextAsset`-URL bootstrap in
[pedestrians/manifest.rs](crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/manifest.rs)
and [weapons/weapon_manifest.rs](crack_demo/demo_resolution_selector_web_bevy/src/plugins/weapons/weapon_manifest.rs)
with an RPC `call` (spawn task + poll, like `manifest_flow.rs` in crack_plugin). Populate the existing
`PedestrianManifest` / `WeaponManifest` resources + `PedestrianAnimations` catalog from the RPC result
instead of parsing locally. Gate systems on `resource_exists::<CrackClient>` as the tile systems do.
`TextAsset`/`TextAssetLoader` can be removed once nothing else uses `.txt` assets.

---

## 7. Preload car wheels into a global resource

[spawn_car.rs:112-133](crack_demo/demo_resolution_selector_web_bevy/src/plugins/cars_driving/driving_plugin/spawn_car.rs#L112-L133)
calls `get_wheel_asset(...)` on every car spawn (re-`asset_server.load` + logs each time).

- Add a `#[derive(Resource)] struct WheelAssets { wheels: Vec<Handle<WorldAsset>> }` holding the two
  wheel handles (`car-wheel_00003_`, `car-wheel_00005_`).
- Populate it once at startup (a `Startup`/`OnEnter` system calling `get_wheel_asset` for both),
  `insert_resource`. Handles stay strong → always resident.
- `spawn_physics_car` takes `Res<WheelAssets>` and picks a handle from it (random index) instead of
  loading. Delete the per-spawn `tracing::info!("loading wheel …")`.
- (Optional, only if wanted) route wheels through `FetchWeaponModel`-style GLB RPC; not required —
  preloaded handles already satisfy "always keep them loaded."

---

## File-change checklist

**game_logic**
- `src/api.rs` — 4 new API entries.
- `src/worker/mod.rs` — 4 new impl registrations.
- `src/worker/http.rs` — shared lazy `reqwest::Client` (native).
- `src/glb.rs` (new), `src/pedestrian.rs` (new), `src/weapon.rs` (new); `lib.rs` `pub mod` lines.
- `src/worker/pedestrian_impl.rs` (new), `src/worker/weapon_impl.rs` (new); reusable LRU (extract
  from `tile_impl.rs`).
- Demote `tile_impl.rs` per-tile `info!`.

**api_asscrack**
- `api/api_client.rs:97`, `api/api_method_macros.rs:77` → `debug!`.

**web_serviceworker_crackloader / crackslave**
- Demote per-message `info!` → `debug!`.

**bevy app**
- `map_plugin/map_lod.rs` — raise parallel budgets.
- `pedestrians/manifest.rs`, `pedestrians/spawn_pedestrian.rs` — RPC manifest + model.
- `weapons/weapon_manifest.rs`, `weapons/weapon_attach.rs` — RPC manifest + model.
- `cars_driving/car_info.rs` — drop wheel log.
- `cars_driving/driving_plugin/spawn_car.rs` + plugin mod — `WheelAssets` resource + preload system.

## Notes / risks
- Keep collider extraction **only** on `FetchMapTile`; GLB responses carry bytes only.
- Postcard-serializing GLB bytes over the RPC pipe is already how tiles work — fine for characters
  (~small) and weapons; the LRU-50 caps bound worker RAM.
- Verify `reqwest::Client` reuse compiles on the wasm target (wasm path keeps `reqwest::get` inside
  `spawn_local`, or share a thread-local client — native is where pooling matters most).
</content>
</invoke>

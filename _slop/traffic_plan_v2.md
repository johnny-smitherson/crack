# Traffic Plugin v2 — Review + Fixes + Pedestrian Traffic + Car↔Ped Damage

Follow-up to `_slop/traffic_plan.md` / `_slop/traffic_prompt.md`. Part 1 reviews what actually
shipped against the v1 plan. Part 2 specifies the new work requested.

All paths are repo-relative under
`crack_demo/demo_resolution_selector_web_bevy/src/`.

---

## Part 1 — Review of the current implementation

The v1 plan is **fully implemented**. Files present under `src/plugins/traffic/`:
`mod.rs`, `road_graph.rs`, `spawn.rs`, `driver.rs`, `despawn.rs`, `debug_ui.rs`.

| v1 feature | State | Notes |
|---|---|---|
| `TrafficPlugin`, run-gated on `OsmDatabaseLoadFinished::OsmFinished` + `InitialMapLoadFinished::Finished` | ✅ `plugins/traffic/mod.rs:49-71` | uses `.and_then` (older bevy combinator); fine. |
| `TrafficRoadGraph` built from `GeoJsonDatabase.categories["roads"]`, `node_index` on quantized endpoints | ✅ `road_graph.rs` | endpoints quantized to 1 m grid; segments < 20 m dropped. |
| Throttled network spawner (0.1 s, `Local<f32>`), max-cars gate, radius + frustum-reject + 8 m spacing | ✅ `spawn.rs:45-123` | |
| Spawn observer: snap to nearest segment point, build path + one continuation, ground-raycast, `spawn_physics_car`, initial velocity, pedestrian driver mesh | ✅ `spawn.rs:125-279` | continuation appends exactly one connected segment then the path ends. |
| Pure-pursuit driver writing `Drive` inputs, stuck timer | ✅ `driver.rs` | |
| Despawn: end-of-path, out-of-range (×1.25), stuck (>6 s), out-of-view raycast (>4 s) | ✅ `despawn.rs` | |
| Debug UI window + road/path gizmos | ✅ `debug_ui.rs` | |

**Gaps that the new requirements target (root causes):**

1. **Stuck cars just wait to die.** `driver.rs:85-90` only accumulates `stuck_timer`;
   `despawn.rs:56-59` despawns at 6 s. No recovery.
2. **Cars despawn at their destination.** `despawn.rs:42-45` despawns the moment
   `next_idx >= path.len()`. Because the observer only appends **one** continuation segment,
   every car has a short finite path and dies at the end instead of driving on.
3. **Despawn ignores visibility for range/stuck/end cases.** Only the "out of view" branch is
   visibility-aware. Range despawn (`despawn.rs:50`) fires even while the car is on-screen.
4. **Spawn rule is "outside frustum", not "behind camera".** `spawn.rs:94-102` rejects
   in-frustum candidates but will still spawn in front of the camera just off-screen.
5. **Constants are scattered / inline** (0.1, 20.0, 8.0, 1.25, 6.0, 4.0, 0.95, …). The new work
   consolidates them.
6. **No pedestrian traffic**, **no car↔pedestrian damage**.

---

## Part 2 — New work

### 0. Shared constants module

Add a `consts` block at the top of `plugins/traffic/mod.rs` (or a new `plugins/traffic/consts.rs`
re-exported from `mod.rs`). All magic numbers below live here:

```rust
// --- spawning ---
pub const SPAWN_INTERVAL_S: f32          = 0.1;   // min time between network spawns
pub const SPAWN_MIN_CAMERA_DIST: f32     = 20.0;  // pop-in guard
pub const CAR_SPAWN_SPACING: f32         = 8.0;   // min dist to any existing car
pub const PED_SPAWN_SPACING: f32         = 4.0;   // min dist to any existing traffic ped
pub const SPAWN_BEHIND_MAX_DOT: f32      = 0.15;  // dot(cam_fwd, dir_to_point) must be < this
                                                  // (i.e. at/behind the camera side plane)
// --- despawn ---
pub const OUT_OF_RANGE_FACTOR: f32       = 1.25;  // * spawn_radius, hysteresis
pub const OUT_OF_VIEW_DESPAWN_S: f32     = 4.0;   // secs occluded/out-of-frustum before despawn
pub const VIEW_RAYCAST_HZ: f32           = 4.0;   // visibility check rate
pub const CAR_TOP_FUDGE: f32             = 0.95;  // fraction of full height for view target
// --- stuck / recovery ---
pub const STUCK_SPEED_EPS: f32           = 0.5;   // m/s below = "not moving"
pub const STUCK_TRIGGER_S: f32           = 1.5;   // secs stuck before reverse maneuver
pub const REVERSE_DURATION_S: f32        = 1.0;   // "move back 1s"
pub const STUCK_HARD_DESPAWN_S: f32      = 12.0;  // give up entirely (fallback)
// --- routing ---
pub const WAYPOINT_REACHED_XZ: f32       = 4.0;
pub const LOOKAHEAD_XZ: f32              = 8.0;
// --- pedestrian traffic ---
pub const PED_ROAD_OFFSET: f32           = 5.0;   // metres from road centre
pub const PED_WALK_SPEED: f32            = 1.6;   // informational; AI walk speed governs
// --- collision damage ---
pub const CAR_HIT_KMH_TO_DAMAGE: f32     = 1.0;   // 100 km/h -> 100 dmg
pub const CAR_HIT_MIN_KMH: f32           = 8.0;   // below this, no damage
pub const CAR_HIT_COOLDOWN_S: f32        = 0.5;   // per (car,victim) re-hit guard
```

The despawn/spawn/driver files switch to these names. This is requirement C's
"all these should go in consts".

---

### 1. Fix stuck traffic → reverse 1 s, then reroute to a random connected node

**Files:** `driver.rs`, `road_graph.rs`, `mod.rs`.

Add a recovery sub-state to `TrafficCar` (`mod.rs`):

```rust
#[derive(Default, PartialEq, Clone, Copy)]
pub enum TrafficDriveMode { #[default] Normal, Reversing(f32) } // f32 = remaining reverse secs

// on TrafficCar:
pub mode: TrafficDriveMode,
```

In `drive_traffic_cars` (change the query to `&mut CarDriveState` so we can set `is_reverse`):

- **Stuck detection** (already present): if `current_speed.abs() < STUCK_SPEED_EPS` while
  `accelerate > 0.3`, accumulate `stuck_timer`. When `stuck_timer > STUCK_TRIGGER_S` and mode is
  `Normal`, enter `Reversing(REVERSE_DURATION_S)` and reset `stuck_timer`.
- **Reversing branch:** set `drive_state.is_reverse = true`, command `Drive { accelerate: 1.0,
  brake: 0.0, steer: 0.0 }` (drives backward — see reverse handling in
  `cars_driving/driving_plugin/mod.rs:610-632`), decrement the timer by `dt`. When it hits 0:
  set `is_reverse = false`, and **reroute randomly**: call the new
  `pick_continuation(..., RerouteMode::Random)` on the car's current nearest node and replace
  `path`/`next_idx`. If no connected segment exists, snap to the nearest segment overall (linear
  scan, same as the spawn observer) and head down it. Return to `Normal`.
- **Hard fallback:** keep a `STUCK_HARD_DESPAWN_S` guard in `despawn.rs` (replaces the old 6 s)
  so a car wedged against a wall that reversing can't fix still eventually despawns.

`road_graph.rs` — extract the continuation logic (currently inline in `spawn.rs:177-201`) into a
reusable, generalized helper used by driver reroute **and** the spawn observer:

```rust
pub enum RerouteMode { ClosestAngle(Vec3 /* incoming forward dir */), Random }

/// Given the node we arrived at, the segment we came from, and a reroute mode, pick a connected
/// segment (excluding `from_seg`) and return its points oriented *away* from `node`.
pub fn pick_continuation(
    graph: &TrafficRoadGraph, node: IVec2, from_seg: usize, mode: RerouteMode,
) -> Option<(usize /*seg*/, Vec<Vec3>)>;
```

`ClosestAngle` scores each candidate by `dir_out.dot(incoming_dir)` (max wins); `Random` picks
uniformly. Orientation: if `quantize(seg.points[0]) == node` keep order, else reverse.

---

### 2. Fix traffic → never despawn at target; reroute by closest-angle node instead

**Files:** `driver.rs`, `despawn.rs`, `road_graph.rs`.

- **Remove** the end-of-path despawn (`despawn.rs:42-45`).
- In `drive_traffic_cars`, when the car has consumed most of its path
  (`next_idx >= path.len() - 1`, or the remaining path length < ~`LOOKAHEAD_XZ`), call
  `pick_continuation(graph, last_node, current_seg, RerouteMode::ClosestAngle(car_forward))`.
  Append (or replace with remaining + continuation) and keep driving. This satisfies
  "choose another node that's closest in angle to the current car forward orientation, set as
  target, go there."
- Track the car's `current_seg` index on `TrafficCar` so `pick_continuation` can exclude the
  segment it's leaving (prevents immediate U-turns). Set it in the spawn observer and update it
  on each reroute.
- **Path growth:** to avoid unbounded `Vec<Vec3>`, drop already-passed points when rerouting
  (retain from `next_idx`), so `path` stays ~2 segments long.
- If `pick_continuation` returns `None` (dead-end node with no other segment), fall back to
  reversing the current segment (turn around) rather than despawning.

Net effect: traffic wanders the road network indefinitely and only leaves via the
range/visibility rules below.

---

### 3. Fix despawn: visibility-gated, spawn strictly behind camera, spacing consts

**Files:** `despawn.rs`, `spawn.rs`, `mod.rs` (consts).

**Despawn (`despawn.rs`) — "never despawn while the camera is looking":**
Compute a single `is_visible` per car per raycast tick (frustum test + occlusion raycast, logic
already there). Then:

- Out-of-range despawn only fires when `dist > spawn_radius * OUT_OF_RANGE_FACTOR` **AND**
  `!is_visible`.
- Stuck-hard despawn (`STUCK_HARD_DESPAWN_S`) only when `!is_visible`.
- Out-of-view despawn: `out_of_view_timer > OUT_OF_VIEW_DESPAWN_S` (unchanged, already implies
  not visible).
- While `is_visible`, no despawn path is allowed to fire (reset `out_of_view_timer = 0`).
- Between raycast ticks, treat the last known `is_visible` as authoritative (store it on
  `TrafficCar`, e.g. `last_visible: bool`) so cheap per-frame range checks still respect it.

**Spawn (`spawn.rs`) — "only spawned behind the camera":**
Add an explicit behind-camera test alongside the existing frustum reject:
`let to_pt = (candidate - camera_pos).normalize_or_zero(); let cam_fwd = cam_gt.forward();`
reject candidate unless `cam_fwd.dot(to_pt) < SPAWN_BEHIND_MAX_DOT`. Keep the frustum reject as a
belt-and-suspenders check. Distance/spacing use `SPAWN_MIN_CAMERA_DIST` and `CAR_SPAWN_SPACING`
consts. (This is stricter than v1's "outside frustum" and matches "spawned behind the camera".)

---

### 4. Pedestrian traffic (new)

**New file:** `plugins/traffic/pedestrian_traffic.rs`; wire into `mod.rs`.

Reuse the existing AI pedestrian pipeline (`plugins/pedestrian_ai/`) — do **not** build a new
character. A traffic pedestrian is an ordinary `SpawnAiPedestrianEvent` ped with an extra
`TrafficPedestrian` component that drives its **Idle** behaviour toward a road path.

Components / events (`mod.rs` or the new file):

```rust
#[derive(Component)]
pub struct TrafficPedestrian {
    pub path: Vec<Vec3>,
    pub next_idx: usize,
    pub current_seg: usize,
    pub offset_sign: f32,      // +1 / -1: which side of the road centre
    pub stuck_timer: f32,
    pub out_of_view_timer: f32,
    pub last_visible: bool,
}

#[derive(Event)]
pub struct SpawnTrafficPedestrianEvent { pub position: Vec3 }
```

Add to `TrafficConfig` (`mod.rs`): `ped_enabled: bool`, `max_peds: usize` (slider 0..=100,
default 20), `ped_spawn_radius` (reuse `spawn_radius` or its own).

**Spawner** `traffic_pedestrian_spawner` (mirror `traffic_network_spawner`, own `Local<f32>`):
same behind-camera / radius / frustum rules, spacing `PED_SPAWN_SPACING` against existing traffic
peds. On a valid candidate → `commands.trigger(SpawnTrafficPedestrianEvent { position })`.

**Observer** `spawn_traffic_pedestrian_observer`:
1. Snap to nearest road segment point + build a path via the same segment-walk + `pick_continuation`
   as cars (peds share the road graph).
2. Pick `offset_sign` randomly (±1); the walked target is offset laterally
   `PED_ROAD_OFFSET` from the centreline (computed per-target at drive time, see below).
3. Ground the spawn point (`get_ground_y`, already in `spawn.rs`).
4. `commands.trigger(SpawnAiPedestrianEvent { position: offset_spawn, faction: Faction::Neutral,
   url: None /*random model*/, weapon: None /*random weapon per requirement*/ })`
   (`plugins/pedestrian_ai/spawn_ai.rs:26-34`). Faction `Neutral` so traffic peds don't
   auto-fight each other; the `WarMatrix` still lets designated hostiles engage them.
5. The AI observer spawns the controller asynchronously (adopt queue). We can't get the controller
   `Entity` back from the trigger directly, so **adopt** the traffic marker the same way
   `adopt_ai_pedestrian` works: keep a small `PendingTrafficPeds` queue of `{spawn_pos, path,
   offset_sign}` and, in a follow-up system, attach `TrafficPedestrian` to the newest
   `Added<AiPedestrian>` controller near that spawn position. (Simplest robust hook: match by
   nearest pending spawn position.)

**Idle-override steering** `drive_traffic_pedestrians`
(register in `PedestrianAiPlugin`'s Update chain **`.after(movement_ai::ai_movement)`**, or in the
traffic plugin with an explicit `.after()` on that system — ordering matters because `ai_movement`
writes `LocomotionInput.move_dir = ZERO` for `AiState::Idle`):

- Query `(&GlobalTransform, &AiState, &TrafficPedestrian, &mut LocomotionInput, &mut TrafficPedestrian)`.
- **Only act when `*state == AiState::Idle`.** For any other state (Hunt/Flee/Reposition), leave
  `LocomotionInput` untouched — the AI fully owns the ped (requirement F: "respects its AI").
- When Idle: advance `next_idx` (reached within `WAYPOINT_REACHED_XZ`), compute lookahead target,
  offset it laterally: `perp = Vec3(dir.z,0,-dir.x)`; `target += perp * offset_sign * PED_ROAD_OFFSET`.
  Set `input.move_dir = Vec2::new(d.x, -d.z)` toward the target (same convention as
  `movement_ai.rs:242-243`). This makes the idle animation become a **walk** automatically —
  `ai_animation` (`anim_ai.rs:52-64`) already picks `Walk_Loop` from `LinearVelocity`, no anim
  changes needed (requirement F: "instead of sitting still, it walks to its destination").
- Reroute at path end via `pick_continuation(ClosestAngle(walk_dir))`; reverse/random-repick if
  stuck (mirror the car logic, but "reverse" = just pick a new random connected node since peds
  don't have a gearbox).

**Despawn** `despawn_traffic_pedestrians`: same visibility-gated range/out-of-view rules as cars
(share helper logic; a traffic ped despawns the whole controller entity — its model child goes
with it). Never despawn while visible.

---

### 5. Pedestrian traffic debug controls

**File:** `debug_ui.rs`.

Extend the "Traffic Manager" window with a **Pedestrians** section:
- `ped_enabled` checkbox.
- `max_peds` slider (0..=100).
- Live label `Peds: N / max` (`Query<(), With<TrafficPedestrian>>`).
- Buttons **Spawn one ped** (random on-road point in range → `SpawnTrafficPedestrianEvent`) and
  **Despawn all peds**.
- Optional: reuse `draw_road_gizmos` to also draw ped paths (different colour).

---

### 6. Car ↔ pedestrian collision damage (proportional to speed)

**New system** `car_pedestrian_damage` in `plugins/cars_driving/driving_plugin/collision_sparks.rs`
(next to `handle_car_collisions`, which already consumes `CollisionStart`) — or a small new file
in the traffic plugin. Register in the driving plugin's Update set.

Physics note: AI/traffic pedestrian controllers use `Collider` on `GamePhysicsLayer::Car` and
collide with `[Map, Car, Wheel]` (`plugins/pedestrian_ai/spawn_ai.rs:96-103`); cars are dynamic
bodies on `GamePhysicsLayer::Car` colliding with `[Map, Car]`
(`spawn_car.rs:68-74`). So car↔ped contacts already generate `CollisionStart` events — verify at
runtime (peds have no `RigidBody`, i.e. static colliders; avian still emits events for
static/dynamic pairs).

System logic:
```
for ev in CollisionStart:
    car   = find_car_entity(collider1/body1 or collider2/body2)   // reuse helper, collision_sparks.rs:35
    victim = resolve the *other* side up its ChildOf chain to a CharacterController with Health
    if car.is_none() or victim.is_none(): continue
    let kmh = car LinearVelocity.length() * 3.6           // relative-to-ped ~ car speed (ped ~static)
    if kmh < CAR_HIT_MIN_KMH: continue
    // per (car,victim) cooldown so one impact = one hit
    if recently_hit(car, victim): continue
    let dmg = kmh * CAR_HIT_KMH_TO_DAMAGE                 // 100 km/h -> 100, 50 -> 50
    commands.trigger(DamageEvent { target: victim, amount: dmg, source: car })
```

- `DamageEvent` + `apply_damage_observer` already handle HP, death, and the death-clip pipeline
  (`plugins/pedestrian_ai/combat.rs:44-92`) — reuse them, no new death code.
- Victim resolution: walk `ChildOf` up to the entity carrying `CharacterController` + `Health`
  (same loop pattern as `combat.rs:293-302`). This covers both AI-combat peds and traffic peds
  (both are AI controllers with `Health`), and the player pedestrian too.
- Cooldown: a small `Resource` `HashMap<(Entity,Entity), f32>` (last-hit time) with
  `CAR_HIT_COOLDOWN_S`, or a `RecentlyHitBy` component on the victim. Prevents multi-fire from a
  single sustained contact.
- Damage uses car speed in km/h directly, matching the requirement (100 km/h = 100 dmg). Optional
  polish: use relative speed `(car_vel - victim_vel)` for moving victims, but ped controllers are
  ~stationary so `car_vel.length()` is fine.

---

## Part 3 — Wiring & order of implementation

`mod.rs` `TrafficPlugin::build` additions:
```rust
.add_observer(spawn::spawn_traffic_car_observer)          // existing
.add_observer(pedestrian_traffic::spawn_traffic_pedestrian_observer)   // new
.add_systems(Update, (
    road_graph::build_road_graph,
    spawn::traffic_network_spawner,
    driver::drive_traffic_cars,                 // + reverse-recovery, + reroute-at-end
    despawn::despawn_traffic_cars,              // visibility-gated
    pedestrian_traffic::traffic_pedestrian_spawner,
    pedestrian_traffic::adopt_traffic_pedestrians,
    pedestrian_traffic::despawn_traffic_pedestrians,
    debug_ui::draw_traffic_gizmos,
).chain().run_if(<same state gate>))
// idle-override must run after AI movement:
.add_systems(Update,
    pedestrian_traffic::drive_traffic_pedestrians.after(crate::plugins::pedestrian_ai::movement_ai::ai_movement))
```
Car↔ped damage: register `car_pedestrian_damage` in the driving plugin alongside
`handle_car_collisions`.

**Suggested order:**
1. Consts module + swap existing magic numbers (no behaviour change; `cargo check`).
2. `pick_continuation` in `road_graph.rs`; refactor spawn observer to use it.
3. Reroute-at-end in `driver.rs` (kills the end-of-path despawn) + remove despawn.rs end case.
4. Reverse-recovery stuck handling in `driver.rs` (+ `TrafficDriveMode`).
5. Visibility-gated despawn + behind-camera spawn.
6. Car↔ped damage system (test against existing AI peds first — easiest to observe).
7. Pedestrian traffic: components, spawner, observer + adopt queue, idle-override steering, despawn.
8. Debug UI ped section.
9. Verify in `traffic_test` binary (add hardcoded peds) and in the main game.

## Risks / notes
- **Reverse via `Drive`:** `is_reverse` is a `CarDriveState` field not carried by the `Drive`
  event; the driver system must take `&mut CarDriveState` to toggle it for the reverse maneuver
  (`mod.rs:610-632` shows reverse only affects drive direction, so setting it + `accelerate=1`
  moves the car backward).
- **Node connectivity:** `pick_continuation` relies on segments sharing quantized (1 m) endpoints.
  Real OSM data mostly does at intersections; isolated segments will dead-end → the turn-around
  fallback handles them. Same assumption the v1 continuation already made.
- **Adopt-by-position** for traffic peds is a heuristic; if two peds spawn on the same frame at the
  same point it could mis-match. Mitigate by spacing (`PED_SPAWN_SPACING`) and one-spawn-per-tick.
- **Perf:** peds are full AI controllers (perception raycasts). Cap `max_peds` low (default 20) and
  keep the same behind-camera/visibility spawn discipline as cars.
- **WASM:** no new deps; raycast counts stay bounded.

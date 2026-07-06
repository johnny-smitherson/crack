# Traffic v3 — Bugfix plan (state of investigation)

Context: v2 plan (`_slop/traffic_plan_v2.md`) was implemented in commit `8277bed` ("pedestrian
traffic") by another model. User reported 7 problems. This file records root causes found so far
+ fixes to apply. Paths relative to `crack_demo/demo_resolution_selector_web_bevy/src/`.

## Verification commands (user-requested)
```
timeout 10s cargo run --bin traffic_test   # (user wrote "traffic_sim"; actual binary is traffic_test)
timeout 10s cargo run                       # native main binary — check both for no crashes
```
Binaries present: `audio_demo, car_sim, fane, pedestrian_controller, pedestrian_v2, traffic_test, turf_war`.

---

## Problem 4 — traffic_test binary needs walking pedestrians too

**Root cause:** `bin/traffic_test.rs` does not add `PedestriansPlugin`/`PedestrianAiPlugin` (or
whatever registers `SpawnAiPedestrianEvent` observer + manifest + animations + locomotion), so
ped traffic can't spawn there. (Check what `turf_war.rs` / main game add for AI peds and mirror
the minimal set.) Add the plugin(s) to `traffic_test.rs`; ped manifest loads from network — if
offline, peds just don't appear (acceptable, same as car drivers).

---

## Deduplication (user asked to consolidate)

Currently ~4 copies of "snap to nearest segment point → orient toward longer side → append one
continuation" (spawn.rs observer ~135-201, pedestrian_traffic.rs observer ~137-185, driver.rs
reversing-fallback ~186-237, ped stuck-fallback ~319-370). And 2 near-identical
spawner-candidate loops (spawn.rs 82-132 vs pedestrian_traffic.rs 69-119), and 2 near-identical
visibility+despawn systems (despawn.rs vs pedestrian_traffic.rs despawn_traffic_pedestrians).

**Refactor into `road_graph.rs` / a new `traffic/common.rs`:**
1. `pub fn build_path_from(graph, pos: Vec3) -> Option<(usize /*seg*/, Vec<Vec3>)>` — the
   snap+orient+continuation block. Used by both observers + both stuck fallbacks.
2. `pub fn pick_spawn_candidate(graph, camera:(&Camera,&GlobalTransform), radius, min_dist,
   spacing, existing: impl Iterator<Item=Vec3>, fast_fill: bool) -> Option<Vec3>` — shared by
   car/ped spawners; `fast_fill` skips behind-camera+frustum rejects (Problem 7).
3. Common agent state: extract shared struct
   `TrafficAgentState { path, next_idx, current_seg, stuck_timer, still/out_of_view timers,
   last_visible }` embedded in both `TrafficCar` and `TrafficPedestrian`, plus
   `pub fn update_visibility(cam, spatial, root_entity, probe_point, q_parent) -> bool`
   (ancestor-walk hit test — fixes Problem 1 for both) and a shared
   `should_despawn(dist, cfg, state) -> bool`.
4. Keep two thin systems (cars vs peds) calling the shared fns — car needs `CarDriveState`
   half-height probe + Drive events; ped needs LocomotionInput + lateral offset.

## Suggested order
1. Problem 1 (visibility ancestor-walk helper) + shared despawn helper — quick, high impact.
2. Problem 2 (offset-aware waypoint advance + 1 s position-based reroute).
3. Problem 3 (melee DamageEvent) — small.
4. Problem 5 (halve run speeds) — small.
5. Problem 6 (instrument, find why CollisionStart missing, fix — maybe RigidBody on peds).
6. Problem 7 (fast-fill) folded into the dedup of the two spawners.
7. Problem 4 (traffic_test gets ped plugins).
8. Run: `timeout 10s cargo run --bin traffic_test` and main binary; check logs for crashes,
   spawn/despawn behavior, car-hit damage log line ("🚗 CAR HIT PEDESTRIAN").

## Facts verified this session (don't re-derive)
- `car_pedestrian_damage` exists at `collision_sparks.rs:316` and is registered in
  `driving_plugin/mod.rs:58`.
- Melee system plays audio only — no damage path anywhere for player melee.
- Ped offset (5 m) > waypoint-reached threshold (4 m) ⇒ ped `next_idx` can never advance.
- Despawn visibility raycast excludes only direct children ⇒ self-occlusion by nested colliders.
- AI ped spawn bundle (`spawn_ai.rs:82-107`): `Collider` + `CollisionLayers(Car, [Map,Car,Wheel])`,
  **no RigidBody**.
- Speed consts: `mod.rs:69-104` (`MOVE_ACCEL=200`, `SPRINT_MAX_MULT=3.0`, `SPRINT_RAMP_TIME=2.5`,
  `WALK_MAX_SPEED=2.2`, `JOG_MAX_SPEED=6.0`, `CROUCH_SPRINT_MULT=2.0`); cap logic
  `controller.rs:159-185`.
- `traffic_test.rs` lacks any pedestrian/AI plugins.

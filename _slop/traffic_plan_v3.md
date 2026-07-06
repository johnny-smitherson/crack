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

## Problem 1 — Cars despawn in front of the camera (must NEVER despawn while visible)

**Root cause found:** the occlusion raycast in `plugins/traffic/despawn.rs:77-91` excludes only
the car entity + its **direct** children (`q_children.get(entity)` is one level). The car's
physics colliders come from `ColliderConstructorHierarchy` on nested descendants of the
`WorldAssetRoot` child, so the camera→car_top ray hits the car's **own nested collider** →
"occluded" → `last_visible=false` → range/out-of-view despawn fires while on screen.

**Fix:** instead of exclusion lists, cast the ray and if the hit entity's `ChildOf` ancestor chain
reaches the car → visible (self-hit counts as seen). Walk-up helper identical to
`find_car_entity` pattern (`collision_sparks.rs:35-51`). Same bug exists in
`despawn_traffic_pedestrians` (`pedestrian_traffic.rs:524-538`) — ped's model is a grandchild
under the scale node. Fix both via one shared helper (see Dedup below).
Also user clarified: visible ⇒ no despawn **regardless of distance** — the range check is already
gated on `!last_visible`, which is correct once visibility is computed correctly.

## Problem 2 — Pedestrian traffic gets stuck; reroute after 1 s idle-in-place

**Root cause found:** waypoint advancement in `drive_traffic_pedestrians`
(`pedestrian_traffic.rs:374-383`) measures distance ped→**centerline** point with threshold
`WAYPOINT_REACHED_XZ = 4.0`, but the ped walks offset `PED_ROAD_OFFSET = 5.0` m from the
centerline ⇒ distance never drops below 4 ⇒ `next_idx` never advances ⇒ end-of-path reroute
never fires; ped pins at final offset target and jitters forever.

**Fix:**
- Advance `next_idx` against the **offset** waypoint (compute per-waypoint offset target), or use
  threshold `PED_ROAD_OFFSET + WAYPOINT_REACHED_XZ`.
- New stuck rule per user: track `last_pos: Vec3` + `still_timer: f32` on `TrafficPedestrian`;
  when Idle with a path and moved < ~0.3 m, accumulate; after **1.0 s** (`PED_STUCK_REROUTE_S`
  const) pick a **random** next node (`pick_continuation(..., RerouteMode::Random)`, fallback:
  nearest-segment scan) and reset. Current velocity-based detection
  (`pedestrian_traffic.rs:283-296`) has an awkward one-frame trigger and `current_seg` gets stale
  after continuations were appended — replace it.

## Problem 3 — Melee hits don't register on pedestrians (main map)

**Root cause found:** `tick_pending_melee_hits` (`plugins/weapons/weapon_shooting.rs:286-338`)
only plays **audio** on hit — it never triggers `DamageEvent`. AI-vs-AI damage lives in
`ai_combat`; the player's melee/punch path has no damage at all.

**Fix:** in `tick_pending_melee_hits`, when `is_person`, resolve the hit entity up the `ChildOf`
chain to the entity holding `Health` (same loop as `pedestrian_ai/combat.rs:293-302`) and trigger
`DamageEvent { target, amount, source }` — amount: sword `SWORD_DAMAGE`(35) when
`pending.is_melee`, else `PUNCH_DAMAGE`(12); reuse/pub the consts from `pedestrian_ai/combat.rs`.
Possibly also lengthen the 1.5 m ray slightly / start at `gt.translation()+0.5Y` is fine.

## Problem 4 — traffic_test binary needs walking pedestrians too

**Root cause:** `bin/traffic_test.rs` does not add `PedestriansPlugin`/`PedestrianAiPlugin` (or
whatever registers `SpawnAiPedestrianEvent` observer + manifest + animations + locomotion), so
ped traffic can't spawn there. (Check what `turf_war.rs` / main game add for AI peds and mirror
the minimal set.) Add the plugin(s) to `traffic_test.rs`; ped manifest loads from network — if
offline, peds just don't appear (acceptable, same as car drivers).

## Problem 5 — Player + pedestrians run too fast → cap at 1/2 current speed

Speed lives in `plugins/pedestrians/pedestrian_controller_plugin/mod.rs`:
- `SPRINT_MAX_MULT: f32 = 3.0` (sprint ramps 2×→3× JOG_SPEED; `apply_speed_cap` in
  `controller.rs:159-185` uses `JOG_SPEED * (2.0 + (SPRINT_MAX_MULT - 2.0) * t)`)
- `JOG_MAX_SPEED = 6.0`, `WALK_MAX_SPEED = 2.2`, `CROUCH_SPRINT_MULT = 2.0`, and `JOG_SPEED`
  (grep it — near mod.rs:69-104).

**Fix:** halve the **run** ceiling: sprint formula becomes `JOG_SPEED * (1.0 + (1.5-1.0)*t)`
(i.e. halve both ends: 2.0→1.0, SPRINT_MAX_MULT 3.0→1.5), or simply halve `JOG_SPEED` and
`SPRINT_MAX_MULT` factors so max run speed = ½ current. Applies to both player and AI (shared
`apply_speed_cap`), matching "both the player and the pedestrians". Also update anim thresholds
if they key off speed (`anim_ai.rs` WALK_MAX_SPEED=2.2/JOG_MAX_SPEED=6.0 and the player driver)
so clips still map sensibly.

## Problem 6 — Car→pedestrian damage not detected

`car_pedestrian_damage` IS registered (`driving_plugin/mod.rs:58`) and logic looks right
(walks `ChildOf` to `CharacterController`, checks `Health`, cooldown, kmh threshold 8).
**Not yet diagnosed.** Prime suspects to check next:
1. Ped controllers have a bare `Collider` **without `RigidBody`** (`spawn_ai.rs:82-107`) — avian
   may not emit `CollisionStart` for dynamic-vs-static-collider pairs unless the static entity
   has a `RigidBody::Static`; ALSO the car controller does velocity-space movement and
   `move_and_slide` (peds) does manual resolution — verify events actually fire (add temp log /
   run turf_war and drive into a ped).
   Likely fix: insert `RigidBody::Static` (or `RigidBody::Kinematic`) on the AI ped controller,
   OR use avian `CollidingEntities`, OR replace event-based detection with a shape/distance test
   from the car system.
2. Player pedestrian collision layers differ from AI peds — check both.
3. `CollisionStart` reader timing vs `.chain()` ordering — less likely.
Note `DamageEvent`/`apply_damage_observer` handles death fine once triggered (melee fix proves path).

## Problem 7 — Fast refill to 40% of max

If `count < 0.4 * max` (cars or peds independently): spawn **one per frame** (bypass
`SPAWN_INTERVAL_S` throttle AND the behind-camera + frustum rejects) at a random road point
within `spawn_radius` of the camera (keep `SPAWN_MIN_CAMERA_DIST` + spacing checks). Const
`FAST_FILL_FRACTION: f32 = 0.4` in `traffic/consts.rs`. Implement inside both spawners as an
early "fast-fill mode" flag that relaxes the candidate filters.

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

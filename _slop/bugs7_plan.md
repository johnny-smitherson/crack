# Bugs6 follow-up fixes

## Context

The `bugs6_plan.md` items were implemented in commit `afd9148 sloopybugs6`, but a
play-through shows several of them are broken or regressed. This plan fixes the four
reported problems (plus their root causes found during review).

## Findings (root causes)

1. **Sound still broken.** `_data/sound_data/sound-fx2/manifest.txt` lists only file
   paths — no `attenuation`/`volume` columns — so `load_sound_manifest_system`
   ([audio/mod.rs:179-186](crack_demo/demo_resolution_selector_web_bevy/src/plugins/audio/mod.rs#L179))
   always defaults `attenuation = 1.0`. Both the old (`1.0/attenuation`) and the
   "fixed" (`attenuation.max(0.1)`) `scale_factor` therefore evaluate to `1.0`. Bevy
   0.19 multiplies **both** emitter and listener positions by this scale
   (`bevy_audio-0.19 audio_output.rs`), so `scale=1.0` means audio distance == world
   metres and rodio's `~1/distance` attenuation kills sounds past a few metres.

2. **Car passengers explode / float.** `spawn_ai_pedestrian_observer`
   ([pedestrian_ai/spawn_ai.rs:69-91](crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrian_ai/spawn_ai.rs#L69))
   spawns passengers with the full `character_physics_bundle` (a kinematic
   `CharacterController` capsule on the `Car` collision layer) and parents them to the
   dynamic car. The capsule overlaps the car collider (both on `Car` layer) → physics
   explosion; move-and-slide integrates them in world space while parented → they
   drift/float. The existing `DriverMesh` seat pattern (physics-less visual model
   parented at a car-local offset) is the correct approach.

3. **Pedestrian aim camera too high / wrong shoulder.** `CAM_LOOK_HEIGHT` was raised to
   `1.5`, applied on top of the capsule-center translation (~0.85 m above feet) → the
   look/anchor point sits ~2.35 m up, above the head. Aim shoulder offset is positive
   (screen right); user wants a lower, tighter, **left**-shoulder aim like GTA.

4. **Car camera low + driveby dead.** `camera_follows_car`
   ([camera_follow.rs:39](crack_demo/demo_resolution_selector_web_bevy/src/plugins/cars_driving/driving_plugin/camera_follow.rs#L39))
   centers only `1.5 m` above the car with a shallow 15° pitch. `apply_arm_ik` aims the
   seated driver's arm while `DrivingCar`, but **no system triggers `FireGunEvent`**
   in that state, so aiming out of the car never produces a shot.

## Fixes

### 1. Sound (audio/mod.rs)
- Treat `attenuation` as "audible reference distance in metres" and revert the formula
  to inverse: `let scale_factor = 1.0 / ev.attenuation.max(0.1);`
  ([mod.rs:214](crack_demo/demo_resolution_selector_web_bevy/src/plugins/audio/mod.rs#L214)).
- Change the missing-column default from `1.0` to a gameplay range (e.g. `45.0`) in
  `load_sound_manifest_system`
  ([mod.rs:182](crack_demo/demo_resolution_selector_web_bevy/src/plugins/audio/mod.rs#L179)),
  giving `scale ≈ 0.022` → sounds audible ~45 m. (Per-sound tuning can later be added
  as optional `path,attenuation,volume` manifest columns — parsing already supports it.)

### 2. Car passengers → seated visual meshes (no physics)
Replace the physics-capsule passenger with a `DriverMesh`-style seated model:
- In `spawn_car_request_event_observer`
  ([spawn_car.rs:247-262](crack_demo/demo_resolution_selector_web_bevy/src/plugins/cars_driving/driving_plugin/spawn_car.rs#L247)),
  for each non-driver seat spawn a **visual-only** pedestrian model parented to the car
  at `CAR_SEAT_OFFSETS[seat_idx]` (rotated 180° like the driver), with `EquippedWeapon`
  + `GunState` equipped, and a `CarPassenger { seat_index, car }` marker — reusing the
  `SpawnPedestrianEvent` + weapon-equip path but **without** `character_physics_bundle`.
- Drop the `car_seat` branch that builds a `CharacterController` in
  `spawn_ai_pedestrian_observer`; passengers are no longer AI capsules. Keep the plain
  `SpawnAiPedestrianEvent` path (no `car_seat`) for normal ground spawns.
- Give seated passenger meshes their own seat-anim + (optional) driveby behavior in
  the driver-mesh systems, so they ride along cleanly instead of colliding.

### 3. Pedestrian camera (mod.rs constants + camera.rs)
Decision: **all cameras over the RIGHT shoulder, all the time** (no side-swap on aim).
- Lower `CAM_LOOK_HEIGHT` to ~`0.6` (look/anchor ≈ 1.45 m above feet — chest/head).
- Add a dedicated **aim** look height (~`0.5`) and use it when `rig.aiming`, so the aim
  camera drops to shoulder height instead of floating above the head (fixes "very high up").
- Keep `CAM_SHOULDER_X` and `CAM_AIM_SHOULDER_X` on the **same (right) side** with the
  same sign so the shoulder never flips; keep the tighter `CAM_AIM_DISTANCE`. Verify in
  the running app that the positive sign is screen-right; flip if not.

### 4. Car camera + driveby
- Raise `camera_follows_car` center to ~`car + 2.6 Y` and pitch to ~`20°`
  ([camera_follow.rs:39,46](crack_demo/demo_resolution_selector_web_bevy/src/plugins/cars_driving/driving_plugin/camera_follow.rs#L39)).
- Add a `driveby_fire` system running `in_state(DrivingCar)` that, on LMB (respecting
  `automatic()`/cooldown/ammo), triggers `FireGunEvent { shooter: driver_model }` for
  the seated `DriverMesh` that owns the active car — mirroring the gun logic in
  `drive_character_animation`. Add a crosshair while driving. This makes the arm-IK aim
  actually fire. Decision: **only the player driver fires** on LMB; passengers stay armed
  but passive (no passenger AI firing).

## Verification
Run the native app (`cargo run` in `crack_demo/demo_resolution_selector_web_bevy`,
unset `ARGV0` if launched from the Cursor AppImage) and:
- Click ground in the audio demo / fire a gun — sound audible across tens of metres.
- Right-click → Car: passengers sit still in seats, car does not explode.
- On foot, hold RMB — aim camera stays over the right shoulder (same side as the normal
  follow) at shoulder height, not floating above the head.
- Enter a car, hold RMB + LMB — driver's arm extends and the gun fires (driveby); camera
  sits higher above the car.
- `cargo check` clean.

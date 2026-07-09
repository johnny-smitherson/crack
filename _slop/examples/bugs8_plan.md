# Bugs6 follow-up: over-the-shoulder camera + in-car weapon UI

## Context

The first bugs6 round (sound distance, seated-passenger physics, raised car chase-cam,
`driveby_fire`) is implemented and compiles clean. A play-through leaves **two** problems:

1. **Camera is dead-centre, not over the shoulder** — both the normal follow camera and the
   RMB aim camera frame the pedestrian in the exact middle of the screen (see screenshot).
   The shoulder offset produces no visible effect.
2. **No in-car weapon UI** — while driving there is no weapon-selector wheel and no top-left
   weapon/ammo HUD, so you can't see or change the gun you drive-by with. The on-foot
   `weapon_wheel` + `weapon_hud_ui` only run in `ControllingPedestrian` on
   `controlled.controller`, which is `None` while driving.

## Root cause — camera

In `follow_camera`
([camera.rs:137-158](crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/pedestrian_controller_plugin/camera.rs#L137))
the `shoulder_offset` is added to the camera **anchor/position** but **not** to the
`look_at` target:

```rust
let anchor = pos_target + Vec3::Y * look_height + shoulder_offset;   // position shifted right
...
cam.look_at(look_pos + Vec3::Y * look_height, Vec3::Y);              // look target NOT shifted
```

Because the camera is shifted ~0.8 m right but then aimed back at the un-shifted character
centre, it "toes in" and re-centres the character in frame — the offset cancels out visually.
Over-the-shoulder framing needs a **parallel** shift: the same `shoulder_offset` applied to
the look target too, so the whole frustum slides right and the character sits on the left of
the frame.

## Fixes

### 1. Over-the-shoulder camera (camera.rs)
- Add `shoulder_offset` to the look target so the shift is parallel, not toe-in:
  `cam.look_at(look_pos + Vec3::Y * look_height + shoulder_offset, Vec3::Y);`
  ([camera.rs:158](crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/pedestrian_controller_plugin/camera.rs#L158)).
- This makes both the normal (`CAM_SHOULDER_X = 0.8`, distance 4 m → ~11° off-centre) and the
  aim (`CAM_AIM_SHOULDER_X = 0.5`, distance 1.5 m → ~18° off-centre) cameras visibly sit off
  the **right** shoulder. Both offsets keep the same positive sign, so the camera never swaps
  shoulders (per the earlier decision "all cameras over the right shoulder all the time").
- Verify in-app that positive X reads as screen-right; if it reads left, flip the sign of
  `CAM_SHOULDER_X` / `CAM_AIM_SHOULDER_X` in
  [mod.rs:144-145](crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/pedestrian_controller_plugin/mod.rs#L144).
  (Tune magnitudes up slightly only if the offset still reads too subtle after the parallel-
  shift fix.)

### 2. In-car weapon wheel + HUD (interaction_ui.rs + mod.rs)
Add two driving-state systems that mirror the on-foot `weapon_wheel` / `weapon_hud_ui`
([interaction_ui.rs:719-885](crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/pedestrian_controller_plugin/interaction_ui.rs#L719))
but target the seated **`DriverMesh`** of the `ActivePlayerVehicle` instead of
`controlled.controller`. The driver mesh already carries `EquippedWeapon` + `GunState`
(copied in `tick_entering_car`) and has the skeleton the weapon attaches to, so the existing
`equip_weapon_observer` + `reconcile_weapon_model` swap the `GunState` (fresh clip) and the
attached gun model automatically — no new attach logic needed.

- **`driving_weapon_wheel`** — copy of `weapon_wheel` with the same debounce (`0.15 s` via a
  `Local<f32>`) and the shared `WeaponSelection` resource, but resolve the target entity as
  `q_driver.iter().find(|(d, ..)| d.car == active_car)` and trigger
  `EquipWeaponEvent { character: driver_ent, weapon: manifest.all[selection.index] }`.
  Reuses `WeaponManifest`, `WeaponSelection`, `MouseWheel`, `EquipWeaponEvent`.
- **`driving_weapon_hud_ui`** — copy of `weapon_hud_ui` drawing the same top-left green weapon
  name + `rounds/clip_size` (+ HP) block, reading `EquippedWeapon`/`GunState`/`Health` from the
  active car's `DriverMesh` (query `q_driver: Query<(&DriverMesh, &EquippedWeapon, Option<&GunState>, &Health)>`).
- Register both in `PedestrianControllerPlugin`
  ([mod.rs](crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/pedestrian_controller_plugin/mod.rs)):
  `driving_weapon_wheel.run_if(in_state(GameControlState::DrivingCar))` in the normal Update
  set (next to `driveby_fire`), and `driving_weapon_hud_ui.run_if(in_state(DrivingCar))` in the
  `EguiPrimaryContextPass` set (next to `driving_crosshair_ui`). Add both to the
  `use interaction_ui::{...}` import.

Note: `driveby_fire` already guards `over_ui` and reload; the mouse-wheel switch will not
conflict with LMB fire. `WeaponSelection.index` is shared with the on-foot wheel and is
re-synced by `equip_on_new_character` on exit, so cycling in the car and then leaving behaves
correctly.

## Verification
Run the native app (`cargo run` in `crack_demo/demo_resolution_selector_web_bevy`; unset
`ARGV0` if launched from the Cursor AppImage) and:
- On foot: character sits on the **left** of the frame with empty space over the right
  shoulder, both normally and while holding RMB (aim drops to shoulder height, tighter, still
  right shoulder — not centred, not above the head).
- Enter a car: top-left shows the weapon name + `rounds/clip` HUD; mouse wheel cycles weapons
  (debounced) and the held gun model swaps; LMB drive-by fires the selected gun.
- `cargo check` clean.

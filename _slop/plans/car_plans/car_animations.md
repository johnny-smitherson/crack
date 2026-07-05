# Car Animations & Enter/Exit Implementation Plan

## Goal
Implement seamless transitions between pedestrian control and car driving. This involves detecting nearby cars, despawning the pedestrian physics controller, playing "enter/exit" animations, attaching the mesh to the car, and allowing the player to regain pedestrian control upon exiting.

## Open Questions
- What are the names/indices of the "enter car", "driving loop", and "get out of car" animations within the character GLTF?
- Should the despawned pedestrian retain state (health, weapons) on an invisible entity, or is it fully recreated upon exiting the car?

## Proposed Changes

### `crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/pedestrian_controller_plugin/interaction_ui.rs` (or similar interaction module)
- **Enter Car Detection**:
  - **[MODIFY]**: Add a system that runs when the player presses `f`.
  - Use a spatial query or crosshair raycast to check if the player is looking at a `Car` entity within a 1m radius.
  - If true, trigger a custom `EnterCarEvent { car_entity, pedestrian_entity }`.

### `crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/pedestrian_controller_plugin/mod.rs` (or a dedicated `car_transition.rs` module)
- **Enter Car Workflow**:
  - **[NEW]**: System `handle_enter_car`.
  - Upon receiving `EnterCarEvent`, transition the player mesh animation state to "enter car / sit down".
  - Despawn the player's `CharacterController`, rigid body, and colliders to remove physics interactions.
  - Parent the player mesh to the target `Car` entity.
  - Wait for the "enter car" animation to finish, then switch to the "driving loop" animation.
  - Add the `CarDriveState` active marker to the car so the player inputs now drive the car instead of the pedestrian.
- **Exit Car Workflow**:
  - **[NEW]**: System `handle_exit_car`.
  - When controlling a car and `f` is pressed, trigger `ExitCarEvent`.
  - Remove player control from the car.
  - Play the "get out of car" animation on the attached mesh.
  - Animate moving the mesh out of the car bounding box.
  - Once out, despawn the mesh from the car and fire a spawn event for a fully controllable pedestrian at the exit location.

### `crack_demo/demo_resolution_selector_web_bevy/src/ui_egui.rs` (or an in-car specific UI module)
- **Debug Offset Menu**:
  - **[NEW]**: Create an EgUi window accessible only when the player is inside the car (e.g., under a "Debug" category menu button).
  - Add sliders to control the X, Y, Z offset of the parented player mesh relative to the car to perfectly align the sitting animation with the car seat.

## Verification Plan
1. Start `fane` or the main game binary.
2. Walk up to a car, look at it, and press `f` (must be within 1m).
3. Verify the player enters the car, sits down, and gains driving control.
4. Open the debug menu, verify the sliders move the character inside the car.
5. Press `f` to exit the car. Verify the exit animation plays and the player regains ground movement.

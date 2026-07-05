# Car Physics Implementation Plan

## Goal
Revamp the car physics system to replace the current scattered raycast-based hovering approach with a more structured grid-based approach. The overall method (calculating distance and ground contact rather than using full physics wheel springs) remains but will be improved for stability and accuracy. We'll also update the user interface and input responsiveness.

## Open Questions
- What default tuning values should be used for the new sliders before we allow user adjustment?
- Which specific part of the car's model bounds (min/max Y) should the 5% offset be calculated against?

## Proposed Changes

### `crack_demo/demo_resolution_selector_web_bevy/src/plugins/cars_driving/driving_plugin/mod.rs`
- **Ray Generation (`update_wheel_contact_normals`)**:
  - **[MODIFY]**: Change the current random distribution of 8 rays per wheel to a fixed grid distribution.
  - **[MODIFY]**: Update the origin points of the rays. Instead of starting from a hardcoded `wheel_y_offset`, start the rays from about 5% higher than the car's minimum Y bounds (in local space). The rays should extend downwards in local space for a total distance of 0.5m.
  - **[MODIFY]**: Restrict the ray grid surface area. Currently, it acts as a full rectangular block. The middle of the car should not have wheel contact area. Restrict the grid to run from the wheel position up to 75% of the distance towards the middle of the car.
- **Traction Logic (`apply_car_steering_and_drive`)**:
  - **[MODIFY]**: Add a check: if traction (contact distance <= 1.0m or defined max suspension) is not achieved on at least 2 out of the 4 wheels, do not apply driving or steering forces. Instead, allow the car to coast/fly based purely on Avian3D physics rules.
- **Input Responsiveness (`car_drive_observer`)**:
  - **[MODIFY]**: Reduce the input integration/averaging period. Currently, `drive_state.history` retains inputs over a 0.2s window, making driving feel laggy. Change this threshold to `0.060s` for tighter response times. Find other smoothing averages and reduce their periods proportionally.
- **Gizmos (`draw_car_gizmos`)**:
  - **[MODIFY]**: Ensure `draw_car_gizmos` is re-enabled in the car simulation binary, specifically visualizing the new grid-based raycasts.

### `crack_demo/demo_resolution_selector_web_bevy/src/plugins/cars_driving/driving_plugin/spawn_car.rs`
- **Car Model Loading**:
  - **[MODIFY]**: Hook into the GLTF loading phase for the car mesh. Once the mesh is loaded, iterate through its vertices to compute the exact bounding box (min/max on X, Y, Z). Store this bounding box data in a component on the car entity, which will be read by the raycast logic to set the correct 5% offset from the bottom.

### `crack_demo/demo_resolution_selector_web_bevy/src/plugins/cars_driving/driving_plugin/speedometer_ui.rs`
- **UI Updates**:
  - **[MODIFY]**: Update the EgUi overlay. Read the `engine_rpm` from the `CarDriveState` component and display it as a numerical value alongside the current gear. The font size for the RPM should be 50% smaller than the main gear/speed font.

### Egui Sliders / Tuning
- **[MODIFY]**: Remove old suspension sliders and replace them with new, user-tunable physics values (e.g., Grid width, offset, traction loss threshold, etc.).

## Verification Plan
1. Launch `car_sim` binary.
2. Verify rays are drawn as grids under the wheels, not randomly.
3. Check the UI for the new RPM number.
4. Drive the car off a ramp or ledge to ensure it loses driving force when < 2 wheels are grounded.

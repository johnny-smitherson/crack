# Cosmetic Wheels Implementation Plan

## Goal
Procedurally place and animate cosmetic wheels on the cars. These wheels serve no physics purpose; they exist purely to make the cars look grounded and functional based on the physics engine's underlying calculations.

## Open Questions
- Is there a specific GLTF asset we should use for the simple cylinder wheel, or should we spawn a raw Bevy cylinder primitive?
- What debug texture path should be applied to the wheels?

## Proposed Changes

### `crack_demo/demo_resolution_selector_web_bevy/src/plugins/cars_driving/driving_plugin/mod.rs` (or a new module `cosmetic_wheels.rs`)
- **Cosmetic Wheel Components**:
  - **[NEW]**: Create a component `CosmeticWheel { wheel_idx: usize, parent_car: Entity }` to track individual wheels.
- **System: `update_cosmetic_wheels`**:
  - **[NEW]**: Add a new system to the `Last` schedule (to ensure it runs after all physics and transform updates).
  - This system will query for `CosmeticWheel` and `Transform`, reading the associated `CarDriveState` and `CarWheelsContactData` from the `parent_car`.
  - **Position**: Compute the visual position using the car's orientation and the hit points/surface contact normal from the physics raycasts.
  - **Rotation**: Read the car's linear velocity and the wheel's radius to compute how fast the wheel should rotate visually around its local X-axis. Also apply steering rotation around the Y-axis for the front wheels based on `drive_state.current_steer_integrated`.

### `crack_demo/demo_resolution_selector_web_bevy/src/plugins/cars_driving/driving_plugin/spawn_car.rs`
- **Spawning Wheels**:
  - **[MODIFY]**: When spawning a new `Car`, also spawn 4 child entities representing the cosmetic wheels.
  - Apply a basic Bevy cylinder mesh (`shape::Cylinder` equivalent) oriented appropriately, painted with a black/white debug texture. Ensure they do not have any physics colliders attached.

## Verification Plan
1. Launch the `car_sim` binary.
2. Drive the car and observe the wheels.
3. Verify the wheels visually spin matching the car's forward velocity.
4. Verify the front wheels turn left and right according to steering input.
5. Ensure wheels follow the ground contour based on ray hits, even when the car chassis tilts.

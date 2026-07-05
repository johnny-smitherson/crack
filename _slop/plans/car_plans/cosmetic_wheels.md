# Cosmetic Wheels Implementation Plan

## Goal
Procedurally place and animate cosmetic wheels on the cars. These wheels serve no physics purpose; they exist purely to make the cars look grounded and functional based on the physics engine's underlying calculations.

## Open Questions
- Is there a specific GLTF asset we should use for the simple cylinder wheel, or should we spawn a raw Bevy cylinder primitive?
  -> actually i added two new wheels. On spawn they are scaled to 60% of their original size and placed in their correct place. The wheel axis is pointing towards +Y in blender, which in bevy means either -Z or +Z, take a guess.
  -> the models are these: _data/3d_data/3d_slop_models_clean/cars/car-wheel_00003_.glb and _data/3d_data/3d_slop_models_clean/cars/car-wheel_00005_.glb - keep them in a rust list next to the car paths, and pick one tyre set randomly to use in whole car when we spawn the car.
  
- What debug texture path should be applied to the wheels?
  -> no need anymore, they will be handled by the glb list

## Proposed Changes

### `crack_demo/demo_resolution_selector_web_bevy/src/plugins/cars_driving/driving_plugin/mod.rs`

#### Cosmetic Wheel Components
**Explanation**: We will introduce a new component that links a spawned cosmetic visual entity to a specific "corner" (wheel index) of the parent car. It tracks accumulated visual rotation over time.
**Invariants**: The `wheel_idx` must strictly map to `0=FL`, `1=FR`, `2=RL`, `3=RR` to correctly pair with the physics data arrays.
```rust
#[derive(Component)]
pub struct CosmeticWheel {
    pub wheel_idx: usize, // 0: FL, 1: FR, 2: RL, 3: RR
    pub parent_car: Entity,
    pub accumulated_rotation: f32,
}
```

#### System: `update_cosmetic_wheels`
**Explanation**: This system runs late in the Bevy schedule (e.g., `PostUpdate`) to read the physics state from the car, compute rotation speed based on linear velocity and wheel radius, apply steering rotation for front wheels, and position the wheel mesh at the average hit point of the raycast grid.
**Invariants**: The system must run strictly *after* the physics solver updates the car's transform, otherwise the wheels will lag behind the chassis by one frame.
```rust
pub fn update_cosmetic_wheels(
    time: Res<Time>,
    q_car: Query<(&Transform, &CarDriveState, &CarWheelsContactData, &LinearVelocity), With<Car>>,
    mut q_wheels: Query<(&mut Transform, &mut CosmeticWheel), Without<Car>>,
) {
    let dt = time.delta_secs();
    
    for (mut wheel_transform, mut cosmetic_wheel) in q_wheels.iter_mut() {
        if let Ok((car_transform, drive_state, contact_data, car_vel)) = q_car.get(cosmetic_wheel.parent_car) {
            let wheel_idx = cosmetic_wheel.wheel_idx;
            let wheel_data = &contact_data.wheels[wheel_idx];
            
            // Math: Compute visual rotation based on car velocity
            let forward_speed = car_vel.dot(car_transform.forward());
            // Circumference = 2 * PI * radius. Rotational velocity = speed / radius
            let angular_velocity = forward_speed / drive_state.wheel_radius;
            cosmetic_wheel.accumulated_rotation += angular_velocity * dt;
            
            // Determine Steering (Front wheels only: 0 and 1)
            let steer_angle = if wheel_idx < 2 {
                drive_state.current_steer_integrated * (1.2 / (1.0 + 0.3 * forward_speed.abs())) // Match apply_car_steering_and_drive logic
            } else {
                0.0
            };
            
            // Build the local rotation:
            // 1. Turn wheel left/right (Y axis)
            // 2. Spin wheel forward/back (X axis)
            let rotation = Quat::from_axis_angle(Vec3::Y, steer_angle) * 
                           Quat::from_axis_angle(Vec3::X, cosmetic_wheel.accumulated_rotation);
            
            // Position interpolation (average of engaged ray hits)
            let mut valid_hits = 0;
            let mut avg_hit = Vec3::ZERO;
            for (i, &dist) in wheel_data.ray_distances.iter().enumerate() {
                if dist <= 1.0 {
                    avg_hit += wheel_data.hit_points[i];
                    valid_hits += 1;
                }
            }
            
            let world_pos = if valid_hits > 0 {
                (avg_hit / valid_hits as f32) + (wheel_data.contact_normal * drive_state.wheel_radius)
            } else {
                // Default suspension hang position
                let origin = wheel_data.ray_origins[0]; // simplify
                origin - (car_transform.up() * 1.0)
            };
            
            wheel_transform.translation = world_pos;
            wheel_transform.rotation = car_transform.rotation * rotation;
        }
    }
}
```

### `crack_demo/demo_resolution_selector_web_bevy/src/plugins/cars_driving/driving_plugin/spawn_car.rs`

#### Spawning Wheels
**Explanation**: When a car is initially requested and built, we must also instantiate 4 cylinder primitives as independent entities (or children) with the `CosmeticWheel` component so they can be driven by the system above.
**Invariants**: The meshes must *not* have Avian3D rigid bodies or colliders attached, as they are purely visual markers.
```rust
// After spawning the car entity `car_entity`
let wheel_mesh = meshes.add(Cylinder::new(0.45, 0.35)); // radius, height
let wheel_mat = materials.add(StandardMaterial {
    base_color_texture: Some(asset_server.load("textures/debug_checkerboard.png")),
    ..default()
});

for i in 0..4 {
    commands.spawn((
        PbrBundle {
            mesh: wheel_mesh.clone(),
            material: wheel_mat.clone(),
            ..default()
        },
        CosmeticWheel {
            wheel_idx: i,
            parent_car: car_entity,
            accumulated_rotation: 0.0,
        },
    ));
}
```

## Verification Plan
1. Launch the `car_sim` binary.
2. Drive the car and observe the wheels.
3. Verify the wheels visually spin matching the car's forward velocity.
4. Verify the front wheels turn left and right according to steering input.
5. Ensure wheels follow the ground contour based on ray hits, even when the car chassis tilts.

# Car Animations & Enter/Exit Implementation Plan

## Goal
Implement seamless transitions between pedestrian control and car driving. This involves detecting nearby cars, despawning the pedestrian physics controller, playing "enter/exit" animations, attaching the mesh to the car, and allowing the player to regain pedestrian control upon exiting.

## Open Questions
- What are the names/indices of the "enter car", "driving loop", and "get out of car" animations within the character GLTF?
  -> use bash + blender script to look at the first glb file and read its animations by printing there. 
- Should the despawned pedestrian retain state (health, weapons) on an invisible entity, or is it fully recreated upon exiting the car?
  -> it will be fully recreated when exiting car, that will be simpler and more robust - we can send a new event to spawn pedestrian as stated earlier. 

## Proposed Changes

### Core Event Structs
**Explanation**: We define discrete Bevy events to handle the hand-off. One to signal a pedestrian is claiming a car, and another to signal a driver is abandoning the car.
**Invariants**: Events must only fire if the conditions are met (e.g., proximity). Handlers must gracefully ignore events if the referenced entities no longer exist.
```rust
#[derive(Event)]
pub struct EnterCarEvent {
    pub car_entity: Entity,
    pub pedestrian_entity: Entity,
}

#[derive(Event)]
pub struct ExitCarEvent {
    pub car_entity: Entity,
}
```

### `crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/pedestrian_controller_plugin/interaction_ui.rs`

#### Enter Car Detection
**Explanation**: A system that checks if the 'F' key is pressed while the player controls a pedestrian. It iterates over all spawned cars and fires the entry event if the nearest car is within a 1.0-meter interaction radius.
**Invariants**: Ensure that crosshair interactions do not inadvertently select cars through walls. Distance must be calculated linearly.
```rust
pub fn detect_car_interaction(
    keys: Res<ButtonInput<KeyCode>>,
    q_player: Query<(Entity, &GlobalTransform), With<CharacterController>>,
    q_cars: Query<(Entity, &GlobalTransform), With<Car>>,
    mut ev_enter: EventWriter<EnterCarEvent>,
) {
    if keys.just_pressed(KeyCode::KeyF) {
        if let Ok((ped_entity, ped_tf)) = q_player.get_single() {
            // Find closest car within 1.0m
            let mut closest_car = None;
            let mut min_dist = 1.0;
            
            for (car_entity, car_tf) in q_cars.iter() {
                let dist = ped_tf.translation().distance(car_tf.translation());
                if dist < min_dist {
                    min_dist = dist;
                    closest_car = Some(car_entity);
                }
            }
            
            if let Some(car) = closest_car {
                ev_enter.send(EnterCarEvent { car_entity: car, pedestrian_entity: ped_entity });
            }
        }
    }
}
```

### `crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/pedestrian_controller_plugin/mod.rs`

#### Enter/Exit Workflows
**Explanation**: These handlers perform the heavy lifting of state transitions. On entering, we strip the player of physics so they don't drag the car, attach their mesh to the car hierarchy, and start the driving animations. On exit, we remove the active marker, play the exit sequence, and request a fresh pedestrian to be spawned beside the car.
**Invariants**: The car must be safely marked as the `ActivePlayerVehicle` so inputs route correctly. The player's mesh transform must be zeroed-out relative to the car seat.
```rust
pub fn handle_enter_car(
    mut commands: Commands,
    mut ev_enter: EventReader<EnterCarEvent>,
    mut q_car: Query<&mut CarDriveState>,
) {
    for ev in ev_enter.read() {
        // 1. Remove physics and controller from pedestrian
        commands.entity(ev.pedestrian_entity)
            .remove::<CharacterController>()
            .remove::<RigidBody>()
            .remove::<Collider>();
            
        // 2. Parent pedestrian mesh to car
        commands.entity(ev.car_entity).add_child(ev.pedestrian_entity);
        
        // 3. Mark car as active player vehicle
        // (Assuming CarDriveState serves as active marker, or add an `ActivePlayerVehicle` component)
        commands.entity(ev.car_entity).insert(ActivePlayerVehicle);
        
        // 4. Trigger "Enter Car" animation (pseudo-code)
        // animation_player.play(asset_server.load("animations/enter_car.glb#Animation0"));
    }
}

pub fn handle_exit_car(
    mut commands: Commands,
    keys: Res<ButtonInput<KeyCode>>,
    q_active_car: Query<(Entity, &Transform, &Children), With<ActivePlayerVehicle>>,
    mut ev_spawn_ped: EventWriter<SpawnPedestrianEvent>, // Assuming this exists
) {
    if keys.just_pressed(KeyCode::KeyF) {
        if let Ok((car_entity, car_tf, children)) = q_active_car.get_single() {
            commands.entity(car_entity).remove::<ActivePlayerVehicle>();
            
            // Trigger exit animation, wait, then:
            // For now, instantly respawn pedestrian outside
            let exit_pos = car_tf.translation() + car_tf.right() * 2.0; 
            
            ev_spawn_ped.send(SpawnPedestrianEvent {
                position: exit_pos,
                // ... state transfer
            });
            
            // Despawn the attached mesh
            for child in children.iter() {
                commands.entity(*child).despawn_recursive();
            }
        }
    }
}
```

### In-Car Debug Menu (EgUi)
**Explanation**: A developer overlay menu that exposes X/Y/Z translation sliders. This allows us to perfectly position the character's sitting mesh relative to the car chassis dynamically without recompiling.
**Invariants**: This UI block must only render if there is exactly one active player vehicle in the world.
```rust
#[derive(Resource, Default)]
pub struct CarSeatOffset {
    pub offset: Vec3,
}

pub fn in_car_debug_menu(
    mut contexts: EguiContexts,
    mut seat_offset: ResMut<CarSeatOffset>,
    q_active_car: Query<(), With<ActivePlayerVehicle>>,
) {
    if q_active_car.is_empty() { return; }

    egui::Window::new("Car Debug Menu").show(contexts.ctx_mut(), |ui| {
        ui.heading("Seat Offset");
        ui.add(egui::Slider::new(&mut seat_offset.offset.x, -2.0..=2.0).text("X Offset"));
        ui.add(egui::Slider::new(&mut seat_offset.offset.y, -2.0..=2.0).text("Y Offset"));
        ui.add(egui::Slider::new(&mut seat_offset.offset.z, -2.0..=2.0).text("Z Offset"));
    });
}
```

## Verification Plan
1. Start `fane` or the main game binary.
2. Walk up to a car, look at it, and press `f` (must be within 1m).
3. Verify the player enters the car, sits down, and gains driving control.
4. Open the debug menu, verify the sliders move the character inside the car.
5. Press `f` to exit the car. Verify the exit animation plays and the player regains ground movement.

use bevy::prelude::*;
use bevy::gltf::GltfAssetLabel;
use bevy::world_serialization::WorldAssetRoot;
use avian3d::prelude::*;
use crate::plugins::map_plugin::MapTree;
use crate::plugins::gta_plugin::GtaSpawnState;

#[derive(Component)]
pub struct Car;

pub fn spawn_car_system(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    time: Res<Time>,
    mut spawn_state: ResMut<GtaSpawnState>,
    car_query: Query<Entity, With<Car>>,
) {
    let mut timer_finished = false;
    if let Some(ref mut timer) = spawn_state.timer {
        timer.tick(time.delta());
        if timer.is_finished() {
            timer_finished = true;
        }
    }

    if timer_finished {
        spawn_state.timer = None;
        if let Some(spawn_point) = spawn_state.spawn_point {
            // Despawn any existing car just to be safe
            for entity in &car_query {
                commands.entity(entity).despawn();
            }

            let car_url = format!("{}/3d_data/MODELS/dacie_00001_.glb", crate::config::DATA_BASE_URL);
            let asset_path = GltfAssetLabel::Scene(0).from_asset(car_url);
            let car_handle = asset_server.load(asset_path);

            info!("Spawning car at {:?}", spawn_point);

            commands.spawn((
                WorldAssetRoot(car_handle),
                Transform::from_translation(spawn_point + Vec3::new(0.0, 1.5, 0.0)),
                RigidBody::Dynamic,
                Collider::cuboid(2.0, 1.2, 4.5),
                LinearVelocity::default(),
                AngularVelocity::default(),
                Friction::new(0.3),
                Restitution::ZERO.with_combine_rule(CoefficientCombine::Min),
                LinearDamping(0.2),
                AngularDamping(1.0),
                SweptCcd::default(),
                Car,
            ));
        }
    }
}

pub fn drive_car_system(
    keyboard: Res<ButtonInput<KeyCode>>,
    time: Res<Time>,
    mut car_query: Query<(&Transform, &mut LinearVelocity, &mut AngularVelocity), With<Car>>,
) {
    let Ok((transform, mut linear_velocity, mut angular_velocity)) = car_query.single_mut() else {
        return;
    };

    let delta = time.delta_secs();

    // Constant parameters
    let max_speed = 35.0;
    let max_reverse_speed = 15.0;
    let acceleration = 25.0;
    let reverse_acceleration = 15.0;
    let braking = 35.0;
    let steer_speed = 2.5;
    let lateral_damping = 10.0;
    let stabilization_strength = 5.0;

    let forward_dir = transform.forward();
    let right_dir = transform.right();

    let current_speed = linear_velocity.dot(*forward_dir);

    // WASD driving keys
    if keyboard.pressed(KeyCode::KeyW) {
        if current_speed < max_speed {
            linear_velocity.0 += *forward_dir * acceleration * delta;
        }
    }
    if keyboard.pressed(KeyCode::KeyS) {
        if current_speed > 0.1 {
            // Apply braking
            linear_velocity.0 -= *forward_dir * braking * delta;
        } else if current_speed > -max_reverse_speed {
            // Reversing
            linear_velocity.0 -= *forward_dir * reverse_acceleration * delta;
        }
    }

    // Steer factor (only steer when moving, steer in reverse if moving backward)
    let speed = linear_velocity.length();
    let turn_factor = (speed / 2.0).min(1.0);
    let direction_sign = if current_speed < 0.0 { -1.0 } else { 1.0 };

    let mut steer = 0.0;
    if keyboard.pressed(KeyCode::KeyA) {
        steer += 1.0;
    }
    if keyboard.pressed(KeyCode::KeyD) {
        steer -= 1.0;
    }
    
    // Steering around local Y axis
    angular_velocity.y = steer * steer_speed * turn_factor * direction_sign;

    // Lateral grip (damp lateral sliding)
    let lateral_speed = linear_velocity.dot(*right_dir);
    let damped_lateral_speed = lateral_speed * (1.0 - lateral_damping * delta).max(0.0);
    let vertical_speed = linear_velocity.y;
    let new_forward_speed = linear_velocity.dot(*forward_dir);

    linear_velocity.0 = *forward_dir * new_forward_speed + *right_dir * damped_lateral_speed + Vec3::Y * vertical_speed;

    // Stabilization torque (keeps the car upright)
    let current_up = transform.up();
    let torque = current_up.cross(Vec3::Y) * stabilization_strength;
    angular_velocity.0 += torque * delta;

    // Damp angular pitch and roll to prevent tumbling
    angular_velocity.x *= (1.0 - 5.0 * delta).max(0.0);
    angular_velocity.z *= (1.0 - 5.0 * delta).max(0.0);
}

pub fn clamp_car_position_system(
    data_res: Res<MapTree>,
    mut car_query: Query<(&mut Transform, &mut LinearVelocity), With<Car>>,
) {
    if !data_res.parsed {
        return;
    }

    let Ok((mut transform, mut linear_velocity)) = car_query.single_mut() else {
        return;
    };

    let bbox = data_res.bbox;
    let min_x = bbox.min.x;
    let max_x = bbox.max.x;
    let min_z = bbox.min.z;
    let max_z = bbox.max.z;

    let center_x = (min_x + max_x) / 2.0;
    let center_z = (min_z + max_z) / 2.0;
    let half_x = ((max_x - min_x) / 2.0) * 0.95;
    let half_z = ((max_z - min_z) / 2.0) * 0.95;

    // Detect if car fell under the bottom of the map
    if transform.translation.y < bbox.min.y {
        transform.translation.y = bbox.max.y;
        linear_velocity.y = 0.0;
        info!("Car fell off the map! Looping around to max Y: {:?}", transform.translation);
    }

    // Cap car Y coord at map bbox max Y
    if transform.translation.y > bbox.max.y {
        transform.translation.y = bbox.max.y;
        if linear_velocity.y > 0.0 {
            linear_velocity.y = 0.0;
        }
    }

    // Cap X and Z coordinates to 95% of the bbox
    transform.translation.x = transform.translation.x.clamp(center_x - half_x, center_x + half_x);
    transform.translation.z = transform.translation.z.clamp(center_z - half_z, center_z + half_z);
}

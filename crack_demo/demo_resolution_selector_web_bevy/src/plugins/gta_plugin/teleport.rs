use bevy::prelude::*;
use crate::plugins::map_plugin::{MapTree, MapLODState};
use crate::plugins::gta_plugin::car::Car;
use crate::plugins::gta_plugin::GtaSpawnState;

pub fn teleport_car_system(
    mut commands: Commands,
    keyboard: Res<ButtonInput<KeyCode>>,
    data_res: Res<MapTree>,
    mut lod_state: ResMut<MapLODState>,
    mut spawn_state: ResMut<GtaSpawnState>,
    mut camera_state: ResMut<super::camera::GtaCameraState>,
    car_query: Query<Entity, With<Car>>,
) {
    if !data_res.parsed {
        return;
    }

    let force_teleport = keyboard.just_pressed(KeyCode::Space);
    let initial_trigger = !spawn_state.initialized;

    if initial_trigger || force_teleport {
        // Force spawn next to our custom models
        let spawn_point = Vec3::new(-1060.0, 3361.0, -20120.0);

        // 1. Replace the reference point list with ONLY the new spawn point
        lod_state.reference_points = vec![spawn_point];
        info!("Set new map reference point to: {:?}", spawn_point);

        // 2. Despawn any existing car immediately
        for entity in &car_query {
            commands.entity(entity).despawn();
        }

        // 3. Set the 3-second timer and target spawn point
        spawn_state.spawn_point = Some(spawn_point);
        spawn_state.timer = Some(Timer::from_seconds(3.0, TimerMode::Once));
        spawn_state.initialized = true;

        // Reset camera state so it snaps directly to the back of the car on spawn
        camera_state.smoothed_target = None;
        camera_state.yaw = 0.0;

        info!("Spawn timer initiated. Waiting 3.0 seconds for map LOD to load at {:?}", spawn_point);
    }
}

use bevy::prelude::*;

pub mod car;
pub mod camera;
pub mod teleport;

#[derive(Resource, Default)]
pub struct GtaSpawnState {
    pub timer: Option<Timer>,
    pub spawn_point: Option<Vec3>,
    pub initialized: bool,
}

pub struct GtaPlugin;

impl Plugin for GtaPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(camera::GtaCameraState::default())
            .insert_resource(GtaSpawnState::default())
            .add_systems(Update, (
                car::spawn_car_system,
                car::drive_car_system,
                car::clamp_car_position_system,
                camera::camera_follow_system,
                teleport::teleport_car_system,
            ));
    }
}

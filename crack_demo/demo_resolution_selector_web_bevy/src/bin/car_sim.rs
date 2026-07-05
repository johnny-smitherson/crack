use avian3d::prelude::LinearVelocity;
use bevy::prelude::*;
use demo_resolution_selector_web_bevy::plugins::cars_driving::driving_plugin::{
    CarDriveState, CarWheelsContactData, SimState,
};
use demo_resolution_selector_web_bevy::{
    basic_app::make_basic_app, plugins::cars_driving::driving_plugin::spawn_car::Car,
    utils::setup_debug_scene::SetupDebugScenePlugin,
};
use demo_resolution_selector_web_bevy::{
    plugins::{
        cars_driving::CarsAndDrivingPlugin, cars_driving::car_info::get_random_car_type,
        cars_driving::driving_plugin::spawn_car::SpawnCarRequestEvent,
        physics_plugin::PhysicsPlugin, states::GameStatesPlugin,
    },
    ui_egui::UiState,
};

#[derive(Resource)]
struct SimLogTimer {
    total_time: f32,
    last_log_time: f32,
}

impl Default for SimLogTimer {
    fn default() -> Self {
        Self {
            total_time: 0.0,
            last_log_time: 0.0,
        }
    }
}

fn main() {
    make_basic_app("Car Sim")
        .add_plugins(bevy_egui::EguiPlugin::default())
        .insert_resource(UiState::with_physics_debug()) // Satisfies PhysicsPlugin's sync_physics_debug_config
        .insert_resource(SimLogTimer::default())
        .insert_resource(SimState {
            is_sim: true,
            ..default()
        })
        .add_plugins(PhysicsPlugin)
        // .insert_resource(SubstepCount(50))
        .add_plugins(GameStatesPlugin)
        .add_plugins(CarsAndDrivingPlugin)
        .add_plugins(SetupDebugScenePlugin)
        .add_systems(Update, (update_sim_control, log_car_state))
        .run();
}

fn update_sim_control(
    time: Res<Time>,
    mut sim_state: ResMut<SimState>,
    mut commands: Commands,
    mut q_car: Query<&mut CarDriveState, With<Car>>,
) {
    let dt = time.delta_secs();
    sim_state.time_elapsed += dt;

    // 1. Wait 1s to spawn a car
    if !sim_state.spawned && sim_state.time_elapsed >= 1.0 {
        sim_state.spawned = true;
        let car_type = get_random_car_type();
        info!("Spawn timer met: Triggering SpawnCarRequestEvent at (40, 0, 40)");

        let car_rot =
            Quat::from_rotation_arc(Vec3::NEG_Z, Vec3::new(-40.0, 0.0, -40.0).normalize());

        commands.trigger(SpawnCarRequestEvent {
            position: Vec3::new(40.0, 0.0, 40.0),
            car_type: car_type.to_string(),
            rotation: Some(car_rot),
        });
    }

    // 2. Set acceleration for 5s (from t = 1.0s to t = 6.0s), then drop controls
    if sim_state.spawned {
        if let Some(mut drive_state) = q_car.iter_mut().next() {
            if sim_state.time_elapsed >= 1.0 && sim_state.time_elapsed < 6.0 {
                drive_state.avg_accelerate = 1.0;
                sim_state.is_sim = true;
            } else {
                drive_state.avg_accelerate = 0.0;
                sim_state.is_sim = false;
            }
        }
    }
}

fn log_car_state(
    time: Res<Time>,
    mut log_timer: ResMut<SimLogTimer>,
    q_car: Query<
        (
            &Transform,
            &LinearVelocity,
            &CarDriveState,
            &CarWheelsContactData,
        ),
        With<Car>,
    >,
) {
    let dt = time.delta_secs();
    log_timer.total_time += dt;

    if log_timer.total_time > 8.0 {
        return;
    }

    if log_timer.total_time - log_timer.last_log_time >= 0.25 {
        log_timer.last_log_time = log_timer.total_time;
        if let Some((transform, velocity, drive_state, contact_data)) = q_car.iter().next() {
            let pos = transform.translation;
            let speed = velocity.0.length();
            let (yaw, pitch, roll) = transform.rotation.to_euler(EulerRot::YXZ);
            let acc = drive_state.avg_accelerate;
            let brake = drive_state.avg_brake;
            let steer = drive_state.avg_steer;

            let mut susp_lengths = [0.0f32; 4];
            for wheel_idx in 0..4 {
                let w_contact = &contact_data.wheels[wheel_idx];
                let mut sum_dist = 0.0f32;
                let mut engaged_rays = 0;
                for &d in &w_contact.ray_distances {
                    if d <= 1.0f32 {
                        sum_dist += d;
                        engaged_rays += 1;
                    }
                }
                let avg_length = if engaged_rays > 0 {
                    sum_dist / engaged_rays as f32
                } else {
                    1.0f32
                };
                susp_lengths[wheel_idx] = avg_length;
            }

            info!(
                "TIME: {:.2}s | POS: ({:.2}, {:.2}, {:.2}) | SPEED: {:.2} m/s | ROT: (Y:{:.1} P:{:.1} R:{:.1}) | CTL: (A:{:.1} B:{:.1} S:{:.1}) | SUSP: [FL: {:.2}m, FR: {:.2}m, RL: {:.2}m, RR: {:.2}m]",
                log_timer.total_time,
                pos.x,
                pos.y,
                pos.z,
                speed,
                yaw.to_degrees(),
                pitch.to_degrees(),
                roll.to_degrees(),
                acc,
                brake,
                steer,
                susp_lengths[0],
                susp_lengths[1],
                susp_lengths[2],
                susp_lengths[3]
            );
        }
    }
}

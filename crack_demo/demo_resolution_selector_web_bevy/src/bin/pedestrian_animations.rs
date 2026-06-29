use bevy::{
    asset::RenderAssetUsages,
    prelude::*,
    render::{
        render_resource::{Extent3d, TextureDimension, TextureFormat},
        settings::{Backends, WgpuSettings},
        RenderPlugin,
    },
    window::WindowResolution,
    world_serialization::WorldAssetRoot,
};
use avian3d::prelude::{CollisionLayers, Restitution, RigidBody};

use demo_resolution_selector_web_bevy::{
    plugins::{
        cars_driving::driving_plugin::GamePhysicsLayer,
        physics_plugin::PhysicsPlugin,
        states::GameStatesPlugin,
    },
    ui_egui::UiState,
};

#[derive(Component)]
struct Pedestrian;

fn main() {
    #[cfg(feature = "web")]
    let backends = Backends::GL;
    #[cfg(not(feature = "web"))]
    let backends = Backends::PRIMARY;

    App::new()
        .add_plugins(
            DefaultPlugins
                .build()
                .set(WindowPlugin {
                    primary_window: Some(Window {
                        title: "Pedestrian Animations".into(),
                        resolution: WindowResolution::new(1280, 720),
                        ..default()
                    }),
                    ..default()
                })
                .set(RenderPlugin {
                    render_creation: bevy::render::settings::RenderCreation::Automatic(Box::new(
                        WgpuSettings {
                            backends: Some(backends),
                            ..default()
                        },
                    )),
                    ..default()
                }),
        )
        .add_plugins(bevy_egui::EguiPlugin::default())
        .init_resource::<UiState>() // Satisfies PhysicsPlugin's sync_physics_debug_config
        .add_plugins(PhysicsPlugin)
        .add_plugins(GameStatesPlugin)
        .add_systems(Startup, setup_scene)
        .add_systems(Update, (move_pedestrian, camera_follows_pedestrian))
        .run();
}

fn create_grayscale_texture(gray1: u8, gray2: u8) -> Image {
    let mut texture_data = vec![0; 32 * 32 * 4];
    for y in 0..32 {
        for x in 0..32 {
            let color = if (x / 4 + y / 4) % 2 == 0 { gray1 } else { gray2 };
            let offset = (y * 32 + x) * 4;
            texture_data[offset] = color;
            texture_data[offset + 1] = color;
            texture_data[offset + 2] = color;
            texture_data[offset + 3] = 255;
        }
    }
    let mut image = Image::new_fill(
        Extent3d {
            width: 32,
            height: 32,
            depth_or_array_layers: 1,
        },
        TextureDimension::D2,
        &texture_data,
        TextureFormat::Rgba8UnormSrgb,
        RenderAssetUsages::default(),
    );
    image.sampler = bevy::image::ImageSampler::Descriptor(bevy::image::ImageSamplerDescriptor {
        address_mode_u: bevy::image::ImageAddressMode::Repeat,
        address_mode_v: bevy::image::ImageAddressMode::Repeat,
        ..default()
    });
    image
}

fn setup_scene(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut images: ResMut<Assets<Image>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    asset_server: Res<AssetServer>,
) {
    // 1. Spawning 4 ground cubes of size 500x500x500
    let cubes_info = [
        (Vec3::new(250.0, -250.0, 250.0), (50, 70)),
        (Vec3::new(-250.0, -250.0, 250.0), (90, 110)),
        (Vec3::new(250.0, -250.0, -250.0), (130, 150)),
        (Vec3::new(-250.0, -250.0, -250.0), (170, 190)),
    ];

    for (center, (gray1, gray2)) in cubes_info {
        let tile_repeat: f32 = 1.0 + rand::random::<f32>() * 2.0; // around 1 to 3 meters

        let mut mesh = Mesh::from(Cuboid::from_size(Vec3::new(500.0, 500.0, 500.0)));
        let repeat = 500.0 / tile_repeat;
        if let Some(bevy::render::mesh::VertexAttributeValues::Float32x2(uvs)) =
            mesh.attribute_mut(Mesh::ATTRIBUTE_UV_0)
        {
            for uv in uvs.iter_mut() {
                uv[0] *= repeat;
                uv[1] *= repeat;
            }
        }
        let mesh_handle = meshes.add(mesh);

        let texture = create_grayscale_texture(gray1, gray2);
        let texture_handle = images.add(texture);

        let material_handle = materials.add(StandardMaterial {
            base_color_texture: Some(texture_handle),
            perceptual_roughness: 0.9,
            ..default()
        });

        commands.spawn((
            Mesh3d(mesh_handle),
            MeshMaterial3d(material_handle),
            Transform::from_translation(center),
            RigidBody::Static,
            avian3d::prelude::Collider::cuboid(500.0, 500.0, 500.0),
            Restitution::ZERO.with_combine_rule(avian3d::prelude::CoefficientCombine::Min),
            CollisionLayers::new(
                [GamePhysicsLayer::Map],
                [GamePhysicsLayer::Map, GamePhysicsLayer::Car, GamePhysicsLayer::Wheel],
            ),
        ));
    }

    // 2. Spawn camera with AmbientLight component
    commands.spawn((
        Camera3d::default(),
        Transform::from_xyz(0.0, 15.0, -30.0).looking_at(Vec3::ZERO, Vec3::Y),
        AmbientLight {
            color: Color::srgb(0.8, 0.85, 1.0),
            brightness: 1000.0,
            ..default()
        },
    ));

    // 3. Spawn DirectionalLight (the sun)
    commands.spawn((
        DirectionalLight {
            illuminance: 10000.0,
            shadow_maps_enabled: true,
            ..default()
        },
        Transform::from_xyz(200.0, 400.0, 200.0).looking_at(Vec3::ZERO, Vec3::Y),
    ));

    // 4. Load & Spawn Pedestrian
    let base_url = demo_resolution_selector_web_bevy::config::DATA_BASE_URL.trim_end_matches('/');
    let pedestrian_url = format!(
        "{}/3d_data/3d_slop_models_clean/pedestrian/armin-1b.glb",
        base_url
    );
    let pedestrian_handle = asset_server.load(GltfAssetLabel::Scene(0).from_asset(pedestrian_url));

    commands.spawn((
        WorldAssetRoot(pedestrian_handle),
        Transform::from_xyz(0.0, 0.0, 0.0),
        Pedestrian,
    ));
}

fn move_pedestrian(
    keyboard: Res<ButtonInput<KeyCode>>,
    time: Res<Time>,
    mut query: Query<&mut Transform, With<Pedestrian>>,
) {
    let Ok(mut transform) = query.single_mut() else {
        return;
    };

    let dt = time.delta_secs();

    // 1. Rotation (A/D or ArrowLeft/ArrowRight)
    let mut rotation_amount = 0.0;
    if keyboard.pressed(KeyCode::KeyA) || keyboard.pressed(KeyCode::ArrowLeft) {
        rotation_amount += 2.0; // radians per second
    }
    if keyboard.pressed(KeyCode::KeyD) || keyboard.pressed(KeyCode::ArrowRight) {
        rotation_amount -= 2.0; // radians per second
    }
    if rotation_amount != 0.0 {
        transform.rotate_y(rotation_amount * dt);
    }

    // 2. Translation (W/S or ArrowUp/ArrowDown)
    let mut move_direction = Vec3::ZERO;
    if keyboard.pressed(KeyCode::KeyW) || keyboard.pressed(KeyCode::ArrowUp) {
        move_direction += *transform.forward();
    }
    if keyboard.pressed(KeyCode::KeyS) || keyboard.pressed(KeyCode::ArrowDown) {
        move_direction += *transform.back();
    }

    if move_direction != Vec3::ZERO {
        let direction = move_direction.normalize();
        transform.translation += direction * 1.0 * dt; // 1m/s
    }
}

fn camera_follows_pedestrian(
    mut camera_query: Query<&mut Transform, (With<Camera3d>, Without<Pedestrian>)>,
    pedestrian_query: Query<&Transform, (With<Pedestrian>, Without<Camera3d>)>,
) {
    let Ok(pedestrian_transform) = pedestrian_query.single() else {
        return;
    };
    let Ok(mut camera_transform) = camera_query.single_mut() else {
        return;
    };

    // Position camera slightly behind and above the pedestrian
    // Pedestrian moves forward along their local forward direction, so we put the camera behind them relative to their rotation
    let back_dir = *pedestrian_transform.back();
    let target_position = pedestrian_transform.translation + back_dir * 6.0 + Vec3::Y * 3.0;

    camera_transform.translation = target_position;
    camera_transform.look_at(pedestrian_transform.translation + Vec3::Y * 1.0, Vec3::Y);
}

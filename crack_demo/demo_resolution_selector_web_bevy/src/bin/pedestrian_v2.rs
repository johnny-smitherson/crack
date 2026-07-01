use avian3d::prelude::{
    Collider, CollisionLayers, Restitution, RigidBody, PhysicsPlugins, PhysicsDebugPlugin,
    SpatialQuery, SpatialQueryFilter,
};
use bevy::world_serialization::{WorldAsset, WorldAssetRoot};
use bevy::{
    asset::{Asset, AssetLoader, LoadContext, RenderAssetUsages, io::Reader},
    ecs::relationship::Relationship,
    prelude::*,
    reflect::TypePath,
    render::{
        RenderPlugin,
        render_resource::{Extent3d, TextureDimension, TextureFormat},
        settings::{Backends, WgpuSettings},
    },
    window::WindowResolution,
};
use bevy_egui::{EguiContexts, EguiPlugin, EguiPrimaryContextPass, egui};

use demo_resolution_selector_web_bevy::plugins::{
    cars_driving::driving_plugin::GamePhysicsLayer,
    game_freecam::camera_controls::{ActiveCameraAnimation, CameraControlsPlugin},
    map_plugin::{BBox, MapTree},
    states::GameControlState,
};

#[derive(Component)]
struct ModelRoot {
    index: usize,
    name: String,
    size: Vec3,
}

#[derive(Component)]
struct NeedAlignment {
    target_position: Vec3,
    scale: f32,
}

#[derive(Event, Clone)]
struct SpawnPedestrianRequest {
    position: Vec3,
    model_name: String,
    handle: Handle<WorldAsset>,
    model_index: usize,
}

#[derive(Resource)]
struct ManifestLoader {
    handle: Handle<TextAsset>,
    glb_handles: Option<Vec<(String, Handle<WorldAsset>)>>,
    spawned: bool,
}

#[derive(Resource, Default)]
struct SelectedModel {
    entity: Option<Entity>,
}

#[derive(Resource, Default)]
struct HoveredModel {
    entity: Option<Entity>,
}

#[derive(Asset, TypePath, Debug, Clone)]
pub struct TextAsset {
    pub text: String,
}

#[derive(Default, TypePath)]
pub struct TextAssetLoader;

impl AssetLoader for TextAssetLoader {
    type Asset = TextAsset;
    type Settings = ();
    type Error = std::io::Error;

    async fn load(
        &self,
        reader: &mut dyn Reader,
        _settings: &Self::Settings,
        _load_context: &mut LoadContext<'_>,
    ) -> Result<Self::Asset, Self::Error> {
        let mut bytes = Vec::new();
        reader.read_to_end(&mut bytes).await?;
        let text = String::from_utf8(bytes)
            .map_err(|e| std::io::Error::new(std::io::ErrorKind::InvalidData, e))?;
        Ok(TextAsset { text })
    }

    fn extensions(&self) -> &[&str] {
        &["txt"]
    }
}

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
                        title: "Pedestrian V2 Viewer".into(),
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
        .add_plugins(EguiPlugin::default())
        .add_plugins(PhysicsPlugins::default())
        .add_plugins(PhysicsDebugPlugin::default())
        .init_state::<GameControlState>()
        .insert_resource(MapTree {
            parsed: true,
            bbox: BBox {
                min: Vec3::new(-1000.0, -100.0, -1000.0),
                max: Vec3::new(1000.0, 100.0, 1000.0),
            },
            ..default()
        })
        .add_plugins(CameraControlsPlugin)
        .init_asset::<TextAsset>()
        .init_asset_loader::<TextAssetLoader>()
        .init_resource::<SelectedModel>()
        .init_resource::<HoveredModel>()
        .add_observer(spawn_pedestrian_observer)
        .add_systems(Startup, setup_scene)
        .add_systems(
            Update,
            (
                load_manifest_system,
                align_pedestrians_system,
                draw_skeletons_system,
                picker_system,
                draw_hovered_bbox_system,
            ),
        )
        .add_systems(EguiPrimaryContextPass, draw_gui_system)
        .run();
}

fn spawn_pedestrian_observer(
    trigger: On<SpawnPedestrianRequest>,
    mut commands: Commands,
) {
    let req = trigger.event();
    commands.spawn((
        Transform::from_translation(req.position),
        Visibility::default(),
        InheritedVisibility::default(),
        ModelRoot {
            index: req.model_index,
            name: req.model_name.clone(),
            size: Vec3::ZERO,
        },
        NeedAlignment {
            target_position: req.position,
            scale: rand::random::<f32>() * 0.2 + 1.3, // 1.3 to 1.5 of initial scale
        },
    ))
    .with_children(|parent| {
        parent.spawn((
            WorldAssetRoot(req.handle.clone()),
            Transform::IDENTITY,
            Visibility::default(),
            InheritedVisibility::default(),
        ));
    });
}

fn create_grayscale_texture(gray1: u8, gray2: u8) -> Image {
    let mut texture_data = vec![0; 32 * 32 * 4];
    for y in 0..32 {
        for x in 0..32 {
            let color = if (x / 4 + y / 4) % 2 == 0 {
                gray1
            } else {
                gray2
            };
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
    mut gizmo_store: ResMut<GizmoConfigStore>,
) {
    // Configure default gizmos depth bias to always show skeleton through mesh
    let (config, _) = gizmo_store.config_mut::<DefaultGizmoConfigGroup>();
    config.depth_bias = -1.0;

    // Spawning 4 ground cubes of size 500x500x500
    let cubes_info = [
        (Vec3::new(250.0, -250.0, 250.0), (50, 70)),
        (Vec3::new(-250.0, -250.0, 250.0), (90, 110)),
        (Vec3::new(250.0, -250.0, -250.0), (130, 150)),
        (Vec3::new(-250.0, -250.0, -250.0), (170, 190)),
    ];

    for (center, (gray1, gray2)) in cubes_info {
        let tile_repeat: f32 = 1.0 + rand::random::<f32>() * 2.0;

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
            Collider::cuboid(500.0, 500.0, 500.0),
            Restitution::ZERO.with_combine_rule(avian3d::prelude::CoefficientCombine::Min),
            CollisionLayers::new(
                [GamePhysicsLayer::Map],
                [
                    GamePhysicsLayer::Map,
                    GamePhysicsLayer::Car,
                    GamePhysicsLayer::Wheel,
                ],
            ),
        ));
    }

    // Spawn camera diagonally looking at the grid center
    commands.spawn((
        Camera3d::default(),
        Transform::from_xyz(10.0, 10.0, 15.0).looking_at(Vec3::new(0.0, 1.0, 0.0), Vec3::Y),
        AmbientLight {
            color: Color::srgb(0.8, 0.85, 1.0),
            brightness: 1000.0,
            ..default()
        },
    ));

    // Spawn DirectionalLight (the sun)
    commands.spawn((
        DirectionalLight {
            illuminance: 10000.0,
            shadow_maps_enabled: true,
            ..default()
        },
        Transform::from_xyz(200.0, 400.0, 200.0).looking_at(Vec3::ZERO, Vec3::Y),
    ));

    // Load manifest
    let base_url = demo_resolution_selector_web_bevy::config::DATA_BASE_URL.trim_end_matches('/');
    let manifest_url = format!("{}/3d_data/pedestrian_3d_gen/manifest.txt", base_url);
    let handle = asset_server.load::<TextAsset>(manifest_url);

    commands.insert_resource(ManifestLoader {
        handle,
        glb_handles: None,
        spawned: false,
    });
}

fn load_manifest_system(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut loader: ResMut<ManifestLoader>,
    text_assets: Res<Assets<TextAsset>>,
    world_assets: Res<Assets<WorldAsset>>,
) {
    if loader.glb_handles.is_none() {
        if let Some(text_asset) = text_assets.get(&loader.handle) {
            let base_url =
                demo_resolution_selector_web_bevy::config::DATA_BASE_URL.trim_end_matches('/');
            let mut handles = Vec::new();
            for line in text_asset.text.lines() {
                let line = line.trim();
                if line.is_empty() {
                    continue;
                }
                let glb_url = format!("{}/3d_data/pedestrian_3d_gen/{}", base_url, line);
                let scene_url = GltfAssetLabel::Scene(0).from_asset(glb_url);
                let handle = asset_server.load::<WorldAsset>(scene_url);
                handles.push((line.to_string(), handle));
            }
            info!(
                "Parsed manifest. Loading {} GLB world assets in parallel...",
                handles.len()
            );
            loader.glb_handles = Some(handles);
        }
    } else if !loader.spawned {
        let handles = loader.glb_handles.as_ref().unwrap();
        let mut all_loaded = true;
        for (_, handle) in handles {
            if world_assets.get(handle).is_none() {
                all_loaded = false;
                break;
            }
        }
        if all_loaded {
            info!("All GLB scenes loaded! Triggering spawn events...");

            let count = handles.len();
            let cols = (count as f32).sqrt().ceil() as usize;

            for (idx, (line, handle)) in handles.iter().enumerate() {
                let col = idx % cols;
                let row = idx / cols;

                const grid_size: f32 = 1.6;
                let x = (col as f32 - (cols - 1) as f32 / 2.0) * grid_size;
                let z = (row as f32 - (((count as f32 / cols as f32).ceil() - 1.0) / 2.0)) * grid_size;
                let y = 1.0;

                let model_name = line.split('/').last().unwrap_or(line).replace(".glb", "");

                commands.trigger(SpawnPedestrianRequest {
                    position: Vec3::new(x, y, z),
                    model_name: model_name.clone(),
                    handle: handle.clone(),
                    model_index: idx,
                });
            }

            loader.spawned = true;
        }
    }
}

fn get_mesh_descendants(
    entity: Entity,
    children_query: &Query<&Children>,
    mesh_query: &Query<&Mesh3d>,
    results: &mut Vec<(Entity, Handle<Mesh>)>,
) {
    if let Ok(mesh3d) = mesh_query.get(entity) {
        results.push((entity, mesh3d.0.clone()));
    }
    if let Ok(children) = children_query.get(entity) {
        for child in children.iter() {
            get_mesh_descendants(child, children_query, mesh_query, results);
        }
    }
}

fn align_pedestrians_system(
    mut commands: Commands,
    query: Query<(Entity, &NeedAlignment, &Children)>,
    children_query: Query<&Children>,
    mesh_query: Query<&Mesh3d>,
    global_transform_query: Query<&GlobalTransform>,
    mut transform_query: Query<&mut Transform>,
    mut model_root_query: Query<&mut ModelRoot>,
    meshes: Res<Assets<Mesh>>,
) {
    for (root_entity, need_align, children) in query.iter() {
        let mut mesh_entities = Vec::new();

        for child in children.iter() {
            get_mesh_descendants(child, &children_query, &mesh_query, &mut mesh_entities);
        }

        if mesh_entities.is_empty() {
            continue;
        }

        let mut all_meshes_loaded = true;
        for (_, mesh_handle) in &mesh_entities {
            if meshes.get(mesh_handle).is_none() {
                all_meshes_loaded = false;
                break;
            }
        }

        if !all_meshes_loaded {
            continue;
        }

        let mut min = Vec3::splat(f32::MAX);
        let mut max = Vec3::splat(f32::MIN);
        let mut found_vertices = false;

        let Ok(root_gt) = global_transform_query.get(root_entity) else {
            continue;
        };
        let root_inv = root_gt.to_matrix().inverse();

        for (ent, mesh_handle) in &mesh_entities {
            let Ok(mesh_gt) = global_transform_query.get(*ent) else {
                continue;
            };

            if let Some(mesh) = meshes.get(mesh_handle) {
                if let Some(bevy::render::mesh::VertexAttributeValues::Float32x3(positions)) =
                    mesh.attribute(Mesh::ATTRIBUTE_POSITION)
                {
                    for pos in positions {
                        let vertex_local = Vec3::from(*pos);
                        let world_pos = mesh_gt.transform_point(vertex_local);
                        let vertex_rel_root = root_inv.transform_point3(world_pos);
                        min = min.min(vertex_rel_root);
                        max = max.max(vertex_rel_root);
                        found_vertices = true;
                    }
                }
            }
        }

        if !found_vertices {
            continue;
        }

        let center = (min + max) / 2.0;
        let size = max - min;

        let s = need_align.scale;

        // Position root at center of scaled model (offset up by half scale-height)
        let root_pos = need_align.target_position + s * Vec3::new(0.0, size.y / 2.0, 0.0);

        if let Ok(mut root_transform) = transform_query.get_mut(root_entity) {
            root_transform.translation = root_pos;
            root_transform.scale = Vec3::splat(s);
        }

        // Center visual child at -center relative to root
        for child in children.iter() {
            if let Ok(mut child_transform) = transform_query.get_mut(child) {
                child_transform.translation = -center;
            }
        }

        commands.entity(root_entity).insert((
            Collider::cuboid(size.x * s, size.y * s, size.z * s),
            RigidBody::Static,
        ));

        if let Ok(mut root) = model_root_query.get_mut(root_entity) {
            root.size = size * s;
        }

        commands.entity(root_entity).remove::<NeedAlignment>();

        info!(
            "Aligned pedestrian root {:?} at target {:?}, original size: {:?}, original center: {:?}",
            root_entity, need_align.target_position, size, center
        );
    }
}

fn traverse_hierarchy(
    entity: Entity,
    children_query: &Query<&Children>,
    name_query: &Query<&Name>,
    transform_query: &Query<&GlobalTransform>,
    nodes: &mut Vec<(Entity, String, Vec3)>,
) {
    let name_str = if let Ok(name) = name_query.get(entity) {
        name.to_string()
    } else {
        format!("Entity_{}", entity.index())
    };

    let pos = if let Ok(gt) = transform_query.get(entity) {
        gt.translation()
    } else {
        Vec3::ZERO
    };

    nodes.push((entity, name_str, pos));

    if let Ok(children) = children_query.get(entity) {
        for child in children.iter() {
            traverse_hierarchy(child, children_query, name_query, transform_query, nodes);
        }
    }
}

fn draw_skeletons_system(
    mut gizmos: Gizmos,
    model_roots: Query<(Entity, &ModelRoot)>,
    children_query: Query<&Children>,
    name_query: Query<&Name>,
    transform_query: Query<&GlobalTransform>,
    parent_query: Query<&ChildOf>,
    camera_query: Query<(&Camera, &GlobalTransform)>,
    mut contexts: EguiContexts,
) {
    let Ok(ctx) = contexts.ctx_mut() else {
        return;
    };

    let Some((camera, camera_transform)) = camera_query.iter().next() else {
        return;
    };

    for (root_entity, _root) in model_roots.iter() {
        let mut nodes = Vec::new();
        traverse_hierarchy(
            root_entity,
            &children_query,
            &name_query,
            &transform_query,
            &mut nodes,
        );

        let entity_to_info: std::collections::HashMap<Entity, (usize, Vec3)> = nodes
            .iter()
            .enumerate()
            .map(|(idx, &(ent, _, pos))| (ent, (idx, pos)))
            .collect();

        for (idx, &(ent, _, pos)) in nodes.iter().enumerate() {
            // Render bones (green lines)
            if let Ok(parent) = parent_query.get(ent) {
                if let Some(&(_, parent_pos)) = entity_to_info.get(&parent.get()) {
                    gizmos.line(parent_pos, pos, Color::srgb(0.0, 1.0, 0.0));
                }
            }

            // Render index alongside node using screen-space projection and egui Area
            if let Ok(viewport_pos) = camera.world_to_viewport(camera_transform, pos) {
                egui::Area::new(egui::Id::new(format!("joint_lbl_{:?}_{}", pos, idx)))
                    .fixed_pos(egui::pos2(viewport_pos.x - 6.0, viewport_pos.y - 6.0))
                    .show(ctx, |ui| {
                        ui.label(
                            egui::RichText::new(format!("{}", idx))
                                .color(egui::Color32::WHITE)
                                .size(9.0)
                                .background_color(egui::Color32::from_rgba_premultiplied(
                                    0, 0, 0, 120,
                                )),
                        );
                    });
            }
        }
    }
}

fn picker_system(
    mut commands: Commands,
    mouse_button: Res<ButtonInput<MouseButton>>,
    windows: Query<&Window>,
    camera_query: Query<(&Camera, &GlobalTransform)>,
    spatial_query: SpatialQuery,
    parent_query: Query<&ChildOf>,
    model_root_query: Query<(Entity, &ModelRoot, &GlobalTransform)>,
    mut hovered: ResMut<HoveredModel>,
    mut selected: ResMut<SelectedModel>,
    mut contexts: EguiContexts,
) {
    let egui_focused = if let Ok(ctx) = contexts.ctx_mut() {
        ctx.egui_wants_pointer_input() || ctx.is_pointer_over_egui()
    } else {
        false
    };
    if egui_focused {
        hovered.entity = None;
        return;
    }

    let Some(window) = windows.iter().next() else {
        return;
    };
    let Some(cursor_pos) = window.cursor_position() else {
        hovered.entity = None;
        return;
    };
    let Some((camera, camera_transform)) = camera_query.iter().next() else {
        return;
    };
    let Ok(ray) = camera.viewport_to_world(camera_transform, cursor_pos) else {
        return;
    };

    let ray_dir = ray.direction;

    hovered.entity = None;

    if let Some(hit) = spatial_query.cast_ray(
        ray.origin,
        ray_dir,
        1000.0,
        true,
        &SpatialQueryFilter::default(),
    ) {
        let mut current = hit.entity;
        let mut found_root = None;
        loop {
            if let Ok((root_ent, root, _)) = model_root_query.get(current) {
                found_root = Some((root_ent, root.index));
                break;
            }
            if let Ok(parent) = parent_query.get(current) {
                current = parent.get();
            } else {
                break;
            }
        }

        if let Some((root_ent, model_idx)) = found_root {
            hovered.entity = Some(root_ent);

            if mouse_button.just_pressed(MouseButton::Left) {
                selected.entity = Some(root_ent);
                info!("Selected model: {} (entity: {:?})", model_idx, root_ent);

                if let Ok((_, _, root_gt)) = model_root_query.get(root_ent) {
                    let model_pos = root_gt.translation();

                    let start_pos = camera_transform.translation();
                    let start_rot = camera_transform.rotation();

                    let target_pos = model_pos + Vec3::new(2.5, 2.0, 3.5);
                    let target_dir = (model_pos + Vec3::Y * 0.5 - target_pos).normalize();
                    let target_rot = Quat::from_rotation_arc(Vec3::NEG_Z, target_dir);

                    commands.insert_resource(ActiveCameraAnimation {
                        start_pos,
                        start_rot,
                        target_pos,
                        target_rot,
                        elapsed: 0.0,
                        duration: 0.8,
                    });
                }
            }
        }
    }
}

fn draw_hovered_bbox_system(
    mut gizmos: Gizmos,
    hovered: Res<HoveredModel>,
    model_root_query: Query<(&GlobalTransform, &ModelRoot)>,
) {
    if let Some(hovered_ent) = hovered.entity {
        if let Ok((gt, root)) = model_root_query.get(hovered_ent) {
            let center = gt.translation();
            let size = root.size;
            let cuboid = Cuboid::new(size.x, size.y, size.z);
            gizmos.primitive_3d(
                &cuboid,
                Isometry3d::from_translation(center),
                Color::srgb(1.0, 1.0, 0.0), // Yellow bounding box
            );
        }
    }
}

fn draw_gui_system(
    mut contexts: EguiContexts,
    selected: Res<SelectedModel>,
    model_roots: Query<&ModelRoot>,
) {
    let Ok(ctx) = contexts.ctx_mut() else {
        return;
    };
    egui::Window::new("Pedestrian V2 Viewer Info")
        .default_pos(egui::pos2(12.0, 50.0))
        .show(ctx, |ui| {
            ui.label("Controls:");
            ui.label("- WASD: Move parallel to ground");
            ui.label("- Space / Ctrl: Move Up / Down");
            ui.label("- Mouse Scroll: Height zoom");
            ui.label("- Left Drag: Rotate Camera");
            ui.label("- Hover a pedestrian to show bbox");
            ui.label("- Click a pedestrian to focus/center");

            ui.separator();
            if let Some(selected_ent) = selected.entity {
                if let Ok(root) = model_roots.get(selected_ent) {
                    ui.heading("Selected Pedestrian:");
                    ui.label(format!("Index: {}", root.index));
                    ui.label(format!("Name: {}", root.name));
                    ui.label(format!("Scaled Size: {:.2} x {:.2} x {:.2}", root.size.x, root.size.y, root.size.z));
                }
            } else {
                ui.label("No pedestrian selected");
            }
        });
}

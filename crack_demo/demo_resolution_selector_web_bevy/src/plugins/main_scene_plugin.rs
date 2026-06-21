use bevy::prelude::*;
use bevy::asset::{Asset, AssetLoader, LoadContext, io::Reader};
use bevy::reflect::TypePath;
use bevy::core_pipeline::tonemapping::Tonemapping;
use parquet::file::reader::{FileReader, SerializedFileReader};
use parquet::record::Field;
use bytes::Bytes;

pub struct MainScenePlugin;

impl Plugin for MainScenePlugin {
    fn build(&self, app: &mut App) {
        info!("loading: MainScenePlugin...");
        crate::ui_egui::web_set_loading_status(true, "Loading MainScenePlugin...");
        app.init_asset::<ParquetAsset>()
            .init_asset_loader::<ParquetAssetLoader>()
            .init_resource::<Data3DResource>()
            .add_systems(Startup, (setup_camera_and_load, || {
                crate::ui_egui::web_set_loading_status(false, "");
            }))
            .add_systems(Update, (check_and_parse_parquet, draw_tree_bboxes));
        info!("done loading: MainScenePlugin");
    }
}

#[derive(Asset, TypePath, Debug, Clone)]
pub struct ParquetAsset {
    pub bytes: Vec<u8>,
}

#[derive(Default, TypePath)]
pub struct ParquetAssetLoader;

impl AssetLoader for ParquetAssetLoader {
    type Asset = ParquetAsset;
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
        Ok(ParquetAsset { bytes })
    }

    fn extensions(&self) -> &[&str] {
        &["parquet"]
    }
}

#[derive(Clone, Debug)]
pub struct TreeNode {
    pub name: String,
    pub r#type: String,
    pub level: Option<i32>,
    pub minx: f32,
    pub maxx: f32,
    pub miny: f32,
    pub maxy: f32,
    pub minz: f32,
    pub maxz: f32,
    pub octant_path: String,
    pub filename: Option<String>,
    pub vertex_count: Option<i64>,
}

#[derive(Clone, Debug)]
pub struct TreeChild {
    pub parent_name: String,
    pub child_name: String,
}

#[derive(Clone, Copy, Debug)]
pub struct BBox {
    pub min: Vec3,
    pub max: Vec3,
}

#[derive(Resource, Default, Debug)]
pub struct Data3DResource {
    pub nodes: Vec<TreeNode>,
    pub children: Vec<TreeChild>,
    pub bbox: Option<BBox>,
    pub parsed: bool,
}

#[derive(Resource)]
struct ParquetHandles {
    nodes: Handle<ParquetAsset>,
    children: Handle<ParquetAsset>,
}

fn setup_camera_and_load(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
) {
    // Keep only default camera spawning
    commands.spawn((
        Transform::from_xyz(0.0, 10.5, -30.0).looking_at(Vec3::ZERO, Vec3::Y),
        Camera {
            clear_color: Color::BLACK.into(),
            ..default()
        },
        Camera3d::default(),
        Tonemapping::None,
    ));

    // Load parquet assets from HTTP URL
    let nodes_url = format!("{}/3d_data/tree_nodes.parquet", crate::config::DATA_BASE_URL);
    let children_url = format!("{}/3d_data/tree_children.parquet", crate::config::DATA_BASE_URL);

    info!("Loading nodes from: {}", nodes_url);
    info!("Loading children from: {}", children_url);

    let nodes_handle = asset_server.load(nodes_url);
    let children_handle = asset_server.load(children_url);

    commands.insert_resource(ParquetHandles {
        nodes: nodes_handle,
        children: children_handle,
    });
}

fn get_string(field: Field) -> Option<String> {
    match field {
        Field::Str(s) => Some(s),
        _ => None,
    }
}

fn get_int(field: Field) -> Option<i64> {
    match field {
        Field::Int(v) => Some(v as i64),
        Field::Long(v) => Some(v),
        Field::UInt(v) => Some(v as i64),
        Field::ULong(v) => Some(v as i64),
        Field::Short(v) => Some(v as i64),
        Field::UShort(v) => Some(v as i64),
        Field::Byte(v) => Some(v as i64),
        Field::UByte(v) => Some(v as i64),
        _ => None,
    }
}

fn get_float(field: Field) -> Option<f32> {
    match field {
        Field::Float(v) => Some(v),
        Field::Double(v) => Some(v as f32),
        _ => None,
    }
}

fn parse_tree_nodes(bytes: &[u8]) -> Vec<TreeNode> {
    let bytes_data = Bytes::copy_from_slice(bytes);
    let reader = match SerializedFileReader::new(bytes_data) {
        Ok(r) => r,
        Err(e) => {
            error!("Failed to initialize SerializedFileReader: {:?}", e);
            return Vec::new();
        }
    };
    let mut nodes = Vec::new();
    let row_iter = match reader.get_row_iter(None) {
        Ok(it) => it,
        Err(e) => {
            error!("Failed to get row iterator: {:?}", e);
            return Vec::new();
        }
    };

    for row in row_iter {
        let row = match row {
            Ok(r) => r,
            Err(e) => {
                error!("Error reading node row: {:?}", e);
                continue;
            }
        };
        let mut name = String::new();
        let mut type_ = String::new();
        let mut level = None;
        let mut minx = 0.0;
        let mut maxx = 0.0;
        let mut miny = 0.0;
        let mut maxy = 0.0;
        let mut minz = 0.0;
        let mut maxz = 0.0;
        let mut octant_path = String::new();
        let mut filename = None;
        let mut vertex_count = None;

        for (col_name, field) in row.into_columns() {
            match col_name.as_str() {
                "name" => { name = get_string(field).unwrap_or_default(); }
                "type" => { type_ = get_string(field).unwrap_or_default(); }
                "level" => { level = get_int(field).map(|v| v as i32); }
                "minx" => { minx = get_float(field).unwrap_or(0.0); }
                "maxx" => { maxx = get_float(field).unwrap_or(0.0); }
                "miny" => { miny = get_float(field).unwrap_or(0.0); }
                "maxy" => { maxy = get_float(field).unwrap_or(0.0); }
                "minz" => { minz = get_float(field).unwrap_or(0.0); }
                "maxz" => { maxz = get_float(field).unwrap_or(0.0); }
                "octant_path" => { octant_path = get_string(field).unwrap_or_default(); }
                "filename" => { filename = get_string(field); }
                "vertex_count" => { vertex_count = get_int(field); }
                _ => {}
            }
        }

        nodes.push(TreeNode {
            name,
            r#type: type_,
            level,
            minx,
            maxx,
            miny,
            maxy,
            minz,
            maxz,
            octant_path,
            filename,
            vertex_count,
        });
    }
    nodes
}

fn parse_tree_children(bytes: &[u8]) -> Vec<TreeChild> {
    let bytes_data = Bytes::copy_from_slice(bytes);
    let reader = match SerializedFileReader::new(bytes_data) {
        Ok(r) => r,
        Err(e) => {
            error!("Failed to initialize SerializedFileReader for children: {:?}", e);
            return Vec::new();
        }
    };
    let mut children = Vec::new();
    let row_iter = match reader.get_row_iter(None) {
        Ok(it) => it,
        Err(e) => {
            error!("Failed to get row iterator for children: {:?}", e);
            return Vec::new();
        }
    };

    for row in row_iter {
        let row = match row {
            Ok(r) => r,
            Err(e) => {
                error!("Error reading child row: {:?}", e);
                continue;
            }
        };
        let mut parent_name = String::new();
        let mut child_name = String::new();

        for (col_name, field) in row.into_columns() {
            match col_name.as_str() {
                "parent_name" => { parent_name = get_string(field).unwrap_or_default(); }
                "child_name" => { child_name = get_string(field).unwrap_or_default(); }
                _ => {}
            }
        }

        children.push(TreeChild {
            parent_name,
            child_name,
        });
    }
    children
}

fn check_and_parse_parquet(
    mut commands: Commands,
    handles: Option<Res<ParquetHandles>>,
    mut parquet_assets: ResMut<Assets<ParquetAsset>>,
    mut data_res: ResMut<Data3DResource>,
    mut camera_query: Query<&mut Transform, With<Camera>>,
) {
    if data_res.parsed {
        return;
    }

    if let Some(handles) = handles {
        if parquet_assets.get(&handles.nodes).is_some() && parquet_assets.get(&handles.children).is_some() {
            info!("Both parquet files loaded! Parsing...");

            let nodes_asset = parquet_assets.remove(&handles.nodes).unwrap();
            let children_asset = parquet_assets.remove(&handles.children).unwrap();

            let nodes = parse_tree_nodes(&nodes_asset.bytes);
            let children = parse_tree_children(&children_asset.bytes);

            info!("Parsed {} nodes and {} children links.", nodes.len(), children.len());

            if !nodes.is_empty() {
                let mut min_x = f32::INFINITY;
                let mut max_x = -f32::INFINITY;
                let mut min_y = f32::INFINITY;
                let mut max_y = -f32::INFINITY;
                let mut min_z = f32::INFINITY;
                let mut max_z = -f32::INFINITY;

                for node in &nodes {
                    min_x = min_x.min(node.minx).min(node.maxx);
                    max_x = max_x.max(node.minx).max(node.maxx);
                    min_y = min_y.min(node.miny).min(node.maxy);
                    max_y = max_y.max(node.miny).max(node.maxy);
                    min_z = min_z.min(node.minz).min(node.maxz);
                    max_z = max_z.max(node.minz).max(node.maxz);
                }

                let bbox = BBox {
                    min: Vec3::new(min_x, min_y, min_z),
                    max: Vec3::new(max_x, max_y, max_z),
                };

                info!("Computed entire scene bbox: {:?}", bbox);

                let middle = (bbox.min + bbox.max) / 2.0;
                let size = bbox.max - bbox.min;
                let offset_y = size.y.max(10.0) * 1.2;
                let camera_pos = Vec3::new(bbox.max.x, bbox.max.y + offset_y, bbox.max.z);

                info!("Placing camera at {:?} looking at {:?}", camera_pos, middle);
                for mut cam_transform in &mut camera_query {
                    *cam_transform = Transform::from_translation(camera_pos).looking_at(middle, Vec3::Y);
                }

                data_res.bbox = Some(bbox);
            }

            data_res.nodes = nodes;
            data_res.children = children;
            data_res.parsed = true;

            commands.remove_resource::<ParquetHandles>();
        }
    }
}

fn draw_tree_bboxes(
    mut gizmos: Gizmos,
    data_res: Res<Data3DResource>,
) {
    if !data_res.parsed {
        return;
    }

    let max_level = match data_res.nodes.iter().filter_map(|n| n.level).max() {
        Some(l) => l,
        None => return,
    };

    for node in &data_res.nodes {
        if let Some(level) = node.level {
            if level == max_level || level == max_level - 1 {
                let center = Vec3::new(
                    (node.minx + node.maxx) / 2.0,
                    (node.miny + node.maxy) / 2.0,
                    (node.minz + node.maxz) / 2.0,
                );
                let size = Vec3::new(
                    (node.maxx - node.minx).abs(),
                    (node.maxy - node.miny).abs(),
                    (node.maxz - node.minz).abs(),
                );

                let color = if level == max_level {
                    Color::srgb(0.0, 1.0, 0.0)
                } else {
                    Color::srgb(0.0, 0.5, 1.0)
                };

                let cuboid = Cuboid::new(size.x, size.y, size.z);
                gizmos.primitive_3d(&cuboid, Isometry3d::from_translation(center), color);
            }
        }
    }
}

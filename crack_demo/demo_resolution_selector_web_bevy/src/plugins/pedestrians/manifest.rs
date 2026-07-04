//! Manifest loading + animation-catalog bootstrap.
//!
//! On startup the plugin loads a `.txt` manifest listing pedestrian GLB filenames, recombines
//! each with the manifest folder into a [`PedestrianUrl`], and populates [`PedestrianManifest`].
//! It then loads only the *first* asset to extract the animation catalog (see
//! [`crate::plugins::pedestrians::animation::PedestrianAnimations`]) and drops it — the animation
//! clips stay alive via the shared [`AnimationGraph`]'s strong handles.

use bevy::{
    asset::{Asset, AssetLoader, LoadContext, io::Reader},
    prelude::*,
    reflect::TypePath,
};

use crate::plugins::pedestrians::animation::{AnimationInfo, PedestrianAnimations};

/// A fully-recombined pedestrian asset URL (manifest folder + inner manifest line).
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct PedestrianUrl(pub String);

/// Public manifest resource: the list of available pedestrian URLs and whether loading finished.
#[derive(Resource, Default)]
pub struct PedestrianManifest {
    pub urls: Vec<PedestrianUrl>,
    pub loaded: bool,
}

/// Internal bootstrap state driving the manifest -> first-asset -> catalog pipeline.
#[derive(Resource)]
pub struct ManifestBootstrap {
    /// Folder prefix used to recombine manifest lines into full URLs.
    folder: String,
    /// Handle to the manifest text asset.
    manifest_handle: Handle<TextAsset>,
    /// True once the manifest text was parsed into `PedestrianManifest.urls`.
    urls_parsed: bool,
    /// Handle to the first pedestrian GLB, loaded only to extract the animation catalog.
    first_gltf: Option<Handle<bevy::gltf::Gltf>>,
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

pub fn start_manifest_load(mut commands: Commands, asset_server: Res<AssetServer>) {
    let base_url = crate::config::DATA_BASE_URL.trim_end_matches('/');
    let folder = format!("{}/3d_data/pedestrian_3d_gen/", base_url);
    let manifest_url = format!("{}manifest.txt", folder);
    let manifest_handle = asset_server.load::<TextAsset>(manifest_url);

    commands.insert_resource(ManifestBootstrap {
        folder,
        manifest_handle,
        urls_parsed: false,
        first_gltf: None,
    });
}

pub fn load_pedestrian_manifest_system(
    asset_server: Res<AssetServer>,
    mut bootstrap: ResMut<ManifestBootstrap>,
    mut manifest: ResMut<PedestrianManifest>,
    mut anims: ResMut<PedestrianAnimations>,
    text_assets: Res<Assets<TextAsset>>,
    gltf_assets: Res<Assets<bevy::gltf::Gltf>>,
    clip_assets: Res<Assets<AnimationClip>>,
    mut graphs: ResMut<Assets<AnimationGraph>>,
) {
    // Stage 1: parse the manifest text into recombined URLs, kick off the first asset load.
    if !bootstrap.urls_parsed {
        if let Some(text_asset) = text_assets.get(&bootstrap.manifest_handle) {
            let mut urls = Vec::new();
            for line in text_asset.text.lines() {
                let line = line.trim();
                if line.is_empty() {
                    continue;
                }
                urls.push(PedestrianUrl(format!("{}{}", bootstrap.folder, line)));
            }
            info!("Parsed pedestrian manifest: {} entries.", urls.len());

            if let Some(first) = urls.first() {
                bootstrap.first_gltf = Some(asset_server.load::<bevy::gltf::Gltf>(first.0.clone()));
            }
            manifest.urls = urls;
            bootstrap.urls_parsed = true;
        }
        return;
    }

    // Stage 2: once the first asset is loaded, build the shared animation graph + catalog.
    if manifest.loaded {
        return;
    }
    let Some(first_gltf) = bootstrap.first_gltf.clone() else {
        // No assets in the manifest; mark loaded to unblock consumers.
        manifest.loaded = true;
        return;
    };
    let Some(gltf) = gltf_assets.get(&first_gltf) else {
        return;
    };

    let mut names = std::collections::BTreeSet::new();
    let mut clips = Vec::new();
    let mut clip_to_name = std::collections::HashMap::new();
    for (name, clip_handle) in &gltf.named_animations {
        let name_str = name.to_string();
        if names.insert(name_str.clone()) {
            clips.push(clip_handle.clone());
            clip_to_name.insert(clip_handle.id(), name_str);
        }
    }

    let (graph, node_indices) = AnimationGraph::from_clips(clips.clone());
    let graph_handle = graphs.add(graph);

    let mut nodes = std::collections::HashMap::new();
    let mut catalog = std::collections::BTreeMap::new();
    for (idx, clip_handle) in clips.iter().enumerate() {
        let Some(name) = clip_to_name.get(&clip_handle.id()) else {
            continue;
        };
        let node = node_indices[idx];
        nodes.insert(name.clone(), node);

        let duration = clip_assets
            .get(clip_handle)
            .map(|c| c.duration())
            .unwrap_or(0.0);
        // Frame count is not stored on the clip; approximate at 30 fps for display purposes.
        let frames = (duration * 30.0).round() as u32;
        catalog.insert(
            name.clone(),
            AnimationInfo {
                name: name.clone(),
                duration,
                frames,
                node,
            },
        );
    }

    info!(
        "Pedestrian animation catalog ready: {} animations.",
        catalog.len()
    );

    anims.graph_handle = graph_handle;
    anims.nodes = nodes;
    anims.catalog = catalog;
    anims.ready = true;

    // Drop the first-asset handle; the graph keeps the clips alive.
    bootstrap.first_gltf = None;
    manifest.loaded = true;
}

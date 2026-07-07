use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnimationMeta {
    pub name: String,
    pub duration: f32,
    pub frames: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PedestrianManifestResult {
    pub urls: Vec<String>,
    pub animations: Vec<AnimationMeta>,
}

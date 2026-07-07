use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FetchGlbRequest {
    pub base_url: String,
    pub glb_path: String,
    pub asset_id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FetchGlbResponse {
    pub asset_id: String,
    pub glb_bytes: Vec<u8>,
    pub from_cache: bool,
}

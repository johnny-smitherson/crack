pub mod api_worker;

pub struct WorkerPipe {
    pub req_tx: tokio::sync::mpsc::Sender<WorkerMessage>,
    pub resp_rx: tokio::sync::mpsc::Receiver<WorkerMessage>,
}

#[derive(Clone, serde::Serialize, serde::Deserialize, Debug)]
pub struct WorkerMessage {
    pub msg_id: u32,
    pub msg_type: String,
    pub msg_content: Vec<u8>,
}

#[async_trait::async_trait(?Send)]
pub trait WorkerLoaderFactory {
    async fn load_worker(&self) -> anyhow::Result<WorkerPipe>;
}

#[cfg(test)]
mod tests {
    #[cfg(target_arch = "wasm32")]
    use wasm_bindgen_test::wasm_bindgen_test as test;
    use super::*;

    #[test]
    fn smoke_worker_message_serde_roundtrip() {
        let msg = WorkerMessage {
            msg_id: 7,
            msg_type: "ping".to_string(),
            msg_content: b"abcd".to_vec(),
        };
        let bytes = postcard::to_stdvec(&msg).unwrap();
        let back: WorkerMessage = postcard::from_bytes(&bytes).unwrap();
        assert_eq!(back.msg_id, 7);
        assert_eq!(back.msg_type, "ping");
        assert_eq!(back.msg_content, b"abcd".to_vec());
    }
}

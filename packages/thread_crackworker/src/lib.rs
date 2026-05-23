use std::sync::Arc;

use api_asscrack::crack_worker::{WorkerLoaderFactory, WorkerMessage, WorkerPipe, api_worker::ApiImplMapping};

// Called when the wasm module is instantiated

pub struct ThreadWorkerFactory {
    pub impl_mapping:  Arc<ApiImplMapping>
}

#[api_asscrack::async_trait::async_trait(?Send)]
impl WorkerLoaderFactory for ThreadWorkerFactory {
    async fn load_worker(&self) -> anyhow::Result<WorkerPipe> {
        // let worker_compute = std::sync::Arc::new(ThreadWorkerCompute);
        let t = init_thread(self.impl_mapping.clone()).await?;

        Ok(t)
    }
}

async fn init_thread(mapping:  Arc<ApiImplMapping>) -> anyhow::Result<WorkerPipe> {
    let (req_tx, mut req_rx) = tokio::sync::mpsc::channel::<WorkerMessage>(1024);
    let (resp_tx, resp_rx) = tokio::sync::mpsc::channel(1024);

    let _t = tokio::task::spawn(async move {
        while let Some(req) = req_rx.recv().await {
            let resp_tx = resp_tx.clone();
            let mapping = mapping.clone();
            // let worker_compute = worker_compute.clone();
            tokio::task::spawn(async move {
                let resp = if &req.msg_type == "ping" {
                    let mut new = req.clone();
                    new.msg_type = "pong".to_string();
                    new
                } else {
                    api_asscrack::crack_worker::api_worker::compute_response_message(req, mapping).await
                };
                let m = resp_tx.send(resp).await;
                match m {
                    Ok(_) => {}
                    Err(e) => {
                        tracing::error!("error sending msg: {e:#?}");
                    }
                }
            });
        }
    });

    Ok(WorkerPipe { req_tx, resp_rx })
}

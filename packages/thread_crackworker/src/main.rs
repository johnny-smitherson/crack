use std::sync::Arc;

use api_asscrack::{api::api_worker_declarations::{WorkerApiGroup2, WorkerPing}, crack_worker::{WorkerLoaderFactory, api_worker::make_api_mapping}};
use thread_crackworker::ThreadWorkerFactory;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    use tracing::Level;

    dioxus_logger::init(Level::INFO).expect("logger failed to init");
    tracing::info!("tracing...");

        let _f = ThreadWorkerFactory{impl_mapping: make_api_mapping(vec![
            Arc::new(WorkerApiGroup2),
        ])}.load_worker().await?;

    let c = api_asscrack::api::api_client::ApiClient::new(_f).await;
    c.call::<WorkerPing>(()).await?;

    Ok(())
}

mod test {
    use std::sync::Arc;

use api_asscrack::{api::api_worker_declarations::WorkerApiGroup2, crack_worker::api_worker::make_api_mapping, declare_api_group2, implement_api_group2};

    #[tokio::test]
    async fn test_api_rx_tx_ping() -> anyhow::Result<()> {
        use api_asscrack::crack_worker::{WorkerLoaderFactory, WorkerMessage};
        use thread_crackworker::ThreadWorkerFactory;

        let mut f = ThreadWorkerFactory{impl_mapping: make_api_mapping(vec![
        ])}.load_worker().await?;

        f.req_tx
            .send(WorkerMessage {
                msg_id: 0,
                msg_type: "ping".to_string(),
                msg_content: "abcd".to_string().as_bytes().to_vec(),
            })
            .await?;
        let t = f.resp_rx.recv().await.unwrap();
        assert!(t.msg_type == "pong");
        assert!(t.msg_content == "abcd".as_bytes().to_vec());
        Ok(())
    }

    #[tokio::test]
    async fn test_api_ping_fn() -> anyhow::Result<()> {
        use api_asscrack::crack_worker::WorkerLoaderFactory;
        use thread_crackworker::ThreadWorkerFactory;
        let f = ThreadWorkerFactory{impl_mapping: make_api_mapping(vec![
            Arc::new(WorkerApiGroup2),
            Arc::new(TestApiGroup),
        ])}.load_worker().await?;
        let c = api_asscrack::api::api_client::ApiClient::new(f).await;

        let _r = c
            .call::<api_asscrack::api::api_worker_declarations::WorkerPing>(())
            .await?;

        let _r2 = c.call::<TestPing>((1, 2)).await?;
        assert!(_r2 == 3);
        Ok(())
    }

    declare_api_group2! {
        TestApiGroup,
        [
            (TestPing, (i32, i32), i32),
        ]
    }

    mod __impl {
        use api_asscrack::implement_api_group2;
        use super::{TestApiGroup,TestPing};

        implement_api_group2! {
            TestApiGroup,
            [
                (TestPing, test_ping),
            ]
        }

        async fn test_ping((x, y): (i32, i32)) -> anyhow::Result<i32> {
            Ok(x + y)
        }
    }
}

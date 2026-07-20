pub use n0_future;

pub fn get_timestamp_now_ms() -> i64 {
    chrono::offset::Utc::now().timestamp_millis()
}

pub fn spawn<F>(f: F) -> n0_future::task::JoinHandle<F::Output>
where
    F: Future + Send + 'static,
    F::Output: Send + 'static,
{
    n0_future::task::spawn(f)
}

pub fn random_u32() -> u32 {
    ::rand::random()
}

pub async fn sleep_ms(dt_ms: u32) {
    let _sleep = n0_future::time::sleep(std::time::Duration::from_millis(dt_ms as u64)).await;
}

#[cfg(test)]
mod tests {
    #[cfg(target_arch = "wasm32")]
    use wasm_bindgen_test::wasm_bindgen_test as test;
    use super::*;

    #[test]
    fn smoke_get_timestamp_now_ms() {
        let ts = get_timestamp_now_ms();
        assert!(ts > 0, "timestamp should be positive, got {ts}");
    }

    #[test]
    fn smoke_random_u32() {
        // Two draws should (overwhelmingly) differ; guards against a stubbed RNG.
        assert_ne!(random_u32(), random_u32());
    }

    async fn sleep_ms_body() {
        let before = get_timestamp_now_ms();
        sleep_ms(20).await;
        let elapsed = get_timestamp_now_ms() - before;
        assert!(elapsed >= 15, "sleep_ms(20) returned after {elapsed}ms");
    }

    #[cfg(not(target_arch = "wasm32"))]
    #[tokio::test]
    async fn smoke_sleep_ms() {
        sleep_ms_body().await;
    }

    #[cfg(target_arch = "wasm32")]
    #[wasm_bindgen_test::wasm_bindgen_test]
    async fn smoke_sleep_ms() {
        sleep_ms_body().await;
    }
}

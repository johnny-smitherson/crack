# thread_crackworker

Native (tokio-thread) implementation of the `api_asscrack` worker abstraction.
`ThreadWorkerFactory` implements `WorkerLoaderFactory` by spawning a tokio task
that dispatches incoming `WorkerMessage`s to an `ApiImplMapping` and sends
responses back over an mpsc channel — the thread-based counterpart to a real
web worker, so the same `ApiClient`/`ApiImplMapping` code paths can be used and
tested natively.

## Usage

```rust
use std::sync::Arc;
use api_asscrack::api::api_client::ApiClient;
use api_asscrack::api::api_worker_declarations::{WorkerApiGroup2, WorkerPing};
use api_asscrack::crack_worker::{WorkerLoaderFactory, api_worker::make_api_mapping};
use thread_crackworker::ThreadWorkerFactory;

let pipe = ThreadWorkerFactory {
    impl_mapping: make_api_mapping(vec![Arc::new(WorkerApiGroup2)]),
}
.load_worker()
.await?;

let client = ApiClient::new(pipe);
let _ = client.call::<WorkerPing>(()).await?;
```

Messages with `msg_type == "ping"` are short-circuited to a `"pong"` echo
without touching the mapping; everything else goes through
`compute_response_message`.

## Gotchas

- Native-only: depends on `tokio` (full) and spawns real tasks; it is not
  built for `wasm32`.
- The `ApiClient::call::<WorkerPing>(())` round-trip here is the canonical ping
  path other crates copy — keep it working.

## Tests

`./test.sh` runs `cargo test` (native only, no wasm target). The inline
`#[tokio::test]` smoke tests cover the raw ping/pong channel echo and the
`ApiClient` round-trip through `make_api_mapping` (built-in `WorkerPing` plus a
local `TestPing` group2 API).

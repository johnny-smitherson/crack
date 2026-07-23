# thread_crackworker

Native tokio-thread `WorkerLoaderFactory` for `api_asscrack`: spawns a task
that routes `WorkerMessage`s to an `ApiImplMapping`, short-circuiting
`"ping"` → `"pong"`. Native-only (`tokio` full); not built for `wasm32`. The
`make_api_mapping` + `ApiClient::call::<WorkerPing>(())` round-trip is the
canonical ping path other crates copy — don't break it.

Run tests with `./test.sh` (native `cargo test` only). See `README.md`.

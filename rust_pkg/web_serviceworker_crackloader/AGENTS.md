# web_serviceworker_crackloader

Browser-wasm **only** loader: `WebWorkerFactory` implements
`api_asscrack::crack_worker::WorkerLoaderFactory`, bridging Rust to a
JS-managed dedicated worker via the page-global `init_workers2()` extern and
returning a `WorkerPipe` (tokio mpsc of `WorkerMessage`). Everything runs
through `web_sys::window()` / `wasm_bindgen_futures::spawn_local` — there is
no native target. Never set `RUSTFLAGS` (the root `.cargo/config.toml` wires
`getrandom_backend="wasm_js"` for wasm32).

Run tests with `./test.sh` (`wasm-pack test --headless --firefox --chrome`,
with `GECKODRIVER`/`CHROMEDRIVER` exported). See `README.md` for details.

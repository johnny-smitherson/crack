# web_serviceworker_crackloader

Browser-wasm loader that bridges Rust to a JS-managed dedicated worker.
`WebWorkerFactory` implements `api_asscrack::crack_worker::WorkerLoaderFactory`:
`load_worker()` calls the page-global JS hook `init_workers2()` (via a
`wasm-bindgen` extern), ping-pongs until the worker answers, then returns a
`WorkerPipe` (tokio mpsc channels of `WorkerMessage`) that forwards requests to
the worker and routes responses back.

Inspired by https://github.com/justinrubek/wasm-bindgen-service-worker/tree/main/crates/loader

## Usage

```rust
use api_asscrack::crack_worker::WorkerLoaderFactory;
use web_serviceworker_crackloader::WebWorkerFactory;

let factory = WebWorkerFactory {};
let pipe = factory.load_worker().await?; // needs `window.init_workers2` defined by the page
```

## Gotchas

- Browser wasm only: everything goes through `web_sys::window()`,
  `wasm_bindgen` externs and `wasm_bindgen_futures::spawn_local`. There is no
  native `cargo test` target.
- The page must define a global `init_workers2()` returning an object with
  `send_message(js_value)` and `set_onmessage(callback)`; `load_worker()`
  polls `window.has_own_property("init_workers2")` for ~3s (20 × 150ms) and
  bails if the hook never shows up.
- Never set `RUSTFLAGS` in scripts — the workspace root `.cargo/config.toml`
  sets `--cfg getrandom_backend="wasm_js"` for wasm32 and env `RUSTFLAGS`
  would clobber it.

## Tests

`./test.sh` runs `wasm-pack test --headless --firefox --chrome` with
`GECKODRIVER`/`CHROMEDRIVER` exported so the container-installed drivers are
reused offline. The smoke test only constructs the factory (and boxes it as
`dyn WorkerLoaderFactory`); it does not require a real service-worker
registration.

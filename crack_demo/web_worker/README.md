# web_worker

Browser-only wasm `cdylib` that runs inside a Dedicated Web Worker. On module
start (`#[wasm_bindgen(start)] init_worker`) it initializes the logger, kicks
off the network bootstrap (`run_bootstrap_if_needed`), and registers the
worker message handler via
`web_serviceworker_crackslave::web_worker_registration` with an API mapping
built from three groups: `StorageCrackhouseApiGroup`, `WorkerApiGroup2`, and
`game_logic::api::GameLogicApiGroup`.

## Usage

The crate is loaded as a wasm module by the loader side
(`web_serviceworker_crackloader`); it is not called directly from Rust.
The JS entry points are re-exported from `web_serviceworker_crackslave`:
`_js_init_dedicated_worker` and `_js_compute_payload_reply`.

## Gotchas

- Wasm-only: do **not** add the workspace `tokio` dependency here — its `full`
  feature set pulls in `mio`/`net` and fails to compile for wasm (see the note
  in `Cargo.toml`).
- `crate-type` includes `rlib` alongside `cdylib` so `wasm-pack test` can link
  the test harness.
- `web_worker_registration` stores the mapping in a `OnceLock` and the
  `#[wasm_bindgen(start)]` function already sets it when the test binary
  loads, so tests must not call it again — they exercise `make_api_mapping` /
  `compute_response_message` directly instead.
- `.cargo/cargo.toml` in this directory is a misnamed, inert file (cargo only
  reads `.cargo/config.toml`); the wasm target is selected by `wasm-pack`
  itself. It is left as-is.
- Never set `RUSTFLAGS` — the workspace root `.cargo/config.toml` sets
  `--cfg getrandom_backend="wasm_js"` for wasm32 and env RUSTFLAGS would
  clobber it.

## Tests

`./test.sh` runs `wasm-pack test --headless --firefox --chrome` with
`GECKODRIVER`/`CHROMEDRIVER` exported so the installed drivers are reused
offline. Two smoke tests build the same `make_api_mapping(...)` composition as
`init_worker()` and check that dispatching an unknown method returns the
missing-key error message.

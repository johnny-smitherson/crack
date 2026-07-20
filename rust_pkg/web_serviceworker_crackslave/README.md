# web_serviceworker_crackslave

Browser-wasm-only crate that runs inside a dedicated worker: it exposes the
JS entry points `initDedicatedWorker` (`_js_init_dedicated_worker`, installs
the OPFS SAH-pool storage) and `computePayloadReply` (`_js_compute_payload_reply`,
dispatches `WorkerMessage` payloads to the registered API mapping and replies),
plus `web_worker_registration` for installing the `ApiImplMapping` once.
Architecture reference:
https://github.com/justinrubek/wasm-bindgen-service-worker/tree/main/crates/worker

## Usage

```rust
web_serviceworker_crackslave::web_worker_registration(mapping).await?;
// then, from JS: await initDedicatedWorker(); await computePayloadReply(msg);
```

## Gotchas

- Needs a real `DedicatedWorkerGlobalScope` at runtime: `js_sys::global()` and
  the OPFS SAH-pool install only work inside an actual dedicated worker, not
  in a window or under node.
- `.cargo/cargo.toml` (which would set `build.target = "wasm32-unknown-unknown"`)
  is **inert**: cargo only reads `.cargo/config.toml`. It is left untouched on
  purpose; builds rely on the workspace root config and on `wasm-pack` passing
  the target explicitly. Never set `RUSTFLAGS` in scripts — it would clobber
  the root `.cargo/config.toml` `--cfg getrandom_backend="wasm_js"` for wasm32.

## Tests

`./test.sh` runs `wasm-pack test --headless --firefox --chrome` with
`GECKODRIVER`/`CHROMEDRIVER` exported (installed drivers, offline). Because a
real worker scope is unavailable in the test harness, the ONLY test is a
`links()` build/link smoke (`#[wasm_bindgen_test]`) that takes the addresses
of the public functions and constructs a `WorkerMessage` without invoking any
worker-scope APIs.

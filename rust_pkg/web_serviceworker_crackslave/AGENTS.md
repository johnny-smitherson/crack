# web_serviceworker_crackslave

Browser-wasm-only dedicated-worker crate: JS entry points `initDedicatedWorker`
/ `computePayloadReply` and `web_worker_registration` (installs the
`ApiImplMapping` once). Runtime requires a real `DedicatedWorkerGlobalScope`,
so the ONLY test is a `links()` build/link smoke — run with `./test.sh`
(`wasm-pack test --headless --firefox --chrome`, GECKODRIVER/CHROMEDRIVER
exported). `.cargo/cargo.toml` is inert (misnamed; should be `config.toml`) and
deliberately left as-is. Never set `RUSTFLAGS`. See `README.md` for details.

## Auto-generated signatures
<!-- Updated by gen-context.js -->
# Code signatures

## SigMap commands

| When | Command |
|------|---------|
| Before answering a question about code | `sigmap ask "<your question>"` |
| To rank files by topic | `sigmap --query "<topic>"` |
| After changing config or source dirs | `sigmap validate` |
| To verify an AI answer is grounded | `sigmap judge --response <file>` |

Always run `sigmap ask` (or `sigmap --query`) before searching for files relevant to a task.

## .

### README.md
```
h1 web_serviceworker_crackslave
h2 Usage
h2 Gotchas
h2 Tests
code-fence rust
code-fence plain
```

### test.sh
```
# Browser-wasm link smoke test for web_serviceworker_crackslave.
```

## src

### src/lib.rs
```
pub async fn _js_init_dedicated_worker() → Result<(), JsValue>
pub async fn _js_compute_payload_reply(msg: JsValue) → Result<JsValue, JsValue>
pub async fn web_worker_registration(mapping: Arc<ApiImplMapping>,) → std::result::Result<(), JsV...
```

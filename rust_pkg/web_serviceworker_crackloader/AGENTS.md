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
h1 web_serviceworker_crackloader
h2 Usage
h2 Gotchas
h2 Tests
code-fence rust
code-fence plain
```

### test.sh
```
# Smoke tests for web_serviceworker_crackloader: browser wasm only (headless firefox + chrome).
```

## src

### src/lib.rs
```
pub struct WebWorkerFactory
impl WebWorkerFactory
```

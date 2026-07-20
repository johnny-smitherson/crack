# web_worker

Browser-only wasm `cdylib` running inside a Dedicated Web Worker: on start it
registers the worker handler with `make_api_mapping(vec![StorageCrackhouseApiGroup,
WorkerApiGroup2, game_logic::api::GameLogicApiGroup])` via
`web_serviceworker_crackslave::web_worker_registration`. Wasm-only — never add
the workspace `tokio` dep (breaks wasm builds). `.cargo/cargo.toml` here is
misnamed and inert; leave it. Never set `RUSTFLAGS` (root `.cargo/config.toml`
wires the getrandom `wasm_js` backend).

Run tests with `./test.sh` (browser wasm only: `wasm-pack test --headless
--firefox --chrome`). See `README.md` for details.

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

## src

### src/lib.rs
```
pub async fn run_bootstrap_if_needed() → anyhow::Result<()>
```

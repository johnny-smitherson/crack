# thread_crackworker

Native tokio-thread `WorkerLoaderFactory` for `api_asscrack`: spawns a task
that routes `WorkerMessage`s to an `ApiImplMapping`, short-circuiting
`"ping"` → `"pong"`. Native-only (`tokio` full); not built for `wasm32`. The
`make_api_mapping` + `ApiClient::call::<WorkerPing>(())` round-trip is the
canonical ping path other crates copy — don't break it.

Run tests with `./test.sh` (native `cargo test` only). See `README.md`.

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
pub struct ThreadWorkerFactory
impl ThreadWorkerFactory
```

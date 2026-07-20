# _crack_utils

Cross-platform (native + wasm) utilities: `get_timestamp_now_ms`, `random_u32`,
`sleep_ms`, `spawn` (via `n0_future`). On wasm, chrono uses `wasmbind` and
getrandom uses the `wasm_js` backend wired in the **root** `.cargo/config.toml`
— never set `RUSTFLAGS` in scripts, it clobbers that config. `tokio` is
native-only.

Run tests with `./test.sh` (native `cargo test` + `wasm-pack test --node`).
See `README.md` for details.

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
pub fn get_timestamp_now_ms() → i64
pub fn spawn(f: F) → n0_future::task::JoinHandle...
pub fn random_u32() → u32
pub async fn sleep_ms(dt_ms: u32)
```

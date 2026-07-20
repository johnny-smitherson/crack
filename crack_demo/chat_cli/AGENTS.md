# chat_cli

Headless CLI client for the global chat over `net_crackpipe`: generates a
`UserIdentitySecrets`, inits a `NetworkManager` with
`game_logic::network::network_manager_config()` (so a bootstrap-slot winner
also carries the gameplay topic), then bridges stdin lines to chat broadcasts
and prints incoming messages. Stdout protocol: `SELF`/`READY`/`SENT`/`RECV`
lines. Native-only (`tokio` multi-thread), no wasm target.

Run tests with `./test.sh` (native `cargo test` only). See `README.md` for
details.

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

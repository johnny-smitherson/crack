# chat_cli

Headless CLI client for the global chat over `net_crackpipe`: generates a
`UserIdentitySecrets`, inits a `NetworkManager` with
`game_logic::network::network_manager_config()` (so a bootstrap-slot winner
also carries the gameplay topic), then bridges stdin lines to chat broadcasts
and prints incoming messages. Stdout protocol: `SELF`/`READY`/`SENT`/`RECV`
lines. Native-only (`tokio` multi-thread), no wasm target.

Run tests with `./test.sh` (native `cargo test` only). See `README.md` for
details.

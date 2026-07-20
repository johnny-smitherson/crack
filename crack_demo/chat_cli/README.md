# chat_cli

Headless CLI client for the global chat: connects to the p2p network via
`net_crackpipe::NetworkManager` using the game's network config
(`game_logic::network::network_manager_config`), joins the global chat room,
and bridges stdin/stdout to chat messages.

## Usage

```sh
cargo run -p chat_cli
```

Line-based protocol on stdout/stdin:

- `SELF <nickname>` — printed once the local identity is generated.
- `READY <nickname>` — printed once at least 2 peers have joined.
- Type a line on stdin to broadcast it; `SENT <text>` confirms the send.
- `RECV <nickname> <text>` — an incoming message from another peer.

Logging goes through `tracing_subscriber` and honors `RUST_LOG`
(default `info`).

## Gotchas

- The binary intentionally uses the game network config (not a chat-only one)
  so that a process which wins a bootstrap slot also carries the gameplay
  topic.
- Native-only crate (`tokio` multi-thread runtime); there is no wasm target.

## Tests

`./test.sh` runs `cargo test` (native only). The smoke test in
`src/main.rs` asserts that `game_logic::network::network_manager_config()`
builds with the gameplay topic in `bootstrap_topics`.

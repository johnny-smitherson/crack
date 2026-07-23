# net_crackpipe

iroh-gossip chat networking: typed rooms (`ChatController`/`ChatSender`/
`ChatReceiver` over `IChatRoomType`), signed postcard wire messages, presence,
tickets, `UserIdentitySecrets`, `SleepManager`. Edition **2021** (rest of the
workspace is 2024) — intentional, leave it.

Two living-guard gotchas (regression-tested in `src/chat/chat_controller.rs`):
- A `ChatController` must be owned for the room's whole life — cloning the
  sender/receiver does NOT keep dispatch/presence alive; dropping the last
  controller clone aborts those tasks and the room silently dies.
- High-rate gossip rooms need `sender().join_peers(...)`, not bootstrap-only
  relay.

On wasm, getrandom/uuid use the `wasm_js`/`js` features; never set `RUSTFLAGS`
(the root `.cargo/config.toml` sets the `getrandom_backend` cfg). Run tests
with `./test.sh` (native `cargo test` + `wasm-pack test --headless --firefox
--chrome`; browser required, node is not enough). See `README.md` for details.

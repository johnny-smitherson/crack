# net_crackpipe

Networking crate for the workspace: iroh-gossip chat rooms with signed
messages, presence/ping tracking, direct messages, and the global matchmaker.
Key pieces:

- `chat::chat_controller` — `ChatController<T>` / `ChatSender<T>` /
  `ChatReceiver<T>` over a typed room (`IChatRoomType` with message `M` and
  presence `P` payloads), plus the `IChatRoomRaw` transport trait.
- `chat::room_raw` — `GossipChatRoom`, the iroh-gossip implementation of
  `IChatRoomRaw`.
- `chat::chat_ticket` — `ChatTicket` (topic id + bootstrap node set);
  `ChatTicket::new_str_bs` maps a string topic (max 30 bytes) into a 32-byte
  `TopicId`.
- `signed_message` — `MessageSigner` / `SignedMessage` postcard-encoded and
  dual-signed (node key + user key) wire format.
- `user_identity` — `UserIdentitySecrets::generate`, nicknames and colors
  derived from the public key.
- `sleep` — `SleepManager`, a wakeable sleep used by the room loops.

Note: this crate is **edition 2021** while the rest of the workspace is 2024 —
left as-is on purpose.

## Usage

```rust
let secrets = net_crackpipe::user_identity::UserIdentitySecrets::generate();
let ticket = net_crackpipe::chat::chat_ticket::ChatTicket::new_str_bs(
    "my-room",
    Default::default(),
);
let controller = node.join_chat::<MyRoomType>(&ticket).await?;
let sender = controller.sender();
sender.broadcast_message(my_message).await?;
```

## Gotchas

- **ChatController lifetime foot-gun:** a `ChatController` must be owned for
  the room's whole life. Its dispatch and presence tasks are
  `AbortOnDropHandle`s held *only* by the controller — cloning the
  sender/receiver does **not** keep them alive. Dropping the last controller
  clone silently kills the room (no more inbound dispatch or presence pings)
  even while cloned senders still appear to work.
- **High-rate gossip rooms need `join_peers`, not bootstrap-only relay.**
  Bootstrap peers in the ticket get the room started, but for busy
  multiplayer rooms you must call `sender().join_peers(vec![node_id, ...])`
  (forwarded to `GossipSender::join_peers`) so the swarm actually meshes;
  relying on the bootstrap set alone leaves peers relay-starved.
- On `wasm32`, `uuid` uses the `js` feature and the transitive `getrandom`
  0.3 uses `wasm_js`; the workspace root `.cargo/config.toml` sets
  `--cfg getrandom_backend="wasm_js"`. Never set `RUSTFLAGS` in scripts — it
  clobbers that config.
- `SleepManager::wake_up` interrupts the current wait but the sleep loop
  re-sleeps for the remaining duration; it does not shorten the total sleep.

## Tests

`./test.sh` runs `cargo test` (native) and
`wasm-pack test --headless --firefox --chrome` (the crate pulls
`rand` → `getrandom`, so wasm tests need a real browser; node is **not**
sufficient). `test.sh` exports `GECKODRIVER`/`CHROMEDRIVER`/`CHROME_BIN` to
reuse the container's offline-installed drivers.

One smoke test per module, using the dual `#[tokio::test]` /
`#[wasm_bindgen_test]` wrapper pattern. Two native-only regression tests live
at the bottom of `src/chat/chat_controller.rs` guarding the two gotchas
above (controller lifetime, `join_peers` plumbing).

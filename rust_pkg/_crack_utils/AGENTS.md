# _crack_utils

Cross-platform (native + wasm) utilities: `get_timestamp_now_ms`, `random_u32`,
`sleep_ms`, `spawn` (via `n0_future`). On wasm, chrono uses `wasmbind` and
getrandom uses the `wasm_js` backend wired in the **root** `.cargo/config.toml`
— never set `RUSTFLAGS` in scripts, it clobbers that config. `tokio` is
native-only.

Run tests with `./test.sh` (native `cargo test` + `wasm-pack test --node`).
See `README.md` for details.

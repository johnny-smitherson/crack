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

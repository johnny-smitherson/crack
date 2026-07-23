# api_asscrack

Typed worker-API RPC framework: `declare_api_group2!` / `implement_api_group2!`
macros generate declaration structs and (de)serializing wrappers;
`ApiClient` calls methods over a `WorkerPipe` (`msg_id`-matched oneshots);
`make_api_mapping` + `compute_response_message` dispatch on the worker side.
Built-in `WorkerApiGroup2` provides the canonical `WorkerPing`. Payloads are
`postcard`-serialized; `make_api_mapping` panics on duplicate or mismatched
declarations/impls. Async runs via `_crack_utils`/`n0_future` (tokio native,
browser/node wasm) — never set `RUSTFLAGS` in scripts.

Run tests with `./test.sh` (native `cargo test` + `wasm-pack test --node`).
See `README.md` for details.

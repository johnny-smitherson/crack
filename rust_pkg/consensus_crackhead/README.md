# consensus_crackhead

Placeholder crate for the future consensus logic of the workspace. `src/lib.rs`
is currently empty apart from the test module — there is no public API yet.

## Usage

Nothing to use yet. Add the crate as a dependency once it exposes an API.

## Gotchas

- The crate intentionally has no dependencies; keep it that way until real
  consensus code lands.
- The workspace root `.cargo/config.toml` sets `--cfg
  getrandom_backend="wasm_js"` for wasm32. Do not override `RUSTFLAGS` in
  scripts — it would clobber that config.

## Tests

`./test.sh` runs `cargo test` (native) and `wasm-pack test --node`. There is a
single dual-target link smoke test (`#[test] fn smoke() {}`) proving the crate
compiles and links on both targets.

# _crack_utils

Small cross-platform (native + wasm) utility crate shared by the rest of the
workspace: wall-clock timestamps (`get_timestamp_now_ms`), randomness
(`random_u32`), async sleeping (`sleep_ms`) and a `spawn` helper that delegates
to `n0_future` so the same code runs on tokio (native) and the browser event
loop (wasm).

## Usage

```rust
let now = _crack_utils::get_timestamp_now_ms();
_crack_utils::sleep_ms(50).await;
let handle = _crack_utils::spawn(async move { 42 });
```

## Gotchas

- On `wasm32`, `chrono` is compiled with the `wasmbind` feature and
  `getrandom` with `wasm_js` (see the target-specific dependencies in
  `Cargo.toml`); the workspace root `.cargo/config.toml` additionally sets
  `--cfg getrandom_backend="wasm_js"` for transitive `getrandom` users. Do not
  override `RUSTFLAGS` in scripts — it would clobber that config.
- `tokio` is only a dependency on non-wasm targets; on wasm, `spawn`/`sleep_ms`
  go through `n0_future` instead.

## Tests

`./test.sh` runs `cargo test` (native) and `wasm-pack test --node`. One smoke
test per public function; async tests use the dual `#[tokio::test]` /
`#[wasm_bindgen_test]` wrapper pattern.

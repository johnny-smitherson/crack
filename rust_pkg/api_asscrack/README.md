# api_asscrack

Typed RPC framework for talking to workers (native threads or browser web
workers) over a `WorkerPipe` of serialized `WorkerMessage`s. API surface is
declared with macros and dispatched by fully-qualified name (`Group.Method`):

- `api::api_method_macros` — the core traits (`ApiGroupDecl`,
  `ApiGroupMethods`, `ApiGroupImpls`, `ApiMethodDecl`) and the
  `declare_api_group2!` / `implement_api_group2!` macros that generate the
  declaration structs and the (de)serializing wrappers.
- `api::api_worker_declarations` — the built-in `WorkerApiGroup2` group with
  the canonical `WorkerPing` method.
- `api::api_client` — `ApiClient`, which sends requests over a `WorkerPipe`
  and matches responses to pending calls by `msg_id`.
- `crack_worker` — `WorkerPipe` / `WorkerMessage` / `WorkerLoaderFactory`,
  plus `api_worker::make_api_mapping` and `compute_response_message`, the
  worker-side dispatch table.

## Usage

```rust
// Worker side: build the dispatch mapping from implemented groups.
let mapping = make_api_mapping(vec![Arc::new(WorkerApiGroup2)]);
let resp = compute_response_message(req, mapping).await;

// Client side: call a declared method over the pipe.
let client = ApiClient::new(pipe);
client.call::<WorkerPing>(()).await?;
```

Declaring a new API group:

```rust
declare_api_group2! {
    MyGroup,
    [
        (MyMethod, (i32, i32), i32),
    ]
}

implement_api_group2! {
    MyGroup,
    [
        (MyMethod, my_method),
    ]
}

async fn my_method((x, y): (i32, i32)) -> anyhow::Result<i32> {
    Ok(x + y)
}
```

## Gotchas

- `make_api_mapping` **panics** if declarations and implementations don't
  line up (duplicate names, or a count mismatch between declared and
  implemented methods) — every declared method must be implemented exactly
  once.
- Arguments and return values are serialized with `postcard`; worker-side
  errors come back as `Result<Ret, String>` inside the `msg_content`, and
  deserialization failures surface as non-`"return"` `msg_type`s.
- `tokio` is used with only the `sync` feature on wasm; the async runtime is
  provided by `n0_future` (via `_crack_utils`) so the same code runs on tokio
  (native) and the browser/node event loop (wasm).

## Tests

`./test.sh` runs `cargo test` (native) and `wasm-pack test --node`. One smoke
test per module; the client/worker tests run the canonical `WorkerPing`
round-trip against an in-process worker, and async tests use the dual
`#[tokio::test]` / `#[wasm_bindgen_test]` wrapper pattern.

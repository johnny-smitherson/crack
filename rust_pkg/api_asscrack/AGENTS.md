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

## Auto-generated signatures
<!-- Updated by gen-context.js -->
# Code signatures

## SigMap commands

| When | Command |
|------|---------|
| Before answering a question about code | `sigmap ask "<your question>"` |
| To rank files by topic | `sigmap --query "<topic>"` |
| After changing config or source dirs | `sigmap validate` |
| To verify an AI answer is grounded | `sigmap judge --response <file>` |

Always run `sigmap ask` (or `sigmap --query`) before searching for files relevant to a task.

## todos
```
src/crack_worker/api_worker.rs:50  # TODO: get which is missing...
```

## .

### README.md
```
h1 api_asscrack
h2 Usage
h2 Gotchas
h2 Tests
code-fence rust
code-fence plain
```

### test.sh
```
# Smoke tests for api_asscrack: native + wasm (node).
```

## src

### src/api/api_client.rs
```
pub struct ApiClient
pub struct MessageLater
impl ApiClient
  pub fn new(pipe: WorkerPipe) → Self
  pub async fn call(&self, arg: T::Arg) → anyhow::Result<T::Ret>
```

### src/api/api_method_macros.rs
```
pub struct ApiGroupDeclStatic
pub struct ApiMethodInfo
pub struct ApiMethodImpl
pub trait ApiGroupDecl
pub trait ApiGroupMethods
pub trait ApiGroupImpls
pub trait ApiMethodDecl
impl ApiMethodImpl
  pub fn fullname(&self) → String
impl ApiMethodInfo
  pub fn fullname(&self) → String
```

### src/api/api_worker_declarations.rs
```
pub async fn worker_ping(_x: () → anyhow::Result<()>
```

### src/crack_worker/api_worker.rs
```
pub struct ApiImplMapping
pub fn make_api_mapping(groups: Vec<Arc<dyn ApiGroupImpls>>) → Arc<ApiImplMapping>
pub async fn compute_response_message(_request: WorkerMessage, mapping: Arc<ApiImplMapping>,) → WorkerMessage
```

### src/crack_worker/mod.rs
```
pub struct WorkerPipe
pub struct WorkerMessage
pub trait WorkerLoaderFactory
```

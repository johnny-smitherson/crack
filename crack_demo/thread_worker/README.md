# thread_worker

Native demo crate that spins up an in-process worker on a tokio thread and
talks to it through the `api_asscrack` API-mapping machinery.
`spawn_in_process_worker()` builds an `ApiImplMapping` from the registered API
groups (`WorkerApiGroup2`, `StorageCrackhouseApiGroup`, `GameLogicApiGroup`)
and loads a `WorkerPipe` via `ThreadWorkerFactory`; the binary in `src/main.rs`
then wraps the pipe in an `ApiClient`, pings it with `WorkerPing`, and loops
reading SQL from stdin to execute through `ExecuteSQL2`.

## Usage

```rust
use crack::api_asscrack::api::{api_client::ApiClient, api_worker_declarations::WorkerPing};

let pipe = thread_worker::spawn_in_process_worker().await?;
let client = ApiClient::new(pipe);
client.call::<WorkerPing>(()).await?;
```

## Gotchas

- `spawn_in_process_worker()` also fires off a detached
  `run_bootstrap_if_needed()` task (network bootstrap via `net_crackpipe`);
  failures there are only logged with `tracing::error!`, never propagated, so
  the worker itself still comes up when the bootstrap cannot run.
- The worker is in-process: requests and responses travel over tokio mpsc
  channels (`WorkerPipe`), not over a real WebWorker boundary.
- Native-only crate; there are no wasm tests here.

## Tests

`./test.sh` runs `cargo test` (native). The smoke test spawns the in-process
worker and pings it with `WorkerPing` through `ApiClient`, mirroring the
canonical ping path in `rust_pkg/thread_crackworker`.

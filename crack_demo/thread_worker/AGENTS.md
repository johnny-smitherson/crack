# thread_worker

Native demo crate: `spawn_in_process_worker()` builds the registered
`ApiImplMapping` (`WorkerApiGroup2`, `StorageCrackhouseApiGroup`,
`GameLogicApiGroup`) and loads an in-process `WorkerPipe` through
`ThreadWorkerFactory`. `src/main.rs` wraps the pipe in an `ApiClient`, pings it
with `WorkerPing`, then executes stdin SQL via `ExecuteSQL2`. The bootstrap
task spawned by `spawn_in_process_worker()` logs errors but never fails the
worker. See `README.md` for usage and gotchas; `./test.sh` runs the native
smoke tests.

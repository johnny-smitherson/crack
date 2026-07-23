# web_serviceworker_crackslave

Browser-wasm-only dedicated-worker crate: JS entry points `initDedicatedWorker`
/ `computePayloadReply` and `web_worker_registration` (installs the
`ApiImplMapping` once). Runtime requires a real `DedicatedWorkerGlobalScope`,
so the ONLY test is a `links()` build/link smoke — run with `./test.sh`
(`wasm-pack test --headless --firefox --chrome`, GECKODRIVER/CHROMEDRIVER
exported). `.cargo/cargo.toml` is inert (misnamed; should be `config.toml`) and
deliberately left as-is. Never set `RUSTFLAGS`. See `README.md` for details.

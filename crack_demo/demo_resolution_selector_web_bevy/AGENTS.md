We are using bevy 0.19 - there is no more `despawn_recursive()`, just `despawn()` - when in doubt, use `cargo doc into a temp dir` and read the documentation from disk.

Check the code builds by running `cargo check --package ...` from this directory. 

When working on a binary command, you can run it with `cd ... && bash timeout 15s cargo run --bin ... --package ...` from this directory, to verify the code does not crash.

This code is supposed to be cross-platform, to work on both browser and native hosts. That means:
- do not use std::Instant::now() as it panics on wasm
- do not use threads. Intead, we will declare API routes to be used in the web worker, see `crack_demo/web_worker` for the web implementation and `crack_demo/thread_worker` for the host implementation.
- do not do heavy computation in bevy; make an async task and call into the worker using a `declare_api_method_group!` declaration

## Headless tests

`src/basic_app.rs` has `make_headless_app(title)` next to `make_basic_app`: same
memory asset source, `AssetMetaCheck::Never`, `LogPlugin` and `ClearColor`, but
`primary_window: None`, `ExitCondition::DontExit`, `RenderPlugin` with
`WgpuSettings { backends: None }` (render types + `AssetServer` stay, no GPU is
initialized) and `WinitPlugin` disabled. Do NOT insert `WinitSettings` there —
it needs an event loop. The smoke test
`main_game_survives_ten_headless_frames` in `src/main.rs` builds the full
`MainGamePlugin` on it, runs 10 `app.update()` frames and asserts a camera
exists. Run with `./test.sh` (native `cargo test` only).

Gotchas hit getting this to survive headless, worth knowing before adding new
systems:
- Driving an `App` manually (no `app.run()`) must still do what
  `bevy_app::app::run_once` does: poll `plugins_state()` until not `Adding`,
  then call `app.finish()` and `app.cleanup()` **before** the first
  `app.update()`. Skipping this breaks anything set up in a plugin's
  `finish()`/`cleanup()` phase, not just rendering.
- Systems that assume a real window/event loop must degrade instead of
  unwrapping: `update_mouse_capture` (`plugins/states/mod.rs`) bails out if
  `Query<_, With<PrimaryWindow>>::single_mut()` is `Err` (headless has no
  window entity), and `install_network_setup`
  (`plugins/network/mod.rs`) takes `Option<Res<EventLoopProxyWrapper>>` and
  skips if `None` (headless has no winit event loop, so no proxy to wake).
- avian3d's collider-tree/spatial-query/collision systems unconditionally
  require diagnostics resources (`ColliderTreeDiagnostics`,
  `SpatialQueryDiagnostics`, ...) that are otherwise inserted alongside the
  render sub-app; since `backends: None` means that sub-app never gets
  created, `make_headless_app` pre-inserts the ones actually hit via
  `init_resource`. If a new avian3d subsystem's system panics headless with
  "Resource does not exist" for another `*Diagnostics` type, add it there
  too (they're all plain `Default` timing counters, safe to pre-insert).

## Physics invariant: car-physics-hover-model

Ground response stays in clamped velocity space; no spring forces, no hit
normals, no Transform teleports.

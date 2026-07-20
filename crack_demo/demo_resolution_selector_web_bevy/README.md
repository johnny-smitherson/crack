# demo_resolution_selector_web_bevy

The main Bevy game ("Crack!") — a 3D open-world demo built on bevy 0.19 with
bevy_egui UI, avian3d physics, procedural cloud sky, map/traffic/pedestrian AI,
cars, weapons and P2P networking. `MainGamePlugin`
(`src/main_game_plugin.rs`) wires all game plugins onto the app built by
`make_basic_app` (`src/basic_app.rs`). This crate also builds to wasm and runs
in the browser via trunk.

## Usage

Run natively:

```bash
cargo run --bin demo_resolution_selector_web_bevy
```

Run in the browser (trunk):

```bash
trunk serve
```

There are also several focused demo binaries under `src/bin` (`clouds`,
`car_sim`, `traffic_test`, `vfx_demo`, ...) runnable with
`cargo run --bin <name>`.

## Gotchas

- bevy 0.19: there is no more `despawn_recursive()`, just `despawn()`.
- Cross-platform (browser + native): do not use `std::Instant::now()` (panics
  on wasm) and do not use threads — declare API routes consumed by the web
  worker (`crack_demo/web_worker`) / thread worker (`crack_demo/thread_worker`)
  via `declare_api_method_group!`.
- Physics invariant — car-physics-hover-model: ground response stays in
  clamped velocity space; no spring forces, no hit normals, no Transform
  teleports.
- Headless apps: use `make_headless_app` (no window, no winit, `backends:
  None` so no GPU is initialized). Do NOT insert `WinitSettings` — it needs an
  event loop. Driving the app manually (no `app.run()`) must still call
  `app.finish()`/`app.cleanup()` before the first `app.update()` — see the
  gotchas in `AGENTS.md` for what breaks headless without those calls
  (avian3d diagnostics resources, mouse-capture/network systems that assume a
  real window/event loop exists).

## Tests

`./test.sh` runs native `cargo test` only (no wasm test line). The smoke test
`main_game_survives_ten_headless_frames` in `src/main.rs` builds
`make_headless_app` + `MainGamePlugin`, runs 10 frames headless and asserts at
least one camera exists.

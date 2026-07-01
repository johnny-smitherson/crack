We are using bevy 0.19.
The main bevy game is crate demo_resolution_selector_web_bevy.

The other folders here are shims to get things working in a web worker, don't worry about it.

In bevy, if you must use the egui system, *always* schedule the ui system in this way, not under `Update`:

```rust
app.add_systems(EguiPrimaryContextPass, draw_gui_system);
```

There are also some bevy executables under `demo_resolution_selector_web_bevy/src/bin` - these either test something in an independent app or are used as tools.
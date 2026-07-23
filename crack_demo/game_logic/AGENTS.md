# game_logic

Pure data-and-math crate shared by the Bevy client and workers: API/wire
types (`api`, `glb`, `tile`, `map`, `osm`, `pedestrian`, `weapon`), geodesy
(`geo`: octant path ↔ lat/lon bbox, ECEF/ENU), LOD selection (`lod`), and
network room types (`network`). The `worker` feature enables the native-only
`visibility`/`worker` modules — never enable it for wasm builds.

Run tests with `./test.sh` (`cargo test`, `cargo test --features worker`,
`wasm-pack test --node`). See `README.md` for details.

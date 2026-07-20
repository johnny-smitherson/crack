# game_logic

Pure data-and-math crate for the crack demo game, shared between the Bevy
client and the workers. It defines the wire/API types (`api`, `glb`, `tile`,
`map`, `osm`, `pedestrian`, `weapon`), the geodesy helpers (`geo`: octant
paths ↔ lat/lon bboxes, ECEF/ENU projection), the LOD selection logic
(`lod`), and the game's network room types (`network`, built on
`net_crackpipe`).

## Usage

```rust
use game_logic::geo::lat_lon_to_ecef;
use game_logic::network::bootstrap_topics;

let ecef = lat_lon_to_ecef(52.52, 13.405);
let topics = bootstrap_topics(); // ["global_gameplay"]
```

## Gotchas

- The `worker` feature pulls in heavy native-only dependencies (`parquet`,
  `reqwest`, `parry3d`, …) and enables the `visibility` and `worker` modules
  (server-side fetch/occlusion implementations). Do not enable it for wasm
  builds; the always-on modules are serde/glam-only and wasm-clean.
- Octant paths (`geo::octant_path_to_geobbox`) encode a quadtree over the
  globe: the first two digits pick a hemisphere quadrant, each further digit
  subdivides it. Paths shorter than 2 chars return `None`.
- `lod::compute_distance_to_aabb` is not a plain point-to-box distance: it
  averages the distance to the clamped point with the distance to the box
  middle.

## Tests

`./test.sh` runs `cargo test`, `cargo test --features worker` (keeps the
`visibility` occlusion tests green), then `wasm-pack test --node`. One smoke
test per always-on module: serde round-trips for the data modules, coordinate
invariants for `geo`, distance math for `lod`.

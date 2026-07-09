# Bugs6 — Technical Implementation Plan

---

## 1. Sound broken — only audible at very small distance

**Root cause**: [play_sound_observer](file:///home/p/VIDOEGAME/crack/crack_demo/demo_resolution_selector_web_bevy/src/plugins/audio/mod.rs#L206-L235) computes `scale_factor` as `1.0 / attenuation`. With Bevy's `SpatialScale`, larger scale = *smaller world* = sounds audible over longer distances. But we're passing `SpatialScale(Vec3::splat(1.0/attenuation))`, meaning an attenuation of e.g. 50.0 gives `scale_factor = 0.02` — the engine thinks the world is 50x bigger than it is, so sound falls off at 1/50th the distance.

Additionally, the `SpatialListener` is created with `SpatialListener::new(0.25)` — the `0.25` is the ear gap in metres, which is fine, but the *listener* doesn't have its own `SpatialScale`, so the mismatch between emitter scale and listener scale makes attenuation nonsensical.

**Fix**: Invert the formula. `SpatialScale` should be *proportional* to the attenuation distance, not inversely proportional. The Bevy docs say `SpatialScale(Vec3::splat(X))` means "1 unit in world = X units in audio engine". To hear a sound from `D` metres away, we want the audio engine to think the distance is *shorter*, so we need `scale > 1`. The correct formula for a sound audible at `attenuation` metres at half volume is:

```rust
// In play_sound_observer:
let scale_factor = ev.attenuation.max(0.1); // NOT 1.0 / attenuation
let playback_settings = PlaybackSettings {
    mode,
    volume: Volume::Linear(ev.volume),
    speed: ev.speed,
    spatial: true,
    spatial_scale: Some(SpatialScale(Vec3::splat(scale_factor))),
    ..default()
};
```

If that still feels wrong, an alternative is to just remove the per-emitter `SpatialScale` entirely and rely on a single global spatial scale set at app init via `AudioPlugin { spatial_scale: SpatialScale::new_2d(100.0), .. }`. Then `attenuation` is only used to multiply the `volume` of the emitter based on distance — but that's manual. The simplest correct fix is flipping the formula above.

**Files to change**: [mod.rs L214](file:///home/p/VIDOEGAME/crack/crack_demo/demo_resolution_selector_web_bevy/src/plugins/audio/mod.rs#L214)
Build/run the native app (`cargo check` in `crack_demo/demo_resolution_selector_web_bevy`).  may need to unset ARGV0 env on that cargo command because we're running in cursor appimage 

---

## 2. Pedestrian camera off-center / aim-zoom shoulder offset

**Current values** in [mod.rs](file:///home/p/VIDOEGAME/crack/crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/pedestrian_controller_plugin/mod.rs#L140-L159):

```rust
const CAM_DISTANCE: f32 = 5.5;
const CAM_AIM_DISTANCE: f32 = 2.5;
const CAM_SHOULDER_X: f32 = 0.6;
const CAM_AIM_SHOULDER_X: f32 = 0.3;
const CAM_LOOK_HEIGHT: f32 = 1.1;
const CAM_PITCH: f32 = -0.35;          // ≈ -20°
```

**Reference values** from popular third-person shooters:
- **GTA V** (on-foot): Camera orbits at ~3.5m behind, ~0.8m right of center, look-at ≈ 1.7m above feet. When aiming (RMB), camera snaps to ~1.5m behind, ~0.4m right, tight over right shoulder — almost looking down the gun barrel.
- **Red Dead Redemption 2**: Similar — orbit ~4m, aim ~1.8m, shoulder ~0.6m right.
- **The Last of Us Part II**: Aim camera is very tight, ~1.2m behind, ~0.35m right shoulder.

**Proposed constants**:

```rust
const CAM_DISTANCE: f32 = 4.0;          // was 5.5 — closer like GTA V on-foot
const CAM_AIM_DISTANCE: f32 = 1.5;      // was 2.5 — tighter over-the-shoulder aim
const CAM_SHOULDER_X: f32 = 0.8;        // was 0.6 — more off-center to right
const CAM_AIM_SHOULDER_X: f32 = 0.4;    // was 0.3 — right shoulder, like GTA V aim
const CAM_LOOK_HEIGHT: f32 = 1.5;       // was 1.1 — look at upper chest / head height
const CAM_PITCH: f32 = -0.2;            // was -0.35 — slightly less downward
```

**Files to change**: [mod.rs L140-L159](file:///home/p/VIDOEGAME/crack/crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/pedestrian_controller_plugin/mod.rs#L140-L159)
Build/run the native app (`cargo check` in `crack_demo/demo_resolution_selector_web_bevy`).  may need to unset ARGV0 env on that cargo command because we're running in cursor appimage 

---

## 3. Car spawns with no occupants — need passenger seats & armed pedestrians

### 3a. Add passenger slots to `SpawnCarRequestEvent`

Currently [SpawnCarRequestEvent](file:///home/p/VIDOEGAME/crack/crack_demo/demo_resolution_selector_web_bevy/src/plugins/cars_driving/driving_plugin/spawn_car.rs#L18-L23) only has `position`, `car_type`, `rotation`. We need:

```rust
#[derive(Event)]
pub struct SpawnCarRequestEvent {
    pub position: Vec3,
    pub car_type: String,
    pub rotation: Option<Quat>,
    /// Optional passengers to spawn in the car's seats.
    /// Index 0 = driver, 1 = front passenger, 2 = rear left, 3 = rear right.
    /// `None` entries leave the seat empty.
    pub passengers: Vec<Option<SpawnCarPassenger>>,
}

#[derive(Clone)]
pub struct SpawnCarPassenger {
    pub url: Option<PedestrianUrl>,  // None = random from manifest
    pub weapon: Option<WeaponId>,    // None = random from manifest
    pub faction: Faction,
}
```

### 3b. Define seat offsets

Add seat offset constants (relative to car center, car-local space):

```rust
/// Seat offsets in car-local space [driver, front-pass, rear-left, rear-right].
pub const CAR_SEAT_OFFSETS: [Vec3; 4] = [
    Vec3::new(-0.4, 0.3, 0.15),   // driver (current CarSeatOffset default)
    Vec3::new(0.4, 0.3, 0.15),    // front passenger
    Vec3::new(-0.4, 0.3, -0.7),   // rear left
    Vec3::new(0.4, 0.3, -0.7),    // rear right
];
```

### 3c. Spawn passengers in `spawn_car_request_event_observer`

After `spawn_physics_car(...)`, iterate `passengers` and trigger `SpawnAiPedestrianEvent` for each non-None entry, then parent the spawned controller entity to the car and insert a new `CarPassenger { seat_index: usize }` component. The driver (index 0) uses the existing `DriverMesh` / `CarSeatOffset` system; indices 1–3 are passive passengers that only need to be parented and positioned.

```rust
// After car_entity is spawned:
for (seat_idx, passenger) in ev.passengers.iter().enumerate() {
    let Some(pass) = passenger else { continue };
    if seat_idx == 0 {
        // Driver seat — use existing DriverMesh logic (already implemented)
        continue;
    }
    let seat_world = car_transform * CAR_SEAT_OFFSETS[seat_idx];
    commands.trigger(SpawnAiPedestrianEvent {
        position: seat_world,
        faction: pass.faction,
        url: pass.url.clone(),
        weapon: pass.weapon.clone(),
    });
    // After the AI ped spawns, a system parents it to the car at the seat offset.
}
```

### 3d. Update right-click menu spawn

In [click_spawn_select_controls.rs](file:///home/p/VIDOEGAME/crack/crack_demo/demo_resolution_selector_web_bevy/src/plugins/cars_driving/click_spawn_select_controls.rs) and [interaction_ui.rs](file:///home/p/VIDOEGAME/crack/crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/pedestrian_controller_plugin/interaction_ui.rs), update the `SpawnCarRequestEvent` trigger to pass passengers:

```rust
commands.trigger(SpawnCarRequestEvent {
    position: hit_point,
    car_type: get_random_car_type().to_string(),
    rotation: None,
    passengers: vec![
        None,  // driver seat empty (player will enter)
        Some(SpawnCarPassenger { url: None, weapon: None, faction: Faction::Civilian }),
        Some(SpawnCarPassenger { url: None, weapon: None, faction: Faction::Civilian }),
        Some(SpawnCarPassenger { url: None, weapon: None, faction: Faction::Civilian }),
    ],
});
```

The arming logic already exists in `spawn_ai_pedestrian_observer` — it calls `EquipWeaponEvent` with a random weapon from `WeaponManifest`. So the only missing piece is hooking up the seat system and passing the `passengers` vec.

**Files to change**:
- [spawn_car.rs](file:///home/p/VIDOEGAME/crack/crack_demo/demo_resolution_selector_web_bevy/src/plugins/cars_driving/driving_plugin/spawn_car.rs) — event struct, seat offsets, spawn logic
- [click_spawn_select_controls.rs](file:///home/p/VIDOEGAME/crack/crack_demo/demo_resolution_selector_web_bevy/src/plugins/cars_driving/click_spawn_select_controls.rs) — pass passengers
- [interaction_ui.rs](file:///home/p/VIDOEGAME/crack/crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/pedestrian_controller_plugin/interaction_ui.rs) — pass passengers
- [spawn_ai.rs](file:///home/p/VIDOEGAME/crack/crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrian_ai/spawn_ai.rs) — already has weapon equip, no changes needed
- New component: `CarPassenger { seat_index: usize, car: Entity }` for tracking who sits where
Build/run the native app (`cargo check` in `crack_demo/demo_resolution_selector_web_bevy`).  may need to unset ARGV0 env on that cargo command because we're running in cursor appimage 

---

## 4. Procedural arm aiming — right arm IK towards target

### Current state

There is no procedural IK. Aiming currently plays a full-body animation blend between walk/idle and an aim animation in [drive_character_animation](file:///home/p/VIDOEGAME/crack/crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/pedestrian_controller_plugin/animation.rs). The skeleton is classified in [skeleton.rs](file:///home/p/VIDOEGAME/crack/crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/skeleton.rs) with `BoneLabel::RightShoulder`, `RightArm`, `RightHand`, `Spine`, etc. The `classify_skeleton` function returns entities for right shoulder, right elbow, right wrist.

### Proposed approach: post-animation IK system

Add a new system `apply_arm_ik` that runs in `PostUpdate` **after** Bevy's animation evaluation but **before** `TransformPropagate`:

```rust
/// Run after animation, before transform propagation.
pub fn apply_arm_ik(
    controlled: Res<ControlledCharacter>,
    rig: Res<CameraRig>,
    camera: Query<(&Camera, &GlobalTransform), With<Camera3d>>,
    skeletons: Query<&PedestrianSkeleton>,
    mut transforms: Query<&mut Transform>,
    global_transforms: Query<&GlobalTransform>,
) {
    // 1. Get aim target from screen center raycast (or crosshair world pos)
    // 2. Get right shoulder, elbow, wrist entities from PedestrianSkeleton
    // 3. Compute two-bone IK (shoulder→elbow→wrist) pointing wrist at target
    // 4. Check if target is in the "dead zone" (to the character's left, > ~120° from forward)
    //    If so, pre-rotate the spine bone to face the target first, THEN solve arm IK
    // 5. Write local Transform rotations to shoulder and elbow entities
}
```

### Two-bone IK algorithm

Standard two-bone IK (shoulder→elbow→wrist→target):

```rust
fn solve_two_bone_ik(
    shoulder_pos: Vec3,
    elbow_pos: Vec3,
    wrist_pos: Vec3,
    target_pos: Vec3,
    pole_target: Vec3,  // usually slightly behind + below the character
) -> (Quat, Quat) {  // shoulder_rot, elbow_rot
    let upper_len = (elbow_pos - shoulder_pos).length();
    let lower_len = (wrist_pos - elbow_pos).length();
    let target_dist = (target_pos - shoulder_pos).length()
        .clamp(0.01, upper_len + lower_len - 0.001);

    // Law of cosines for elbow angle
    let cos_elbow = ((upper_len * upper_len + lower_len * lower_len
        - target_dist * target_dist)
        / (2.0 * upper_len * lower_len))
        .clamp(-1.0, 1.0);
    let elbow_angle = cos_elbow.acos();

    // ... standard two-bone IK math with pole vector for twist resolution
    // Returns local-space rotations for shoulder and elbow joints
}
```

### Spine pre-rotation for dead zone

```rust
const ARM_DEAD_ZONE_ANGLE: f32 = 120.0 * (std::f32::consts::PI / 180.0);

fn compute_spine_compensation(
    char_forward: Vec3,
    to_target: Vec3,
) -> Option<Quat> {
    let angle = char_forward.xz().angle_to(to_target.xz());
    if angle.abs() > ARM_DEAD_ZONE_ANGLE {
        // Rotate spine by the excess angle so the arm can reach
        let excess = angle - ARM_DEAD_ZONE_ANGLE.copysign(angle);
        Some(Quat::from_rotation_y(excess))
    } else {
        None
    }
}
```

### In-car shooting — left or right arm

When `GameControlState::DrivingCar`, pick arm based on relative target position:
- Target to the right of car → right arm
- Target to the left of car → left arm

The skeleton already classifies `LeftShoulder`, `LeftArm`, `LeftHand` equivalently.

**Files to change**:
- **NEW** `src/plugins/pedestrians/pedestrian_controller_plugin/arm_ik.rs` — the IK system
- [mod.rs](file:///home/p/VIDOEGAME/crack/crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/pedestrian_controller_plugin/mod.rs) — register the system in `PostUpdate`
- [animation.rs](file:///home/p/VIDOEGAME/crack/crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/pedestrian_controller_plugin/animation.rs) — remove the aim animation blend for the right arm (keep lower body / left arm blends)
- [skeleton.rs](file:///home/p/VIDOEGAME/crack/crack_demo/demo_resolution_selector_web_bevy/src/plugins/pedestrians/skeleton.rs) — ensure `PedestrianSkeleton` stores spine entity as well
Build/run the native app (`cargo check` in `crack_demo/demo_resolution_selector_web_bevy`).  may need to unset ARGV0 env on that cargo command because we're running in cursor appimage 

---

## 5. Road graph — discard steep segments (>15°)

### Current code

[build_road_graph](file:///home/p/VIDOEGAME/crack/crack_demo/demo_resolution_selector_web_bevy/src/plugins/traffic/road_graph.rs#L22-L59) iterates `GeoJsonDatabase.categories["roads"]` and calls `process_points` which already filters out segments shorter than 20m. We add inclination filtering at the same stage.

### Implementation

Add a constant and a filtering step inside `process_points`:

```rust
/// Maximum road segment inclination in degrees. Segments steeper than this
/// are discarded to remove broken / vertical OSM road markers from traffic.
const MAX_ROAD_INCLINATION_DEG: f32 = 15.0;

fn process_points(
    points: &[Vec3],
    segments: &mut Vec<RoadSegment>,
    node_index: &mut HashMap<IVec2, Vec<usize>>,
) {
    if points.len() < 2 { return; }

    let length: f32 = points.windows(2).map(|w| w[0].distance(w[1])).sum();
    if length < 20.0 { return; }

    // NEW: reject segments where any sub-segment is steeper than threshold
    let max_slope = MAX_ROAD_INCLINATION_DEG.to_radians().tan();
    for w in points.windows(2) {
        let dx = (w[1].x - w[0].x).hypot(w[1].z - w[0].z); // horizontal distance
        let dy = (w[1].y - w[0].y).abs();                     // vertical distance
        if dx < 0.01 || dy / dx > max_slope {
            return; // entire segment is discarded
        }
    }

    // ... rest of existing code unchanged
}
```

After discarding steep segments, some nodes in `node_index` may reference only discarded segments and become orphaned. A cleanup pass removes those:

```rust
// After all segments are processed, in build_road_graph:
// Remove orphan nodes whose segments were all discarded
graph.node_index.retain(|_, seg_indices| !seg_indices.is_empty());

let pre_count = segments.len();
info!(
    "TrafficRoadGraph: discarded {} steep segments (>{} deg)",
    pre_count - graph.segments.len(),
    MAX_ROAD_INCLINATION_DEG,
);
```

Actually — since we `return` early in `process_points`, the segment is never added to `segments` and its index never goes into `node_index`, so no orphan cleanup is needed. The filtering is fully transparent to the client; it simply receives fewer road segments.

**Files to change**: [road_graph.rs](file:///home/p/VIDOEGAME/crack/crack_demo/demo_resolution_selector_web_bevy/src/plugins/traffic/road_graph.rs) — add constant + slope check in `process_points`

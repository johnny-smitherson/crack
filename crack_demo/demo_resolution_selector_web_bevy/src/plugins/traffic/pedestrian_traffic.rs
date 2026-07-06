use bevy::prelude::*;
use avian3d::prelude::*;

use crate::plugins::{
    map_plugin::MapTree,
    pedestrians::{
        pedestrian_controller_plugin::LocomotionInput,
    },
    pedestrian_ai::{
        AiPedestrian, AiState, Faction,
        spawn_ai::SpawnAiPedestrianEvent,
    },
};
use super::{
    TrafficConfig, TrafficPedestrian, SpawnTrafficPedestrianEvent,
    SPAWN_INTERVAL_S, SPAWN_MIN_CAMERA_DIST, PED_SPAWN_SPACING, SPAWN_BEHIND_MAX_DOT,
    OUT_OF_RANGE_FACTOR, OUT_OF_VIEW_DESPAWN_S, VIEW_RAYCAST_HZ, STUCK_HARD_DESPAWN_S,
    WAYPOINT_REACHED_XZ, LOOKAHEAD_XZ, PED_ROAD_OFFSET, STUCK_SPEED_EPS, STUCK_TRIGGER_S,
};
use super::road_graph::{TrafficRoadGraph, quantize, pick_continuation, RerouteMode};
use super::spawn::get_ground_y;

#[derive(Resource, Default)]
pub struct PendingTrafficPeds {
    pub pending: Vec<PendingTrafficPedEntry>,
}

pub struct PendingTrafficPedEntry {
    pub spawn_pos: Vec3,
    pub path: Vec<Vec3>,
    pub current_seg: usize,
    pub offset_sign: f32,
}

pub fn traffic_pedestrian_spawner(
    time: Res<Time>,
    mut last_spawn: Local<f32>,
    config: Res<TrafficConfig>,
    graph: Res<TrafficRoadGraph>,
    q_camera: Query<(&Camera, &GlobalTransform), With<Camera3d>>,
    q_traffic_peds: Query<(), With<TrafficPedestrian>>,
    q_all_peds: Query<&Transform, With<AiPedestrian>>,
    mut commands: Commands,
) {
    if !config.ped_enabled || !graph.built {
        return;
    }

    let now = time.elapsed_secs();
    if now - *last_spawn < SPAWN_INTERVAL_S {
        return;
    }

    if q_traffic_peds.iter().count() >= config.max_peds {
        return;
    }

    let Some((camera, cam_gt)) = q_camera.iter().next() else {
        return;
    };

    let camera_pos = cam_gt.translation();
    let cam_fwd = cam_gt.forward();
    let num_segments = graph.segments.len();
    if num_segments == 0 {
        return;
    }

    // Try up to 10 candidates
    for _ in 0..10 {
        let seg_idx = (rand::random::<f32>() * num_segments as f32) as usize;
        let seg = &graph.segments[seg_idx];
        if seg.points.is_empty() {
            continue;
        }
        let pt_idx = (rand::random::<f32>() * seg.points.len() as f32) as usize;
        let candidate_point = seg.points[pt_idx];

        let dist = camera_pos.distance(candidate_point);
        if dist > config.spawn_radius || dist < SPAWN_MIN_CAMERA_DIST {
            continue;
        }

        // Must be behind/side of the camera
        let to_pt = (candidate_point - camera_pos).normalize_or_zero();
        if cam_fwd.dot(to_pt) >= SPAWN_BEHIND_MAX_DOT {
            continue;
        }

        // Check if inside frustum
        if let Some(ndc) = camera.world_to_ndc(cam_gt, candidate_point) {
            let inside_x = ndc.x >= -1.0 && ndc.x <= 1.0;
            let inside_y = ndc.y >= -1.0 && ndc.y <= 1.0;
            let inside_z = ndc.z >= 0.0 && ndc.z <= 1.0;
            if inside_x && inside_y && inside_z {
                // Reject visible candidate
                continue;
            }
        }

        // Check distance to existing pedestrians
        let mut too_close = false;
        for ped_tf in q_all_peds.iter() {
            if ped_tf.translation.distance(candidate_point) < PED_SPAWN_SPACING {
                too_close = true;
                break;
            }
        }
        if too_close {
            continue;
        }

        // Success! Spawn it
        commands.trigger(SpawnTrafficPedestrianEvent {
            position: candidate_point,
        });
        *last_spawn = now;
        break;
    }
}

pub fn spawn_traffic_pedestrian_observer(
    trigger: On<SpawnTrafficPedestrianEvent>,
    mut commands: Commands,
    graph: Res<TrafficRoadGraph>,
    map_tree: Option<Res<MapTree>>,
    spatial_query: avian3d::prelude::SpatialQuery,
    mut pending_traffic: ResMut<PendingTrafficPeds>,
) {
    if !graph.built || graph.segments.is_empty() {
        warn!("SpawnTrafficPedestrianEvent: road graph is not built or empty.");
        return;
    }

    let req_pos = trigger.event().position;

    // 1. Find closest road segment point
    let mut _closest_pt = req_pos;
    let mut closest_dist = f32::MAX;
    let mut closest_seg_idx = 0;
    let mut closest_pt_idx = 0;

    for (s_idx, seg) in graph.segments.iter().enumerate() {
        for (p_idx, &pt) in seg.points.iter().enumerate() {
            let d = pt.distance(req_pos);
            if d < closest_dist {
                closest_dist = d;
                _closest_pt = pt;
                closest_seg_idx = s_idx;
                closest_pt_idx = p_idx;
            }
        }
    }

    // 2. Build path from closest segment point in the direction of the longer side
    let seg = &graph.segments[closest_seg_idx];
    let mut forward_dist = 0.0;
    for w in seg.points[closest_pt_idx..].windows(2) {
        forward_dist += w[0].distance(w[1]);
    }
    let mut backward_dist = 0.0;
    for w in seg.points[..=closest_pt_idx].windows(2) {
        backward_dist += w[0].distance(w[1]);
    }
    let forward = forward_dist >= backward_dist;

    let mut path_points = if forward {
        seg.points[closest_pt_idx..].to_vec()
    } else {
        seg.points[..=closest_pt_idx].iter().cloned().rev().collect::<Vec<_>>()
    };

    // Append one next segment
    if path_points.len() >= 2 {
        let end_node = quantize(*path_points.last().unwrap());
        let walk_dir = (path_points[1] - path_points[0]).normalize_or_zero();
        if let Some((_next_seg, next_points)) = pick_continuation(
            &graph,
            end_node,
            closest_seg_idx,
            RerouteMode::ClosestAngle(walk_dir),
        ) {
            path_points.extend(next_points[1..].iter().cloned());
        }
    }

    if path_points.len() < 2 {
        return;
    }

    // 3. Pick offset_sign randomly (+1 / -1)
    let offset_sign = if rand::random::<bool>() { 1.0 } else { -1.0 };

    // 4. Ground the spawn position (with offset applied)
    let start_pos = path_points[0];
    let next_pos = path_points[1];
    let dir = (next_pos - start_pos).normalize_or_zero();
    let perp = Vec3::new(dir.z, 0.0, -dir.x);
    let offset_spawn = start_pos + perp * offset_sign * PED_ROAD_OFFSET;

    let ground_y = get_ground_y(offset_spawn, map_tree.as_ref().map(|r| &**r), &spatial_query);
    let spawn_pos = Vec3::new(offset_spawn.x, ground_y, offset_spawn.z);

    // 5. Trigger SpawnAiPedestrianEvent with Neutral faction (no weapon, random model)
    commands.trigger(SpawnAiPedestrianEvent {
        position: spawn_pos,
        faction: Faction::Neutral,
        url: None,
        weapon: None,
    });

    // 6. Push to PendingTrafficPeds queue
    pending_traffic.pending.push(PendingTrafficPedEntry {
        spawn_pos,
        path: path_points,
        current_seg: closest_seg_idx,
        offset_sign,
    });
}

pub fn adopt_traffic_pedestrians(
    mut commands: Commands,
    mut pending: ResMut<PendingTrafficPeds>,
    q_new_ai: Query<(Entity, &Transform), (Added<AiPedestrian>, Without<TrafficPedestrian>)>,
) {
    if pending.pending.is_empty() {
        return;
    }

    for (entity, transform) in q_new_ai.iter() {
        let ped_pos = transform.translation;
        let mut best_idx = None;
        let mut best_dist = 5.0; // 5m radius to match the spawned ped

        for (idx, entry) in pending.pending.iter().enumerate() {
            let dist = ped_pos.distance(entry.spawn_pos);
            if dist < best_dist {
                best_dist = dist;
                best_idx = Some(idx);
            }
        }

        if let Some(idx) = best_idx {
            let entry = pending.pending.remove(idx);
            commands.entity(entity).insert(TrafficPedestrian {
                path: entry.path,
                next_idx: 1,
                current_seg: entry.current_seg,
                offset_sign: entry.offset_sign,
                stuck_timer: 0.0,
                out_of_view_timer: 0.0,
                last_visible: true,
            });
        }
    }
}

pub fn drive_traffic_pedestrians(
    time: Res<Time>,
    graph: Res<TrafficRoadGraph>,
    mut q_peds: Query<(
        Entity,
        &GlobalTransform,
        &AiState,
        &mut TrafficPedestrian,
        &mut LocomotionInput,
        Option<&LinearVelocity>,
    )>,
) {
    let dt = time.delta_secs();
    if dt <= 0.0 || !graph.built {
        return;
    }

    for (_entity, gt, state, mut tp, mut input, opt_lin_vel) in q_peds.iter_mut() {
        // Only override when AI is idle
        if *state != AiState::Idle {
            continue;
        }

        let ped_pos = gt.translation();

        // 1. Stuck detection & recovery
        let mut is_stuck = false;
        if let Some(lin_vel) = opt_lin_vel {
            let current_speed = lin_vel.0.length();
            if input.move_dir.length() > 0.1 && current_speed < STUCK_SPEED_EPS {
                tp.stuck_timer += dt;
                // Check if we just crossed the trigger threshold
                if tp.stuck_timer > STUCK_TRIGGER_S && (tp.stuck_timer - dt) <= STUCK_TRIGGER_S {
                    is_stuck = true;
                }
            } else {
                tp.stuck_timer = 0.0;
            }
        }

        if is_stuck {
            // Reroute randomly from current nearest node
            let seg = &graph.segments[tp.current_seg];
            let dist_a = seg.points[0].distance(ped_pos);
            let dist_b = seg.points.last().unwrap().distance(ped_pos);
            let nearest_node = if dist_a < dist_b {
                quantize(seg.points[0])
            } else {
                quantize(*seg.points.last().unwrap())
            };

            if let Some((next_seg, next_points)) = pick_continuation(
                &graph,
                nearest_node,
                tp.current_seg,
                RerouteMode::Random,
            ) {
                tp.path = next_points;
                tp.next_idx = 1;
                tp.current_seg = next_seg;
            } else {
                // Linear scan fallback
                let mut _closest_pt = ped_pos;
                let mut closest_dist = f32::MAX;
                let mut closest_seg_idx = 0;
                let mut closest_pt_idx = 0;

                for (s_idx, seg) in graph.segments.iter().enumerate() {
                    for (p_idx, &pt) in seg.points.iter().enumerate() {
                        let d = pt.distance(ped_pos);
                        if d < closest_dist {
                            closest_dist = d;
                            _closest_pt = pt;
                            closest_seg_idx = s_idx;
                            closest_pt_idx = p_idx;
                        }
                    }
                }

                let seg = &graph.segments[closest_seg_idx];
                let mut forward_dist = 0.0;
                for w in seg.points[closest_pt_idx..].windows(2) {
                    forward_dist += w[0].distance(w[1]);
                }
                let mut backward_dist = 0.0;
                for w in seg.points[..=closest_pt_idx].windows(2) {
                    backward_dist += w[0].distance(w[1]);
                }
                let forward = forward_dist >= backward_dist;

                let mut path_points = if forward {
                    seg.points[closest_pt_idx..].to_vec()
                } else {
                    seg.points[..=closest_pt_idx].iter().cloned().rev().collect::<Vec<_>>()
                };

                if path_points.len() >= 2 {
                    let end_node = quantize(*path_points.last().unwrap());
                    let walk_dir = (path_points[1] - path_points[0]).normalize_or_zero();
                    if let Some((_next_seg, next_points)) = pick_continuation(
                        &graph,
                        end_node,
                        closest_seg_idx,
                        RerouteMode::ClosestAngle(walk_dir),
                    ) {
                        path_points.extend(next_points[1..].iter().cloned());
                    }
                }

                tp.path = path_points;
                tp.next_idx = 1;
                tp.current_seg = closest_seg_idx;
            }
            continue;
        }

        // 2. Advance waypoint index if close in XZ plane
        while tp.next_idx < tp.path.len() {
            let target = tp.path[tp.next_idx];
            let dist_xz = Vec2::new(ped_pos.x - target.x, ped_pos.z - target.z).length();
            if dist_xz < WAYPOINT_REACHED_XZ {
                tp.next_idx += 1;
            } else {
                break;
            }
        }

        // 3. Reroute at path end
        if tp.next_idx >= tp.path.len() {
            let last_node = quantize(*tp.path.last().unwrap());
            let current_points = &tp.path;
            let last_dir = if current_points.len() >= 2 {
                let len = current_points.len();
                (current_points[len - 1] - current_points[len - 2]).normalize_or_zero()
            } else {
                Vec3::ZERO
            };

            if let Some((next_seg, next_points)) = pick_continuation(
                &graph,
                last_node,
                tp.current_seg,
                RerouteMode::ClosestAngle(last_dir),
            ) {
                let mut new_path = vec![*tp.path.last().unwrap()];
                new_path.extend(next_points[1..].iter().cloned());
                tp.path = new_path;
                tp.next_idx = 1;
                tp.current_seg = next_seg;
            } else {
                // Reverse current segment to turn around
                let seg = &graph.segments[tp.current_seg];
                let start_quant = quantize(seg.points[0]);
                let reversed_points: Vec<Vec3> = if start_quant == last_node {
                    seg.points.clone()
                } else {
                    seg.points.iter().cloned().rev().collect()
                };

                let mut new_path = vec![*tp.path.last().unwrap()];
                new_path.extend(reversed_points[1..].iter().cloned());
                tp.path = new_path;
                tp.next_idx = 1;
            }
        }

        // 4. Lookahead target
        let mut target_idx = tp.next_idx;
        while target_idx < tp.path.len() {
            let target = tp.path[target_idx];
            let dist_xz = Vec2::new(ped_pos.x - target.x, ped_pos.z - target.z).length();
            if dist_xz >= LOOKAHEAD_XZ {
                break;
            }
            target_idx += 1;
        }
        let target_idx = target_idx.min(tp.path.len() - 1);
        if tp.path.is_empty() {
            continue;
        }
        let mut target = tp.path[target_idx];

        // 5. Offset laterally
        let dir = if target_idx > 0 {
            (tp.path[target_idx] - tp.path[target_idx - 1]).normalize_or_zero()
        } else if tp.path.len() >= 2 {
            (tp.path[1] - tp.path[0]).normalize_or_zero()
        } else {
            Vec3::ZERO
        };

        if dir != Vec3::ZERO {
            let perp = Vec3::new(dir.z, 0.0, -dir.x);
            target += perp * tp.offset_sign * PED_ROAD_OFFSET;
        }

        // Set move direction in LocomotionInput
        let to_target = target - ped_pos;
        let d = to_target.normalize_or_zero();
        input.move_dir = Vec2::new(d.x, -d.z);
    }
}

pub fn despawn_traffic_pedestrians(
    time: Res<Time>,
    config: Res<TrafficConfig>,
    mut q_peds: Query<(Entity, &Transform, &mut TrafficPedestrian)>,
    q_children: Query<&Children>,
    q_camera: Query<(&Camera, &GlobalTransform), With<Camera3d>>,
    spatial_query: SpatialQuery,
    mut commands: Commands,
    mut raycast_timer: Local<f32>,
) {
    let dt = time.delta_secs();
    if dt <= 0.0 {
        return;
    }

    *raycast_timer += dt;
    let run_raycasts = if *raycast_timer >= 1.0 / VIEW_RAYCAST_HZ {
        *raycast_timer = 0.0;
        true
    } else {
        false
    };

    let Some((camera, cam_gt)) = q_camera.iter().next() else {
        return;
    };
    let camera_pos = cam_gt.translation();

    for (entity, transform, mut tp) in q_peds.iter_mut() {
        let ped_pos = transform.translation;
        let dist_to_camera = ped_pos.distance(camera_pos);

        // 1. Out of range check (visibility gated)
        if dist_to_camera > config.spawn_radius * OUT_OF_RANGE_FACTOR && !tp.last_visible {
            commands.entity(entity).despawn();
            continue;
        }

        // 2. Stuck check (visibility gated)
        if tp.stuck_timer > STUCK_HARD_DESPAWN_S && !tp.last_visible {
            commands.entity(entity).despawn();
            continue;
        }

        // 3. Out of view timer check
        if run_raycasts {
            let ped_top = ped_pos + Vec3::Y * 1.6;
            
            // Check frustum first
            let in_frustum = if let Some(ndc) = camera.world_to_ndc(cam_gt, ped_top) {
                ndc.x >= -1.0 && ndc.x <= 1.0 && ndc.y >= -1.0 && ndc.y <= 1.0 && ndc.z >= 0.0 && ndc.z <= 1.0
            } else {
                false
            };

            let mut visible = false;
            if in_frustum {
                // In frustum, run occlusion raycast
                let cam_to_ped = ped_top - camera_pos;
                let dist = cam_to_ped.length();
                let dir_vec = cam_to_ped.normalize_or_zero();

                if dir_vec != Vec3::ZERO {
                    let mut excluded = vec![entity];
                    if let Ok(children) = q_children.get(entity) {
                        excluded.extend(children.iter());
                    }
                    let filter = SpatialQueryFilter::default().with_excluded_entities(excluded);

                    if let Some(hit_dir) = bevy::prelude::Dir3::new(dir_vec).ok() {
                        if let Some(_hit) = spatial_query.cast_ray(camera_pos, hit_dir, dist - 0.1, true, &filter) {
                            // Hit something else (occluded)
                        } else {
                            // Line of sight clear -> visible!
                            visible = true;
                        }
                    }
                }
            }

            tp.last_visible = visible;
            if visible {
                tp.out_of_view_timer = 0.0;
            }
        }

        if !tp.last_visible {
            tp.out_of_view_timer += dt;
        } else {
            tp.out_of_view_timer = 0.0;
        }

        if tp.out_of_view_timer > OUT_OF_VIEW_DESPAWN_S {
            commands.entity(entity).despawn();
        }
    }
}

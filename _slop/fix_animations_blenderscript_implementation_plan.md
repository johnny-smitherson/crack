# Animation Retargeting Bug Analysis & Fix Plan

## Problem Summary

The Stage 3 animation retargeting in [blender_normalize_skel.py](file:///c:/Users/Naxxramas/Desktop/TETROS/crack/_data/3d_data/pedestrian_animations/blender_normalize_skel.py) produces severely distorted poses. The retargeted pedestrian model has wildly incorrect limb positions compared to the reference model.

## Visual Evidence

### Reference Model (Correct)
````carousel
![Reference Idle Front](C:\Users\Naxxramas\.gemini\antigravity-ide\brain\ae33d798-6c30-4680-8a4b-b46a82327b9b\ref_idle_front.jpg)
<!-- slide -->
![Reference Idle Side](C:\Users\Naxxramas\.gemini\antigravity-ide\brain\ae33d798-6c30-4680-8a4b-b46a82327b9b\ref_idle_side.jpg)
<!-- slide -->
![Reference Walk Front](C:\Users\Naxxramas\.gemini\antigravity-ide\brain\ae33d798-6c30-4680-8a4b-b46a82327b9b\ref_walk_front.jpg)
<!-- slide -->
![Reference Crouch Front](C:\Users\Naxxramas\.gemini\antigravity-ide\brain\ae33d798-6c30-4680-8a4b-b46a82327b9b\ref_crouch_front.jpg)
````

### Target Model Output (Broken)
````carousel
![Output Idle Front](C:\Users\Naxxramas\.gemini\antigravity-ide\brain\ae33d798-6c30-4680-8a4b-b46a82327b9b\out_idle_front.jpg)
<!-- slide -->
![Output Idle Side](C:\Users\Naxxramas\.gemini\antigravity-ide\brain\ae33d798-6c30-4680-8a4b-b46a82327b9b\out_idle_side.jpg)
<!-- slide -->
![Output Walk Front](C:\Users\Naxxramas\.gemini\antigravity-ide\brain\ae33d798-6c30-4680-8a4b-b46a82327b9b\out_walk_front.jpg)
<!-- slide -->
![Output Crouch Front](C:\Users\Naxxramas\.gemini\antigravity-ide\brain\ae33d798-6c30-4680-8a4b-b46a82327b9b\out_crouch_front.jpg)
````

### Stage 2 Rest Pose (Correct)
![Stage 2 - Rest pose looks correct](C:\Users\Naxxramas\.gemini\antigravity-ide\brain\ae33d798-6c30-4680-8a4b-b46a82327b9b\out_stage2_front.jpg)

> [!IMPORTANT]
> The Stage 2 rest pose (T-pose) looks correct — the model is properly upright, centered, with arms extended. This confirms the problem is **entirely in Stage 3** (animation retargeting), not in the skeleton alignment stages.

---

## Root Cause Analysis

### Bug #1: Wrong dictionary passed as `ref_rest_matrices` (Critical)

> [!CAUTION]
> This is the **primary cause** of the broken animations.

At [line 1284](file:///c:/Users/Naxxramas/Desktop/TETROS/crack/_data/3d_data/pedestrian_animations/blender_normalize_skel.py#L1284):
```python
stage_3_apply_animations(target_armature, target_bone_mapping, ref_key_bones, ref_actions, ref_rest_matrices=ref_key_matrices)
```

**`ref_key_matrices`** is keyed by **label names** (e.g. `'neck'`, `'left_arm'`, `'left_forearm'`), built at [line 1207](file:///c:/Users/Naxxramas/Desktop/TETROS/crack/_data/3d_data/pedestrian_animations/blender_normalize_skel.py#L1207):
```python
ref_key_matrices[key] = bone.matrix_local.copy()  # key = 'neck', 'left_arm', etc.
```

But inside `stage_3_apply_animations`, at [line 843](file:///c:/Users/Naxxramas/Desktop/TETROS/crack/_data/3d_data/pedestrian_animations/blender_normalize_skel.py#L843), the lookup uses **bone names**:
```python
m_r_mat = ref_rest_matrices.get(r_b)  # r_b = 'upperarm_l', 'lowerarm_l', etc.
```

**The keys don't match**, so `m_r_mat` is **always `None`**, and the C matrix falls back to `Identity(3)` at [line 850](file:///c:/Users/Naxxramas/Desktop/TETROS/crack/_data/3d_data/pedestrian_animations/blender_normalize_skel.py#L850). This means:
- **No coordinate space transformation** is applied to rotations
- The raw reference animation quaternions are applied directly to the target skeleton
- Since the reference model (UAL1_Standard) and the target model (generated pedestrian) have completely different bone orientations in rest pose, applying rotations without transformation produces wildly incorrect results

**Meanwhile**, the **correct** dictionary is already built at [line 1215](file:///c:/Users/Naxxramas/Desktop/TETROS/crack/_data/3d_data/pedestrian_animations/blender_normalize_skel.py#L1215):
```python
ref_rest_matrices = {b.name: b.matrix_local.copy() for b in ref_armature.data.bones}
```
This one IS keyed by bone name — but it's stored in a local variable that's **never passed** to `stage_3_apply_animations`.

### Bug #2: `ref_rest_matrices` is stale after `clear_scene()` (Secondary)

At [line 1215](file:///c:/Users/Naxxramas/Desktop/TETROS/crack/_data/3d_data/pedestrian_animations/blender_normalize_skel.py#L1215), `ref_rest_matrices` is captured from the reference armature's bones. But then at [line 1224](file:///c:/Users/Naxxramas/Desktop/TETROS/crack/_data/3d_data/pedestrian_animations/blender_normalize_skel.py#L1224), `render_reference_animations()` calls `clear_scene()` which destroys all objects. This isn't directly a problem for the matrices (they're already copied as pure data), but it does mean the reference armature is gone before Stage 3 runs.

This is fine because the matrices are value-copied. Not a bug, just worth noting.

### Bug #3: C matrix formula applied incompletely (Potential)

The current formula is:
```python
C = M_target_rest_3x3.inverted() @ M_ref_rest_3x3
```
And then applied as:
```python
R_target = C @ R_ref
```

The correct formula for bone-space retargeting should be:
```python
R_target = M_target_rest_3x3.inverted() @ M_ref_rest_3x3 @ R_ref @ M_ref_rest_3x3.inverted() @ M_target_rest_3x3
```

However, the simplified `C @ R_ref` approach can work if the animation data is in local bone space (which Blender's pose quaternions are). The current formula `C = T_inv @ R` is a standard shortcut. **This may need adjustment once Bug #1 is fixed**, but it's the correct general approach.

---

## Proposed Fix

### Fix 1: Pass the correct `ref_rest_matrices` dictionary (one-line fix)

Change [line 1284](file:///c:/Users/Naxxramas/Desktop/TETROS/crack/_data/3d_data/pedestrian_animations/blender_normalize_skel.py#L1284) from:
```diff
-    stage_3_apply_animations(target_armature, target_bone_mapping, ref_key_bones, ref_actions, ref_rest_matrices=ref_key_matrices)
+    stage_3_apply_animations(target_armature, target_bone_mapping, ref_key_bones, ref_actions, ref_rest_matrices=ref_rest_matrices)
```

This passes the dictionary keyed by **bone names** (e.g. `'upperarm_l'`, `'lowerarm_l'`) which matches how `stage_3_apply_animations` looks up the matrices.

### Fix 2 (already done): Absolute path resolution for Windows

Already applied — `os.path.abspath()` on all three CLI arguments in `main()`.

---

## Verification Plan

### Automated Tests
- Re-run the single-file test: `blender --background --python blender_normalize_skel.py -- UAL1_Standard.glb ../pedestrian_3d_gen/3d_with_skeleton/round2/3d-output-v2_00001__with_skel.glb out2`
- Visually compare the output animation render images against the reference images in `ref/`

### Success Criteria
- **Idle Loop**: Model should stand upright with arms at sides, slight natural stance (matching reference)
- **Walk Loop**: Natural walking gait with swinging arms and stepping legs
- **Jog Loop**: Running with one foot lifted, arms pumping
- **Crouch Loop**: Bent-knee crouch with arms forward
- The overall pose silhouettes should closely match the reference model, accounting for different body proportions

---

## Open Questions

> [!IMPORTANT]
> **After fixing Bug #1, is the `C = T_inv @ R` formula sufficient?** If the results are still distorted after applying the correct matrices, the full sandwich formula `R_target = T_inv @ R_ref_rest @ R_ref_anim @ R_ref_rest_inv @ T_target_rest` may be needed. I recommend fixing Bug #1 first, re-rendering, and evaluating before making any formula changes.

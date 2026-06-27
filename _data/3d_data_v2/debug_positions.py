"""Quick diagnostic: check if parent and child tile vertices overlap in ENU space."""
import json, base64, numpy as np, sys, os, math

def unpack_vertices(packed: bytes):
    count = len(packed) // 3
    if count == 0:
        return np.zeros((0, 3), dtype=np.uint8)
    data = np.frombuffer(packed, dtype=np.uint8)
    x = np.cumsum(data[0:count], dtype=np.uint8)
    y = np.cumsum(data[count:2*count], dtype=np.uint8)
    z = np.cumsum(data[2*count:3*count], dtype=np.uint8)
    return np.stack([x, y, z], axis=1)

def apply_matrix(vertices, matrix):
    n = len(vertices)
    if n == 0:
        return np.zeros((0, 3), dtype=np.float64)
    M = np.array(matrix, dtype=np.float64).reshape(4, 4).T
    pts = np.ones((n, 4), dtype=np.float64)
    pts[:, :3] = vertices.astype(np.float64)
    result = pts @ M.T
    return result[:, :3]

def get_enu_rotation_matrix(ref_point):
    rx, ry, rz = ref_point
    L = math.sqrt(rx*rx + ry*ry + rz*rz)
    if L == 0:
        return np.eye(3)
    u = np.array([rx/L, ry/L, rz/L])
    xy_len = math.sqrt(rx*rx + ry*ry)
    if xy_len > 0:
        e = np.array([-ry/xy_len, rx/xy_len, 0.0])
    else:
        e = np.array([1.0, 0.0, 0.0])
    n = np.cross(u, e)
    R = np.stack([e, n, u], axis=0)
    return R

ref_point = np.array([4094370.9, 2009573.3, 4443568.4])
R = get_enu_rotation_matrix(ref_point)

json_dir = "data_cache/json_decoded/NodeData"
jsons = []
for root, dirs, files in os.walk(json_dir):
    for f in files:
        if f.endswith(".json"):
            jsons.append(os.path.join(root, f))

tiles = []
for jp in sorted(jsons):
    with open(jp) as f:
        data = json.load(f)
    ma = data["matrix_globe_from_mesh"]
    
    all_verts = []
    for mesh in data["meshes"]:
        verts_b64 = mesh.get("vertices", "")
        raw = unpack_vertices(base64.b64decode(verts_b64))
        if len(raw) == 0:
            continue
        ecef = apply_matrix(raw, ma)
        enu = (ecef - ref_point) @ R.T
        all_verts.append(enu)
    
    if not all_verts:
        continue
    verts = np.vstack(all_verts)
    mn = verts.min(axis=0)
    mx = verts.max(axis=0)
    
    tiles.append({
        "file": os.path.basename(jp),
        "tx": ma[12], "ty": ma[13], "tz": ma[14],
        "e_min": mn[0], "e_max": mx[0],
        "n_min": mn[1], "n_max": mx[1],
        "u_min": mn[2], "u_max": mx[2],
        "n_verts": len(verts),
        "area": (mx[0]-mn[0]) * (mx[1]-mn[1]),
    })

# Sort by area (largest first = coarsest LOD)
tiles.sort(key=lambda t: -t["area"])

print(f"{'#':>3s}  {'E range':>25s}  {'N range':>25s}  {'nV':>6s}  {'area':>10s}")
print("-" * 80)
for i, t in enumerate(tiles[:20]):
    e_range = f"[{t['e_min']:>8.1f}, {t['e_max']:>8.1f}]"
    n_range = f"[{t['n_min']:>8.1f}, {t['n_max']:>8.1f}]"
    print(f"{i:>3d}  {e_range:>25s}  {n_range:>25s}  {t['n_verts']:>6d}  {t['area']:>10.0f}")

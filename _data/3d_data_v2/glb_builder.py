"""
GLB file builder for decoded Google Earth meshes.

Constructs GLB binary files using pygltflib from DecodedMesh objects.
Handles vertex positions, normals, UVs, indices, and JPG textures.
"""

import io
import struct
import ctypes
from pathlib import Path
import numpy as np
from PIL import Image
import pygltflib

from mesh_decoder import DecodedMesh

# Load libcrn for Crunch texture decompression
_libcrn = None
try:
    _libcrn_path = Path(__file__).parent / "libcrn.so"
    if _libcrn_path.exists():
        _libcrn = ctypes.CDLL(str(_libcrn_path))
        _libcrn.crn_get_decompressed_size.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint]
        _libcrn.crn_get_decompressed_size.restype = ctypes.c_uint
        _libcrn.crn_decompress.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint]
        _libcrn.crn_decompress.restype = None
except Exception as e:
    print(f"Warning: Failed to load libcrn.so: {e}")


def build_glb(
    meshes: list[DecodedMesh],
    octant_path: str,
    reference_point: np.ndarray | None = None,
) -> bytes:
    """
    Build a GLB file from decoded meshes.

    If reference_point is provided, vertex positions are offset by subtracting it
    (to keep coordinates near-origin for game engine use).

    Returns the GLB file content as bytes.
    """
    if not meshes:
        return b""

    gltf = pygltflib.GLTF2(
        asset=pygltflib.Asset(version="2.0", generator="earth-tile-exporter"),
        scene=0,
        scenes=[pygltflib.Scene(nodes=list(range(len(meshes))))],
        nodes=[],
        meshes=[],
        accessors=[],
        bufferViews=[],
        buffers=[],
        materials=[],
        textures=[],
        images=[],
        samplers=[],
    )

    # Single buffer for all binary data
    buffer_data = bytearray()

    for mesh_idx, dm in enumerate(meshes):
        if len(dm.positions) == 0 or len(dm.indices) == 0:
            continue

        # Offset positions to local ECEF space (translated by reference_point)
        positions = dm.positions.copy()
        if reference_point is not None:
            positions -= reference_point

        positions_f32 = positions.astype(np.float32)
        normals_f32 = dm.normals.astype(np.float32)
        uvs_f32 = dm.uvs.astype(np.float32)

        # Determine index type
        max_index = int(dm.indices.max())
        if max_index < 65536:
            indices_data = dm.indices.astype(np.uint16)
            index_component_type = pygltflib.UNSIGNED_SHORT
        else:
            indices_data = dm.indices.astype(np.uint32)
            index_component_type = pygltflib.UNSIGNED_INT

        # -- Material and texture --
        material_idx = len(gltf.materials)
        tex_idx = len(gltf.textures)
        img_idx = len(gltf.images)

        # Encode texture as PNG for GLB embedding
        tex_bytes = _prepare_texture(dm)

        if tex_bytes:
            # Image buffer view
            img_bv_start = len(buffer_data)
            buffer_data.extend(tex_bytes)
            _pad_to_4(buffer_data)
            img_bv_idx = len(gltf.bufferViews)
            gltf.bufferViews.append(
                pygltflib.BufferView(
                    buffer=0,
                    byteOffset=img_bv_start,
                    byteLength=len(tex_bytes),
                )
            )

            gltf.images.append(
                pygltflib.Image(
                    bufferView=img_bv_idx,
                    mimeType="image/png",
                )
            )

            if not gltf.samplers:
                gltf.samplers.append(
                    pygltflib.Sampler(
                        magFilter=pygltflib.LINEAR,
                        minFilter=pygltflib.LINEAR_MIPMAP_LINEAR,
                        wrapS=pygltflib.CLAMP_TO_EDGE,
                        wrapT=pygltflib.CLAMP_TO_EDGE,
                    )
                )

            gltf.textures.append(
                pygltflib.Texture(
                    sampler=0,
                    source=img_idx,
                )
            )

            gltf.materials.append(
                pygltflib.Material(
                    pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(
                        baseColorTexture=pygltflib.TextureInfo(index=tex_idx),
                        metallicFactor=0.0,
                        roughnessFactor=1.0,
                    ),
                    doubleSided=True,
                )
            )
        else:
            gltf.materials.append(
                pygltflib.Material(
                    pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(
                        metallicFactor=0.0,
                        roughnessFactor=1.0,
                    ),
                    doubleSided=True,
                )
            )

        # -- Indices buffer view + accessor --
        idx_bytes = indices_data.tobytes()
        idx_bv_start = len(buffer_data)
        buffer_data.extend(idx_bytes)
        _pad_to_4(buffer_data)
        idx_bv_idx = len(gltf.bufferViews)
        gltf.bufferViews.append(
            pygltflib.BufferView(
                buffer=0,
                byteOffset=idx_bv_start,
                byteLength=len(idx_bytes),
                target=pygltflib.ELEMENT_ARRAY_BUFFER,
            )
        )

        idx_accessor_idx = len(gltf.accessors)
        gltf.accessors.append(
            pygltflib.Accessor(
                bufferView=idx_bv_idx,
                byteOffset=0,
                componentType=index_component_type,
                count=len(indices_data),
                type=pygltflib.SCALAR,
                max=[int(indices_data.max())],
                min=[int(indices_data.min())],
            )
        )

        # -- Position buffer view + accessor --
        pos_bytes = positions_f32.tobytes()
        pos_bv_start = len(buffer_data)
        buffer_data.extend(pos_bytes)
        _pad_to_4(buffer_data)
        pos_bv_idx = len(gltf.bufferViews)
        gltf.bufferViews.append(
            pygltflib.BufferView(
                buffer=0,
                byteOffset=pos_bv_start,
                byteLength=len(pos_bytes),
                target=pygltflib.ARRAY_BUFFER,
            )
        )

        pos_accessor_idx = len(gltf.accessors)
        gltf.accessors.append(
            pygltflib.Accessor(
                bufferView=pos_bv_idx,
                byteOffset=0,
                componentType=pygltflib.FLOAT,
                count=len(positions_f32),
                type=pygltflib.VEC3,
                max=positions_f32.max(axis=0).tolist(),
                min=positions_f32.min(axis=0).tolist(),
            )
        )

        # -- Normal buffer view + accessor --
        norm_bytes = normals_f32.tobytes()
        norm_bv_start = len(buffer_data)
        buffer_data.extend(norm_bytes)
        _pad_to_4(buffer_data)
        norm_bv_idx = len(gltf.bufferViews)
        gltf.bufferViews.append(
            pygltflib.BufferView(
                buffer=0,
                byteOffset=norm_bv_start,
                byteLength=len(norm_bytes),
                target=pygltflib.ARRAY_BUFFER,
            )
        )

        norm_accessor_idx = len(gltf.accessors)
        gltf.accessors.append(
            pygltflib.Accessor(
                bufferView=norm_bv_idx,
                byteOffset=0,
                componentType=pygltflib.FLOAT,
                count=len(normals_f32),
                type=pygltflib.VEC3,
            )
        )

        # -- UV buffer view + accessor --
        uv_bytes = uvs_f32.tobytes()
        uv_bv_start = len(buffer_data)
        buffer_data.extend(uv_bytes)
        _pad_to_4(buffer_data)
        uv_bv_idx = len(gltf.bufferViews)
        gltf.bufferViews.append(
            pygltflib.BufferView(
                buffer=0,
                byteOffset=uv_bv_start,
                byteLength=len(uv_bytes),
                target=pygltflib.ARRAY_BUFFER,
            )
        )

        uv_accessor_idx = len(gltf.accessors)
        gltf.accessors.append(
            pygltflib.Accessor(
                bufferView=uv_bv_idx,
                byteOffset=0,
                componentType=pygltflib.FLOAT,
                count=len(uvs_f32),
                type=pygltflib.VEC2,
            )
        )

        # -- Mesh primitive --
        primitive = pygltflib.Primitive(
            attributes=pygltflib.Attributes(
                POSITION=pos_accessor_idx,
                NORMAL=norm_accessor_idx,
                TEXCOORD_0=uv_accessor_idx,
            ),
            indices=idx_accessor_idx,
            material=material_idx,
        )

        gltf_mesh_idx = len(gltf.meshes)
        gltf.meshes.append(
            pygltflib.Mesh(
                primitives=[primitive],
                name=f"tile_{octant_path}_mesh{mesh_idx}",
            )
        )

        gltf.nodes.append(
            pygltflib.Node(
                mesh=gltf_mesh_idx,
                name=f"node_{octant_path}_mesh{mesh_idx}",
            )
        )

    # Set buffer
    gltf.buffers.append(
        pygltflib.Buffer(byteLength=len(buffer_data))
    )

    # Set binary blob
    gltf.set_binary_blob(bytes(buffer_data))

    # Serialize to GLB bytes
    glb_bytes = b"".join(gltf.save_to_bytes())
    return glb_bytes


def _pad_to_4(data: bytearray):
    """Pad bytearray to 4-byte alignment."""
    while len(data) % 4 != 0:
        data.append(0)


def _prepare_texture(dm: DecodedMesh) -> bytes | None:
    """
    Prepare texture data for GLB embedding.
    Converts JPG and CRN-DXT1 to PNG. Returns PNG bytes or None.
    """
    if not dm.texture_data:
        return None

    try:
        if dm.texture_format == 1:  # JPG
            img = Image.open(io.BytesIO(dm.texture_data))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
        elif dm.texture_format == 6:  # CRN-DXT1 (Crunch compressed DXT1)
            if _libcrn is None:
                print("Warning: libcrn not available, skipping CRN texture")
                return None

            # 1. Decompress CRN to DXT1
            src_buf = ctypes.create_string_buffer(dm.texture_data)
            dst_size = _libcrn.crn_get_decompressed_size(src_buf, len(dm.texture_data), 0)
            dst_buf = ctypes.create_string_buffer(dst_size)
            _libcrn.crn_decompress(src_buf, len(dm.texture_data), dst_buf, dst_size, 0)
            
            dxt1_data = dst_buf.raw

            # 2. Decode DXT1 to raw RGBA
            rgba_data = _decode_dxt1(dxt1_data, dm.texture_width, dm.texture_height)

            # 3. Save as PNG
            img = Image.frombytes("RGBA", (dm.texture_width, dm.texture_height), rgba_data)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
        else:
            return None
    except Exception as e:
        print(f"Warning: Failed to decode texture: {e}")
        return None


def _decode_dxt1(dxt_data: bytes, width: int, height: int) -> bytes:
    """
    Decode raw DXT1 texture bytes to 32-bit RGBA pixels.
    """
    rgba = bytearray(width * height * 4)
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4

    offset = 0
    for by in range(blocks_y):
        for bx in range(blocks_x):
            if offset >= len(dxt_data):
                break

            color0, color1, code = struct.unpack_from("<HHI", dxt_data, offset)
            offset += 8

            # Unpack color0 (RGB 565)
            r0_5 = (color0 >> 11) & 31
            g0_6 = (color0 >> 5) & 63
            b0_5 = color0 & 31
            r0 = (r0_5 << 3) | (r0_5 >> 2)
            g0 = (g0_6 << 2) | (g0_6 >> 4)
            b0 = (b0_5 << 3) | (b0_5 >> 2)

            # Unpack color1 (RGB 565)
            r1_5 = (color1 >> 11) & 31
            g1_6 = (color1 >> 5) & 63
            b1_5 = color1 & 31
            r1 = (r1_5 << 3) | (r1_5 >> 2)
            g1 = (g1_6 << 2) | (g1_6 >> 4)
            b1 = (b1_5 << 3) | (b1_5 >> 2)

            # Build color palette
            if color0 > color1:
                colors = [
                    (r0, g0, b0, 255),
                    (r1, g1, b1, 255),
                    ((2*r0 + r1) // 3, (2*g0 + g1) // 3, (2*b0 + b1) // 3, 255),
                    ((r0 + 2*r1) // 3, (g0 + 2*g1) // 3, (b0 + 2*b1) // 3, 255)
                ]
            else:
                colors = [
                    (r0, g0, b0, 255),
                    (r1, g1, b1, 255),
                    ((r0 + r1) // 2, (g0 + g1) // 2, (b0 + b1) // 2, 255),
                    (0, 0, 0, 0)
                ]

            for py in range(4):
                y = by * 4 + py
                if y >= height:
                    continue
                for px in range(4):
                    x = bx * 4 + px
                    if x >= width:
                        continue

                    pixel_idx = py * 4 + px
                    color_idx = (code >> (2 * pixel_idx)) & 3

                    rgba_offset = (y * width + x) * 4
                    r, g, b, a = colors[color_idx]
                    rgba[rgba_offset] = r
                    rgba[rgba_offset+1] = g
                    rgba[rgba_offset+2] = b
                    rgba[rgba_offset+3] = a

    return bytes(rgba)

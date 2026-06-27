"use strict";

const fs = require('fs-extra');
const path = require('path');
const decodeResource = require('./lib/decode-resource');

async function main() {
    try {
        const bytesPath = process.argv[2];
        const glbPath = process.argv[3];
        const refX = parseFloat(process.argv[4] || '0');
        const refY = parseFloat(process.argv[5] || '0');
        const refZ = parseFloat(process.argv[6] || '0');
        const maskedOctantsStr = process.argv[7] || '';
        const maskedOctants = new Set(maskedOctantsStr ? maskedOctantsStr.split(',').map(Number) : []);

        if (!bytesPath || !glbPath) {
            console.error("Usage: node our-script.js <bytesPath> <glbPath> [refX] [refY] [refZ] [maskedOctants]");
            process.exit(1);
        }

        const fileBytes = fs.readFileSync(bytesPath);
        
        // Command 3 is NodeData
        const result = await decodeResource(3, fileBytes);
        const nodeData = result.payload;

        if (!nodeData.meshes || nodeData.meshes.length === 0) {
            console.warn(`No meshes found in ${bytesPath}`);
            // Write a dummy empty file or empty GLB if needed, or exit
            process.exit(0);
        }

        let bufferData = [];
        let byteOffset = 0;
        let bufferViews = [];
        let accessors = [];
        let gltfMeshes = [];
        let gltfNodes = [];
        let gltfImages = [];
        let gltfTextures = [];
        let gltfMaterials = [];
        let sceneNodes = [];

        function addBufferView(dataBuffer, target) {
            // Start of each bufferView must be 4-byte aligned.
            // Since we pad the bufferViews to multiple of 4, byteOffset is always aligned.
            const padding = (4 - (dataBuffer.length % 4)) % 4;
            let paddedBuffer = dataBuffer;
            if (padding > 0) {
                paddedBuffer = Buffer.concat([dataBuffer, Buffer.alloc(padding)]);
            }
            const viewIdx = bufferViews.length;
            const start = byteOffset;
            bufferData.push(paddedBuffer);
            byteOffset += paddedBuffer.length;

            const view = {
                buffer: 0,
                byteOffset: start,
                byteLength: dataBuffer.length
            };
            if (target) {
                view.target = target;
            }
            bufferViews.push(view);
            return viewIdx;
        }

        const ma = nodeData.matrixGlobeFromMesh;

        for (let meshIdx = 0; meshIdx < nodeData.meshes.length; meshIdx++) {
            const mesh = nodeData.meshes[meshIdx];
            const vertices = mesh.vertices;
            const indices = mesh.indices;
            const normals = mesh.normals;
            const uvOffsetAndScale = mesh.uvOffsetAndScale;

            const vertexCount = vertices.length / 8;
            const filteredIndices = [];

            // 1. Process triangle strip indices and apply octant mask
            for (let i = 0; i < indices.length - 2; i += 1) {
                if (i === mesh.layerBounds[3]) break;
                const a = indices[i + 0];
                const b = indices[i + 1];
                const c = indices[i + 2];
                if (a === b || a === c || b === c) continue;

                // Octant check
                const wa = vertices[a * 8 + 3];
                const wb = vertices[b * 8 + 3];
                const wc = vertices[c * 8 + 3];

                if (maskedOctants.has(wa) || maskedOctants.has(wb) || maskedOctants.has(wc)) {
                    continue;
                }

                if (i & 1) {
                    filteredIndices.push(a, c, b);
                } else {
                    filteredIndices.push(a, b, c);
                }
            }

            // Skip mesh if no triangles are left
            if (filteredIndices.length === 0) {
                continue;
            }

            // 2. Build positions and get bounding box
            const positionsF32 = new Float32Array(vertexCount * 3);
            let minX = Infinity, minY = Infinity, minZ = Infinity;
            let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;

            for (let i = 0; i < vertexCount; i++) {
                const x_raw = vertices[i * 8 + 0];
                const y_raw = vertices[i * 8 + 1];
                const z_raw = vertices[i * 8 + 2];

                const x = x_raw * ma[0] + y_raw * ma[4] + z_raw * ma[8] + ma[12] - refX;
                const y = x_raw * ma[1] + y_raw * ma[5] + z_raw * ma[9] + ma[13] - refY;
                const z = x_raw * ma[2] + y_raw * ma[6] + z_raw * ma[10] + ma[14] - refZ;

                positionsF32[i * 3 + 0] = x;
                positionsF32[i * 3 + 1] = y;
                positionsF32[i * 3 + 2] = z;

                if (x < minX) minX = x;
                if (y < minY) minY = y;
                if (z < minZ) minZ = z;
                if (x > maxX) maxX = x;
                if (y > maxY) maxY = y;
                if (z > maxZ) maxZ = z;
            }

            // 3. Build normals
            const normalsF32 = new Float32Array(vertexCount * 3);
            if (normals && normals.length > 0) {
                for (let i = 0; i < vertexCount; i++) {
                    const x_raw = normals[i * 4 + 0] - 127;
                    const y_raw = normals[i * 4 + 1] - 127;
                    const z_raw = normals[i * 4 + 2] - 127;

                    let nx = x_raw * ma[0] + y_raw * ma[4] + z_raw * ma[8];
                    let ny = x_raw * ma[1] + y_raw * ma[5] + z_raw * ma[9];
                    let nz = x_raw * ma[2] + y_raw * ma[6] + z_raw * ma[10];

                    const len = Math.sqrt(nx*nx + ny*ny + nz*nz);
                    if (len > 0) {
                        nx /= len;
                        ny /= len;
                        nz /= len;
                    } else {
                        nz = 1.0;
                    }

                    normalsF32[i * 3 + 0] = nx;
                    normalsF32[i * 3 + 1] = ny;
                    normalsF32[i * 3 + 2] = nz;
                }
            } else {
                for (let i = 0; i < vertexCount; i++) {
                    normalsF32[i * 3 + 2] = 1.0;
                }
            }

            // 4. Build UVs
            const uvsF32 = new Float32Array(vertexCount * 2);
            if (uvOffsetAndScale) {
                for (let i = 0; i < vertexCount; i++) {
                    const u = vertices[i * 8 + 4] + vertices[i * 8 + 5] * 256;
                    const v = vertices[i * 8 + 6] + vertices[i * 8 + 7] * 256;

                    const ut = (u + uvOffsetAndScale[0]) * uvOffsetAndScale[2];
                    let vt = (v + uvOffsetAndScale[1]) * uvOffsetAndScale[3];

                    // Flip texture coordinates if format is CRN-DXT1
                    if (mesh.texture && mesh.texture.textureFormat === 6) {
                        vt = 1.0 - vt;
                    }

                    uvsF32[i * 2 + 0] = ut;
                    uvsF32[i * 2 + 1] = vt;
                }
            }

            // 5. Build Indices buffer format
            let indexComponentType = 5123; // UNSIGNED_SHORT
            let indicesBuffer;

            let maxIndex = 0;
            for (let idx of filteredIndices) {
                if (idx > maxIndex) maxIndex = idx;
            }

            if (maxIndex < 65536) {
                indicesBuffer = new Uint16Array(filteredIndices);
                indexComponentType = 5123;
            } else {
                indicesBuffer = new Uint32Array(filteredIndices);
                indexComponentType = 5125;
            }

            // 6. Push to Binary buffer
            const posBuffer = Buffer.from(positionsF32.buffer, positionsF32.byteOffset, positionsF32.byteLength);
            const normBuffer = Buffer.from(normalsF32.buffer, normalsF32.byteOffset, normalsF32.byteLength);
            const uvBuffer = Buffer.from(uvsF32.buffer, uvsF32.byteOffset, uvsF32.byteLength);
            const idxBuffer = Buffer.from(indicesBuffer.buffer, indicesBuffer.byteOffset, indicesBuffer.byteLength);

            const posBvIdx = addBufferView(posBuffer, 34962);
            const normBvIdx = addBufferView(normBuffer, 34962);
            const uvBvIdx = addBufferView(uvBuffer, 34962);
            const idxBvIdx = addBufferView(idxBuffer, 34963);

            const posAccIdx = accessors.length;
            accessors.push({
                bufferView: posBvIdx,
                byteOffset: 0,
                componentType: 5126,
                count: vertexCount,
                type: "VEC3",
                max: [maxX, maxY, maxZ],
                min: [minX, minY, minZ]
            });

            const normAccIdx = accessors.length;
            accessors.push({
                bufferView: normBvIdx,
                byteOffset: 0,
                componentType: 5126,
                count: vertexCount,
                type: "VEC3"
            });

            const uvAccIdx = accessors.length;
            accessors.push({
                bufferView: uvBvIdx,
                byteOffset: 0,
                componentType: 5126,
                count: vertexCount,
                type: "VEC2"
            });

            const idxAccIdx = accessors.length;
            accessors.push({
                bufferView: idxBvIdx,
                byteOffset: 0,
                componentType: indexComponentType,
                count: filteredIndices.length,
                type: "SCALAR"
            });

            // 7. Extract and build texture
            let texBytes = null;
            if (mesh.texture && mesh.texture.bytes) {
                const decodeTexture = require('./lib/decode-texture');
                const tex = mesh.texture;
                if (tex.textureFormat === 1) { // JPG
                    const texDecoded = decodeTexture(tex);
                    texBytes = texDecoded.buffer;
                } else if (tex.textureFormat === 6) { // CRN-DXT1
                    const decodeDXT = require('decode-dxt');
                    const buf = Buffer.from(tex.bytes);
                    const abuf = new Uint8Array(buf).buffer;
                    const imageDataView = new DataView(abuf, 0, tex.bytes.length);
                    const rgbaData = decodeDXT(imageDataView, tex.width, tex.height, 'dxt1');

                    // Convert to PNG using pngjs
                    const { PNG } = require('pngjs');
                    const png = new PNG({ width: tex.width, height: tex.height });
                    png.data = Buffer.from(rgbaData);
                    texBytes = PNG.sync.write(png);
                }
            }

            let matIdx = null;
            if (texBytes) {
                const imgBvIdx = addBufferView(texBytes);
                const imgIdx = gltfImages.length;
                gltfImages.push({
                    bufferView: imgBvIdx,
                    mimeType: "image/png"
                });

                const texIdx = gltfTextures.length;
                gltfTextures.push({
                    sampler: 0,
                    source: imgIdx
                });

                matIdx = gltfMaterials.length;
                gltfMaterials.push({
                    pbrMetallicRoughness: {
                        baseColorTexture: {
                            index: texIdx
                        },
                        metallicFactor: 0.0,
                        roughnessFactor: 1.0
                    }
                });
            }

            // 8. Add primitive, mesh, node
            const primitive = {
                attributes: {
                    POSITION: posAccIdx,
                    NORMAL: normAccIdx,
                    TEXCOORD_0: uvAccIdx
                },
                indices: idxAccIdx
            };
            if (matIdx !== null) {
                primitive.material = matIdx;
            }

            const currentGltfMeshIdx = gltfMeshes.length;
            gltfMeshes.push({
                primitives: [primitive],
                name: `mesh_${meshIdx}`
            });

            const currentGltfNodeIdx = gltfNodes.length;
            gltfNodes.push({
                mesh: currentGltfMeshIdx,
                name: `node_${meshIdx}`
            });
            sceneNodes.push(currentGltfNodeIdx);
        }

        if (sceneNodes.length === 0) {
            console.warn(`No non-degenerate visible meshes left to export for ${bytesPath}`);
            process.exit(0);
        }

        // 9. Assemble GLTF JSON structure
        const gltfJson = {
            asset: {
                version: "2.0",
                generator: "node-glb-builder"
            },
            scene: 0,
            scenes: [
                {
                    nodes: sceneNodes
                }
            ],
            nodes: gltfNodes,
            meshes: gltfMeshes,
            buffers: [
                {
                    byteLength: byteOffset
                }
            ],
            bufferViews: bufferViews,
            accessors: accessors
        };

        if (gltfMaterials.length > 0) gltfJson.materials = gltfMaterials;
        if (gltfTextures.length > 0) gltfJson.textures = gltfTextures;
        if (gltfImages.length > 0) gltfJson.images = gltfImages;
        if (gltfTextures.length > 0) {
            gltfJson.samplers = [
                {
                    magFilter: 9729, // LINEAR
                    minFilter: 9987, // LINEAR_MIPMAP_LINEAR
                    wrapS: 33071, // CLAMP_TO_EDGE
                    wrapT: 33071  // CLAMP_TO_EDGE
                }
            ];
        }

        const jsonStr = JSON.stringify(gltfJson);
        const jsonBuffer = Buffer.from(jsonStr, 'utf-8');

        // Pad JSON to 4-byte boundary
        const jsonPadding = (4 - (jsonBuffer.length % 4)) % 4;
        const jsonChunkLength = jsonBuffer.length + jsonPadding;
        const jsonChunkBuffer = Buffer.concat([
            jsonBuffer,
            Buffer.alloc(jsonPadding, 0x20)
        ]);

        const binChunkLength = byteOffset;
        const binChunkBuffer = Buffer.concat(bufferData);

        const totalGlbSize = 12 + 8 + jsonChunkLength + 8 + binChunkLength;

        const headerBuffer = Buffer.alloc(12);
        headerBuffer.writeUInt32LE(0x46546C67, 0); // Magic: 'glTF'
        headerBuffer.writeUInt32LE(2, 4);          // Version
        headerBuffer.writeUInt32LE(totalGlbSize, 8);

        const jsonHeaderBuffer = Buffer.alloc(8);
        jsonHeaderBuffer.writeUInt32LE(jsonChunkLength, 0);
        jsonHeaderBuffer.writeUInt32LE(0x4E4F534A, 4); // Type: 'JSON'

        const binHeaderBuffer = Buffer.alloc(8);
        binHeaderBuffer.writeUInt32LE(binChunkLength, 0);
        binHeaderBuffer.writeUInt32LE(0x004E4942, 4); // Type: 'BIN'

        const glbBuffer = Buffer.concat([
            headerBuffer,
            jsonHeaderBuffer,
            jsonChunkBuffer,
            binHeaderBuffer,
            binChunkBuffer
        ]);

        fs.ensureDirSync(path.dirname(glbPath));
        fs.writeFileSync(glbPath, glbBuffer);
        console.log(`Saved GLB to ${glbPath}`);

    } catch (e) {
        console.error("GLB export failed:", e);
        process.exit(1);
    }
}

main();

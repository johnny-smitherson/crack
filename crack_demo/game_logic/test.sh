#!/usr/bin/env bash
# Smoke tests for game_logic: native (default + worker feature) + wasm (node).
set -euo pipefail
cd "$(dirname "$0")"
echo "== game_logic: game data types, geo math, LOD, network rooms =="
cargo test
cargo test --features worker
wasm-pack test --node

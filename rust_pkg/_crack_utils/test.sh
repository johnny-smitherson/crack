#!/usr/bin/env bash
# Smoke tests for _crack_utils: native + wasm (node).
set -euo pipefail
cd "$(dirname "$0")"
echo "== _crack_utils: shared cross-platform utility helpers (time, rng, sleep, spawn) =="
cargo test
wasm-pack test --node

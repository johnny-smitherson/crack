#!/usr/bin/env bash
# Smoke tests for api_asscrack: native + wasm (node).
set -euo pipefail
cd "$(dirname "$0")"
echo "== api_asscrack: typed worker-API RPC framework (declare/implement macros, ApiClient, ApiImplMapping) =="
cargo test
wasm-pack test --node

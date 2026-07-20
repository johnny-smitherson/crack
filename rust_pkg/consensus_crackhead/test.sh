#!/usr/bin/env bash
# Smoke tests for consensus_crackhead: native + wasm (node).
set -euo pipefail
cd "$(dirname "$0")"
echo "== consensus_crackhead: placeholder consensus crate (link smoke test) =="
cargo test
wasm-pack test --node

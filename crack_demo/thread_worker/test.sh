#!/usr/bin/env bash
# Smoke tests for thread_worker: native only.
set -euo pipefail
cd "$(dirname "$0")"
echo "== thread_worker: in-process thread worker demo (spawn + WorkerPing) =="
cargo test

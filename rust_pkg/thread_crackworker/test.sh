#!/usr/bin/env bash
# Smoke tests for thread_crackworker: native only.
set -euo pipefail
cd "$(dirname "$0")"
echo "== thread_crackworker: tokio-thread WorkerLoaderFactory for api_asscrack =="
cargo test

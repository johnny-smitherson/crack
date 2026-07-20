#!/usr/bin/env bash
# Smoke tests for chat_cli: native only (bin-only crate).
set -euo pipefail
cd "$(dirname "$0")"
echo "== chat_cli: stdin/stdout global chat client over net_crackpipe =="
cargo test

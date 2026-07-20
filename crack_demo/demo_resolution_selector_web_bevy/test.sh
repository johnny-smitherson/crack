#!/usr/bin/env bash
# Smoke tests for demo_resolution_selector_web_bevy: native only (headless bevy app).
set -euo pipefail
cd "$(dirname "$0")"
echo "== demo_resolution_selector_web_bevy: main Bevy game (headless smoke test) =="
cargo test

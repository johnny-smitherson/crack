#!/usr/bin/env bash
# Smoke tests for web_worker: browser wasm only (headless firefox + chrome).
set -euo pipefail
cd "$(dirname "$0")"
echo "== web_worker: dedicated-worker wasm binary (API mapping surface) =="
# NOTE: export only one driver per invocation — when both GECKODRIVER and
# CHROMEDRIVER are set, wasm-bindgen-test-runner silently picks geckodriver
# even for `--chrome`.
GECKODRIVER=/usr/local/bin/geckodriver wasm-pack test --headless --firefox
CHROMEDRIVER=/usr/bin/chromedriver CHROME_BIN=/usr/bin/chromium wasm-pack test --headless --chrome

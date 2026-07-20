#!/usr/bin/env bash
# Smoke tests for web_serviceworker_crackloader: browser wasm only (headless firefox + chrome).
set -euo pipefail
cd "$(dirname "$0")"
echo "== web_serviceworker_crackloader: browser Worker loader factory (WebWorkerFactory) =="
# NOTE: export only one driver per invocation — when both GECKODRIVER and
# CHROMEDRIVER are set, wasm-bindgen-test-runner silently picks geckodriver
# even for `--chrome`.
GECKODRIVER=/usr/local/bin/geckodriver wasm-pack test --headless --firefox
CHROMEDRIVER=/usr/bin/chromedriver wasm-pack test --headless --chrome

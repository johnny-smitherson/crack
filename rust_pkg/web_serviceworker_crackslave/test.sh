#!/usr/bin/env bash
# Browser-wasm link smoke test for web_serviceworker_crackslave.
# The crate needs a real dedicated-worker scope at runtime, so the only test is
# a `links()` build/link smoke; it still must run in a browser (not node).
#
# NOTE: the wasm-bindgen test runner prefers geckodriver when both driver env
# vars are set, so each browser gets its own wasm-pack invocation with only its
# driver exported — otherwise the --chrome leg would silently re-run Firefox.
set -euo pipefail
cd "$(dirname "$0")"
echo "== web_serviceworker_crackslave: dedicated-worker payload shim (browser wasm only) =="
echo "-- firefox --"
GECKODRIVER=/usr/local/bin/geckodriver wasm-pack test --headless --firefox
echo "-- chrome --"
CHROME=/usr/bin/chromium CHROMEDRIVER=/usr/bin/chromedriver wasm-pack test --headless --chrome

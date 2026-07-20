#!/usr/bin/env bash
# Smoke tests for net_crackpipe: native + wasm (headless browsers).
set -euo pipefail
cd "$(dirname "$0")"
echo "== net_crackpipe: iroh gossip chat networking (rooms, presence, tickets) =="
cargo test
# rand -> getrandom needs a real browser; node is not sufficient.
# NOTE: export only one driver per invocation — when both GECKODRIVER and
# CHROMEDRIVER are set, wasm-bindgen-test-runner silently picks geckodriver
# even for `--chrome`.
GECKODRIVER=/usr/local/bin/geckodriver wasm-pack test --headless --firefox
CHROMEDRIVER=/usr/bin/chromedriver CHROME_BIN=/usr/bin/chromium wasm-pack test --headless --chrome

#!/usr/bin/env bash
# Smoke tests for storage_crackhouse: native (real rusqlite file) + wasm (OPFS, headless browsers).
set -euo pipefail
cd "$(dirname "$0")"
echo "== storage_crackhouse: declarative SQLite models + typed SQL API (native rusqlite / wasm OPFS) =="
cargo test
# OPFS is a browser-only storage API; `wasm-pack test --node` cannot exercise it.
# NOTE: export only one driver per invocation — when both GECKODRIVER and
# CHROMEDRIVER are set, wasm-bindgen-test-runner silently picks geckodriver
# even for `--chrome`.
GECKODRIVER=/usr/local/bin/geckodriver wasm-pack test --headless --firefox
CHROMEDRIVER=/usr/bin/chromedriver CHROME_BIN=/usr/bin/chromium wasm-pack test --headless --chrome

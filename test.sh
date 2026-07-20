#!/usr/bin/env bash
# Runs every crate's own test.sh, bottom-up in dependency order, stopping at
# the first failure. Each crate's script decides native vs wasm-node vs
# headless-browser for itself; see the individual test.sh files and READMEs.
set -euo pipefail
cd "$(dirname "$0")"

CRATES=(
    rust_pkg/_crack_utils
    rust_pkg/api_asscrack
    rust_pkg/thread_crackworker
    crack_demo/thread_worker
    rust_pkg/consensus_crackhead
    rust_pkg/net_crackpipe
    rust_pkg/storage_crackhouse
    rust_pkg/web_serviceworker_crackloader
    rust_pkg/web_serviceworker_crackslave
    crack_demo/game_logic
    crack_demo/chat_cli
    crack_demo/web_worker
    crack_demo/demo_resolution_selector_web_bevy
)

for crate in "${CRATES[@]}"; do
    echo "############################################################"
    echo "# ${crate}"
    echo "############################################################"
    if ! "./${crate}/test.sh"; then
        echo "!!! FAILED: ${crate}/test.sh !!!" >&2
        exit 1
    fi
done

echo "ALL TESTS OK"

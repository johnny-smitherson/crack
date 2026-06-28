#!/bin/bash
set -ex

if command -v sccache &> /dev/null; then
    export RUSTC_WRAPPER=sccache
fi

export RUST_LOG=info

cd crack_demo/demo_resolution_selector_web_bevy
trunk serve "$@"
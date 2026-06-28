#!/bin/bash
set -ex

if command -v sccache &> /dev/null; then
    export RUSTC_WRAPPER=sccache
fi

export RUST_LOG=info
export WGPU_BACKEND=gl

cd crack_demo/demo_resolution_selector_web_bevy
cargo run
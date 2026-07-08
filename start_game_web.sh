#!/bin/bash
set -ex

export RUST_LOG=info
./build_worker.sh

cd crack_demo/demo_resolution_selector_web_bevy
trunk watch "$@"
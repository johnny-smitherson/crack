#!/bin/bash

set -ex
export IMG_NAME=crack-dev:latest

if ! ( docker volume ls | grep crack-dev-root-dir ) ; then 
    docker volume create crack-dev-root-dir
fi

if ! ( docker volume ls | grep crack-dev-target-dir ) ; then 
    docker volume create crack-dev-target-dir
fi

docker rm -f crack-dev || true
# ./build.sh

# Docker-out-of-docker: mount the host's rootless podman API socket so crack-dev
# can spawn sibling sandbox containers on the host. CRACK_HOST_REPO_ROOT is the
# HOST path of the repo (crack-dev sees it at /workspace) — sandbox :O overlays
# must reference host paths, not container paths, since host podman resolves them.
HOST_PODMAN_SOCK="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/podman/podman.sock"
systemctl --user enable --now podman.socket || true

docker run -d \
  --name crack-dev \
  -v "$(dirname $PWD):/workspace" \
  -v "crack-dev-root-dir:/root" \
  -v "crack-dev-target-dir:/workspace/target" \
  -v "${HOST_PODMAN_SOCK}:/run/podman/podman.sock" \
  -e "CONTAINER_HOST=unix:///run/podman/podman.sock" \
  -e "CRACK_HOST_REPO_ROOT=$(dirname $PWD)" \
  -p "127.0.0.1:9847:9847" \
  -p "127.0.0.1:21122:22" \
  -p "127.0.0.1:9930:9930" \
  -p "127.0.0.1:9931:9931" \
  -p "127.0.0.1:9932:9932" \
  -p "127.0.0.1:9877:9877" \
  --init \
  $IMG_NAME /bin/bash _docker/_cont_start.sh
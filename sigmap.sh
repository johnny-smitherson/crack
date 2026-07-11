#!/bin/bash
set -e

cd "$(dirname "$0")/"

sigmap 2>&1 | grep wrote
sigmap --monorepo 2>&1 | grep monorepo
echo ok
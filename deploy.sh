#!/bin/bash
set -ex

rsync -av --exclude 'target' --exclude '.git' ./ dj-vaslui:crack/

ssh dj-vaslui "cd crack && cd _data && docker compose up -d"


#!/bin/bash
# le-registry-create.sh - Create a registry in LE AID

set -e
echo "Creating registry in LE AID"
source ./task-scripts/workshop-env-vars.sh

# create ACDC registry
docker compose exec tsx-shell \
  /vlei/tsx-script-runner.sh le/le-registry-create.ts \
    'docker' \
    "${LE_SALT}" \
    "le" \
    "le-oor-registry" \
    "/task-data/le-registry-info.json"

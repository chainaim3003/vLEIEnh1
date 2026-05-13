#!/bin/bash
# le-acdc-admit-le.sh - Admit the LE ACDC Credential

set -e

GRANT_SAID=$(jq -r .grantSaid ./task-data/le-credential-info.json)
QVI_PREFIX=$(jq -r .aid ./task-data/qvi-info.json)
echo "Admitting LE ACDC with IPEX Grant SAID: ${GRANT_SAID}"
source ./task-scripts/workshop-env-vars.sh
docker compose exec tsx-shell \
  /vlei/tsx-script-runner.sh le/le-acdc-admit-le.ts \
    'docker' \
    "${LE_SALT}" \
    "${GRANT_SAID}" \
    "${QVI_PREFIX}"

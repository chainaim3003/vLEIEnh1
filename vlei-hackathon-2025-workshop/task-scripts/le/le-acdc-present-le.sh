#!/bin/bash
# le-acdc-present-le.sh - Present the LE ACDC to the verifier (Sally)

set -e

CRED_SAID=$(jq -r .said ./task-data/le-credential-info.json)
echo "Presenting LE ACDC to verifier Credential SAID: ${CRED_SAID}"
source ./task-scripts/workshop-env-vars.sh
docker compose exec tsx-shell \
  /vlei/tsx-script-runner.sh le/le-acdc-present-le.ts \
    'docker' \
    "${LE_SALT}" \
    "le" \
    "${CRED_SAID}" \
    "${VERIFIER_AID}"

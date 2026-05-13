#!/bin/bash
# person-acdc-present-oor.sh - Present the OOR ACDC to the verifier (Sally)

set -e

CRED_SAID=$(jq -r .said ./task-data/oor-credential-info.json)
echo "Presenting OOR ACDC to verifier Credential SAID: ${CRED_SAID}"
source ./task-scripts/workshop-env-vars.sh
docker compose exec tsx-shell \
  /vlei/tsx-script-runner.sh person/person-acdc-present-oor.ts \
    'docker' \
    "${PERSON_SALT}" \
    "person" \
    "${CRED_SAID}" \
    "${VERIFIER_AID}"

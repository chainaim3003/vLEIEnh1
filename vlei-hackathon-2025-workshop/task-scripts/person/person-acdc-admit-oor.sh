#!/bin/bash
# person-acdc-admit-oor.sh - Admit the OOR ACDC Credential

set -e

GRANT_SAID=$(jq -r .grantSaid ./task-data/oor-credential-info.json)
QVI_PREFIX=$(jq -r .aid ./task-data/qvi-info.json)
echo "Admitting OOR ACDC with IPEX Grant SAID: ${GRANT_SAID}"
source ./task-scripts/workshop-env-vars.sh
docker compose exec tsx-shell \
  /vlei/tsx-script-runner.sh person/person-acdc-admit-oor.ts \
    'docker' \
    "${PERSON_SALT}" \
    "${GRANT_SAID}" \
    "${QVI_PREFIX}"

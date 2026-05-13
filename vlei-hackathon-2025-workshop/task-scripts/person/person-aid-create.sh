#!/bin/bash
# person-aid-create.sh - Create Person AID using SignifyTS and KERIA
# This script creates the Person AID using the SignifyTS client

set -e

echo "Creating Person AID using SignifyTS and KERIA"

# gets PERSON_SALT
source ./task-scripts/workshop-env-vars.sh

# Create Person Agent and AID
docker compose exec tsx-shell \
  /vlei/tsx-script-runner.sh person/person-aid-create.ts \
    'docker' \
    "${PERSON_SALT}" \
    "/task-data"

# Get the prefix
PERSON_PREFIX=$(cat ./task-data/person-aid.txt | tr -d " \t\n\r")
echo "   Prefix: ${PERSON_PREFIX}"

PERSON_OOBI=$(cat ./task-data/person-info.json | jq -r .oobi)
echo "   OOBI: ${PERSON_OOBI}"


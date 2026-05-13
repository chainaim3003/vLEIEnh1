#!/bin/bash
# le-acdc-issue-oor-auth.sh - Issue OOR Auth Credential from LE to QVI AID

# Create OOR Auth ACDC Credential
# This script issues the OOR Auth credential from the LE AID to the QVI AID

set -e

echo "Creating OOR Auth ACDC Credential"
source ./task-scripts/workshop-env-vars.sh

# Check if required info files exist
if [ ! -f "./task-data/person-info.json" ]; then
    echo "Required Person AID info file not found. Please run person-aid-create.sh first."
    exit 1
fi
if [ ! -f "./task-data/le-registry-info.json" ]; then
    echo "Required LE registry info file not found. Please run le-registry-create.sh first."
    exit 1
fi
if [ ! -f "./task-data/le-credential-info.json" ]; then
    echo "Required LE credential info file not found. Please run qvi-acdc-issue-le.sh first."
    exit 1
fi

# get QVI AID from qvi-info.json
QVI_AID=$(jq -r '.aid' ./task-data/qvi-info.json)

# get Person AID from person-info.json
PERSON_AID=$(jq -r '.aid' ./task-data/person-info.json)

# get LE Credential SAID from le-credential-info.json for the edge
LE_CRED_SAID=$(jq -r '.said' ./task-data/le-credential-info.json)

# Sample person data for OOR Auth credential
PERSON_NAME="John Smith"
PERSON_OOR="Head of Standards"

# Issue the OOR Auth credential
echo "Issuing OOR Auth credential to ${QVI_AID} for person ${PERSON_NAME}"
docker compose exec tsx-shell \
  /vlei/tsx-script-runner.sh le/le-acdc-issue-oor-auth.ts \
    'docker' \
    'le' \
    "${LE_SALT}" \
    "le-oor-registry" \
    "${OOR_AUTH_SCHEMA_SAID}" \
    "${QVI_AID}" \
    "${PERSON_AID}" \
    "${PERSON_NAME}" \
    "${PERSON_OOR}" \
    "${LE_CRED_SAID}" \
    "/task-data/oor-auth-credential-info.json"


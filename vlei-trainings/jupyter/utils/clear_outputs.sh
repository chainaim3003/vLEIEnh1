#!/usr/bin/env bash

echo "Clearing outputs of all notebooks in /app/notebooks"

cd /app/notebooks

jupyter nbconvert \
  --clear-output \
  --ClearOutputPreprocessor.enabled=True \
  --inplace \
  /app/notebooks/*.ipynb
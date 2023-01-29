#!/usr/bin/env bash
# exit on error
set -o errexit

poetry lock --no-update
poetry env use $PYTHON_VERSION
poetry install

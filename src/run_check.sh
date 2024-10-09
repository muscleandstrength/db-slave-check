#!/bin/bash

set -eu -o pipefail

# Set the path to your virtual environment
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_PATH="${SCRIPT_DIR}/../venv"

# Set the path to your Python script
SCRIPT_PATH="${SCRIPT_DIR}/checkslave.py"

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Run the Python script
python "$SCRIPT_PATH"

# Deactivate the virtual environment
deactivate

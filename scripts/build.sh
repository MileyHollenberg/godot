#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define the name of the virtual environment directory
VENV_DIR=".venv"

# Function to determine which python command to use (python3 or python)
find_python_command() {
    if command -v python3 &> /dev/null; then
        echo "python3"
    else
        echo "python"
    fi
}

PY_CMD=$(find_python_command)

# 1. Check if the virtual environment exists; if not, create it
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment in $VENV_DIR..."
    $PY_CMD -m venv "$VENV_DIR"
fi

# 2. Activate the virtual environment
# This works for Linux, macOS, and Git Bash on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source "$VENV_DIR/Scripts/activate"
else
    source "$VENV_DIR/bin/activate"
fi

# 3. Install InquirerPy (pip will skip this automatically if it's already installed)
echo "Ensuring dependencies are installed..."
python3 -m pip install InquirerPy > /dev/null

# 4. Run the build script
echo "Running build..."
python ./scripts/build.py

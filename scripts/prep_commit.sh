#!/bin/bash

if command -v py >/dev/null 2>&1; then
  PYTHON_CMD="py"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo "Error: No Python interpreter found (py, python3, or python)."
  exit 1
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
  source ~/pythonEnv/bin/activate
  $PYTHON_CMD -m pip install pre-commit
fi

# Check if pre-commit is already installed
if ! command -v pre-commit &> /dev/null; then
  echo "pre-commit not found. Installing..."
  $PYTHON_CMD -m pip install pre-commit
  if [ $? -ne 0 ]; then
    echo "Error: Failed to install pre-commit. Check your pip configuration and internet connection."
    exit 1
  fi
else
  echo "pre-commit already installed."
fi

# Get all changed files (unstaged)
UNSTAGED_FILES=$(git diff --name-only --diff-filter=ACMRTUB)

# Get all staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACMRTUB)

# Combine the lists, removing duplicates
if [ -n "$UNSTAGED_FILES" ] && [ -n "$STAGED_FILES" ]; then
  CHANGED_FILES=$(echo "$UNSTAGED_FILES $STAGED_FILES" | xargs -n 1 | sort -u | tr '\n' ' ')
elif [ -n "$UNSTAGED_FILES" ]; then
  CHANGED_FILES="$UNSTAGED_FILES"
elif [ -n "$STAGED_FILES" ]; then
  CHANGED_FILES="$STAGED_FILES"
else
  CHANGED_FILES=""
fi

# Check if there are any changed files
if [ -z "$CHANGED_FILES" ]; then
  echo "No changed files found. Exiting."
  exit 0
fi

# Run pre-commit on the changed files
echo "Running pre-commit on the following files: $CHANGED_FILES"
pre-commit run --show-diff-on-failure --color=always --files $CHANGED_FILES

if [ $? -ne 0 ]; then
  echo "pre-commit checks failed."
  exit 1
else
  echo "pre-commit checks passed."
fi

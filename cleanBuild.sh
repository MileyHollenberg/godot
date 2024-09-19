#!/bin/bash

# Check if the user has provided a directory
if [ -z "$1" ]; then
  echo "Usage: $0 <directory>"
  exit 1
fi

# Define the target directory
TARGET_DIR="$1"

# Find and delete all .d and .o files
find "$TARGET_DIR" -type f \( -name "*.d" -o -name "*.o" -o -name "*.a" \) -exec rm -f {} \;

# Success message
echo "Deleted all .d and .o files from $TARGET_DIR and its subdirectories."

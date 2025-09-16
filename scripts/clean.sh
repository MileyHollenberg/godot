
#!/bin/bash

# Check if the user has provided a directory
if [ -z "$1" ]; then
  echo "Usage: $0 <directory>"
  exit 1
fi

# Define the target directory
TARGET_DIR="$1"

# Find all .d, .o, and .a files and store them in an array
FILES=($(find "$TARGET_DIR" -type f \( -name "*.d" -o -name "*.o" -o -name "*.a" \)))

# Get the total number of files
TOTAL_FILES=${#FILES[@]}

# Loop through the files and delete them
for ((i=0; i<TOTAL_FILES; i++)); do
  FILE="${FILES[$i]}"
  printf "[%d/%d] Deleting: %s\n" "$((i+1))" "$TOTAL_FILES" "$FILE"
  rm -f "$FILE"
done

# Success message
echo "Deleted all .d, .o, and .a files from $TARGET_DIR and its subdirectories."

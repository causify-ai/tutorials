#!/bin/bash
# Wrapper script for fix_timestamps.py
# This script fixes timestamps in prediction files to match the current date

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment if it exists
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Default to today's date
TODAY=$(date +"%Y-%m-%d")
TARGET_DATE=${1:-$TODAY}

echo "Running timestamp fix with target date: $TARGET_DATE"

# Run the Python script with the target date
python "$SCRIPT_DIR/fix_timestamps.py" --target-date "$TARGET_DATE"

# Check if the script ran successfully
if [ $? -eq 0 ]; then
    echo "✅ Timestamps fixed successfully!"
else
    echo "❌ Error fixing timestamps."
    exit 1
fi 
#!/bin/bash
# Script to clean up obsolete files in the Bitcoin forecast project

# Set the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Running cleanup script from $SCRIPT_DIR"
echo "Project root: $PROJECT_ROOT"

# Make the Python script executable
chmod +x "$SCRIPT_DIR/cleanup_obsolete_files.py"

# First run in dry-run mode to show what would be deleted
echo "Running in dry-run mode to show what would be deleted:"
python "$SCRIPT_DIR/cleanup_obsolete_files.py" --check-usage

# Ask for confirmation
read -p "Do you want to delete these files? (y/n) " -n 1 -r
echo    # Move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Run with delete flag
    echo "Deleting obsolete files..."
    python "$SCRIPT_DIR/cleanup_obsolete_files.py" --delete --check-usage
    echo "Cleanup complete."
else
    echo "Cleanup cancelled."
fi 
#!/bin/bash
# Run the data fix script to repair any malformed data files

# Set the correct paths
export PYTHONPATH=/app:$PYTHONPATH

# Print informational message
echo "Starting data file repair process..."
echo "This script will fix any malformed CSV data files causing errors in the Bitcoin forecast application."
echo "Backups of original files will be created before making changes."
echo

# Run the data fix script
python3 /app/scripts/fix_data_files.py

# Check the exit status
if [ $? -eq 0 ]; then
    echo "Data file repair completed successfully."
    echo "You may need to restart the bitcoin-forecast-app and dashboard services."
    exit 0
elif [ $? -eq 1 ]; then
    echo "Data file repair completed with warnings. Some files could not be repaired."
    echo "Please check the logs for more information."
    echo "You may need to restart the bitcoin-forecast-app and dashboard services."
    exit 1
else
    echo "Data file repair failed. Please check the logs for more information."
    exit 2
fi 
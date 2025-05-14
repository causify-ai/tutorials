#!/bin/bash
# Script to fix issues with metrics data, focusing on data veracity
# This script identifies and corrects issues with metrics data, especially timestamp alignment

# Set the correct paths
export PYTHONPATH=/app:$PYTHONPATH

# Print informational message
echo "Starting metrics data validation and repair process..."
echo "This script will ensure that metrics data only includes entries where both"
echo "actual and predicted data exist for the same timestamp, maintaining data veracity."
echo

# Run the data fix script with focus on metrics
python3 /app/scripts/fix_data_files.py --metrics-only

# Check the exit status
if [ $? -eq 0 ]; then
    echo "Metrics data repair completed successfully."
    echo "The dashboard will now show accurate MAE values that correspond to actual predictions."
    exit 0
elif [ $? -eq 1 ]; then
    echo "Metrics data repair completed with warnings. Some issues could not be fixed."
    echo "Please check the logs for more information."
    exit 1
else
    echo "Metrics data repair failed. Please check the logs for more information."
    exit 2
fi 
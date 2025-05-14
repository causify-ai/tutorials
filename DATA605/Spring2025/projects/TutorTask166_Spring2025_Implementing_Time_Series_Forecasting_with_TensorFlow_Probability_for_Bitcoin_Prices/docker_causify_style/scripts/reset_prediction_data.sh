#!/bin/bash
# Script to reset prediction and metrics data, ensuring a fresh start with proper timestamps

echo "Resetting prediction and metrics data files to fix timestamp issues..."

# Define file paths
# Check if we're running in Docker or locally
if [ -d "/app" ]; then
    # Docker path
    PREDICTIONS_FILE="/app/data/predictions/instant_predictions.csv"
    METRICS_FILE="/app/data/predictions/instant_metrics.csv"
else
    # Local path
    PREDICTIONS_FILE="data/predictions/instant_predictions.csv"
    METRICS_FILE="data/predictions/instant_metrics.csv"
fi

# Create directories if they don't exist
mkdir -p $(dirname "$PREDICTIONS_FILE")
mkdir -p $(dirname "$METRICS_FILE")

# Backup existing files with timestamp
TIMESTAMP=$(date +%Y%m%d%H%M%S)
if [ -f "$PREDICTIONS_FILE" ]; then
    PRED_BACKUP="${PREDICTIONS_FILE}.bak.${TIMESTAMP}"
    cp "$PREDICTIONS_FILE" "$PRED_BACKUP"
    echo "Backed up predictions file to ${PRED_BACKUP}"
fi

if [ -f "$METRICS_FILE" ]; then
    METRICS_BACKUP="${METRICS_FILE}.bak.${TIMESTAMP}"
    cp "$METRICS_FILE" "$METRICS_BACKUP"
    echo "Backed up metrics file to ${METRICS_BACKUP}"
fi

# Reset files with just headers
echo "timestamp,pred_price,pred_lower,pred_upper" > "$PREDICTIONS_FILE"
echo "timestamp,std,mae,rmse" > "$METRICS_FILE"

# Add a test entry with the current timestamp to ensure proper alignment
CURRENT_ISO_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S")
echo "$CURRENT_ISO_TIME,100000,99000,101000" >> "$PREDICTIONS_FILE"
echo "$CURRENT_ISO_TIME,500,1000,1200" >> "$METRICS_FILE"

echo "Reset complete. Files now have headers and one test entry with the current timestamp."
echo "This should fix the dashboard display issues." 
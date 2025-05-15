#!/bin/bash
# Script to clean up obsolete data files and limit growth
# This helps prevent performance degradation over time

set -e

echo "Starting data cleanup process..."

# Set the max number of lines to keep in the data file
MAX_LINES=1000

# Get the data directory
DATA_DIR="/app/data"
RAW_DATA_FILE="${DATA_DIR}/raw/instant_data.csv"
BACKUP_DIR="${DATA_DIR}/backup"

# Make sure backup directory exists
mkdir -p "${BACKUP_DIR}"

# Function to trim large files
trim_large_file() {
    local file=$1
    local max_lines=$2
    
    if [ -f "$file" ]; then
        # Count lines in the file
        local lines=$(wc -l < "$file")
        
        if [ "$lines" -gt "$max_lines" ]; then
            echo "File $file has $lines lines, trimming to $max_lines lines"
            
            # Create a backup before trimming
            local backup_file="${BACKUP_DIR}/$(basename $file).$(date +%Y%m%d%H%M%S).bak"
            cp "$file" "$backup_file"
            
            # Keep header and last MAX_LINES-1 data lines
            head -1 "$file" > "${file}.tmp"
            tail -n $(($max_lines - 1)) "$file" >> "${file}.tmp"
            mv "${file}.tmp" "$file"
            
            echo "Trimmed $file to $max_lines lines"
        else
            echo "File $file has $lines lines, no trimming needed"
        fi
    fi
}

# Trim data files
trim_large_file "$RAW_DATA_FILE" "$MAX_LINES"

# Clean up old backup files (keep only last 5)
if [ -d "$BACKUP_DIR" ]; then
    echo "Cleaning up old backup files..."
    ls -t "${BACKUP_DIR}"/*.bak 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null || true
fi

echo "Data cleanup completed" 
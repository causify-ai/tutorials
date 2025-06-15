#!/bin/bash
set -euo pipefail
# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load config values

# 1) Figure out where *this* script lives
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &>/dev/null && pwd )"
# 2) Project root is one level up from scripts/
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." &>/dev/null && pwd )"
# 3) Point at your real config file
CONFIG_FILE="$PROJECT_ROOT/configs/config.yml"
# 4) Now use yq against that
RAW_DATA_FILE=$( yq e '.data.raw_data.instant_data.file'   "$CONFIG_FILE" )
PREDICTIONS_FILE=$( yq e '.data.predictions.instant.path'  "$CONFIG_FILE" )
METRICS_FILE=$( yq e '.data.predictions.instant.metrics'   "$CONFIG_FILE" )
echo "raw → $RAW_DATA_FILE"
echo "pred → $PREDICTIONS_FILE"
echo "metrics → $METRICS_FILE"

# Function to check if a service is running
check_service() {
    local service=$1
    local status=$(docker-compose ps -q $service)
    if [ -z "$status" ]; then
        echo "❌ $service is not running"
        return 1
    else
        echo "✅ $service is running"
        return 0
    fi
}

# Function to check data file
check_data_file() {
    local file="data/raw_data/instant_data/bitcoin_prices.csv"
    if [ -f "$file" ]; then
        echo "✅ Data file exists: $file"
        echo "Last 5 entries:"
        tail -n 5 "$file"
    else
        echo "❌ Data file not found: $file"
    fi
}

# Function to check Kafka
check_kafka() {
    local status=$(docker-compose ps -q kafka)
    if [ -z "$status" ]; then
        echo "❌ Kafka is not running"
    else
        echo "✅ Kafka is running"
        echo "Kafka topics:"
        docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
    fi
}

# Main monitoring loop
echo "=== Bitcoin Price Data Collection Monitor ==="
echo "Checking services..."
check_service "data-collector"
check_service "bitcoin-forecast-app"
check_service "dashboard"

echo -e "\nChecking Kafka..."
check_kafka

echo -e "\nChecking data collection..."
check_data_file

echo -e "\nMonitoring logs (press Ctrl+C to exit)..."
docker-compose logs -f data-collector bitcoin-forecast-app dashboard 
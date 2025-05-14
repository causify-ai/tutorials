#!/bin/bash
# Script to update all Docker services to use the unified configuration

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "===== Bitcoin Price Forecasting System Configuration Update ====="
echo "This script will update all Docker services to use the unified configuration."

# Check if the unified config file exists
if [ ! -f "$PROJECT_ROOT/configs/unified_config.yaml" ]; then
    echo "❌ Error: Unified configuration file not found at $PROJECT_ROOT/configs/unified_config.yaml"
    exit 1
fi

# Create backup of the original config files
echo "📁 Creating backups of original configuration files..."
mkdir -p "$PROJECT_ROOT/configs/backups"
cp "$PROJECT_ROOT/configs/config.yaml" "$PROJECT_ROOT/configs/backups/config.yaml.bak" 2>/dev/null || true
cp "$PROJECT_ROOT/data_collector/configs/config.yaml" "$PROJECT_ROOT/configs/backups/data_collector_config.yaml.bak" 2>/dev/null || true

# Copy the unified config to the main config location
echo "📋 Installing unified configuration..."
cp "$PROJECT_ROOT/configs/unified_config.yaml" "$PROJECT_ROOT/configs/config.yaml"

# Rebuild the Docker services
echo "🔄 Rebuilding Docker services to use the new configuration..."
cd "$PROJECT_ROOT/.."
docker-compose build --no-cache data-collector bitcoin-forecast-app dashboard

echo "✅ Configuration update complete!"
echo "To apply changes, restart the services with: docker-compose up -d" 
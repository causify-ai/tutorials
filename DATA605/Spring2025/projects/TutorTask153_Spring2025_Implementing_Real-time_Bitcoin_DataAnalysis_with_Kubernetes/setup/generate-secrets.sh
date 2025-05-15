#!/bin/bash
set -e

# Check if .env.secrets exists
if [ ! -f .env.secrets ]; then
  echo "Error: .env.secrets file not found!"
  echo "Please create this file with your secret values. See .env.secrets.example"
  exit 1
fi

# Source the secret values
source .env.secrets

# Encode the PostgreSQL password in base64
POSTGRES_PASSWORD_BASE64=$(echo -n "$POSTGRES_PASSWORD" | base64)

# Generate postgres-secret.yaml
sed "s/\${POSTGRES_PASSWORD_BASE64}/$POSTGRES_PASSWORD_BASE64/g" kubernetes/postgres-secret.yaml.template > kubernetes/postgres-secret.yaml
echo "Generated kubernetes/postgres-secret.yaml"

# Create Grafana secret separately
kubectl create secret generic grafana-secret \
  --from-literal=admin-password="$GRAFANA_ADMIN_PASSWORD" \
  --dry-run=client -o yaml > kubernetes/grafana/grafana-secret.yaml
echo "Generated kubernetes/grafana/grafana-secret.yaml"

# Process other templates if needed

echo "All secret files have been generated successfully!"
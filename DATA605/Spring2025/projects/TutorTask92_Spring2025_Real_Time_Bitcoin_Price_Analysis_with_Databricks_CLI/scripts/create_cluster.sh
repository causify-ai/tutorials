#!/bin/bash

echo "Creating Databricks cluster from config..."

# Create cluster and capture response
response=$(databricks clusters create --json-file config/cluster_config.json)

# Extract cluster_id using jq
cluster_id=$(echo "$response" | jq -r '.cluster_id')

# Save the cluster_id for later use
echo "$cluster_id" > config/cluster_id.txt

echo " Cluster created successfully!"
echo "Cluster ID: $cluster_id"
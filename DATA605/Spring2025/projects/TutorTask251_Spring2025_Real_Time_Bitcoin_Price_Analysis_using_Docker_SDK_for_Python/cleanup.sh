#!/bin/bash
# Stop and remove all project containers and volumes

docker rm -f influxdb grafana btc-fetcher fetch-data-scheduler 2>/dev/null || true
docker volume rm influxdb-data 2>/dev/null || true
echo "All project containers and volumes removed."

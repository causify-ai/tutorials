#!/bin/bash

# Run the Bitcoin monitor in interactive mode
docker compose build bitcoin-monitor

docker compose run --rm --service-ports bitcoin-monitor "$@"
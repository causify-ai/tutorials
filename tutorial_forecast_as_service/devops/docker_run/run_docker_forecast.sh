#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-1.0.0}"
export IMAGE="causify/tutorial_forecast_as_service:local-${USER}-${VERSION}"
echo "Using IMAGE=${IMAGE}"

COMPOSE_BASE="devops/compose/tmp.docker-compose.yml"
COMPOSE_OVERRIDE="devops/compose/docker-compose.forecast.yml"
ENV_FILE="devops/env/default.env"

[[ -f ${COMPOSE_BASE} ]] || { echo "Error:  ${COMPOSE_BASE} missing"; exit 1; }

COMPOSE_FLAGS=(
  --env-file "${ENV_FILE}"
  -f "${COMPOSE_BASE}"
  -f "${COMPOSE_OVERRIDE}"
)

cleanup() {
  echo -e "Stopping forecast containers…"
  docker compose "${COMPOSE_FLAGS[@]}" \
      down forecast_api forecast_frontend \
      2>/dev/null || true
}
trap cleanup INT TERM

# Start containers.
docker compose "${COMPOSE_FLAGS[@]}" \
    up -d forecast_api forecast_frontend

# Show status.
docker compose "${COMPOSE_FLAGS[@]}" \
    ps forecast_api forecast_frontend

# Show frontend logs.
docker compose "${COMPOSE_FLAGS[@]}" \
    logs -f --tail=20 forecast_frontend

#!/bin/bash

# Flags
SKIP_BUILD=false
CLEAN=false

# Parse arguments
for arg in "$@"; do
  case $arg in
    --skip-build)
      SKIP_BUILD=true
      shift
      ;;
    --clean)
      CLEAN=true
      shift
      ;;
    *)
      ;;
  esac
done

# Clean old Docker image if requested
if [ "$CLEAN" = true ]; then
  echo "[STEP 0] Cleaning old Docker image..."
  docker rmi -f bitcoin_project 2>/dev/null || echo "No existing image to remove."
fi

# Build Docker image unless skipped
if [ "$SKIP_BUILD" = false ]; then
  echo "[STEP 1] Building Docker image..."
  ./docker/docker_build.sh || {
    echo "❌ Docker build failed."
    exit 1
  }
else
  echo "[STEP 1] Skipping Docker build as requested."
fi

# Run the container
echo "[STEP 2] Launching Jupyter Lab in Docker..."
./docker/docker_jupyter.sh

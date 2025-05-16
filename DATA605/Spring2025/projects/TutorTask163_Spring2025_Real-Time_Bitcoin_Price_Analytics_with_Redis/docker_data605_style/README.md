# Bitcoin Price Analytics with Redis - Docker Setup

This directory contains Docker configuration files for running the Bitcoin Price Analytics project in a containerized environment. The setup includes both Redis server and Jupyter Lab environments.

## Prerequisites

- Docker installed on your system
- Basic knowledge of Docker commands
- Git repository cloned to your local machine

## Quick Start

### 1. Build the Docker Image

```bash
# From the docker_data605_style directory
./docker_build.sh
```

### 2. Run the Container with Jupyter and Redis

```bash
# From the docker_data605_style directory
./docker_jupyter.sh
```

This will:
- Start a container with Redis and Jupyter Lab
- Mount your project files into the container
- Expose Jupyter on port 8888
- Expose Redis on port 6379
- Set up persistent storage for Redis data

### 3. Access the Jupyter Environment

Open your browser and navigate to:
```
http://localhost:8888
```

### 4. Access a Shell in the Container

If you need to access a bash shell in the running container:

```bash
./docker_bash.sh
```

## Configuration Details

### Environment Variables

The container uses the following environment variables for Redis connection:

- `REDIS_HOST`: Set to "localhost" by default
- `REDIS_PORT`: Set to 6379 by default
- `REDIS_PASSWORD`: Empty by default (no password)

### Data Persistence

- Redis data is persisted in the `./redis_data` directory
- This ensures your data survives container restarts

### Project Files

- The parent directory of `docker_data605_style` is mounted at `/home/jupyter/work`
- This makes all your project files available inside the container

## Custom Configuration

If you need to customize the Redis configuration, you can modify:

1. `start_redis.sh` - Redis startup configuration
2. `docker_jupyter.sh` - Container environment variables

## Troubleshooting

### Redis Connection Issues

If your application cannot connect to Redis, verify:

1. The Redis server is running inside the container:
```bash
docker exec bitcoin-analytics-container redis-cli ping
```

2. The correct environment variables are set:
```bash
docker exec bitcoin-analytics-container env | grep REDIS
```

### Jupyter Access Issues

If you cannot access Jupyter in your browser:

1. Check if the container is running:
```bash
docker ps
```

2. Verify port forwarding is working:
```bash
docker port bitcoin-analytics-container
``` 
import docker
import os

# Use environment variables for all secrets. For local dev, use a .env file and `dotenv` if needed.

# Initialize Docker client
client = docker.from_env()

# InfluxDB Config from environment variables
influxdb_env = {
    "DOCKER_INFLUXDB_INIT_MODE": "setup",
    "DOCKER_INFLUXDB_INIT_USERNAME": os.getenv("INFLUXDB_USERNAME"),
    "DOCKER_INFLUXDB_INIT_PASSWORD": os.getenv("INFLUXDB_PASSWORD"),
    "DOCKER_INFLUXDB_INIT_ORG": os.getenv("INFLUXDB_ORG"),
    "DOCKER_INFLUXDB_INIT_BUCKET": os.getenv("INFLUXDB_BUCKET"),
    "DOCKER_INFLUXDB_INIT_ADMIN_TOKEN": os.getenv("INFLUXDB_ADMIN_TOKEN")
}

# Container name for reference
container_name = "influxdb"

# Port binding: host:container
ports = {"8086/tcp": 8086}

try:
    print("Pulling influxdb image...")
    client.images.pull("influxdb:latest")

    print("Starting InfluxDB container...")
    container = client.containers.run(
        image="influxdb:latest",
        name=container_name,
        environment=influxdb_env,
        ports=ports,
        detach=True,
        remove=True  # auto-remove after stopping
    )

    print(f"InfluxDB started with container ID: {container.id[:12]}")
except docker.errors.APIError as e:
    print(f"Error: {e}")
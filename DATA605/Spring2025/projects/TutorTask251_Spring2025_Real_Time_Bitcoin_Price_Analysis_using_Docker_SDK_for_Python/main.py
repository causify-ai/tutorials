import docker
import time
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

def build_and_run_containers():
    client = docker.from_env()

    # InfluxDB container configuration - now from environment variables
    influxdb_container_name = "influxdb"
    influxdb_image = "influxdb:latest"
    influxdb_port = 8086

    # Read environment variables (with defaults if not provided)
    influxdb_username = os.getenv("INFLUXDB_USERNAME")
    influxdb_password = os.getenv("INFLUXDB_PASSWORD")
    influxdb_admin_token = os.getenv("INFLUXDB_ADMIN_TOKEN")
    influxdb_org = os.getenv("INFLUXDB_ORG")
    influxdb_bucket = os.getenv("INFLUXDB_BUCKET")

    influxdb_env = {
        "DOCKER_INFLUXDB_INIT_MODE": "setup",
        "DOCKER_INFLUXDB_INIT_USERNAME": influxdb_username,
        "DOCKER_INFLUXDB_INIT_PASSWORD": influxdb_password,
        "DOCKER_INFLUXDB_INIT_ADMIN_TOKEN": influxdb_admin_token,
        "DOCKER_INFLUXDB_INIT_ORG": influxdb_org,
        "DOCKER_INFLUXDB_INIT_BUCKET": influxdb_bucket
    }

    # Fetch data scheduler container configuration
    scheduler_container_name = "fetch-data-scheduler"
    scheduler_dockerfile_path = "./fetch_data_api"
    scheduler_image_name = "fetch-data-scheduler:latest"

    try:
        # Step 1: Pull InfluxDB image
        logger.info("Pulling InfluxDB image...")
        client.images.pull(influxdb_image)

        # Step 2: Run InfluxDB container
        logger.info("Starting InfluxDB container...")
        try:
            container = client.containers.get(influxdb_container_name)
            container.stop()
            container.remove()
        except docker.errors.NotFound:
            pass  # Container doesn't exist, proceed to create it

        client.containers.run(
            influxdb_image,
            name=influxdb_container_name,
            ports={f"{influxdb_port}/tcp": influxdb_port},
            environment=influxdb_env,
            volumes={"influxdb-data": {"bind": "/var/lib/influxdb2", "mode": "rw"}},
            detach=True
        )
        logger.info(f"InfluxDB container '{influxdb_container_name}' is running on port {influxdb_port}.")

        # Wait for InfluxDB to initialize
        logger.info("Waiting for InfluxDB to initialize...")
        time.sleep(10)

        # Step 3: Build the fetch data scheduler image
        logger.info("Building the fetch data scheduler image...")
        client.images.build(path=scheduler_dockerfile_path, tag=scheduler_image_name)

        # Step 4: Run the fetch data scheduler container
        logger.info("Starting fetch data scheduler container...")
        try:
            container = client.containers.get(scheduler_container_name)
            container.stop()
            container.remove()
        except docker.errors.NotFound:
            pass  # Container doesn't exist, proceed to create it

        client.containers.run(
            scheduler_image_name,
            name=scheduler_container_name,
            network_mode="host",  # Use host networking to communicate with InfluxDB
            detach=True
        )
        logger.info(f"Fetch data scheduler container '{scheduler_container_name}' is running.")

    except docker.errors.APIError as e:
        logger.error(f"Docker API error: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    build_and_run_containers()
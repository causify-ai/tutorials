import docker
import time

def build_and_run_containers():
    client = docker.from_env()

    # InfluxDB container configuration
    influxdb_container_name = "influxdb"
    influxdb_image = "influxdb:latest"
    influxdb_port = 8086
    influxdb_env = {
        "DOCKER_INFLUXDB_INIT_MODE": "setup",
        "DOCKER_INFLUXDB_INIT_USERNAME": "admin",
        "DOCKER_INFLUXDB_INIT_PASSWORD": "adminpassword",
        "DOCKER_INFLUXDB_INIT_ADMIN_TOKEN": "As1W8vixBZwzD3dDvmrAvZi79sx1QdyAXH0H73FShCxVfOf4hBWHPwa5osmXkw6r",
        "DOCKER_INFLUXDB_INIT_ORG": "data-605",
        "DOCKER_INFLUXDB_INIT_BUCKET": "crypto-bucket"
    }

    # Fetch data scheduler container configuration
    scheduler_container_name = "fetch-data-scheduler"
    scheduler_dockerfile_path = "./fetch_data_api"
    scheduler_image_name = "fetch-data-scheduler:latest"

    try:
        # Step 1: Pull InfluxDB image
        print("Pulling InfluxDB image...")
        client.images.pull(influxdb_image)

        # Step 2: Run InfluxDB container
        print("Starting InfluxDB container...")
        try:
            client.containers.get(influxdb_container_name).stop()
            client.containers.get(influxdb_container_name).remove()
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
        print(f"InfluxDB container '{influxdb_container_name}' is running on port {influxdb_port}.")

        # Wait for InfluxDB to initialize
        print("Waiting for InfluxDB to initialize...")
        time.sleep(10)

        # Step 3: Build the fetch data scheduler image
        print("Building the fetch data scheduler image...")
        client.images.build(path=scheduler_dockerfile_path, tag=scheduler_image_name)

        # Step 4: Run the fetch data scheduler container
        print("Starting fetch data scheduler container...")
        try:
            client.containers.get(scheduler_container_name).stop()
            client.containers.get(scheduler_container_name).remove()
        except docker.errors.NotFound:
            pass  # Container doesn't exist, proceed to create it

        client.containers.run(
            scheduler_image_name,
            name=scheduler_container_name,
            network_mode="host",  # Use host networking to communicate with InfluxDB
            detach=True
        )
        print(f"Fetch data scheduler container '{scheduler_container_name}' is running.")

    except docker.errors.APIError as e:
        print(f"Docker API error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    build_and_run_containers()
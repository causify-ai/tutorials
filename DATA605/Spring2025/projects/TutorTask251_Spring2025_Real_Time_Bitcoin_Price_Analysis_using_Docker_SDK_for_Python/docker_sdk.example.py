import os
import time
from dotenv import load_dotenv
import docker
import logging
from docker_sdk_utils import (
    start_influxdb_container,
    start_grafana_container,
    start_btc_fetcher_container,
    stop_docker_container,
    stop_grafana_container,
    wait_for_influxdb_ready
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

INFLUXDB_PORT = 8086
GRAFANA_PORT = 3000

INFLUXDB_URL = f"http://influxdb:{INFLUXDB_PORT}"
INFLUXDB_TOKEN = os.getenv("INFLUXDB_ADMIN_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

def run_pipeline():
    logger.info("Starting containers with Docker SDK...")

    client = docker.from_env()
    try:
        client.networks.get("btc-net")
    except docker.errors.NotFound:
        client.networks.create("btc-net", driver="bridge")

    try:
        start_influxdb_container(client=client, container_name="influxdb", port=INFLUXDB_PORT)
        # wait_for_influxdb_ready(url=INFLUXDB_URL)
        time.sleep(10)

        start_grafana_container(container_name="grafana", port=GRAFANA_PORT, network="btc-net")
        time.sleep(5)

        logger.info("Fetching BTC data...")
        start_btc_fetcher_container(
            container_name="btc-fetcher",
            image_name="bitcoin_realtime_sdk",
            fsym="BTC",
            tsym="USD",
            limit=60,
            network="btc-net"
        )
        logger.info("BTC fetcher is running in the background...")

        logger.info("Running analysis in a separate container...")

        output_path = os.path.abspath("output")
        os.makedirs(output_path, exist_ok=True)

        analysis_container = client.containers.run(
            image="bitcoin_realtime_sdk",
            name="btc-analyzer",
            command="python analyze.py",
            environment={
                "INFLUXDB_URL": INFLUXDB_URL,
                "INFLUXDB_TOKEN": INFLUXDB_TOKEN,
                "INFLUXDB_ORG": INFLUXDB_ORG,
                "INFLUXDB_BUCKET": INFLUXDB_BUCKET
            },
            volumes={
                output_path: {"bind": "/output", "mode": "rw"}
            },
            network="btc-net",
            detach=True,
            remove=True
        )

        logs = analysis_container.logs(stream=True)
        for line in logs:
            logger.info(line.decode().strip())

        analysis_container.wait()
        input("Press Enter to clean up containers...")

    finally:
        logger.info("Cleaning up containers...")
        stop_docker_container("btc-fetcher")
        try:
            stop_docker_container("influxdb")
        except docker.errors.APIError as e:
            logger.warning(f"Could not stop influxdb cleanly: {e}")
        stop_grafana_container("grafana")
        logger.info("Cleanup complete.")

if __name__ == "__main__":
    try:
        run_pipeline()
    except KeyboardInterrupt:
        logger.warning("Interrupted by user (Ctrl+C)")
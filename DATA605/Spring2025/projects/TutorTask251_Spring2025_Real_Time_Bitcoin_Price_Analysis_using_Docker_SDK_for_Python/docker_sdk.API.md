# Docker SDK for Python: API Reference

## Overview

The [Docker SDK for Python](https://docker-py.readthedocs.io/en/stable/) allows you to programmatically control and manage Docker containers and images from Python code.  
This project demonstrates how the Docker SDK can automate real-time data ingestion pipelines by controlling container lifecycle, injecting environment variables, and provisioning dashboards — all from Python.  
This file documents the core API functions demonstrated in our project and the corresponding utility wrappers provided in `docker_sdk_utils.py`.

## Native Docker SDK Functions

- **Listing Images:**  
  Use `docker.from_env().images.list()` to list all local Docker images.

- **Listing Containers:**  
  Use `docker.from_env().containers.list(all=True)` to view all Docker containers.

- **Pulling Images:**  
  Use `client.images.pull(image_name)` to download an image from Docker Hub.

- **Starting Containers:**  
  Use `client.containers.run(...)` to start a new container (see InfluxDB example).

- **Stopping/Removing Containers:**  
  Use `container.stop()` and `container.remove()` to shut down and clean up containers.

## Abstraction Layer Purpose

To make the Docker SDK more approachable and beginner-friendly, we created an abstraction layer in `docker_sdk_utils.py`. This utility module simplifies complex SDK calls by providing intuitive, single-line functions for common container operations.

This allows developers, especially those new to containerization, to quickly set up and manage services like InfluxDB and Grafana with minimal code.

## Our Utility Wrappers

To simplify usage, we provide the following functions in `docker_sdk_utils.py`:

- `list_docker_images()`: Returns all local Docker images. Useful to verify what images are available before pulling new ones.
- `list_docker_containers(all=True)`: Returns all Docker containers, including stopped ones, for visibility into current resources.
- `pull_docker_image(image_name)`: Pulls an image from Docker Hub. Use this if an image is not yet available locally.
- `start_influxdb_container(container_name='influxdb', port=8086)`: Starts an InfluxDB container. Ideal for storing real-time time-series data like cryptocurrency prices. Automatically mounts required volumes and connects to a Docker network shared with other services.
- `start_grafana_container(container_name='grafana', port=3000)`: Starts a Grafana container with provisioning config. Used to display dashboards connected to InfluxDB. Uses provisioning configs to load a prebuilt dashboard with real-time update panels and data-source filtering.
- `start_btc_fetcher_container(...)`: Starts the BTC data fetcher container. Passes API parameters and InfluxDB credentials via environment variables. This container now supports writing both historical and real-time data tagged with 'source' for Grafana filtering.
- `stop_docker_container(container_name)`: Stops and removes a container. Used for cleanup to avoid dangling resources.

## When and Why to Use the Docker SDK

- **Reproducible Experiments:**  
  Automate database and service setup for data pipelines and analytics projects.
- **Automated Testing:**  
  Bring up/tear down environments for integration and system testing.
- **Deployment Pipelines:**  
  Orchestrate multi-service data workflows with full control from Python.
- **Educational Demonstrations:**  
  Ideal for showcasing how data infrastructure can be controlled directly from code, especially in classroom or tutorial projects like this one.

## Limitations and Best Practices

- Always clean up containers to avoid resource leaks.
- Handle exceptions in production code (e.g., for missing images, ports in use).
- For production, consider using Docker Compose or orchestration tools for complex stacks.

## References

- [Docker SDK for Python Docs](https://docker-py.readthedocs.io/en/stable/): Official reference for low-level container management.
- [Project Utilities: docker_sdk_utils.py](./docker_sdk_utils.py): Wrapper functions built to streamline real-time container orchestration in this project.
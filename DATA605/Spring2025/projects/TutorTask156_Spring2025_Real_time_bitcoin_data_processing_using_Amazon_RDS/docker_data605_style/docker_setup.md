# Docker Setup for Bitcoin RDS Project

This document explains the Docker infrastructure for the Bitcoin RDS project, which containerizes both the Jupyter notebook environment and the Streamlit dashboard.

## Overview

The Docker setup consists of two main containers:
1. **Jupyter Container**: For running Bitcoin RDS analysis notebooks
2. **Streamlit Container**: For running the interactive Bitcoin dashboard

These containers are configured to work with the same Amazon RDS PostgreSQL database, allowing for a consistent development and presentation environment.

## Key Files

### Dockerfiles

- **`Dockerfile`**: Defines the main Jupyter notebook environment with Python libraries, database connectors, and visualization tools
- **`Dockerfile.streamlit`**: Defines the Streamlit environment for the Bitcoin dashboard

### Build Scripts

- **`docker_build.sh`**: Builds the main Jupyter container
- **`docker_build_streamlit.sh`**: Builds the Streamlit dashboard container
- **`docker_push.sh`**: Pushes built images to a container registry (if configured)

### Run Scripts

- **`docker_jupyter.sh`**: Runs only the Jupyter notebook container
- **`docker_streamlit.sh`**: Runs only the Streamlit dashboard container
- **`docker_start_all.sh`**: Runs both Jupyter and Streamlit containers together
- **`docker_bash.sh`**: Opens a bash shell inside the running Jupyter container
- **`docker_exec.sh`**: Executes a command inside the running container

### Configuration

- **`docker-compose.yml`**: Defines the services, networks, and volume mappings
- **`run_jupyter.sh`**: Script that runs inside the container to start Jupyter
- **`jupyter_no_auth.py`**: Configuration for Jupyter to run without authentication token
- **`bashrc_copy`** and **`bashrc`**: Bash configuration for the container environment
- **`etc_sudoers_copy`** and **`etc_sudoers`**: Sudo permissions configuration

### Utilities

- **`docker_clean.sh`**: Cleans up unused Docker resources
- **`docker_name.sh`**: Utility script for getting the Docker image name
- **`version.sh`**: Manages version information for the Docker images
- **`install_jupyter_extensions.sh`** and **`install_jupyter_extensions_copy.sh`**: Scripts for installing Jupyter extensions

## Getting Started

### Building the Docker Images

Before running the containers, you need to build the Docker images:

```bash
cd docker_data605_style

# Build the Jupyter notebook container
./docker_build.sh

# Build the Streamlit dashboard container
./docker_build_streamlit.sh
```

### Running the Containers

You have three options for running the environment:

#### Option 1: Run both Jupyter and Streamlit (recommended)

```bash
./docker_start_all.sh
```

This starts both containers, making them available at:
- Jupyter: http://localhost:8888
- Streamlit: http://localhost:8080

#### Option 2: Run only Jupyter

```bash
./docker_jupyter.sh
```

This starts only the Jupyter notebook environment at http://localhost:8888.

#### Option 3: Run only Streamlit

```bash
./docker_streamlit.sh
```

This starts only the Streamlit dashboard at http://localhost:8080.

## Container Management

### Interactive Shell Access

To open a shell inside the running Jupyter container:

```bash
./docker_bash.sh
```

### Cleaning Up

To remove unused Docker resources (containers, images, networks):

```bash
./docker_clean.sh
```

## Environment Configuration

### Volume Mapping

The Docker setup maps the following volumes:
- Project directory to `/home/jovyan/work` inside the container
- User's home directory to `/home/jovyan/home` for access to local files

### Port Mapping

- Jupyter container: Port 8888
- Streamlit container: Port 8080

### Environment Variables

Both containers have access to the environment variables defined in the `.env` file at the project root, which contains the Amazon RDS connection details.

## Customization

### Extending the Dockerfile

To add new packages or dependencies:

1. Edit the appropriate Dockerfile (`Dockerfile` or `Dockerfile.streamlit`)
2. Add your requirements (e.g., `RUN pip install package-name`)
3. Rebuild the image using the corresponding build script

### Modifying Jupyter Configuration

The Jupyter server is configured in `run_jupyter.sh` and `jupyter_no_auth.py`. Edit these files to change Jupyter settings.

### Changing Port Mappings

If you need to use different ports:

1. Edit the corresponding run script (`docker_jupyter.sh`, `docker_streamlit.sh`, or `docker_start_all.sh`)
2. Modify the `-p` parameter to map to your desired port

## Troubleshooting

### Docker Build Issues

If you encounter issues during building:

- Check your Docker installation (`docker --version`)
- Ensure you have sufficient disk space
- Review the build logs in `docker_build.version.log`

### Container Startup Problems

If containers fail to start:

- Check if the ports are already in use by other applications
- Verify you have the correct permissions to access the mounted directories
- Ensure your `.env` file is properly configured

### Permission Issues

If you encounter permission problems:

- Make sure the configuration files (`bashrc_copy`, `etc_sudoers_copy`) are properly set up
- Use `sudo` before the Docker commands if necessary
- Check file ownership of the mounted volumes

## Advanced Usage

### Running Custom Commands

To run a specific command inside the container:

```bash
./docker_exec.sh "your-command-here"
```

### Updating Container Versions

Update the version information in `version.sh` when making significant changes to maintain proper versioning. 
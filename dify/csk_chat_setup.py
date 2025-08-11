#!/usr/bin/env python3
"""
Comprehensive Setup Script for Dify Documentation Chatbot with Weaviate
Integration.

This script automates the entire setup process by combining shell commands and
Docker Compose orchestration to set up:
- Weaviate vector database
- Ollama embedding service
- Document processing pipeline
- Retrieval API service

Usage:
    python3 csk_chat_setup.py --help
    python3 csk_chat_setup.py --install-all
    python3 csk_chat_setup.py --start-services
    python3 csk_chat_setup.py --process-docs --docs-dir ./docs

Prerequisites:
    - Python 3.8+
    - Docker and Docker Compose
    - Internet connection for downloads

Workflow:
    1. Install dependencies (Python packages, Ollama)
    2. Create configuration files (.env, docker-compose.yml)
    3. Start services (Weaviate, Ollama)
    4. Process documentation files
    5. Start retrieval API

Import as:

import dify.csk_chat_setup as csksetup
"""

import argparse
import logging
import pathlib
import subprocess
import sys
import time
from typing import List, Optional, Union

import requests  # type: ignore

import dify.weaviate_docs as dweadocs
import helpers.hdbg as hdbg
import helpers.hparser as hparser

_LOG = logging.getLogger(__name__)

# Default configuration constants.
DEFAULT_WEAVIATE_URL = "http://localhost:8080"
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_RETRIEVAL_API_URL = "http://localhost:2001"
DEFAULT_COLLECTION_NAME = "Documents"
DEFAULT_OLLAMA_MODEL = "nomic-embed-text"
DEFAULT_API_KEY = "your-secure-api-key-here"
DEFAULT_DOCS_DIR = "docs"

# Service configuration.
DOCKER_COMPOSE_CONTENT = """
version: '3.8'

services:
  weaviate:
    image: cr.weaviate.io/semitechnologies/weaviate:1.24.4
    container_name: weaviate
    restart: unless-stopped
    ports:
      - "8080:8080"
      - "50051:50051"
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      DEFAULT_VECTORIZER_MODULE: 'none'
      ENABLE_MODULES: ''
      CLUSTER_HOSTNAME: 'node1'
    volumes:
      - weaviate_data:/var/lib/weaviate
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/v1/meta"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  weaviate_data:
    driver: local
"""


# #############################################################################
# DifyDocumentationChatbotSetup
# #############################################################################


class DifyDocumentationChatbotSetup:
    """
    Main setup orchestrator for the Dify documentation chatbot system.
    """

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the setup manager.

        :param project_root: project root directory path
        """
        self.project_root = (
            pathlib.Path(project_root) if project_root else pathlib.Path.cwd()
        )
        self.env_file = self.project_root / ".env"
        self.docker_compose_file = self.project_root / "docker-compose.yml"
        self.docs_dir = self.project_root / DEFAULT_DOCS_DIR
        # Service endpoints.
        self.weaviate_url = DEFAULT_WEAVIATE_URL
        self.ollama_url = DEFAULT_OLLAMA_URL
        self.retrieval_api_url = DEFAULT_RETRIEVAL_API_URL
        # Default configuration.
        self.config = {
            "PWD": str(self.project_root),
            "OLLAMA_EMBED_URL": f"{self.ollama_url}/api/embed",
            "OLLAMA_MODEL": DEFAULT_OLLAMA_MODEL,
            "API_KEY": DEFAULT_API_KEY,
            "APP_HOST": "0.0.0.0",
            "APP_PORT": "2001",
            "WEAVIATE_URL": self.weaviate_url,
            "COLLECTION_NAME": DEFAULT_COLLECTION_NAME,
        }

    def run_command(
        self,
        command: Union[List[str], str],
        *,
        check: bool = True,
        shell: bool = False,
        capture_output: bool = False,
    ) -> subprocess.CompletedProcess:
        """
        Run a shell command with proper error handling.

        :param command: command to execute
        :param check: whether to raise exception on non-zero exit
        :param shell: whether to run in shell mode
        :param capture_output: whether to capture stdout/stderr
        :return: completed process result
        """
        cmd_str = " ".join(command) if isinstance(command, list) else command
        _LOG.info("Executing command: %s", cmd_str)

        try:
            result = subprocess.run(
                command,
                check=check,
                shell=shell,
                capture_output=capture_output,
                text=True,
                cwd=self.project_root,
            )
            if capture_output:
                _LOG.debug("Command output: %s", result.stdout)
            return result
        except subprocess.CalledProcessError as e:
            _LOG.error("Command failed: %s", cmd_str)
            _LOG.error("Error: %s", e.stderr if capture_output else str(e))
            raise RuntimeError(f"Command execution failed: {cmd_str}") from e

    def create_environment_file(self) -> None:
        """
        Create .env file with required configuration.
        """
        _LOG.info("Creating environment configuration file")
        if self.env_file.exists():
            _LOG.info("Environment file already exists, backing up")
            backup_file = self.env_file.with_suffix(".env.backup")
            self.env_file.rename(backup_file)
        env_content = []
        for key, value in self.config.items():
            env_content.append(f"{key}={value}")
        self.env_file.write_text("\n".join(env_content) + "\n")
        _LOG.info("Environment file created: %s", self.env_file)

    def create_docker_compose_file(self) -> None:
        """
        Create Docker Compose configuration for Weaviate.
        """
        _LOG.info("Creating Docker Compose configuration")
        self.docker_compose_file.write_text(DOCKER_COMPOSE_CONTENT.strip())
        _LOG.info("Docker Compose file created: %s", self.docker_compose_file)

    def install_python_dependencies(self) -> None:
        """
        Install required Python packages.
        """
        _LOG.info("Installing Python dependencies")
        # Python packages required for the chatbot system.
        python_deps = [
            "weaviate-client",
            "langchain",
            "langchain-community",
            "requests",
            "fastapi",
            "uvicorn",
            "pydantic",
        ]
        pip_command = [sys.executable, "-m", "pip", "install"] + python_deps
        self.run_command(pip_command)
        _LOG.info("Python dependencies installed successfully")

    def install_ollama(self) -> None:
        """
        Install Ollama if not already present.
        """
        _LOG.info("Checking Ollama installation")
        try:
            self.run_command(["ollama", "-v"], capture_output=True)
            _LOG.info("Ollama is already installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            _LOG.info("Installing Ollama")
            # Download and install Ollama.
            install_script = "curl -fsSL https://ollama.ai/install.sh | sh"
            self.run_command(install_script, shell=True)
            _LOG.info("Ollama installation completed")

    def start_weaviate_service(self) -> None:
        """
        Start Weaviate using Docker Compose.
        """
        _LOG.info("Starting Weaviate service")
        if not self.docker_compose_file.exists():
            self.create_docker_compose_file()
        # Start Weaviate.
        self.run_command(["docker", "compose", "up", "-d", "weaviate"])
        # Wait for Weaviate to be ready.
        self._wait_for_service(self.weaviate_url + "/v1/meta", "Weaviate")

    def start_ollama_service(self) -> None:
        """
        Start Ollama service and pull required model.
        """
        _LOG.info("Starting Ollama service")
        # Check if Ollama is already running without causing a fatal error.
        is_running = False
        try:
            # Use requests for a simpler check that doesn't rely on run_command's exception.
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                is_running = True
                _LOG.info("Ollama is already running")
        except requests.RequestException:
            _LOG.info("Ollama is not running, will attempt to start it.")
        if not is_running:
            # Start Ollama daemon in the background.
            _LOG.info("Starting Ollama daemon")
            # Using Popen to run 'ollama serve' as a non-blocking background process.
            # The 'nohup' and '&' ensure it continues running after the script exits.
            command = "nohup ollama serve > /dev/null 2>&1 &"
            # pylint: disable=consider-using-with
            subprocess.Popen(command, shell=True, cwd=self.project_root)
            _LOG.info("Ollama serve command issued.")
        # Wait a moment for service to start.
        time.sleep(5)
        # Pull the embedding model.
        _LOG.info("Pulling Ollama embedding model: %s", DEFAULT_OLLAMA_MODEL)
        self.run_command(["ollama", "pull", DEFAULT_OLLAMA_MODEL])
        # Wait for Ollama to be ready.
        self._wait_for_service(self.ollama_url + "/api/tags", "Ollama")

    def process_documents(self, docs_dir: Optional[str] = None) -> None:
        """
        Process markdown documents and upload to Weaviate.
        """
        _LOG.info("Processing and uploading documents to Weaviate")
        docs_path = pathlib.Path(docs_dir) if docs_dir else self.docs_dir
        if not docs_path.exists():
            raise FileNotFoundError(
                f"Documentation directory not found: {docs_path}"
            )
        # Import and use the document processing module.
        try:
            # Process documents.
            result = dweadocs.upload_markdown_docs_to_weaviate(
                docs_dir=str(docs_path), collection_name=DEFAULT_COLLECTION_NAME
            )
            _LOG.info(
                "Successfully processed %s files", result.get("total_files", 0)
            )
        except ImportError as e:
            _LOG.error(
                "Document processing module not found. Ensure dify package is available."
            )
            raise ImportError(
                "Document processing failed - missing dify.weaviate_docs module"
            ) from e

    def start_retrieval_api(self) -> None:
        """
        Start the FastAPI retrieval service.
        """
        _LOG.info("Starting retrieval API service")
        try:
            # Check if the retrieval module is available.
            # Print instructions for starting the API server.
            _LOG.info(
                "Starting retrieval API on %s:%s",
                self.config["APP_HOST"],
                self.config["APP_PORT"],
            )
            # Command to start the API server.
            command = [
                sys.executable,
                "-m",
                "dify.weaviate_retrieval",
                "--host",
                self.config["APP_HOST"],
                "--port",
                self.config["APP_PORT"],
            ]
            _LOG.info(
                "Starting retrieval API with command: %s", " ".join(command)
            )
            # Run as a non-blocking background process.
            # pylint: disable=consider-using-with
            subprocess.Popen(command, cwd=self.project_root)
            # Wait for the API to be ready.
            self._wait_for_service(
                f"{self.retrieval_api_url}/health", "Retrieval API"
            )
        except ImportError as e:
            _LOG.error(
                "Retrieval API module not found. Ensure dify package is available."
            )
            raise ImportError(
                "Retrieval API startup failed - missing dify.weaviate_retrieval module"
            ) from e

    def test_system_integration(self) -> None:
        """
        Test the complete integration setup.
        """
        _LOG.info("Testing system integration")
        # Test Weaviate.
        try:
            response = requests.get(f"{self.weaviate_url}/v1/meta", timeout=10)
            response.raise_for_status()
            _LOG.info("✓ Weaviate is responding")
        except requests.RequestException as e:
            _LOG.error("✗ Weaviate test failed: %s", e)
        # Test Ollama.
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            response.raise_for_status()
            _LOG.info("✓ Ollama is responding")
        except requests.RequestException as e:
            _LOG.error("✗ Ollama test failed: %s", e)
        # Test Retrieval API.
        try:
            response = requests.get(
                f"{self.retrieval_api_url}/health", timeout=10
            )
            response.raise_for_status()
            _LOG.info("✓ Retrieval API is responding")
        except requests.RequestException as e:
            _LOG.warning(
                "⚠ Retrieval API test failed (may not be started yet): %s", e
            )

    def run_full_setup(self, docs_dir: Optional[str] = None) -> None:
        """
        Run the complete setup process.
        """
        _LOG.info("Starting full setup process")
        try:
            # Environment setup.
            self.create_environment_file()
            self.create_docker_compose_file()
            # Install dependencies.
            self.install_python_dependencies()
            self.install_ollama()
            # Start services.
            self.start_weaviate_service()
            self.start_ollama_service()
            # Process documents.
            if docs_dir or self.docs_dir.exists():
                self.process_documents(docs_dir)
            else:
                _LOG.warning(
                    "No docs directory found, skipping document processing"
                )
            # Start retrieval API (instructions only).
            self.start_retrieval_api()
            # Test integration.
            self.test_system_integration()
            _LOG.info("Setup completed successfully!")
        except Exception as e:
            _LOG.error("Setup failed: %s", e)
            raise

    def _wait_for_service(
        self,
        url: str,
        service_name: str,
        *,
        max_attempts: int = 30,
        delay: int = 5,
    ) -> None:
        """
        Wait for a service to become available.

        :param url: service health check URL
        :param service_name: human-readable service name
        :param max_attempts: maximum number of attempts
        :param delay: delay between attempts in seconds
        """
        _LOG.info("Waiting for %s to be ready at %s", service_name, url)

        for attempt in range(max_attempts):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    _LOG.info("%s is ready", service_name)
                    return
            except requests.RequestException:
                pass

            _LOG.debug(
                "Attempt %s/%s - %s not ready yet",
                attempt + 1,
                max_attempts,
                service_name,
            )
            time.sleep(delay)

        raise RuntimeError(
            f"{service_name} failed to start within {max_attempts * delay} seconds"
        )


def _parse() -> argparse.ArgumentParser:
    """
    Parse command line arguments for the setup script.

    :return: configured argument parser
    """
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--project-root",
        type=str,
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--docs-dir",
        type=str,
        help="Documentation directory to process (default: PROJECT_ROOT/docs)",
    )
    parser.add_argument(
        "--install-all",
        action="store_true",
        help="Run complete installation and setup",
    )
    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Create environment and Docker Compose configuration files",
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install Python dependencies and Ollama",
    )
    parser.add_argument(
        "--start-services",
        action="store_true",
        help="Start Weaviate and Ollama services",
    )
    parser.add_argument(
        "--process-docs",
        action="store_true",
        help="Process and upload documents to Weaviate",
    )
    parser.add_argument(
        "--test-integration",
        action="store_true",
        help="Test system integration",
    )
    hparser.add_verbosity_arg(parser)
    return parser


def _main(parser: argparse.ArgumentParser) -> None:
    """
    Run the setup process with command line arguments.

    :param parser: configured argument parser
    """
    args = parser.parse_args()
    hdbg.init_logger(verbosity=args.log_level, use_exec_path=True)
    # Initialize setup manager.
    setup = DifyDocumentationChatbotSetup(args.project_root)
    try:
        if args.install_all:
            setup.run_full_setup(args.docs_dir)
        else:
            # Run individual components.
            if args.create_config:
                setup.create_environment_file()
                setup.create_docker_compose_file()
            if args.install_deps:
                setup.install_python_dependencies()
                setup.install_ollama()
            if args.start_services:
                setup.start_weaviate_service()
                setup.start_ollama_service()
            if args.process_docs:
                setup.process_documents(args.docs_dir)
            if args.test_integration:
                setup.test_system_integration()
        if not any(
            [
                args.install_all,
                args.create_config,
                args.install_deps,
                args.start_services,
                args.process_docs,
                args.test_integration,
            ]
        ):
            parser.print_help()
    except (ImportError, FileNotFoundError) as e:
        _LOG.error("Setup failed: %s", e)
        sys.exit(1)
    except KeyboardInterrupt:
        _LOG.info("Setup interrupted by user")
        sys.exit(1)
    except RuntimeError as e:
        _LOG.exception("Unexpected error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    _main(_parse())

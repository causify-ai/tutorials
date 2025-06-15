#!/usr/bin/env python3
"""
Environment initialization script for the Bitcoin forecasting system.
This script ensures all required dependencies are installed.
"""
import sys
import subprocess
import logging
import importlib.util
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("environment_setup")

# Essential packages for the application
REQUIRED_PACKAGES = [
    "tensorflow",
    "tensorflow-probability",
    "pandas",
    "numpy",
    "statsmodels",
    "scipy",
    "dash",
    "kafka-python",
    "plotly",
    "pyyaml"
]

def check_package(package_name):
    """Check if a package is installed."""
    try:
        spec = importlib.util.find_spec(package_name)
        return spec is not None
    except ImportError:
        return False

def install_package(package_name):
    """Install a package using pip."""
    try:
        logger.info(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        logger.info(f"Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {package_name}: {e}")
        return False

def initialize_environment():
    """Check and install all required packages."""
    logger.info("Checking environment setup...")
    
    # Check and install required packages
    missing_packages = []
    for package in REQUIRED_PACKAGES:
        if not check_package(package.split("==")[0]):  # Handle version requirements
            missing_packages.append(package)
    
    if missing_packages:
        logger.info(f"Missing packages: {', '.join(missing_packages)}")
        
        # Try installing missing packages
        for package in missing_packages:
            install_package(package)
            
        # Verify all packages were installed
        still_missing = []
        for package in missing_packages:
            package_name = package.split("==")[0]  # Handle version requirements
            if not check_package(package_name):
                still_missing.append(package)
        
        if still_missing:
            logger.error(f"Failed to install required packages: {', '.join(still_missing)}")
            logger.error("Application may not function properly!")
        else:
            logger.info("All required packages successfully installed")
    else:
        logger.info("All required packages are already installed")
    
    # Check for optional packages
    try:
        import matplotlib
        logger.info("Optional package matplotlib is available")
    except ImportError:
        logger.info("Optional package matplotlib is not installed")
    
    # Set environment variables if needed
    if 'TF_CPP_MIN_LOG_LEVEL' not in os.environ:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce TensorFlow logging
    
    logger.info("Environment setup complete")

if __name__ == "__main__":
    initialize_environment() 
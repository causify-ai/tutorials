#!/usr/bin/env python3
import os
import subprocess
import time
import sys

# Create necessary directories
os.makedirs("data/bitcoin", exist_ok=True)
os.makedirs("forecasts", exist_ok=True)
os.makedirs("tfx_pipeline_output", exist_ok=True)

# Run setup
print("Running setup...")
subprocess.run(["python", "setup.py"])

# Run TFX pipeline
print("Running TFX pipeline...")
subprocess.run(["python", "tf_pipeline.py"])

# Generate forecast
print("Generating forecast...")
subprocess.run(["python", "predict.py"])

# Print success
print("\nAll processes completed successfully!")
print("You can now run the dashboard with: python simple_dashboard.py")
print("And the API server with: python api_server.py")
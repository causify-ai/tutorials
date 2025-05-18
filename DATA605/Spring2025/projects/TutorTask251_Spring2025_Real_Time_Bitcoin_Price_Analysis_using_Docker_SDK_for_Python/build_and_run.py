import subprocess
import sys
import os

def build_image(image_name="bitcoin_realtime_sdk"):
    print(f"Building Docker image: {image_name} ...")
    result = subprocess.run(["docker", "build", "-t", image_name, "."], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(result.returncode)
    print("Docker image build complete.")

def run_pipeline():
    print("Running orchestrate.py for full pipeline...")
    result = subprocess.run([sys.executable, "orchestrate.py"])
    if result.returncode != 0:
        sys.exit(result.returncode)

def main():
    build_image()
    run_pipeline()

if __name__ == "__main__":
    main()

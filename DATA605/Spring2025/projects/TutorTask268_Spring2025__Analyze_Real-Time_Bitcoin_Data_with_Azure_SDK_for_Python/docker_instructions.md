# Docker Instructions – Bitcoin Streaming Project (DATA605)

This guide explains how to build and run the Docker container for the "Analyze Real-Time Bitcoin Data with Azure SDK for Python" project.

---

## Prerequisites

- Docker Desktop must be installed and running
- PowerShell (recommended for Windows users)
- Internet connection (for pulling base image and installing dependencies)

---

## Project Folder Structure

Ensure your project root contains the following:
/your-project-folder/
```text
├── Dockerfile
├── requirements.txt
├── docker_build.ps1
├── docker_bash.ps1
├── docker_jupyter.ps1
├── bitcoin_utils.py
├── bitcoin_streamer.py
├── bitcoin_receiver.py
├── bitcoin.API.ipynb
├── bitcoin.example.ipynb
├── bitcoin_visualization.ipynb
└── other project files...
```

---

## Step-by-Step Setup

### 1. Build the Docker Image

Open PowerShell and run:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass 
(this is used to temporarily allow PowerShell scripts to run, even if your system has restricted policies.)

and then run this
.\docker_build.ps1

This builds a Docker image named bitcoin-project.


### 2. Open a Terminal in the Container

run this in powershell

.\docker_bash.ps1
(This opens a bash shell inside the running container where you can test scripts like python bitcoin_streamer.py)

### 3. Launch Jupyter Notebook from Docker

Run the following command in PowerShell:

powershell
.\docker_jupyter.ps1

To access the notebook, open this file in a browser: 
  http://localhost:8888/?token=your-unique-token

You’ll see a file browser where you can run all your notebooks (.ipynb files) inside the container.



### Why PowerShell Instead of Bash?

Since this project was developed and tested on a Windows machine, I used **PowerShell scripts (`.ps1`) instead of Bash scripts (`.sh`)**. PowerShell is more compatible with Docker Desktop for Windows, especially for handling paths and executing Docker commands without issues.

Bash scripts can run into problems with volume mounting (`-v`) and path resolution (`$(pwd)`) on Windows, particularly when using Git Bash. PowerShell ensures smoother execution of Docker commands, especially when launching containers and starting Jupyter Notebook.





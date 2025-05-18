# Use SageMath base image
FROM --platform=linux/amd64 sagemath/sagemath:latest

# Switch to root to install system packages
USER root

RUN apt-get update && apt-get install -y \
    tmux \
    python3 \
    sqlite3 \
    cron \
    nano \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Switch back to default 'sage' user
USER sage

# Set working directory
WORKDIR /home/sage/project

# Install required Python libraries using Sage's pip
RUN sage -pip install \
    jupyterlab \
    pandas \
    matplotlib \
    seaborn \
    requests \
    scikit-learn \
    sympy

# Expose Jupyter port
EXPOSE 8888

# Launch JupyterLab by default
CMD sage -n jupyterlab --ip=0.0.0.0 --port=8888 --no-browser --notebook-dir=/home/sage/project

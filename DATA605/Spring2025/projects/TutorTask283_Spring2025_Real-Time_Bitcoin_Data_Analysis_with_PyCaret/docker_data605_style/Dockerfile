FROM arm64v8/python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    libgomp1

# Preemptively set LD_PRELOAD for OpenMP compatibility
ENV LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1

# Install Python packages
RUN pip install --upgrade pip \
    jupyterlab \
    pandas \
    numpy \
    matplotlib \
    pycaret

WORKDIR /notebooks
EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
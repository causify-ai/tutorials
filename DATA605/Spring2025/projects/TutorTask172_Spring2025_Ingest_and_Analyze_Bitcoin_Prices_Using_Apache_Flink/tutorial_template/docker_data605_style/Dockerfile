FROM ubuntu:20.04

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install system dependencies
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        openjdk-11-jdk \
        python3 \
        python3-pip \
        python3-dev \
        curl \
        git \
        build-essential \
        tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set JAVA path for Flink (needed on ARM64)
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64
ENV PATH=$JAVA_HOME/bin:$PATH

# Upgrade pip and install base Python packages (excluding prophet/pystan)
RUN python3 -m pip install --upgrade pip setuptools wheel && \
    pip install \
        apache-flink==1.17.1 \
        ipython \
        tornado==6.1 \
        jupyter-client==7.3.2 \
        jupyter-contrib-core \
        jupyter-contrib-nbextensions \
        notebook \
        influxdb-client \
        requests \
        psycopg2-binary \
        yapf \
        numpy \
        pandas \
        matplotlib \
        yfinance

# Create working directory
WORKDIR /data

# Expose Jupyter port
EXPOSE 8888

# Start Jupyter on container boot
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--allow-root", "--NotebookApp.token=''"]

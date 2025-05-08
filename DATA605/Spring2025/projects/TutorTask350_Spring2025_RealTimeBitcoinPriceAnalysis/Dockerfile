# Dockerfile
FROM jupyter/datascience-notebook:latest

USER root

# 1. Install Java
RUN apt-get update && \
    apt-get install -y openjdk-17-jre-headless wget

# 2. Install OpenRefine with explicit path handling
RUN wget https://github.com/OpenRefine/OpenRefine/releases/download/3.7.6/openrefine-linux-3.7.6.tar.gz && \
    mkdir -p /opt/openrefine && \
    tar -xzf openrefine-linux-3.7.6.tar.gz -C /opt/openrefine --strip-components=1 && \
    rm openrefine-linux-3.7.6.tar.gz && \
    chmod +x /opt/openrefine/refine

# 3. Install Python client
RUN pip install requests pandas matplotlib git+https://github.com/PaulMakepeace/refine-client-py.git




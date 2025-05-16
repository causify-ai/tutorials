FROM python:3.12-slim

# Install essential packages and Redis server
RUN apt-get update && apt-get install -y \
    sudo \
    curl \
    vim \
    git \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
ARG USERNAME=jupyter
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Set up working directory
WORKDIR /home/$USERNAME/work

# Install Python packages required for Bitcoin price analytics
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Install Jupyter and extensions
RUN pip install --no-cache-dir \
    jupyter \
    jupyterlab \
    jupyterlab-git

# Configure Redis
RUN mkdir -p /data/redis
RUN chown -R $USERNAME:$USERNAME /data/redis

# Copy startup scripts
COPY start_redis.sh /usr/local/bin/
COPY run_jupyter.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start_redis.sh /usr/local/bin/run_jupyter.sh

# Create a basic bashrc file
RUN echo 'export PS1="\\[\\033[01;32m\\]\\u@bitcoin-analytics\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]\\$ "' > /home/$USERNAME/.bashrc \
    && echo 'alias ll="ls -alF"' >> /home/$USERNAME/.bashrc

# Set ownership for the workspace
RUN chown -R $USERNAME:$USERNAME /home/$USERNAME

# Switch to non-root user
USER $USERNAME

# Set default command to start Jupyter Notebook
CMD ["/usr/local/bin/run_jupyter.sh"]

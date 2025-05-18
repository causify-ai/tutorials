# Start from Jupyter's Python notebook base
FROM jupyter/base-notebook:python-3.10.8

# Switch to root to install OS deps
USER root

# 1. Install system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential sudo \
  && rm -rf /var/lib/apt/lists/*

# 2. Allow passwordless sudo for jovyan
COPY etc_sudoers /etc/sudoers.d/jovyan
RUN chmod 0440 /etc/sudoers.d/jovyan

# 3. Install optional Jupyter extensions
COPY install_jupyter_extensions.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/install_jupyter_extensions.sh \
  && /usr/local/bin/install_jupyter_extensions.sh

# 4. Install Python libraries
RUN pip install --no-cache-dir \
    causallearn statsmodels seaborn yfinance networkx matplotlib numpy pandas

# 5. Copy run script and set permissions
COPY run_jupyter.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/run_jupyter.sh

# 6. Copy in project code and notebooks
WORKDIR /home/jovyan/project
COPY . /home/jovyan/project

# 7. Expose Jupyter port
EXPOSE 8888

# 8. Launch via your script
ENTRYPOINT ["bash","/usr/local/bin/run_jupyter.sh"]
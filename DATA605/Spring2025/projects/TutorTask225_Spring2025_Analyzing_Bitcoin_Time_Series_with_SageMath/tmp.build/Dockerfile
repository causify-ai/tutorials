FROM sagemath/sagemath:latest

# --- Install system packages ---
RUN apt-get update && apt-get install -y \
    sqlite3 \
    cron \
    nano \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --- Create working directory ---
WORKDIR /home/sage/project

# --- Copy and install requirements if exists ---
COPY ../requirements.txt /tmp/requirements.txt
RUN sage -pip install -r /tmp/requirements.txt || true

# --- Extra packages directly (fallback) ---
RUN sage -pip install \
    jupyterlab \
    pandas \
    matplotlib \
    seaborn \
    requests \
    scikit-learn \
    sympy

# --- Expose Jupyter port ---
EXPOSE 8888

# --- Start JupyterLab ---
CMD sage -n jupyterlab --ip=0.0.0.0 --port=8888 --no-browser --notebook-dir=/home/sage/project

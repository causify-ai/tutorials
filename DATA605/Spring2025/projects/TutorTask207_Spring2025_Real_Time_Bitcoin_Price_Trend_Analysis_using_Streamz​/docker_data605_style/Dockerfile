# Dockerfile
FROM jupyter/base-notebook:python-3.10.8

# Switch to root to install system-level bits (if any) & configure sudoers
# USER root

# (1) Sudoers—allow the jovyan user to run needed commands without password
# COPY etc_sudoers /etc/sudoers.d/jovyan_sudoers
# RUN chmod 440 /etc/sudoers.d/jovyan_sudoers

# (2) Install your Python dependencies in one layer
RUN pip install --no-cache-dir \
      yfinance \
      scikit-learn \
      streamz \
      pandas \
      numpy \
      requests \
      matplotlib

# (3) Copy in your notebooks, modules, scripts, and version file
COPY Realtime_Bitcoin_Analysis_Using_StreamZ.ipynb /home/jovyan/work/
COPY template_utils.py                              /home/jovyan/work/
COPY version.sh                                     /home/jovyan/work/
# …and any other code/data you need

# (4) Expose Jupyter’s default port and switch back to non-root
EXPOSE 8888
USER jovyan
WORKDIR /home/jovyan/work

# (5) Default entry is the notebook server (inherited from base-image),
# but you can override in docker_jupyter.sh if desired.

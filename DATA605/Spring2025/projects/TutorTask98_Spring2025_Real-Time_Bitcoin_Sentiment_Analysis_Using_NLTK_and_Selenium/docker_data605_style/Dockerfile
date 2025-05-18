# Dockerfile
FROM python:3.10-slim-bullseye
ENV DEBIAN_FRONTEND=noninteractive

# 1) Install sudo, Chromium + driver, and all needed libs
RUN apt-get update && apt-get install -y --no-install-recommends \
      sudo \
      chromium \
      chromium-driver \
      wget \
      ca-certificates \
      fonts-liberation \
      libx11-xcb1 \
      libxcomposite1 \
      libxdamage1 \
      libxext6 \
      libxfixes3 \
      libxi6 \
      libxtst6 \
      libatk1.0-0 \
      libatk-bridge2.0-0 \
      libgtk-3-0 \
      libnss3 \
      libxrandr2 \
      libasound2 \
      libpangocairo-1.0-0 \
      xdg-utils \
  && rm -rf /var/lib/apt/lists/*

# 2) Install Python & Jupyter/Selenium stack
RUN pip install --no-cache-dir \
      notebook \
      jupyter-contrib-nbextensions \
      selenium \
      webdriver-manager \
      nltk \
      pandas \
      numpy \
      matplotlib \
      seaborn \
      scikit-learn \
      requests

# 3) Run your existing Jupyter-extensions installer
COPY install_jupyter_extensions.sh /install/install_jupyter_extensions.sh
RUN chmod +x /install/install_jupyter_extensions.sh \
 && /install/install_jupyter_extensions.sh

# 4) Expose and launch Jupyter
EXPOSE 8888
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--no-browser", "--allow-root"]

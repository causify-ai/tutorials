FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

# 1) Core system + Chrome deps + Python
RUN apt-get update && apt-get -y upgrade && \
    apt-get install -y --no-install-recommends \
      sudo \
      curl \
      wget \
      ca-certificates \
      gnupg2 \
      unzip \
      git \
      vim \
      python3 \
      python3-pip \
      python3-dev \
      # Chrome GUI / sandbox deps
      fonts-liberation \
      libappindicator3-1 \
      libasound2 \
      libatk-bridge2.0-0 \
      libatk1.0-0 \
      libcups2 \
      libdbus-1-3 \
      libgdk-pixbuf2.0-0 \
      libnspr4 \
      libnss3 \
      libx11-xcb1 \
      libxcomposite1 \
      libxdamage1 \
      libxext6 \
      libxfixes3 \
      libxi6 \
      libxtst6 \
      libxrandr2 \
      libxrender1 \
      libxss1 \
      libu2f-udev \
      libvulkan1 \
      libpangocairo-1.0-0 \
      libpango-1.0-0 \
      libdrm2 \
      libgbm1 \
      libgtk-3-0 \
      xdg-utils && \
    rm -rf /var/lib/apt/lists/*

# 2) Download & install Google Chrome Stable
RUN wget -qO /tmp/google-chrome.deb \
      https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i /tmp/google-chrome.deb || true && \
    apt-get update && \
    apt-get install -y --no-install-recommends -f && \
    rm -f /tmp/google-chrome.deb && \
    rm -rf /var/lib/apt/lists/*

# 3) Upgrade pip & install Python packages
RUN python3 -m pip install --upgrade pip
RUN pip3 install \
    ipython \
    tornado==6.1 \
    jupyter-client==7.3.2 \
    jupyter-contrib-core \
    jupyter-contrib-nbextensions \
    psycopg2-binary \
    yapf \
    fake-headers \
    selenium \
    webdriver-manager \
    nltk \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    scikit-learn \
    requests

RUN ln -s /usr/bin/chromium /usr/bin/google-chrome-stable \
&& ln -s /usr/bin/chromedriver /usr/local/bin/chromedriver
   
# 4) Install Jupyter extensions (your existing script)
COPY install_jupyter_extensions.sh /install/install_jupyter_extensions.sh
RUN chmod +x /install/install_jupyter_extensions.sh \
 && /install/install_jupyter_extensions.sh

# 5) Config & version reporting
COPY etc_sudoers /etc/sudoers
COPY bashrc /root/.bashrc
COPY version.sh /install/version.sh
RUN chmod +x /install/version.sh \
 && /install/version.sh 2>&1 | tee version.log

# 6) Expose Jupyter port & default to bash
EXPOSE 8888
CMD ["bash"]
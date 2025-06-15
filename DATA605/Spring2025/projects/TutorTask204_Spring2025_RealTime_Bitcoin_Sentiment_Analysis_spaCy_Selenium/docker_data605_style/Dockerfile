FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg \
    sudo git vim \
    python3 python3-pip python3-dev \
    build-essential libffi-dev libssl-dev libpng-dev libjpeg-dev \
    libfreetype6-dev gfortran libopenblas-dev liblapack-dev \
    libnss3 libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1 \
    libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 \
    libxrandr2 libasound2 libpangocairo-1.0-0 libpangoft2-1.0-0 \
    fonts-liberation libgbm1 xdg-utils ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Set ChromeDriver version matching Chrome 136
ENV CHROMEDRIVER_VERSION=136.0.7103.113

# Install ChromeDriver manually
RUN wget -O /tmp/chromedriver.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" && \
    unzip -o /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64


# Upgrade pip and install core Python dependencies
RUN python3 -m pip install --upgrade pip setuptools wheel && \
    pip3 install numpy==1.24.4 && \
    pip3 install "cython<3" "blis<0.8" "thinc<8.2" "murmurhash<1.1.0" "cymem<2.1.0" "preshed<3.1.0"

# Now install high-level packages that depend on those
RUN pip3 install spacy==3.5.4 && \
    python3 -m spacy download en_core_web_sm && \
    pip3 install \
        ipython \
        notebook \
        psycopg2-binary \
        yapf \
        selenium \
        pandas \
        matplotlib \
        requests \
        vaderSentiment \
        jupyter \
        seaborn \
        scipy

# Download spaCy model
RUN python3 -m spacy download en_core_web_sm

# Copy your local files into the container
COPY . /data
WORKDIR /data

# Optional scripts (handle gracefully if not present)
RUN bash /data/install_jupyter_extensions.sh || true
RUN bash /data/version.sh || true

# Jupyter exposed
EXPOSE 8888
CMD ["jupyter-notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]


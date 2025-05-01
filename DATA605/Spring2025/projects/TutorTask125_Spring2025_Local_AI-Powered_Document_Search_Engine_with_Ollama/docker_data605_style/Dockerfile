FROM ubuntu:22.04

# Install build tools and dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libffi-dev \
    curl \
    git \
    vim \
    ca-certificates \
    gnupg \
    lsb-release

# Install Python 3.13.1 from source
RUN wget https://www.python.org/ftp/python/3.13.1/Python-3.13.1.tgz && \
    tar xvf Python-3.13.1.tgz && \
    cd Python-3.13.1 && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make altinstall

# Set python3.13 as default
RUN ln -s /usr/local/bin/python3.13 /usr/bin/python && \
    ln -s /usr/local/bin/pip3.13 /usr/bin/pip

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Setup app
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    faiss-cpu \
    sentence-transformers \
    streamlit \
    PyMuPDF \
    python-docx \
    requests \
    ollama \
    langchain \
    langchain-community

# Expose ports for Streamlit and Ollama
EXPOSE 8501 11434

# Start Ollama service and run the Streamlit app
CMD ["bash", "-c", "ollama serve & streamlit run app.py --server.port=8501 --server.address=0.0.0.0"]

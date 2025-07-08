FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update
RUN apt-get -y upgrade

# Install system utilities
RUN apt install -y --no-install-recommends \
    sudo \
    curl \
    wget \
    gnupg \
    git \
    vim \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libffi-dev \
    ca-certificates \
    lsb-release

# Install Python
RUN apt install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev

RUN python3 -m pip install --upgrade pip
    
# Install Python packages with fixed versions for compatibility
RUN pip3 install \
    ipython \
    tornado==6.1 \
    jupyter-client==7.3.2 \
    notebook \
    jupyter \
    faiss-cpu \
    sentence-transformers \
    streamlit \
    PyMuPDF \
    python-docx \
    requests \
    ollama \
    langchain \
    langchain-community \
    matplotlib

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Setup app
WORKDIR /app
COPY . /app

# Jupyter, Streamlit, and Ollama ports
EXPOSE 8888 8501 11434

# Start Ollama service alongside Jupyter
CMD ["bash", "-c", "ollama serve & jupyter notebook --ip 0.0.0.0 --port 8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''"]

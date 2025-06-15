FROM python:3.10-slim

WORKDIR /workspace

# Install system packages and Java
RUN apt-get update && apt-get install -y \
    default-jdk \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Dynamically configure JAVA_HOME at runtime
RUN echo "export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))" >> /etc/profile \
 && echo "export PATH=\$JAVA_HOME/bin:\$PATH" >> /etc/profile

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY bitcoin_utils.py .
COPY plot.py .
COPY run_jupyter.sh .
COPY Bitcoin.API.ipynb .
COPY Bitcoin.example.ipynb .

EXPOSE 8888

CMD ["bash", "run_jupyter.sh"]

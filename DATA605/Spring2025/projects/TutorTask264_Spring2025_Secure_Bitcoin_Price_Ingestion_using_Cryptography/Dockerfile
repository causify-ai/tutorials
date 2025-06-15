# 1) Start from a lightweight Python image
FROM python:3.10-slim

# 2) Install system tools and Jupyter
RUN apt-get update && \
    apt-get install -y --no-install-recommends git build-essential && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip jupyter

# 3) Set working directory inside the container
WORKDIR /app

# 4) Copy requirements file first (for faster rebuilds)
COPY requirements.txt .

# 5) Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6) Copy all your code into the container
COPY . .

# 7) Expose Jupyter’s default port
EXPOSE 8888

# 8) Default command: drop to bash shell
CMD ["bash"]

FROM python:3.9-slim
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8888

# Disable token authentication for local usage
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser", "--ServerApp.token=''", "--ServerApp.password=''"]

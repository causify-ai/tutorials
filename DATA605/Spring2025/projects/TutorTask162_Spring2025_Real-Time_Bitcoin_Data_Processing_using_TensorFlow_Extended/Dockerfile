FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install tensorflow==2.15.1 \
 && pip install tfx==1.15.1 \
 && pip install pandas matplotlib requests

COPY . .

CMD [ "jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root" ]

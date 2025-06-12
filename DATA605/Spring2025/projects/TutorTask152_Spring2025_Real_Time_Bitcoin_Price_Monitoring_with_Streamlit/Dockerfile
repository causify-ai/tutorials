# Dockerfile for Streamlit Bitcoin Tracker
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "Streamlit.example.py", "--server.enableCORS=false", "--server.port=8501"]

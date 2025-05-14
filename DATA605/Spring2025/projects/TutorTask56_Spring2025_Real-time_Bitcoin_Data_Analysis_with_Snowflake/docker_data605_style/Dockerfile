FROM python:3.10-slim

WORKDIR /project

RUN apt-get update && \
    apt-get install -y git sudo curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x docker_data605_style/run_all.sh

EXPOSE 8888
EXPOSE 8502

CMD ["bash", "docker_data605_style/run_all.sh"]

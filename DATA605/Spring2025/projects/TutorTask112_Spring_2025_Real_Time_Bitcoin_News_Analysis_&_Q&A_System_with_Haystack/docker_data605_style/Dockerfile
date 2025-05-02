FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y \
    build-essential curl git && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN pip install jupyter

COPY run_jupyter.sh /run_jupyter.sh
RUN chmod +x /run_jupyter.sh

EXPOSE 8888

CMD ["/run_jupyter.sh"]

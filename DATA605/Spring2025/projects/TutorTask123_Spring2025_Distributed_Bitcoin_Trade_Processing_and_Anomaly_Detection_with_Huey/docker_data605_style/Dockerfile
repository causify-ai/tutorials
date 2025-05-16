FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r docker_data605_style/requirements.txt

EXPOSE 8000

CMD bash -c "huey_consumer btc_trade_tasks.huey & python coinbase_stream.py"



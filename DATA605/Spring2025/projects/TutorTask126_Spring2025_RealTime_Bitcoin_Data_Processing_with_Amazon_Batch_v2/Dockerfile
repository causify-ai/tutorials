FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir pandas matplotlib boto3 statsmodels

CMD ["python", "run_pipeline.py"]

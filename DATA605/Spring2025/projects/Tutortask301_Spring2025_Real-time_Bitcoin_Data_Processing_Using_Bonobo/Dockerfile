# Use Python 3.9 (Bonobo compatible)
FROM python:3.9-slim

WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

#CMD ["python", "bitcoin_pipeline.py"]
CMD ["python", "bitcoin_example.py"]
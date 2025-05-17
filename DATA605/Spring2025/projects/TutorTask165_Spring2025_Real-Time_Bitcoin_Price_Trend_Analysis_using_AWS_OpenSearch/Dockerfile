# Use Python base image
FROM python:3.10-slim

WORKDIR /app

# Copy project files
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY bitcoin_utils.py ./
COPY data/ data/
COPY results/ results/
COPY scripts/ scripts/

CMD ["bash"]

FROM python:3.10-slim

# Install common Python packages
RUN pip install --no-cache-dir pandas requests datasette schedule jupyter

# Set working directory
WORKDIR /app

# Copy requirements.txt (optional)
COPY requirements.txt .

# Expose ports for Jupyter and Datasette
EXPOSE 8888 8001

CMD ["bash"]

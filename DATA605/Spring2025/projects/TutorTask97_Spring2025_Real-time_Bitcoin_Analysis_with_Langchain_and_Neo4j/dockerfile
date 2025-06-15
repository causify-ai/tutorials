FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt streamlit

# Copy your code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run scripts sequentially: first the loader, then the Streamlit app
CMD ["/bin/bash", "-c", "python load_backup_to_db.py && streamlit run app.py --server.address=0.0.0.0"]

# Use slim Python image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /project

# Install system dependencies
RUN apt-get update && \
    apt-get install -y git sudo curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install JupyterLab
RUN pip install jupyterlab

# Copy project files
COPY . .

# Allow sudo if needed for extensions
COPY docker_data605_style/etc_sudoers /etc/sudoers

# Make sure entrypoint script is executable
RUN chmod +x docker_data605_style/run_all.sh

# Expose ports: 8501 (Streamlit) and 8888 (Jupyter)
EXPOSE 8501
EXPOSE 8888

# Run both Jupyter and Streamlit
CMD ["bash", "docker_data605_style/run_all.sh"]

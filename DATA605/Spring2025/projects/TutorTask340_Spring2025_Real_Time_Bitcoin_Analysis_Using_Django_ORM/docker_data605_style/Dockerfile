FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Expose ports for Django and Jupyter
EXPOSE 8000
EXPOSE 8888

CMD ["bash"]


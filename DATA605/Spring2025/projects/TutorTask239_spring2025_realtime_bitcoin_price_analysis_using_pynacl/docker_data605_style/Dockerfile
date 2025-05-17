FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Create project directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p static/plots

# Create supervisor configuration
RUN echo '[supervisord]\n\
nodaemon=true\n\
logfile=/var/log/supervisord.log\n\
pidfile=/var/run/supervisord.pid\n\
\n\
[program:data_collection]\n\
command=python main.py\n\
directory=/app\n\
autostart=true\n\
autorestart=true\n\
stderr_logfile=/var/log/data_collection.err.log\n\
stdout_logfile=/var/log/data_collection.out.log\n\
\n\
[program:hourly_analysis]\n\
command=python -m analysis.run_hourly_analysis\n\
directory=/app\n\
autostart=true\n\
autorestart=true\n\
stderr_logfile=/var/log/hourly_analysis.err.log\n\
stdout_logfile=/var/log/hourly_analysis.out.log\n\
\n\
[program:dashboard]\n\
command=python -m visualize.dashboard\n\
directory=/app\n\
autostart=true\n\
autorestart=true\n\
stderr_logfile=/var/log/dashboard.err.log\n\
stdout_logfile=/var/log/dashboard.out.log\n\
' > /etc/supervisor/conf.d/bitcoin-analysis.conf

# Expose ports
# 8050 for Dash dashboard
# 8888 for Jupyter (optional)
EXPOSE 8050 8888

# Set entrypoint to supervisor
ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/bitcoin-analysis.conf"]

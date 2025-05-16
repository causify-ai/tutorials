#!/bin/bash
# Script to start Redis server in the Docker container

# Create Redis data directory if it doesn't exist
mkdir -p /data/redis

# Configure Redis to use the data directory
cat > /tmp/redis.conf << EOF
dir /data/redis
appendonly yes
protected-mode no
bind 0.0.0.0
port 6379
EOF

echo "Starting Redis server with custom configuration..."
redis-server /tmp/redis.conf --daemonize yes

# Check if Redis is running
echo "Checking Redis status..."
sleep 1
if redis-cli ping | grep -q "PONG"; then
    echo "Redis server started successfully!"
else
    echo "Failed to start Redis server!"
    exit 1
fi 
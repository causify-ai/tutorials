#!/bin/bash
# Start Minikube
minikube start

# Enable the metrics server for later HPA implementation
minikube addons enable metrics-server

# Build the Docker image using Minikube's Docker daemon
eval $(minikube docker-env)
docker build -t bitcoin-fetcher:latest -f docker/Dockerfile .

# Apply Kubernetes configurations
kubectl apply -f kubernetes/postgres-secret.yaml
kubectl apply -f kubernetes/postgres-pv.yaml
kubectl apply -f kubernetes/postgres-deployment.yaml
kubectl apply -f kubernetes/postgres-service.yaml

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=available deployment/postgres --timeout=300s

# Apply the rest of the configurations
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml

# Check deployment status
kubectl get all

echo "Bitcoin data fetcher has been deployed to Minikube!"
echo "Data is being stored in PostgreSQL."
echo "To check the logs: kubectl logs -f deployment/bitcoin-fetcher"
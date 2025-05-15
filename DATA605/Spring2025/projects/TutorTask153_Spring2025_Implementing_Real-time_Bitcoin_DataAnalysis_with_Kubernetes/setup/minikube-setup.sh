#!/bin/bash

set -e

echo "Starting Bitcoin Data Processing on Kubernetes Setup..."

# Generate secret files
./setup/generate-secrets.sh

# Start Minikube with sufficient resources
echo "Starting Minikube with 4 CPUs and 8GB memory..."
minikube start --cpus=4 --memory=8192

# Enable the metrics server for HPA and Prometheus scraping
echo "Enabling metrics server add-on..."
minikube addons enable metrics-server

# Build the Docker images using Minikube's Docker daemon
echo "Building Docker images..."
eval $(minikube docker-env)
docker build -t bitcoin-fetcher:latest -f docker/Dockerfile .

# Create namespaces
echo "Creating namespaces..."
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Apply secrets first
echo "Applying secrets..."
kubectl apply -f kubernetes/postgres-secret.yaml
kubectl apply -f kubernetes/grafana/grafana-secret.yaml

# Apply PVCs
echo "Applying persistent volume claims..."
kubectl apply -f kubernetes/postgres-pv.yaml
# kubectl apply -f kubernetes/prometheus/prometheus-pvc.yaml
# kubectl apply -f kubernetes/grafana/grafana-pvc.yaml

# Apply RBAC configurations for Prometheus
echo "Applying RBAC for Prometheus..."
kubectl apply -f kubernetes/prometheus/prometheus-rbac.yaml

# Apply ConfigMaps
echo "Applying ConfigMaps..."
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/prometheus/prometheus-configmap.yaml
kubectl apply -f kubernetes/grafana/grafana-datasource.yaml
kubectl apply -f kubernetes/grafana/grafana-dashboard-configmap.yaml

# Deploy Postgres
echo "Deploying PostgreSQL..."
kubectl apply -f kubernetes/postgres-deployment.yaml
kubectl apply -f kubernetes/postgres-service.yaml

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=available deployment/postgres --timeout=300s

# Deploy Prometheus
echo "Deploying Prometheus..."
kubectl apply -f kubernetes/prometheus/prometheus-deployment.yaml
kubectl apply -f kubernetes/prometheus/prometheus-service.yaml

# Deploy Grafana
echo "Deploying Grafana..."
kubectl apply -f kubernetes/grafana/grafana-deployment.yaml
kubectl apply -f kubernetes/grafana/grafana-service.yaml

# Finally deploy the Bitcoin fetcher application
echo "Deploying Bitcoin data fetcher..."
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml

# Apply HPA after deployment is available
echo "Waiting for Bitcoin fetcher deployment to be ready..."
kubectl wait --for=condition=available deployment/bitcoin-fetcher --timeout=300s

echo "Applying Horizontal Pod Autoscaler..."
kubectl apply -f kubernetes/hpa.yaml

# Show status of all components
echo "Showing deployment status..."
kubectl get all

# Provide access URLs
echo ""
echo "Setup complete! Here's how to access the services:"
echo ""
echo "Grafana Dashboard: $(minikube service grafana --url)"
echo "  Username: admin"
echo "  Password: admin"
echo ""
echo "Prometheus: $(minikube service prometheus --url)"
echo ""
echo "To view logs of the Bitcoin fetcher:"
echo "kubectl logs -f deployment/bitcoin-fetcher"
echo ""
echo "To port-forward to access the services directly:"
echo "kubectl port-forward svc/grafana 3000:3000"
echo "kubectl port-forward svc/prometheus 9090:9090"
echo ""
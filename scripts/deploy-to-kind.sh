#!/bin/bash

# Script to deploy the application to kind cluster

echo "Building and pushing images to registry..."
./scripts/build-and-push.sh

echo "Deploying to Kubernetes..."
kubectl apply -f k8s/airlines-deployment.yaml
kubectl apply -f k8s/flights-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml

echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/airlines
kubectl wait --for=condition=available --timeout=300s deployment/flights
kubectl wait --for=condition=available --timeout=300s deployment/frontend

echo "Getting service endpoints..."
kubectl get services

echo "Application deployed successfully!"
echo "To check status: kubectl get pods"
echo "To get logs: kubectl logs -f deployment/airlines"
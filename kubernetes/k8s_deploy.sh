#!/bin/bash

# Kubernetes Deployment Script for S&P 500 Predictor

set -e

NAMESPACE="sp500-predictor"
CLUSTER_NAME="sp500-cluster"
REGION="us-east-1"

echo "🚀 Deploying S&P 500 Predictor to Kubernetes"

# Create namespace
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply secrets (replace with actual values)
kubectl create secret generic sp500-secrets \
  --from-literal=ALPHA_VANTAGE_KEY=$ALPHA_VANTAGE_KEY \
  --from-literal=FRED_API_KEY=$FRED_API_KEY \
  --namespace=$NAMESPACE \
  --dry-run=client -o yaml | kubectl apply -f -

# Apply all manifests
kubectl apply -f kubernetes/configmap.yaml -n $NAMESPACE
kubectl apply -f kubernetes/pvc.yaml -n $NAMESPACE
kubectl apply -f kubernetes/deployment.yaml -n $NAMESPACE
kubectl apply -f kubernetes/service.yaml -n $NAMESPACE
kubectl apply -f kubernetes/hpa.yaml -n $NAMESPACE
kubectl apply -f kubernetes/ingress.yaml -n $NAMESPACE
kubectl apply -f kubernetes/networkpolicy.yaml -n $NAMESPACE

# Wait for deployment
kubectl rollout status deployment/sp500-predictor-api -n $NAMESPACE

# Get service URL
SERVICE_URL=$(kubectl get service sp500-predictor-api -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "✅ Deployment complete!"
echo "📍 API URL: http://$SERVICE_URL"
echo "📍 Health Check: http://$SERVICE_URL/health"

# Setup monitoring (optional)
kubectl apply -f kubernetes/servicemonitor.yaml -n $NAMESPACE

echo "🎉 S&P 500 Predictor deployed successfully!"
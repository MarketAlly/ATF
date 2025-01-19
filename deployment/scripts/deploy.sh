#!/bin/bash
set -e

# Configuration
NAMESPACE="atf-service"
DEPLOYMENT="atf-service"
IMAGE_NAME="atf-service"
REGISTRY="your-registry.azurecr.io"  # Change this to your registry

# Get the version from args or use latest
VERSION=${1:-latest}

# Functions
log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*"
}

check_dependencies() {
    command -v kubectl >/dev/null 2>&1 || { echo "kubectl is required but not installed. Aborting." >&2; exit 1; }
    command -v docker >/dev/null 2>&1 || { echo "docker is required but not installed. Aborting." >&2; exit 1; }
}

# Check dependencies
check_dependencies

# Start deployment
log "Starting deployment of ATF Service version ${VERSION}"

# Build and push Docker image
log "Building Docker image..."
docker build -t ${REGISTRY}/${IMAGE_NAME}:${VERSION} .

log "Pushing image to registry..."
docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION}

# Update Kubernetes manifests
log "Updating kubernetes manifests..."
kubectl apply -f deployment/k8s/service.yaml -n ${NAMESPACE}

# Update the deployment with the new image
log "Updating deployment..."
kubectl set image deployment/${DEPLOYMENT} \
    ${DEPLOYMENT}=${REGISTRY}/${IMAGE_NAME}:${VERSION} \
    -n ${NAMESPACE}

# Wait for rollout
log "Waiting for rollout to complete..."
kubectl rollout status deployment/${DEPLOYMENT} -n ${NAMESPACE}

# Verify deployment
log "Verifying deployment..."
kubectl get deployment ${DEPLOYMENT} -n ${NAMESPACE} -o wide

log "Deployment completed successfully!"
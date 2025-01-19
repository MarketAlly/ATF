#!/bin/bash
set -e

# Configuration
NAMESPACE="atf-service"
DEPLOYMENT="atf-service"

# Functions
log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*"
}

check_dependencies() {
    command -v kubectl >/dev/null 2>&1 || { echo "kubectl is required but not installed. Aborting." >&2; exit 1; }
}

# Check if revision is provided
if [ -z "$1" ]; then
    log "No revision specified, rolling back to previous version"
    REVISION="previous"
else
    REVISION=$1
    log "Rolling back to revision ${REVISION}"
fi

# Check dependencies
check_dependencies

# Start rollback
log "Starting rollback of ATF Service"

if [ "$REVISION" = "previous" ]; then
    # Rollback to previous version
    log "Rolling back to previous version..."
    kubectl rollout undo deployment/${DEPLOYMENT} -n ${NAMESPACE}
else
    # Rollback to specific revision
    log "Rolling back to revision ${REVISION}..."
    kubectl rollout undo deployment/${DEPLOYMENT} -n ${NAMESPACE} --to-revision=${REVISION}
fi

# Wait for rollout
log "Waiting for rollback to complete..."
kubectl rollout status deployment/${DEPLOYMENT} -n ${NAMESPACE}

# Verify rollback
log "Verifying deployment status..."
kubectl get deployment ${DEPLOYMENT} -n ${NAMESPACE} -o wide

# Check deployment history
log "Deployment history:"
kubectl rollout history deployment/${DEPLOYMENT} -n ${NAMESPACE}

log "Rollback completed successfully!"

# Add warning about monitoring
log "Please monitor the application logs and metrics for any issues:"
log "kubectl logs -f deployment/${DEPLOYMENT} -n ${NAMESPACE}"
log "Access metrics at: http://your-grafana-url/d/atf-service"
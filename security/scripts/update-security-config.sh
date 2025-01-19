#!/bin/bash
set -e

# Configuration
NAMESPACE="atf-service"
CONFIG_DIR="./security/config"
BACKUP_DIR="./security/backups/config"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Functions
log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*"
}

backup_config() {
    log "Backing up current configuration..."
    mkdir -p "$BACKUP_DIR"
    cp -r "$CONFIG_DIR" "$BACKUP_DIR/config_$TIMESTAMP"
}

update_security_policies() {
    log "Updating security policies..."
    
    # Update network policies
    kubectl apply -f security/policies/network-policy.yaml -n $NAMESPACE
    
    # Update RBAC policies
    kubectl apply -f security/policies/rbac.yaml -n $NAMESPACE
    
    # Update pod security policies
    kubectl apply -f security/policies/pod-security.yaml -n $NAMESPACE
}

update_security_headers() {
    log "Updating security headers configuration..."
    kubectl create configmap security-headers \
        --from-file=security/config/headers.yaml \
        -n $NAMESPACE \
        --dry-run=client -o yaml | kubectl apply -f -
}

update_rate_limits() {
    log "Updating rate limiting configuration..."
    kubectl create configmap rate-limits \
        --from-file=security/config/rate-limits.yaml \
        -n $NAMESPACE \
        --dry-run=client -o yaml | kubectl apply -f -
}

validate_config() {
    log "Validating security configuration..."
    # Add validation logic here
    if ! yamllint security/config/*.yaml; then
        log "Error: Configuration validation failed"
        exit 1
    fi
}

# Backup current configuration
backup_config

# Validate new configuration
validate_config

# Apply updates
update_security_policies
update_security_headers
update_rate_limits

# Restart affected services
log "Restarting services to apply new configuration..."
kubectl rollout restart deployment -n $NAMESPACE

# Wait for rollout
log "Waiting for rollout to complete..."
kubectl rollout status deployment/atf-service -n $NAMESPACE

log "Security configuration update completed successfully"
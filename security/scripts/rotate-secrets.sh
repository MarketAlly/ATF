#!/bin/bash
set -e

# Configuration
NAMESPACE="atf-service"
SECRETS=("jwt-keys" "tls-certs" "api-keys" "encryption-keys")
BACKUP_DIR="./security/backups/secrets"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Functions
log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*"
}

backup_secret() {
    local secret=$1
    log "Backing up secret: $secret"
    kubectl get secret $secret -n $NAMESPACE -o yaml > "$BACKUP_DIR/${secret}_${TIMESTAMP}.yaml"
}

rotate_jwt_keys() {
    log "Rotating JWT keys..."
    python security/generate_keys.py --key-type jwt
    kubectl create secret generic jwt-keys \
        --from-file=private.pem=security/keys/jwt_private_latest.pem \
        --from-file=public.pem=security/keys/jwt_public_latest.pem \
        -n $NAMESPACE \
        --dry-run=client -o yaml | kubectl apply -f -
}

rotate_tls_certs() {
    log "Rotating TLS certificates..."
    # Implementation would generate new TLS certificates
    # This is a placeholder
    log "TLS certificate rotation not implemented"
}

rotate_api_keys() {
    log "Rotating API keys..."
    # Generate new API keys and update secrets
    NEW_KEY=$(openssl rand -base64 32)
    kubectl create secret generic api-keys \
        --from-literal=key=$NEW_KEY \
        -n $NAMESPACE \
        --dry-run=client -o yaml | kubectl apply -f -
}

rotate_encryption_keys() {
    log "Rotating encryption keys..."
    python security/generate_keys.py --key-type encryption
    kubectl create secret generic encryption-keys \
        --from-file=key=security/keys/encryption_latest.key \
        -n $NAMESPACE \
        --dry-run=client -o yaml | kubectl apply -f -
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup existing secrets
log "Starting secret rotation process..."
for secret in "${SECRETS[@]}"; do
    backup_secret $secret
done

# Rotate each type of secret
rotate_jwt_keys
rotate_tls_certs
rotate_api_keys
rotate_encryption_keys

# Update deployments to use new secrets
log "Restarting deployments to pick up new secrets..."
kubectl rollout restart deployment -n $NAMESPACE

# Wait for rollout
log "Waiting for rollout to complete..."
kubectl rollout status deployment/atf-service -n $NAMESPACE

log "Secret rotation completed successfully"
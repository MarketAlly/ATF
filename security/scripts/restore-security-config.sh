#!/bin/bash
set -e

# Configuration
NAMESPACE="atf-service"
BACKUP_ROOT="./security/backups"

# Functions
log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*"
}

usage() {
    echo "Usage: $0 <backup-file> [--force]"
    echo "Example: $0 ./security/backups/20250119_120000.tar.gz.gpg"
    exit 1
}

decrypt_backup() {
    local backup_file=$1
    log "Decrypting backup..."
    gpg --decrypt "$backup_file" > "${backup_file%.gpg}"
    tar xzf "${backup_file%.gpg}" -C "$BACKUP_ROOT"
    rm -f "${backup_file%.gpg}"
}

restore_keys() {
    log "Restoring encryption keys..."
    cp -r "$RESTORE_DIR/keys/"* ./security/keys/
}

restore_configs() {
    log "Restoring security configurations..."
    cp -r "$RESTORE_DIR/config/"* ./security/config/
}

restore_secrets() {
    log "Restoring Kubernetes secrets..."
    kubectl apply -f "$RESTORE_DIR/secrets/all-secrets.yaml" -n $NAMESPACE
}

restore_policies() {
    log "Restoring security policies..."
    kubectl apply -f "$RESTORE_DIR/policies/network-policies.yaml" -n $NAMESPACE
    kubectl apply -f "$RESTORE_DIR/policies/rbac-policies.yaml" -n $NAMESPACE
}

validate_restore() {
    log "Validating restored configuration..."
    
    # Check key files
    if ! ls ./security/keys/*.pem >/dev/null 2>&1; then
        log "Error: Missing key files"
        return 1
    fi
    
    # Check configurations
    if ! ls ./security/config/*.yaml >/dev/null 2>&1; then
        log "Error: Missing configuration files"
        return 1
    fi
    
    # Verify secrets
    if ! kubectl get secrets -n $NAMESPACE >/dev/null 2>&1; then
        log "Error: Failed to verify secrets"
        return 1
    fi
    
    return 0
}

restart_services() {
    log "Restarting services to apply restored configuration..."
    kubectl rollout restart deployment -n $NAMESPACE
    kubectl rollout status deployment/atf-service -n $NAMESPACE
}

# Main execution

# Check arguments
if [ "$#" -lt 1 ]; then
    usage
fi

BACKUP_FILE=$1
FORCE=0

if [ "$2" = "--force" ]; then
    FORCE=1
fi

# Verify backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    log "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Create temporary restore directory
RESTORE_DIR=$(mktemp -d)
trap 'rm -rf "$RESTORE_DIR"' EXIT

# Prompt for confirmation unless --force is used
if [ "$FORCE" -ne 1 ]; then
    read -p "This will restore security configuration from $BACKUP_FILE. Continue? [y/N] " response
    if [[ ! "$response" =~ ^[yY]$ ]]; then
        log "Restore cancelled"
        exit 0
    fi
fi

# Perform restore
log "Starting security configuration restore from $BACKUP_FILE"

# Decrypt and extract backup
decrypt_backup "$BACKUP_FILE"

# Perform restore steps
restore_keys
restore_configs
restore_secrets
restore_policies

# Validate restore
if ! validate_restore; then
    log "Error: Restore validation failed"
    exit 1
fi

# Restart services
restart_services

log "Security configuration restore completed successfully"
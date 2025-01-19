#!/bin/bash
set -e

# Configuration
NAMESPACE="atf-service"
BACKUP_ROOT="./security/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$TIMESTAMP"

# Functions
log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*"
}

backup_keys() {
    log "Backing up encryption keys..."
    mkdir -p "$BACKUP_DIR/keys"
    cp -r ./security/keys/* "$BACKUP_DIR/keys/"
}

backup_configs() {
    log "Backing up security configurations..."
    mkdir -p "$BACKUP_DIR/config"
    cp -r ./security/config/* "$BACKUP_DIR/config/"
}

backup_secrets() {
    log "Backing up Kubernetes secrets..."
    mkdir -p "$BACKUP_DIR/secrets"
    
    # Backup all secrets in namespace
    kubectl get secrets -n $NAMESPACE -o yaml > "$BACKUP_DIR/secrets/all-secrets.yaml"
}

backup_policies() {
    log "Backing up security policies..."
    mkdir -p "$BACKUP_DIR/policies"
    
    # Backup network policies
    kubectl get networkpolicies -n $NAMESPACE -o yaml > \
        "$BACKUP_DIR/policies/network-policies.yaml"
    
    # Backup RBAC policies
    kubectl get roles,rolebindings -n $NAMESPACE -o yaml > \
        "$BACKUP_DIR/policies/rbac-policies.yaml"
}

encrypt_backup() {
    log "Encrypting backup..."
    tar czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
    gpg --encrypt --recipient security@example.com "$BACKUP_DIR.tar.gz"
    rm -f "$BACKUP_DIR.tar.gz"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Perform backups
backup_keys
backup_configs
backup_secrets
backup_policies

# Encrypt backup
encrypt_backup

# Cleanup unencrypted files
rm -rf "$BACKUP_DIR"

log "Backup completed: $BACKUP_DIR.tar.gz.gpg"
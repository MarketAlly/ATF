#!/bin/bash
set -e

# Configuration
NAMESPACE="atf-service"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
INCIDENT_DIR="./security/incidents/$TIMESTAMP"

# Functions
log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*"
}

capture_state() {
    local dir=$1
    mkdir -p "$dir"
    
    log "Capturing current state..."
    
    # Capture pod states
    kubectl get pods -n $NAMESPACE -o yaml > "$dir/pods.yaml"
    
    # Capture logs
    for pod in $(kubectl get pods -n $NAMESPACE -o name); do
        kubectl logs $pod -n $NAMESPACE > "$dir/${pod##*/}.log"
    done
    
    # Capture network policies
    kubectl get networkpolicies -n $NAMESPACE -o yaml > "$dir/network-policies.yaml"
    
    # Capture metrics
    curl -s http://localhost:9090/api/v1/query?query=up > "$dir/metrics.json"
}

restrict_network() {
    log "Applying restrictive network policies..."
    cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: emergency-lockdown
  namespace: $NAMESPACE
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: monitoring
EOF
}

revoke_tokens() {
    log "Revoking active tokens..."
    kubectl create configmap token-blacklist \
        --from-literal=timestamp=$TIMESTAMP \
        -n $NAMESPACE \
        --dry-run=client -o yaml | kubectl apply -f -
}

notify_team() {
    log "Sending emergency notifications..."
    # Implementation would send notifications through multiple channels
    # This is a placeholder
    echo "EMERGENCY: Service lockdown initiated at $TIMESTAMP" | \
        mail -s "EMERGENCY: ATF Service Lockdown" security-team@example.com
}

generate_incident_report() {
    local report_file="$INCIDENT_DIR/incident_report.md"
    
    log "Generating incident report..."
    cat <<EOF > "$report_file"
# Security Incident Report

## Incident Details
- Timestamp: $TIMESTAMP
- Service: ATF Service
- Namespace: $NAMESPACE

## Actions Taken
1. Service locked down
2. Network restricted
3. Tokens revoked
4. State captured

## State Captures
- Pod states: \`pods.yaml\`
- Network policies: \`network-policies.yaml\`
- Service logs: \`*.log\`
- Metrics: \`metrics.json\`

## Next Steps
1. Investigate root cause
2. Review security logs
3. Plan recovery steps
4. Update security measures
EOF
}

# Capture pre-lockdown state
capture_state "$INCIDENT_DIR/pre-lockdown"

# Execute lockdown
restrict_network
revoke_tokens

# Capture post-lockdown state
capture_state "$INCIDENT_DIR/post-lockdown"

# Generate report and notify
generate_incident_report
notify_team

log "Emergency lockdown completed. Incident directory: $INCIDENT_DIR"
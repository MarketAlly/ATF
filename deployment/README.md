# ATF Service Deployment

This directory contains deployment configurations and scripts for the ATF (Algorithmic Transparency Feed) service.

## Directory Structure
```
deployment/
├── k8s/
│   ├── deployment.yaml    # Kubernetes deployment configuration
│   └── service.yaml       # Kubernetes service configuration
└── scripts/
    ├── deploy.sh         # Deployment automation script
    └── rollback.sh       # Rollback automation script
```

## Quick Start

1. Build and deploy locally:
```bash
docker-compose up --build
```

2. Deploy to Kubernetes:
```bash
./scripts/deploy.sh v1.0.0
```

3. Rollback if needed:
```bash
./scripts/rollback.sh     # Roll back to previous version
# or
./scripts/rollback.sh 2   # Roll back to specific revision
```

## Configuration

### Kubernetes
- `deployment.yaml`: Configures the deployment specifications
  - Replicas: 3 (default)
  - Resource limits and requests
  - Health checks
  - Environment variables

- `service.yaml`: Configures the service exposure
  - Type: LoadBalancer
  - Port: 80 -> 8000
  - Prometheus annotations

### Scripts

#### deploy.sh
- Builds Docker image
- Pushes to registry
- Updates Kubernetes deployment
- Monitors rollout status

#### rollback.sh
- Reverts to previous/specific version
- Monitors rollout status
- Verifies deployment health

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| ENVIRONMENT | Deployment environment | production |
| PORT | Service port | 8000 |
| LOG_LEVEL | Logging level | INFO |

## Deployment Environments

1. Development
```bash
export ENVIRONMENT=development
docker-compose up
```

2. Staging
```bash
./scripts/deploy.sh --env staging v1.0.0
```

3. Production
```bash
./scripts/deploy.sh --env production v1.0.0
```

## Health Checks

The service exposes the following health endpoints:
- `/health`: Basic service health
- `/ready`: Service readiness
- `/metrics`: Prometheus metrics

## Security

1. Container Security
- Non-root user
- Read-only filesystem
- Resource limits
- Security context

2. Network Security
- TLS termination
- Network policies
- WAF integration

## Troubleshooting

1. Check deployment status:
```bash
kubectl get deployment atf-service -n atf
```

2. View logs:
```bash
kubectl logs -f deployment/atf-service -n atf
```

3. Check events:
```bash
kubectl get events -n atf
```

## Maintenance

1. Update dependencies:
```bash
docker-compose pull
```

2. Clean up old deployments:
```bash
kubectl delete pods -l app=atf-service --field-selector status.phase=Succeeded
```

3. Update certificates:
```bash
./scripts/update-certs.sh
```
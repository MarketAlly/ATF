# ATF Service Monitoring

This directory contains monitoring configurations and dashboards for the ATF (Algorithmic Transparency Feed) service.

## Directory Structure
```
monitoring/
├── prometheus/
│   ├── prometheus.yml    # Prometheus configuration
│   └── rules/
│       └── atf_alerts.yml # Alert rules
├── grafana/
│   ├── dashboards/
│   │   └── atf-service.json  # Service dashboard
│   └── datasources/
│       └── prometheus.yml    # Prometheus data source
└── alertmanager/
    └── config.yml            # Alert manager configuration
```

## Metrics Overview

### Key Metrics
1. Request Metrics
   - Request rate by status code
   - Response time percentiles
   - Error rates

2. Business Metrics
   - Feed generation rate
   - Update frequency
   - Validation success rate

3. Resource Metrics
   - CPU usage
   - Memory usage
   - Network I/O

## Dashboards

### ATF Service Dashboard
- Request Rate Panel
- Response Times Panel
- Error Rate Panel
- Feed Generation Stats
- Resource Usage Gauges

### Installation
1. Import dashboard:
```bash
curl -X POST http://grafana:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @grafana/dashboards/atf-service.json
```

2. Configure data source:
```bash
curl -X POST http://grafana:3000/api/datasources \
  -H "Content-Type: application/json" \
  -d @grafana/datasources/prometheus.yml
```

## Alerts

### Alert Rules
1. High Error Rate
   - Condition: >5% errors over 5m
   - Severity: critical
   - Notification: Slack + Email

2. Slow Response Time
   - Condition: p95 > 500ms
   - Severity: warning
   - Notification: Slack

3. Resource Usage
   - CPU: >80% for 5m
   - Memory: >85% for 5m
   - Severity: warning

### Alert Manager
- Slack integration
- Email notifications
- PagerDuty integration
- De-duplication
- Grouping rules

## Metric Collection

### Prometheus Configuration
1. Scrape configuration:
```yaml
scrape_configs:
  - job_name: 'atf-service'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['atf-service:8000']
```

2. Retention settings:
- Local storage retention: 15d
- Resolution: 15s

### Custom Metrics
1. Feed Metrics
```python
feed_generation_total = Counter(
    'atf_feeds_generated_total',
    'Total number of feeds generated'
)
```

2. Validation Metrics
```python
validation_duration = Histogram(
    'atf_validation_duration_seconds',
    'Time spent validating feeds'
)
```

## Troubleshooting

1. Check Prometheus targets:
```bash
curl http://prometheus:9090/api/v1/targets
```

2. Verify metrics endpoint:
```bash
curl http://atf-service:8000/metrics
```

3. Test alert rules:
```bash
curl http://prometheus:9090/api/v1/rules
```

## Maintenance

1. Backup Grafana:
```bash
./scripts/backup-grafana.sh
```

2. Clean old data:
```bash
./scripts/clean-metrics.sh
```

3. Update dashboards:
```bash
./scripts/update-dashboards.sh
```
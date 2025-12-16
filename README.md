# TEMS Observability – Project Context

## Goal
Multi-participant dataspace observability with:
- Participant A
- Participant B
- Central Authority

## Stack
- Docker Compose
- Observability service (FastAPI + Prometheus metrics)
- Central Prometheus
- Central Grafana
- PostgreSQL per participant
- API Gateway (nginx)
- Simulated EDC events (POC)

## Architecture
- A and B have separate stacks
- Central Prometheus scrapes A and B
- Central Grafana has 3 dashboards: A / B / Central

## Key files
- docker-compose.ab-central.yml
- observability/app.py
- prometheus/prometheus.yml
- api-gateway-a/nginx.conf
- api-gateway-b/nginx.conf
- grafana/provisioning/*
- grafana/dashboards/*

## Metrics
- tems_api_requests_total
- tems_http_request_duration_seconds (histogram)
- tems_transfers_total
- tems_transfer_bytes_total
- tems_transfer_duration_seconds
- dataspace_ready
- dependency_up

## Status
POC working, next step:
- connect real Eclipse EDC
- standardize EDC event schema
- add contract negotiation metrics

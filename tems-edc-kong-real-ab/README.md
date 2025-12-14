# TEMS Data Space (local) — EDC réel A↔B + Kong API Gateway TEMS + Observabilité (Central)

## Pourquoi ton `manifest unknown` ?
Tu avais une image EDC inexistante (`ghcr.io/eclipse-edc/connector:latest`).  
Ici on utilise les **images TEMS** de ton ZIP:
- `ghcr.io/tems-git-hub/tems-edc-connector:0.0.1`
- `ghcr.io/tems-git-hub/api-gateway:0.0.1`
- `ghcr.io/tems-git-hub/mocked-policy-engine:0.0.1`

## Démarrage
```bash
docker compose up --build
```

## Endpoints (Codespaces)
- Gateway A: http://localhost:8080
- Gateway B: http://localhost:8081
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000  (admin / admin)

## Routes via gateways
- /management/*  -> EDC Management API (X-Api-Key ajouté automatiquement par Kong)
- /protocol/*    -> EDC DSP/Protocol
- /temsapigateway/token  -> token (mocked-policy-engine)
- /temsapigateway/validate -> validate (mocked-policy-engine)
- /metrics, /health, /ready, /observability/* -> Observability locale

## Test échange A -> B
> Le script fait un "happy path" EDC (Asset+Policy+ContractDef), puis essaie de récupérer le catalogue via DSP.
> La partie negotiation/transfer dépend de la version exacte EDC TEMS (payloads/offers).  
> Même si ta version diffère, tu auras la stack (EDC+Gateway+Obs+Central) qui tourne, et tu verras les métriques.

```bash
python3 scripts/ab_publish_and_catalog.py
```

## Vérification observabilité
```bash
curl -sS http://localhost:8080/metrics | head
curl -sS http://localhost:8081/metrics | head
```

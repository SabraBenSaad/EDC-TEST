# TEMS Docker Compose - Participant Environment

This repository contains Docker Compose configurations to run two EDC participants (A and B) for both local development and production deployments.

## Prerequisites

- Docker Engine 20.10 or higher
- Docker Compose 2.0 or higher
- Access to GitHub Container Registry (ghcr.io) for pulling images
- Valid Keycloak credentials for the central governance

## Architecture

Each participant stack includes:
- **EDC Connector**: Eclipse Dataspace Connector for data exchange
- **API Gateway**: Kong-based gateway with TEMS plugin
- **Policy Engine**: Mocked policy manager for contract validation
- **Nginx**: Reverse proxy to expose services on a single port
- **Petstore**: Sample API for testing

## Deployment Modes

This repository supports two deployment modes:

### Development Mode (Default)
- **Protocol**: HTTP
- **Ports**: 8080 (Participant A), 8081 (Participant B)
- **Domains**: localhost
- **SSL Certificates**: Not required
- **Use case**: Local development and testing

### Production Mode
- **Protocol**: HTTPS
- **Ports**: 80, 443
- **Domains**: participant-a.tems-dataspace.eu, participant-b.tems-dataspace.eu
- **SSL Certificates**: Let's Encrypt with auto-renewal every 12h
- **Use case**: Production deployment on public servers

## Common Setup

### Configure Keycloak Credentials

Before starting the services, you must configure the central governance Keycloak credentials in both docker compose files.

Edit the following files:
- `docker-compose-participant-a.yml`
- `docker-compose-participant-b.yml`

Replace the placeholders in the `policy-engine` service:

```yaml
policy-engine:
  environment:
    KEYCLOAK_URL: <ADD_GOVERNANCE_KEYCLOAK_URL_HERE>         # e.g., https://governance.tems-dataspace.eu/auth/
    KEYCLOAK_REALM: <ADD_GOVERNANCE_KEYCLOAK_REALM_HERE>     # e.g., common
    KEYCLOAK_CLIENT_ID: <ADD_GOVERNANCE_KEYCLOAK_CLIENT_ID_HERE>
    KEYCLOAK_CLIENT_SECRET: <ADD_GOVERNANCE_KEYCLOAK_CLIENT_SECRET_HERE>
```

# Development Mode

## Starting the Participants

Start each participant in a separate terminal:

```bash
# Participant A
docker compose -f docker-compose-participant-a.yml up

# Participant B
docker compose -f docker-compose-participant-b.yml up
```

## Available Endpoints

### Participant A
Base URL: `http://localhost:8080`

- `http://localhost:8080/management` - EDC Management API (create assets, policies, contract definitions)
- `http://localhost:8080/protocol` - EDC Protocol API (DSP communication between connectors)
- `http://localhost:8080/apigateway` - Kong API Gateway (access protected APIs)

### Participant B
Base URL: `http://localhost:8081`

- `http://localhost:8081/management` - EDC Management API (create assets, policies, contract definitions)
- `http://localhost:8081/protocol` - EDC Protocol API (DSP communication between connectors)
- `http://localhost:8081/apigateway` - Kong API Gateway (access protected APIs)

## Health Check

Verify that both participants are running:

```bash
# Check Participant A
curl -X POST http://localhost:8080/management/v3/assets/request \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: 123456"

# Check Participant B
curl -X POST http://localhost:8081/management/v3/assets/request \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: 123456"
```

Both should return an empty array `[]` if no assets have been created yet.

## Stopping the Services

```bash
# Stop Participant A
docker compose -f docker-compose-participant-a.yml down

# Stop Participant B
docker compose -f docker-compose-participant-b.yml down
```

# Production Mode

## Prerequisites

- DNS records pointing to your server:
  - `participant-a.tems-dataspace.eu` → Server IP
  - `participant-b.tems-dataspace.eu` → Server IP
- Ports 80 and 443 open in your firewall
- Valid email address for Let's Encrypt notifications

## Security Configuration

**IMPORTANT**: Before deploying to production, you **must**:

### 1. Change API Keys

Edit the following files for each participant:
- [participant-a/configuration.properties](participant-a/configuration.properties)
- [participant-b/configuration.properties](participant-b/configuration.properties)

Change the default value `123456` to a strong custom API key for these properties:
- `web.http.management.auth.key`
- `edc.api.auth.key`
- `edc.api.control.auth.apikey.value`

Generate a secure random API key:
```bash
openssl rand -hex 32
```

Replace `123456` with the generated key in all three properties.

### 2. Update Callback URLs to Production Domains

**IMPORTANT**: In production, EDC connectors must use **public domain names** instead of `host.docker.internal`.

Edit the same configuration files and update these properties with your production domains:

**For Participant A** ([participant-a/configuration.properties](participant-a/configuration.properties)):
```properties
edc.dsp.callback.address=https://participant-a.tems-dataspace.eu/protocol
edc.transfer.dataplane.sync.endpoint=https://participant-a.tems-dataspace.eu/public
edc.dataplane.token.validation.endpoint=https://participant-a.tems-dataspace.eu/control/token
```

**For Participant B** ([participant-b/configuration.properties](participant-b/configuration.properties)):
```properties
edc.dsp.callback.address=https://participant-b.tems-dataspace.eu/protocol
edc.transfer.dataplane.sync.endpoint=https://participant-b.tems-dataspace.eu/public
edc.dataplane.token.validation.endpoint=https://participant-b.tems-dataspace.eu/control/token
```

**Note**: The current configuration uses `host.docker.internal` which is **only for local development** where both participants run on the same machine. In production, each participant must be reachable via its public domain.

## Step 1: Obtain SSL Certificates

Before starting in production mode, obtain SSL certificates using Certbot.

For **Participant A**:

```bash
# Create required directories
mkdir -p certbot/conf certbot/www

# Obtain certificate
docker run -it --rm \
  -p 80:80 \
  -v ./certbot/conf:/etc/letsencrypt \
  -v ./certbot/www:/var/www/certbot \
  certbot/certbot certonly \
  --standalone \
  --preferred-challenges http \
  -d participant-a.tems-dataspace.eu \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email
```

For **Participant B**:

```bash
# Create required directories
mkdir -p certbot/conf certbot/www

# Use the same certbot directories
docker run -it --rm \
  -p 80:80 \
  -v ./certbot/conf:/etc/letsencrypt \
  -v ./certbot/www:/var/www/certbot \
  certbot/certbot certonly \
  --standalone \
  --preferred-challenges http \
  -d participant-b.tems-dataspace.eu \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email
```

## Step 2: Start Services in Production Mode

Start each participant with the `--profile prod` flag:

```bash
# On Participant A VM (production)
docker compose -f docker-compose-participant-a.yml --profile prod up -d

# On Participant B VM (production)
docker compose -f docker-compose-participant-b.yml --profile prod up -d
```

Wait until all services are started.

## Available Endpoints

### Participant A
Base URL: `https://participant-a.tems-dataspace.eu`

- `https://participant-a.tems-dataspace.eu/management` - EDC Management API
- `https://participant-a.tems-dataspace.eu/protocol` - EDC Protocol API
- `https://participant-a.tems-dataspace.eu/apigateway` - Kong API Gateway

### Participant B
Base URL: `https://participant-b.tems-dataspace.eu`

- `https://participant-b.tems-dataspace.eu/management` - EDC Management API
- `https://participant-b.tems-dataspace.eu/protocol` - EDC Protocol API
- `https://participant-b.tems-dataspace.eu/apigateway` - Kong API Gateway

## Certificate Auto-Renewal

The Certbot container will automatically attempt to renew certificates every 12 hours. Nginx reloads every 6 hours to pick up renewed certificates.

## Health Check

Verify that both participants are running:

```bash
# Check Participant A
curl -X POST https://participant-a.tems-dataspace.eu/management/v3/assets/request \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: <<yourEdcApiKey>>" \
  -d '{}'

# Check Participant B
curl -X POST https://participant-b.tems-dataspace.eu/management/v3/assets/request \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: <<yourEdcApiKey>>" \
  -d '{}'
```

## Stopping the Services

```bash
# Stop Participant A (production)
docker compose -f docker-compose-participant-a.yml --profile prod down

# Stop Participant B (production)
docker compose -f docker-compose-participant-b.yml --profile prod down
```

# Complete Workflow

This section demonstrates a complete end-to-end flow between Participant A and Participant B.

**Note**: The examples below use Development Mode URLs (`http://localhost:8080` and `http://localhost:8081`). For Production Mode, replace with the appropriate HTTPS URLs and the EDC API Key.

## Step 1: Create an Asset (Participant A)

Create a data asset representing the Petstore API:

```bash
curl -X POST http://localhost:8080/management/v3/assets \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: 123456" \
  -d '{
  "@context": {
    "@vocab": "https://w3id.org/edc/v0.0.1/ns/",
    "dcterms": "http://purl.org/dc/terms/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "prov": "http://www.w3.org/ns/prov#",
    "tc": "http://tems.org/2024/temscore#",
    "dcat": "http://www.w3.org/ns/dcat#"
  },
  "@type": "Asset",
  "properties": {
    "dcat:service": {
      "@type": ["dcat:DataService"],
      "dcterms:title": "Access to the Petstore API",
      "rdfs:comment": "This offer allows access to the Petstore REST API.",
      "dcat:keyword": ["Petstore", "REST API"],
      "dcat:version": "1.0.0",
      "dcterms:creator": {
        "@type": ["foaf:Organization", "prov:Agent"],
        "foaf:name": "Participant A"
      }
    }
  },
  "dataAddress": {
    "@type": "DataAddress",
    "type": "HttpData",
    "baseUrl": "http://localhost:8080/apigateway/v2",
    "proxyPath": "true"
  }
}'
```

## Step 2: Create a Policy (Participant A)

Create an access policy for the asset:

```bash
curl -X POST http://localhost:8080/management/v3/policydefinitions \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: 123456" \
  -d '{
  "@context": {
    "@vocab": "https://w3id.org/edc/v0.0.1/ns/",
    "odrl": "http://www.w3.org/ns/odrl/2/"
  },
  "policy": {
    "@context": "http://www.w3.org/ns/odrl.jsonld",
    "@type": "Set",
    "permission": [{
      "action": "use",
      "constraint": [{
        "@type": "Constraint",
        "leftOperand": "dateTime",
        "operator": "lteq",
        "rightOperand": "2025-12-31T12:00:00Z"
      }]
    }]
  }
}'
```

## Step 3: Create a Contract Definition (Participant A)

Link the asset and policy in a contract definition:

```bash
curl -X POST http://localhost:8080/management/v3/contractdefinitions \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: 123456" \
  -d '{
  "@context": ["https://w3id.org/edc/connector/management/v0.0.1"],
  "@type": "ContractDefinition",
  "accessPolicyId": "<<policyId>>",
  "contractPolicyId": "<<policyId>>",
  "assetsSelector": {
    "@type": "Criterion",
    "operandLeft": "https://w3id.org/edc/v0.0.1/ns/id",
    "operator": "=",
    "operandRight": "<<assetId>>"
  }
}'
```

## Step 4: Query the Catalog (Participant B)

Participant B queries Participant A's catalog to discover available offerings:

```bash
curl -X POST http://localhost:8081/management/v3/catalog/request \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: 123456" \
  -d '{
  "@context": ["https://w3id.org/edc/connector/management/v0.0.1"],
  "@type": "CatalogRequest",
  "counterPartyAddress": "http://host.docker.internal:8080/protocol",
  "counterPartyId": "participant-a",
  "protocol": "dataspace-protocol-http",
  "querySpec": {
    "offset": 0,
    "limit": 200
  }
}'
```

The response will contain the catalog with the asset and its contract offer. Note the policy `@id` (used as `hasPolicyId`) and the `assetId` for the next step.

## Step 5: Initiate Contract Negotiation (Participant B)

Start a contract negotiation using the policy and asset information from the catalog:

```bash
curl -X POST http://localhost:8081/management/v3/contractnegotiations \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: 123456" \
  -d '{
  "@context": ["https://w3id.org/edc/connector/management/v0.0.1"],
  "@type": "ContractRequest",
  "counterPartyAddress": "http://host.docker.internal:8080/protocol",
  "counterPartyId": "participant-a",
  "protocol": "dataspace-protocol-http",
  "policy": {
    "@id": "<<hasPolicyId>>",
    "@type": "odrl:Offer",
    "assigner": "participant-a",
    "target": "<<assetId>>",
    "odrl:permission": {
      "odrl:action": {
        "@id": "odrl:use"
      },
      "odrl:constraint": {
        "odrl:leftOperand": {
          "@id": "odrl:dateTime"
        },
        "odrl:operator": {
          "@id": "odrl:lteq"
        },
        "odrl:rightOperand": "2025-12-31T12:00:00Z"
      }
    },
    "odrl:prohibition": [],
    "odrl:obligation": []
  },
  "assetId": "<<assetId>>",
  "callbackAddresses": []
}'
```

The response contains a negotiation ID. Now you can see the negotiations to obtain the agreement id:

```bash
curl -X POST http://localhost:8081/management/v3/contractnegotiations/request \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: 123456" \
  -d '{
  "@context": ["https://w3id.org/edc/connector/management/v0.0.1"],
  "@type": "QuerySpec"
}'
```

Wait until the state is `FINALIZED`. Note the `contractAgreementId`.

## Step 6: Obtain Keycloak Token (from Central Governance)

Before accessing the API Gateway, obtain a token from the central governance Keycloak:

```bash
curl -X POST <<KEYCLOAK_URL>>/realms/<<REALM>>/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=<<CLIENT_ID>>" \
  -d "client_secret=<<CLIENT_SECRET>>" \
  -d "scope=openid" \
  -d "username=<<USERNAME_HERE>>" \
  -d "password=<<PASSWORD_HERE>>"
```

Extract the `access_token` from the response.

## Step 7: Request API Gateway Token (on Participant A)

Use the Keycloak token to obtain an API Gateway token:

```bash
curl -X POST http://localhost:8080/apigateway/temsapigateway/token \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <<access_token>>" \
  -d '{
    "agreementId": "<<contractAgreementId>>"
  }'
```

The response contains an `apiGatewayToken` for accessing the protected API.

## Step 8: Access Petstore via API Gateway (on Participant A)

Use the API Gateway token to access the Petstore API:

```bash
# Get store inventory
curl http://localhost:8080/apigateway/v2/store/inventory \
  -H "X-API-Gateway-Token: <<apiGatewayToken>>"
```

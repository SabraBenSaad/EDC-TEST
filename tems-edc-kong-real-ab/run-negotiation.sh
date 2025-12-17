#!/usr/bin/env bash
set -euo pipefail

############################################
# REQUIRED ENV VARS
############################################
: "${EDC_API_KEY:?Missing EDC_API_KEY}"
: "${A_MGMT:?Missing A_MGMT}"
: "${B_MGMT:?Missing B_MGMT}"
: "${A_PROTOCOL:?Missing A_PROTOCOL}"
: "${A_ID:?Missing A_ID}"
: "${ASSET_ID:?Missing ASSET_ID}"

############################################
# GLOBALS
############################################
HDR=(-H "Content-Type: application/json" -H "X-Api-Key: ${EDC_API_KEY}")

echo "🚀 Starting EDC contract negotiation + transfer (A → B)"
echo "A_MGMT=$A_MGMT"
echo "B_MGMT=$B_MGMT"
echo "A_PROTOCOL=$A_PROTOCOL"
echo "A_ID=$A_ID"
echo "ASSET_ID=$ASSET_ID"
echo

############################################
# Helper
############################################
curl_json() {
  curl -sS "$@" "${HDR[@]}"
}

############################################
# 1) POLICY
############################################
echo "==> 1) Upsert PolicyDefinition"

cat > /tmp/policy.json <<EOF
{
  "@context": { "edc": "https://w3id.org/edc/v0.0.1/ns/" },
  "@id": "policydef-a-allow",
  "@type": "edc:PolicyDefinition",
  "edc:policy": {
    "@type": "odrl:Set",
    "odrl:permission": [ { "odrl:action": "USE" } ]
  }
}
EOF

curl_json -X POST "$A_MGMT/v3/policydefinitions" \
  -d @/tmp/policy.json | jq -e . >/dev/null || true

echo "✅ PolicyDefinition OK"
echo

############################################
# 2) ASSET
############################################
echo "==> 2) Upsert Asset"

cat > /tmp/asset.json <<EOF
{
  "@context": { "edc": "https://w3id.org/edc/v0.0.1/ns/" },
  "@type": "edc:AssetCreateRequest",
  "asset": {
    "@id": "$ASSET_ID",
    "properties": {
      "name": "Demo Asset A",
      "contenttype": "text/plain"
    }
  },
  "dataAddress": {
    "type": "HttpData",
    "baseUrl": "https://raw.githubusercontent.com/eclipse-edc/Connector/main/README.md"
  }
}
EOF

curl_json -X POST "$A_MGMT/v3/assets" \
  -d @/tmp/asset.json | jq -e . >/dev/null || true

echo "✅ Asset OK"
echo

############################################
# 3) CONTRACT DEFINITION
############################################
echo "==> 3) Upsert ContractDefinition"

cat > /tmp/contractdef.json <<EOF
{
  "@context": { "edc": "https://w3id.org/edc/v0.0.1/ns/" },
  "@id": "contractdef-a-fixed",
  "@type": "edc:ContractDefinition",
  "accessPolicyId": "policydef-a-allow",
  "contractPolicyId": "policydef-a-allow",
  "assetsSelector": [
    {
      "@type": "Criterion",
      "operandLeft": "edc:id",
      "operator": "=",
      "operandRight": "$ASSET_ID"
    }
  ]
}
EOF

curl_json -X POST "$A_MGMT/v3/contractdefinitions" \
  -d @/tmp/contractdef.json | jq -e . >/dev/null || true

echo "✅ ContractDefinition OK"
echo

############################################
# 4) CATALOG REQUEST (FROM B)
############################################
echo "==> 4) Fetch catalog from A (via B)"

cat > /tmp/catalog.json <<EOF
{
  "@context": { "edc": "https://w3id.org/edc/v0.0.1/ns/" },
  "counterPartyAddress": "$A_PROTOCOL",
  "counterPartyId": "$A_ID",
  "protocol": "dataspace-protocol-http",
  "querySpec": { "offset": 0, "limit": 50 }
}
EOF

CATALOG=$(curl_json -X POST "$B_MGMT/v3/catalog/request" \
  -d @/tmp/catalog.json)

############################################
# 5) EXTRACT OFFER ID (IMPORTANT)
############################################
OFFER_ID=$(echo "$CATALOG" | jq -r '
  .. | objects
  | select(has("odrl:hasPolicy"))
  | ."odrl:hasPolicy"."@id"
  ' | head -n1)

if [[ -z "$OFFER_ID" || "$OFFER_ID" == "null" ]]; then
  echo "❌ No OFFER_ID found in catalog"
  exit 1
fi

echo "✅ OFFER_ID=$OFFER_ID"
echo

############################################
# 6) CONTRACT NEGOTIATION
############################################
echo "==> 5) Start Contract Negotiation"

cat > /tmp/contract-request.json <<EOF
{
  "@context": {
    "edc": "https://w3id.org/edc/v0.0.1/ns/",
    "odrl": "http://www.w3.org/ns/odrl/2/"
  },
  "@type": "ContractRequest",
  "protocol": "dataspace-protocol-http",
  "counterPartyAddress": "$A_PROTOCOL",
  "counterPartyId": "$A_ID",
  "policy": {
    "@id": "$OFFER_ID"
  }
}
EOF

NEGOTIATION_ID=$(curl_json -X POST "$B_MGMT/v3/contractnegotiations" \
  -d @/tmp/contract-request.json | jq -r '.["@id"]')

echo "NEGOTIATION_ID=$NEGOTIATION_ID"
echo

############################################
# 7) POLL NEGOTIATION
############################################
echo "==> 6) Poll ContractNegotiation"

while true; do
  RESP=$(curl_json -X POST "$B_MGMT/v3/contractnegotiations/request" \
    -d "{
      \"filterExpression\": [{
        \"operandLeft\": \"@id\",
        \"operator\": \"=\",
        \"operandRight\": \"$NEGOTIATION_ID\"
      }],
      \"limit\": 1
    }")

  STATE=$(echo "$RESP" | jq -r '.[0].state // empty')
  AGREEMENT=$(echo "$RESP" | jq -r '.[0].contractAgreementId // empty')

  echo "state=$STATE agreement=$AGREEMENT"

  [[ "$STATE" == "FINALIZED" ]] && break
  [[ "$STATE" == "TERMINATED" ]] && { echo "❌ Negotiation failed"; exit 1; }

  sleep 2
done

echo
echo "🎉 Contract Agreement finalized!"
echo "AGREEMENT_ID=$AGREEMENT"

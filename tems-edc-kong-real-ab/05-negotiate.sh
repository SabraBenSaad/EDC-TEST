#!/usr/bin/env bash
set -e
source scripts/00-env.sh

OFFER_ID=$(jq -r '
  .. | objects | .["odrl:hasPolicy"]? | .["@id"]? // empty
' "$TMPDIR/catalog-response.json" | head -n 1)

if [[ -z "$OFFER_ID" ]]; then
  echo "❌ No OFFER_ID found"
  exit 1
fi

jq -c '
  .. | objects | .["odrl:hasPolicy"]?
' "$TMPDIR/catalog-response.json" | head -n 1 > "$TMPDIR/policy.json"

cat > "$TMPDIR/contract-request.json" <<EOF
{
  "@context": {
    "edc": "https://w3id.org/edc/v0.0.1/ns/",
    "odrl": "http://www.w3.org/ns/odrl/2/"
  },
  "@type": "ContractRequest",
  "protocol": "dataspace-protocol-http",
  "counterPartyAddress": "${A_PROTOCOL}",
  "counterPartyId": "${A_ID}",
  "policy": $(cat "$TMPDIR/policy.json")
}
EOF

curl -sS -X POST "$B_MGMT/v3/contractnegotiations" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $EDC_API_KEY" \
  -d @"$TMPDIR/contract-request.json" | jq .

echo "✅ Negotiation started"

#!/usr/bin/env bash
set -e
source scripts/00-env.sh

cat > "$TMPDIR/catalog.json" <<EOF
{
  "@context": { "edc": "https://w3id.org/edc/v0.0.1/ns/" },
  "counterPartyAddress": "${A_PROTOCOL}",
  "counterPartyId": "${A_ID}",
  "protocol": "dataspace-protocol-http",
  "querySpec": { "offset": 0, "limit": 50 }
}
EOF

curl -sS -X POST "$B_MGMT/v3/catalog/request" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $EDC_API_KEY" \
  -d @"$TMPDIR/catalog.json" | tee "$TMPDIR/catalog-response.json" | jq .

echo "✅ Catalog fetched"

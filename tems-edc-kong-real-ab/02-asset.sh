#!/usr/bin/env bash
set -e
source scripts/00-env.sh

cat > "$TMPDIR/asset.json" <<EOF
{
  "@context": { "edc": "https://w3id.org/edc/v0.0.1/ns/" },
  "@type": "edc:AssetCreateRequest",
  "assetId": "${ASSET_ID}",
  "properties": {
    "name": "Demo Asset A",
    "contenttype": "text/plain"
  },
  "dataAddress": {
    "type": "HttpData",
    "properties": {
      "baseUrl": "https://raw.githubusercontent.com/eclipse-edc/Connector/main/README.md"
    }
  }
}
EOF

curl -sS -X POST "$A_MGMT/v3/assets" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $EDC_API_KEY" \
  -d @"$TMPDIR/asset.json" | jq .

echo "✅ Asset done"

#!/usr/bin/env bash
set -e
source scripts/00-env.sh

cat > "$TMPDIR/policy.json" <<EOF
{
  "@context": {
    "edc": "https://w3id.org/edc/v0.0.1/ns/",
    "odrl": "http://www.w3.org/ns/odrl/2/"
  },
  "@id": "${POLICYDEF_ID}",
  "@type": "edc:PolicyDefinition",
  "edc:policy": {
    "@type": "odrl:Set",
    "odrl:permission": [
      { "odrl:action": "USE" }
    ]
  }
}
EOF

curl -sS -X POST "$A_MGMT/v3/policydefinitions" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $EDC_API_KEY" \
  -d @"$TMPDIR/policy.json" | jq .

echo "✅ Policy done"

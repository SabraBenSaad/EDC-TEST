#!/usr/bin/env bash
set -e
source scripts/00-env.sh

cat > "$TMPDIR/contractdef.json" <<EOF
{
  "@context": { "edc": "https://w3id.org/edc/v0.0.1/ns/" },
  "@id": "${CONTRACTDEF_ID}",
  "@type": "edc:ContractDefinition",
  "edc:accessPolicyId": "${POLICYDEF_ID}",
  "edc:contractPolicyId": "${POLICYDEF_ID}",
  "edc:assetsSelector": [
    {
      "@type": "edc:Criterion",
      "edc:operandLeft": "edc:id",
      "edc:operator": "=",
      "edc:operandRight": "${ASSET_ID}"
    }
  ]
}
EOF

curl -sS -X POST "$A_MGMT/v3/contractdefinitions" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $EDC_API_KEY" \
  -d @"$TMPDIR/contractdef.json" | jq .

echo "✅ ContractDefinition done"

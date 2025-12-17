#!/usr/bin/env bash
set -e

export EDC_API_KEY="password"

export A_MGMT="http://localhost:8080/management"
export B_MGMT="http://localhost:8081/management"

export A_PROTOCOL="http://api-gateway-a:8080/protocol"
export A_ID="participant-a"

export ASSET_ID="asset-a-1"
export POLICYDEF_ID="policydef-a-allow"
export CONTRACTDEF_ID="contractdef-a-1-fixed"

export TMPDIR="/tmp/edc"
mkdir -p "$TMPDIR"

echo "✅ Environment loaded"

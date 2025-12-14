#!/usr/bin/env python3
import requests, json, time
from urllib.parse import urljoin

A = "http://localhost:8080"
B = "http://localhost:8081"

def post(url, payload):
    r = requests.post(url, headers={"Content-Type":"application/json"}, data=json.dumps(payload))
    print("POST", url, r.status_code, r.text[:300])
    r.raise_for_status()
    return r.json() if r.text else {}

def get(url):
    r = requests.get(url)
    print("GET", url, r.status_code, r.text[:400])
    r.raise_for_status()
    return r.json() if r.text else {}

def main():
    # NOTE: payloads EDC varient selon versions. On tente les endpoints courants.
    asset = {"assetId":"asset-demo-1","properties":{"name":"demo-asset","contenttype":"application/json"},"dataAddress":{"type":"HttpData","baseUrl":"https://example.com/data.json"}}
    policy = {"policyId":"policy-demo-1","policy":{"permissions":[{"action":"USE"}]}}
    contractdef = {"id":"contractdef-demo-1","accessPolicyId":"policy-demo-1","contractPolicyId":"policy-demo-1","criteria":[{"operandLeft":"asset:prop:id","operator":"=","operandRight":"asset-demo-1"}]}

    # Try common management paths (v2/v3 differences)
    candidates = [
        ("assets", asset),
        ("assets/request", asset),
    ]
    for path, payload in candidates:
        try:
            post(urljoin(A, f"/management/{path}"), payload)
            break
        except Exception:
            continue

    for path in ["policydefinitions","policydefinitions/request","policies","policies/request"]:
        try:
            post(urljoin(A, f"/management/{path}"), policy)
            break
        except Exception:
            continue

    for path in ["contractdefinitions","contractdefinitions/request","contractdefinitions", "contractdefinitions/request"]:
        try:
            post(urljoin(A, f"/management/{path}"), contractdef)
            break
        except Exception:
            continue

    print("\n--- Fetch catalog from A via DSP ---")
    # Common DSP catalog endpoints differ; try a couple
    for p in ["/protocol/catalog", "/protocol/catalog/request", "/protocol/v1/catalog"]:
        try:
            r = requests.get(A+p, timeout=10)
            print("GET", A+p, r.status_code, r.text[:600])
            if r.status_code == 200:
                break
        except Exception:
            pass

    # Emit business event so you see metrics in central
    for base in [A,B]:
        requests.post(base+"/observability/event/transfer", json={"status":"SUCCESS","duration":1.1})

    print("\nCheck metrics:")
    print("A:", A+"/metrics")
    print("B:", B+"/metrics")
    print("Prometheus:", "http://localhost:9090")
    print("Grafana:", "http://localhost:3000 (admin/admin)")

if __name__ == "__main__":
    main()

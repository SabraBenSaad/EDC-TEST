import os
from fastapi import FastAPI, Request
from starlette.responses import Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest

PARTICIPANT = os.getenv("PARTICIPANT_ID","unknown")
app = FastAPI(title=f"Observability ({PARTICIPANT})")

transfers = Counter("dataspace_transfers_total","Transfers (business)",["participant","status"])
latency = Histogram("dataspace_transfer_latency_seconds","Transfer latency (s)",["participant"])
ready_g = Gauge("dataspace_ready","Readiness",["participant"])

@app.get("/health")
def health():
    return {"status":"UP","participant":PARTICIPANT}

@app.get("/ready")
def ready():
    ready_g.labels(PARTICIPANT).set(1)
    return {"status":"READY","participant":PARTICIPANT}

@app.post("/event/transfer")
async def event_transfer(req: Request):
    payload = await req.json()
    status = str(payload.get("status","SUCCESS"))
    duration = float(payload.get("duration",0.5))
    transfers.labels(PARTICIPANT,status).inc()
    latency.labels(PARTICIPANT).observe(duration)
    return {"ok": True, "participant": PARTICIPANT, "status": status, "duration": duration}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain; version=0.0.4; charset=utf-8")

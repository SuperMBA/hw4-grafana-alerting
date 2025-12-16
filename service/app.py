import time
import random

from fastapi import FastAPI, Query, Response
from prometheus_client import Histogram, Counter, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "Request latency in seconds",
    buckets=(0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0)
)

REQUESTS_TOTAL = Counter("requests_total", "Total requests", ["endpoint", "status"])


@app.get("/predict")
def predict(
    sleep_ms: int = Query(50, ge=0, le=5000),
    fail_prob: float = Query(0.0, ge=0.0, le=1.0),
):
    with REQUEST_LATENCY.time():
        time.sleep(sleep_ms / 1000.0)

        if random.random() < fail_prob:
            REQUESTS_TOTAL.labels(endpoint="/predict", status="500").inc()
            return Response(content="error", status_code=500)

        REQUESTS_TOTAL.labels(endpoint="/predict", status="200").inc()
        return {"ok": True, "slept_ms": sleep_ms}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

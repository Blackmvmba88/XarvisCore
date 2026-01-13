from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .pydantic_models import DeviceViewModel, DeviceViewWithHistory, TelemetrySampleModel
from .telemetry_ingest import get_all_device_views, get_device_view, get_device_history

app = FastAPI(title="Hero Scheduler API", version="0.1")

# Allow local dashboards during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/devices/status", response_model=list[DeviceViewModel])
def devices_status():
    views = get_all_device_views()
    # convert DeviceView dataclasses to pydantic models
    out = []
    for v in views:
        out.append(DeviceViewModel(
            device_id=v.device_id,
            last_ts=v.last_ts,
            avg_temp=v.avg_temp,
            max_temp=v.max_temp,
            mem_pressure=v.mem_pressure,
            sample_count=v.sample_count,
            health={
                'status': v.health.status.value if hasattr(v.health.status, 'value') else v.health.status,
                'score': v.health.score,
                'reason': v.health.reason,
                'flags': v.health.flags,
            }
        ))
    return out


@app.get("/devices/status/history", response_model=list[DeviceViewWithHistory])
def devices_status_history(limit: int = 20):
    """Return recent history for all known devices; `limit` controls per-device samples returned (most recent first)."""
    views = get_all_device_views()
    out = []
    for v in views:
        hist = [
            {
                'ts': s.ts,
                'device_id': s.device_id,
                'gpu_temp': s.gpu_temp,
                'gpu_memory_used_gb': s.gpu_memory_used_gb,
                'gpu_memory_total_gb': s.gpu_memory_total_gb,
                'is_throttling': s.is_throttling,
                'power_watts': s.power_watts,
            }
            for s in get_device_history(v.device_id, limit=limit)
        ]
        out.append(DeviceViewWithHistory(
            device_id=v.device_id,
            last_ts=v.last_ts,
            avg_temp=v.avg_temp,
            max_temp=v.max_temp,
            mem_pressure=v.mem_pressure,
            sample_count=v.sample_count,
            health={
                'status': v.health.status.value if hasattr(v.health.status, 'value') else v.health.status,
                'score': v.health.score,
                'reason': v.health.reason,
                'flags': v.health.flags,
            },
            history=hist,
        ))
    return out


@app.get("/devices/{device_id}", response_model=DeviceViewModel)
def device_status(device_id: str):
    try:
        v = get_device_view(device_id)
    except Exception:
        raise HTTPException(status_code=404, detail="device not found")
    return DeviceViewModel(
        device_id=v.device_id,
        last_ts=v.last_ts,
        avg_temp=v.avg_temp,
        max_temp=v.max_temp,
        mem_pressure=v.mem_pressure,
        sample_count=v.sample_count,
        health={
            'status': v.health.status.value if hasattr(v.health.status, 'value') else v.health.status,
            'score': v.health.score,
            'reason': v.health.reason,
            'flags': v.health.flags,
        }
    )


@app.get('/metrics')
def metrics():
    """Return current observability metrics snapshot as JSON."""
    from .telemetry_observability import metrics as observability_metrics

    return JSONResponse(content=observability_metrics.snapshot())


@app.get("/devices/{device_id}", response_model=DeviceViewModel)
def device_status(device_id: str):
    try:
        v = get_device_view(device_id)
    except Exception:
        raise HTTPException(status_code=404, detail="device not found")
    return DeviceViewModel(
        device_id=v.device_id,
        last_ts=v.last_ts,
        avg_temp=v.avg_temp,
        max_temp=v.max_temp,
        mem_pressure=v.mem_pressure,
        sample_count=v.sample_count,
        health={
            'status': v.health.status.value if hasattr(v.health.status, 'value') else v.health.status,
            'score': v.health.score,
            'reason': v.health.reason,
            'flags': v.health.flags,
        }
    )


@app.get('/metrics')
def metrics():
    """Return current observability metrics snapshot as JSON."""
    from .telemetry_observability import metrics as observability_metrics

    return JSONResponse(content=observability_metrics.snapshot())


@app.get('/devices/{device_id}/history', response_model=list[TelemetrySampleModel])
def device_history(device_id: str, limit: int = 100, since: str = None):
    """Return the recent history for a single device. `since` should be an ISO timestamp if provided."""
    from datetime import datetime
    since_dt = None
    if since:
        try:
            since_dt = datetime.fromisoformat(since)
        except Exception:
            raise HTTPException(status_code=400, detail='invalid since timestamp')

    samples = get_device_history(device_id, limit=limit, since=since_dt)
    out = []
    for s in samples:
        out.append(TelemetrySampleModel(
            ts=s.ts,
            device_id=s.device_id,
            gpu_temp=s.gpu_temp,
            gpu_memory_used_gb=s.gpu_memory_used_gb,
            gpu_memory_total_gb=s.gpu_memory_total_gb,
            is_throttling=s.is_throttling,
            power_watts=s.power_watts,
        ))
    return out


# a small convenience for local dev
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8787)

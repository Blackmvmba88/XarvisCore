from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .pydantic_models import DeviceViewModel
from .telemetry_ingest import get_all_device_views, get_device_view

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


# a small convenience for local dev
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8787)

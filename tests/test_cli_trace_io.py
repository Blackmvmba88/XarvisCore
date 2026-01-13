import json
import tempfile
from datetime import datetime, timedelta

from 20_BLENDER_INTEGRATION.hero.replay import Simulator
from 20_BLENDER_INTEGRATION.hero.telemetry_model import TelemetrySample
from 20_BLENDER_INTEGRATION.hero.scheduler import Task, RenderJob


def make_serializable_trace(tmp_path):
    now = datetime(2025, 1, 1, 0, 0, 0)

    trace = []
    trace.append({'type': 'telemetry', 'ts': now, 'sample': TelemetrySample(ts=now, device_id='gpu0', gpu_temp=60.0, gpu_memory_used_gb=2.0, gpu_memory_total_gb=16.0)})
    job_ts = now + timedelta(seconds=1)
    job = RenderJob('job1', [Task('t1', required_memory_mb=1000, requires_gpu=True, allow_cpu_fallback=False)], priority=1)
    trace.append({'type': 'job', 'ts': job_ts, 'job': job, 'deadline': job_ts + timedelta(seconds=5)})

    return trace


def test_save_and_load_trace(tmp_path):
    trace = make_serializable_trace(tmp_path)
    path = tmp_path / 'trace.json'
    Simulator.save_trace_to_file(trace, str(path))

    loaded = Simulator.load_trace_from_file(str(path))
    assert isinstance(loaded, list)
    assert loaded[0]['type'] == 'telemetry'
    assert loaded[1]['type'] == 'job'
    assert loaded[0]['sample'].device_id == 'gpu0'


def test_cli_run_and_report(tmp_path):
    trace = make_serializable_trace(tmp_path)
    trace_path = tmp_path / 't.json'
    Simulator.save_trace_to_file(trace, str(trace_path))

    report_path = tmp_path / 'report.json'
    report = Simulator().simulate(Simulator.load_trace_from_file(str(trace_path)), None)
    # report is a SimulationResult, convert to dict
    d = report.to_dict()
    assert 'assignments' in d

    # run via CLI helper run_simulate (imported dynamically)
    from 20_BLENDER_INTEGRATION.hero.cli import run_simulate

    out = run_simulate(str(trace_path), 'greedy', report_out=str(report_path))
    assert isinstance(out, dict)
    assert 'deadline_misses' in out
    # check file written
    with open(report_path, 'r') as f:
        j = json.load(f)
    assert 'deadline_misses' in j

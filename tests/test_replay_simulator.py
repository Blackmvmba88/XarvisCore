from datetime import datetime, timedelta

from 20_BLENDER_INTEGRATION.hero.replay import Simulator, GreedyPolicy, EDFPolicy, SimulationResult
from 20_BLENDER_INTEGRATION.hero.telemetry_model import TelemetrySample
from 20_BLENDER_INTEGRATION.hero.scheduler import Device


def make_trace_case():
    now = datetime(2025, 1, 1, 0, 0, 0)
    # devices
    devices = [
        {'id': 'gpu0', 'backend': 'CUDA', 'total_memory_mb': 16000, 'free_memory_mb': 16000, 'compute_score': 1.0},
        {'id': 'cpu0', 'backend': 'CPU', 'total_memory_mb': 32000, 'free_memory_mb': 32000, 'compute_score': 0.5},
    ]

    trace = []
    # healthy telemetry sample
    trace.append({'type': 'telemetry', 'ts': now, 'sample': TelemetrySample(ts=now, device_id='gpu0', gpu_temp=60.0, gpu_memory_used_gb=2.0, gpu_memory_total_gb=16.0)})

    # submit job at t+1s
    job_ts = now + timedelta(seconds=1)
    from 20_BLENDER_INTEGRATION.hero.scheduler import Task, RenderJob

    job = RenderJob('job1', [Task('t1', required_memory_mb=1000, requires_gpu=True, allow_cpu_fallback=False)], priority=1)
    trace.append({'type': 'job', 'ts': job_ts, 'job': job, 'deadline': job_ts + timedelta(seconds=5)})

    # then at t+2s device degrades
    bad_ts = now + timedelta(seconds=2)
    trace.append({'type': 'telemetry', 'ts': bad_ts, 'sample': TelemetrySample(ts=bad_ts, device_id='gpu0', gpu_temp=120.0, gpu_memory_used_gb=15.0, gpu_memory_total_gb=16.0, is_throttling=True)})

    return devices, trace


def test_simulator_deterministic():
    devices, trace = make_trace_case()
    sim1 = Simulator(devices=devices)
    sim2 = Simulator(devices=devices)

    res1 = sim1.simulate(trace, GreedyPolicy())
    res2 = sim2.simulate(trace, GreedyPolicy())

    assert isinstance(res1, SimulationResult)
    assert res1.assignments == res2.assignments
    assert res1.deadline_misses == res2.deadline_misses


def test_policy_comparison_differs():
    devices, trace = make_trace_case()
    sim_g = Simulator(devices=devices)
    sim_e = Simulator(devices=devices)

    res_g = sim_g.simulate(trace, GreedyPolicy())
    res_e = sim_e.simulate(trace, EDFPolicy())

    # policies may behave differently; ensure we can compare results deterministically
    assert isinstance(res_g, SimulationResult)
    assert isinstance(res_e, SimulationResult)
    # at least one difference in assignments or deadline miss counts
    assert (res_g.assignments != res_e.assignments) or (res_g.deadline_misses != res_e.deadline_misses)

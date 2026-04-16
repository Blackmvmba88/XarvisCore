import importlib.util
from pathlib import Path


def _load_module(path):
    spec = importlib.util.spec_from_file_location('scheduler', str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_scheduler_dry_run_basic():
    m = _load_module(Path('20_BLENDER_INTEGRATION/hero/scheduler.py'))
    Scheduler = m.Scheduler
    Task = m.Task
    RenderJob = m.RenderJob

    s = Scheduler()
    s.register_devices([
        {'id': 'gpu0', 'backend': 'CUDA', 'total_memory_mb': 16000, 'free_memory_mb': 16000, 'compute_score': 1.0},
    ])

    j1 = RenderJob('job1', tasks=[Task('t1', required_memory_mb=100, requires_gpu=True, frames=10)], priority=0)
    j2 = RenderJob('job2', tasks=[Task('t2', required_memory_mb=100, requires_gpu=True, frames=5)], priority=0)
    s.submit(j1)
    s.submit(j2)

    plan = s.dry_run()
    assert isinstance(plan, dict)
    assert [p['job_id'] for p in plan['plans']] == ['job1', 'job2']
    assert [p['frames'] for p in plan['plans']] == [10, 5]


def test_scheduler_empty_dry():
    m = _load_module(Path('20_BLENDER_INTEGRATION/hero/scheduler.py'))
    Scheduler = m.Scheduler
    s = Scheduler()
    plan = s.dry_run()
    assert plan['plans'] == []

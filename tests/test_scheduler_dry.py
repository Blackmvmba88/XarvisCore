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
    RenderJob = m.RenderJob

    s = Scheduler()
    j1 = RenderJob('job1', 'mk1', 10)
    j2 = RenderJob('job2', 'mk2', 5)
    s.submit(j1)
    s.submit(j2)

    plan = s.dry_run()
    assert plan == [('job1', 'mk1', 10), ('job2', 'mk2', 5)]


def test_scheduler_empty_dry():
    m = _load_module(Path('20_BLENDER_INTEGRATION/hero/scheduler.py'))
    Scheduler = m.Scheduler
    s = Scheduler()
    assert s.dry_run() == []

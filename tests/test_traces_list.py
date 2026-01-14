from 20_BLENDER_INTEGRATION.hero.cli import list_traces


def test_list_traces_contains_files():
    l = list_traces()
    assert 'burst.json' in l
    assert 'starvation.json' in l
    assert 'throttle.json' in l
    assert 'clustered_deadlines.json' in l
    assert 'backfill.json' in l
    assert 'ramp.json' in l
    assert 'mem_pressure.json' in l
    assert 'offline.json' in l

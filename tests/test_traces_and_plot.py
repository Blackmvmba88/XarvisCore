import tempfile
from pathlib import Path

from 20_BLENDER_INTEGRATION.hero.replay import Simulator
from 20_BLENDER_INTEGRATION.hero.cli import generate_timeline_plot, run_simulate


def test_plot_generation_from_trace(tmp_path):
    traces_dir = Path('traces')
    # use the burst trace that was added
    trace_path = traces_dir / 'burst.json'
    assert trace_path.exists()

    report_out = tmp_path / 'report.json'
    plot_out = tmp_path / 'timeline.png'

    # run simulation and export report
    report = run_simulate(str(trace_path), 'greedy', report_out=str(report_out), plot_out=str(plot_out))
    assert plot_out.exists()
    assert report_out.exists()
    assert 'deadline_misses' in report

    # also call plot helper directly (load trace) to ensure it runs
    trace = Simulator.load_trace_from_file(str(trace_path))
    generate_timeline_plot(trace, report, str(tmp_path / 'timeline2.png'))
    assert (tmp_path / 'timeline2.png').exists()

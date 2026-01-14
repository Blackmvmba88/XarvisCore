"""CLI for running simulations: load trace JSON, run policy, export report."""
import argparse
import json
from pathlib import Path
from typing import Any

from .replay import Simulator, GreedyPolicy, EDFPolicy

POLICIES = {
    'greedy': GreedyPolicy,
    'edf': EDFPolicy,
}


def run_simulate(trace_path: str, policy_name: str, report_out: str = None, plot_out: str = None) -> Any:
    sim = Simulator()
    trace = Simulator.load_trace_from_file(trace_path)
    policy_cls = POLICIES.get(policy_name)
    if not policy_cls:
        raise SystemExit(f'unknown policy: {policy_name}')
    policy = policy_cls()
    res = sim.simulate(trace, policy)
    report = res.to_dict()
    if report_out:
        p = Path(report_out)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
    if plot_out:
        generate_timeline_plot(trace, report, plot_out)
    return report


# plotting helpers -------------------------------------------------------
def generate_timeline_plot(trace: list, report: dict, out_path: str):
    """Create a simple timeline PNG showing assignments (by device) and per-device temperature over time.

    trace: list of serialized events (as produced by Simulator.save_trace_to_file)
    report: SimulationResult.to_dict()
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from datetime import datetime
    except Exception as e:
        raise RuntimeError('matplotlib is required for plot export') from e

    # extract telemetry per device
    device_temps = {}
    times = []
    for ev in trace:
        if ev['type'] == 'telemetry':
            ts = datetime.fromisoformat(ev['ts'])
            d = ev['sample']['device_id']
            device_temps.setdefault(d, {'ts': [], 'temp': []})
            device_temps[d]['ts'].append(ts)
            device_temps[d]['temp'].append(ev['sample']['gpu_temp'])
            times.append(ts)

    # assignments
    assign_by_device = {}
    for a in report.get('assignments', []):
        ts = datetime.fromisoformat(a['ts'])
        d = a.get('assigned_device_id') or 'rejected'
        assign_by_device.setdefault(d, []).append((ts, a['job_id']))
        times.append(ts)

    if not times:
        raise ValueError('no time points in trace')

    min_t, max_t = min(times), max(times)

    fig, ax = plt.subplots(figsize=(10, 3 + 1 * len(device_temps)))

    # plot temp lines for devices on secondary axis
    ax2 = ax.twinx()
    colors = plt.cm.get_cmap('tab10')
    device_list = sorted(device_temps.keys())
    for idx, d in enumerate(device_list):
        ts = device_temps[d]['ts']
        temp = device_temps[d]['temp']
        ax2.plot(ts, temp, label=f'{d} temp', color=colors(idx))

    # plot assignments as scatter on primary y (device index)
    device_index = {d: i for i, d in enumerate(device_list)}
    for d, assigns in assign_by_device.items():
        if d == 'rejected':
            y = -1
            ax.scatter([t for t, _ in assigns], [y] * len(assigns), marker='x', color='k', label='rejected')
            for t, job in assigns:
                ax.annotate(job, (t, y), xytext=(3, 3), textcoords='offset points', fontsize=6)
        else:
            y = device_index.get(d, 0)
            ax.scatter([t for t, _ in assigns], [y] * len(assigns), label=d, color=colors(device_index.get(d, 0)))
            for t, job in assigns:
                ax.annotate(job, (t, y), xytext=(3, 3), textcoords='offset points', fontsize=6)

    ax.set_ylim(-2, max(0, len(device_list) - 1) + 1)
    ax.set_yticks(list(range(len(device_list))) + [-1])
    ax.set_yticklabels(device_list + ['rejected'])
    ax.set_xlim(min_t, max_t)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    fig.autofmt_xdate()
    ax.set_xlabel('time')
    ax.set_title('Simulation timeline: assignments (y) and device temps')
    ax.grid(True, axis='x', linestyle='--', linewidth=0.5)
    ax2.set_ylabel('temperature (C)')
    ax.legend(loc='upper left', fontsize='small')

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches='tight')
    plt.close(fig)


def list_traces(traces_dir: str = 'traces'):
    p = Path(traces_dir)
    if not p.exists():
        return []
    return sorted([str(x.name) for x in p.iterdir() if x.is_file() and x.suffix == '.json'])


def main():
    p = argparse.ArgumentParser(prog='hero-sim')
    p.add_argument('--trace', help='Path to trace JSON file')
    p.add_argument('--policy', default='greedy', choices=POLICIES.keys())
    p.add_argument('--report', help='Optional path to write report JSON')
    p.add_argument('--plot', help='Optional path to write timeline PNG')
    p.add_argument('--list-traces', action='store_true', help='List available sample traces and exit')
    args = p.parse_args()

    if args.list_traces:
        for t in list_traces():
            print(t)
        return

    if not args.trace:
        raise SystemExit('missing --trace (or use --list-traces)')

    report = run_simulate(args.trace, args.policy, args.report, plot_out=args.plot)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
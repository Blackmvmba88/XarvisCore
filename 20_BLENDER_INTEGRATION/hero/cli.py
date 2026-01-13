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


def run_simulate(trace_path: str, policy_name: str, report_out: str = None) -> Any:
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
    return report


def main():
    p = argparse.ArgumentParser(prog='hero-sim')
    p.add_argument('--trace', required=True, help='Path to trace JSON file')
    p.add_argument('--policy', default='greedy', choices=POLICIES.keys())
    p.add_argument('--report', help='Optional path to write report JSON')
    args = p.parse_args()

    report = run_simulate(args.trace, args.policy, args.report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
from __future__ import annotations

import argparse
import json

from xarvis.integrations.warpblack import WarpBlackAdapter, WarpBlackError


def _command_argv(raw: list[str]) -> list[str]:
    argv = list(raw)
    if argv and argv[0] == "--":
        argv = argv[1:]
    return argv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xarvis-warp",
        description="XarvisCore client for the local WARPBLACK execution bridge",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("health")
    sub.add_parser("capabilities")

    execute = sub.add_parser("exec")
    execute.add_argument("--cwd", default=".")
    execute.add_argument("--timeout", type=float, default=60.0)
    execute.add_argument("--approve", action="store_true")
    execute.add_argument("argv", nargs=argparse.REMAINDER)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        adapter = WarpBlackAdapter.from_env()
        if args.command == "health":
            result = adapter.health()
        elif args.command == "capabilities":
            result = adapter.capabilities()
        else:
            command = _command_argv(args.argv)
            if not command:
                raise ValueError("missing command argv")
            result = adapter.execute(
                command,
                cwd=args.cwd,
                timeout_s=args.timeout,
                approved=args.approve,
            )
    except (ValueError, WarpBlackError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 3

    print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

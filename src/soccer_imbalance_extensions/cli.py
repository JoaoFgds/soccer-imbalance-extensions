from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from .acquisition import collect_transfermarkt_pilot, fetch_reference
from .data import discover_source, load_standings
from .pipeline import run_pipeline


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(prog="sie")
    command.add_argument("--project-root", type=Path, default=Path.cwd())
    sub = command.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate-source")
    validate.add_argument("--source-root", type=Path, required=True)
    fetch = sub.add_parser("fetch-reference")
    fetch.add_argument("--destination", type=Path, default=Path("data/raw/reference"))
    pilot = sub.add_parser("collect-pilot")
    pilot.add_argument("--delay-seconds", type=float, default=3.0)
    run = sub.add_parser("run-all")
    run.add_argument("--source-root", type=Path, required=True)
    one = sub.add_parser("run-mvp")
    one.add_argument("number", type=int, choices=range(1, 6))
    one.add_argument("--source-root", type=Path, required=True)
    return command


def main() -> None:
    args = parser().parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    root = args.project_root.resolve()
    if args.command == "validate-source":
        layout = discover_source(args.source_root)
        standings = load_standings(layout)
        print(json.dumps({"valid": True, "rows": len(standings), "root": str(layout.root)}, indent=2))
    elif args.command == "fetch-reference":
        print(json.dumps(fetch_reference((root / args.destination).resolve()), indent=2))
    elif args.command == "collect-pilot":
        result = collect_transfermarkt_pilot(
            root / "data/raw/transfermarkt_pilot",
            root / "reports/transfermarkt_pilot.json",
            args.delay_seconds,
        )
        print(json.dumps(result, indent=2))
    elif args.command == "run-all":
        print(json.dumps(run_pipeline(args.source_root, root), indent=2, ensure_ascii=False))
    elif args.command == "run-mvp":
        print(json.dumps(run_pipeline(args.source_root, root, only=args.number), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

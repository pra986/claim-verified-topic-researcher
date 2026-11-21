"""Runnable CLI demo entrypoint for claim-verified topic research."""

from __future__ import annotations

import argparse
import json
from typing import Optional

from topic_researcher.engine import ClaimVerifiedTopicResearcher


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run ClaimVerifiedTopicResearcher in offline or live mode."
    )
    parser.add_argument(
        "--topic",
        default="RBI 2026 UPI Lite offline wallet cap",
        help="Research topic to investigate.",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2026,
        help="Target publication/policy year to retain.",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    researcher = ClaimVerifiedTopicResearcher(target_year=args.year)
    report = researcher.research(topic=args.topic, target_year=args.year)
    print(json.dumps(report.model_dump(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

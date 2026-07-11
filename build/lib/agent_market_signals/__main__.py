"""CLI: scan a JSON file of listings for deceptive marketplace signals.

Usage:
    python -m agent_market_signals path/to/listings.json

The JSON is an array of listing objects; see SCHEMA.md for the fields.
``created_at`` is ISO 8601. Output is a JSON report on stdout; exit code is
1 if any "high"-severity finding was raised, else 0 (useful in CI / cron).
"""

from __future__ import annotations

import json
import sys

from .detectors import Listing, scan


def load_listings(raw: list[dict]) -> list[Listing]:
    return [Listing.from_dict(item) for item in raw]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    with open(argv[1], encoding="utf-8") as fh:
        raw = json.load(fh)
    report = scan(load_listings(raw))
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 1 if report["summary"].get("high", 0) > 0 else 0


def _console() -> None:
    """Entry point for the ``agent-market-signals`` console script."""
    raise SystemExit(main(sys.argv))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

"""Privacy-preserving, opt-in contribution primitive — the safe core of the
"flywheel" (see FLYWHEEL.md).

This turns a local scan into a minimal, non-reversible aggregate *observation*
that a user MAY choose to contribute, so the community can calibrate thresholds
and discover new patterns over time. It is the ONLY thing this project ever
proposes sharing, and it is built so that sharing it leaks nothing:

- No platform is ever named — the data model has no platform field to begin with.
- No listing ids, text, budgets, timestamps, or poster identities are included.
- Only coarse buckets and boolean flags ever leave the machine.
- A k-anonymity floor refuses to emit for samples too small to be safe.

Nothing in this module sends anything anywhere. Producing an observation and
sharing one are separate, explicit, human-controlled acts.
"""

from __future__ import annotations

from typing import Optional

from .detectors import Listing, scan

OBSERVATION_SCHEMA_VERSION = "0.1"

# Below this many listings, an aggregate can start to fingerprint a specific
# small board or moment, so we refuse to produce a shareable observation.
DEFAULT_MIN_SAMPLE = 5


def _sample_size_bucket(n: int) -> str:
    """Coarse bucket instead of an exact count — an exact N is more identifying."""
    if n < 20:
        return "5-19"
    if n < 50:
        return "20-49"
    if n < 100:
        return "50-99"
    if n < 500:
        return "100-499"
    return "500+"


def to_observation(
    listings: list[Listing], min_sample: int = DEFAULT_MIN_SAMPLE
) -> Optional[dict]:
    """Produce a shareable, non-reversible observation, or ``None`` if the
    sample is too small to share safely.

    The returned dict deliberately contains only: a schema version, a bucketed
    sample size, whether views were tracked, which fields were present at all
    (booleans, not counts), and which indicator IDs fired at least once. That
    is enough to learn base rates and tune thresholds across many contributors
    without any single contribution revealing a platform, a listing, or a user.
    """
    if len(listings) < min_sample:
        return None

    report = scan(listings)
    indicators_fired = sorted({f["indicator"] for f in report["findings"]})
    coverage_present = {
        field: info["present"] > 0 for field, info in report["coverage"].items()
    }

    return {
        "schema_version": OBSERVATION_SCHEMA_VERSION,
        "sample_size_bucket": _sample_size_bucket(len(listings)),
        "views_tracked": report["views_tracked"],
        "coverage_present": coverage_present,
        "indicators_fired": indicators_fired,
    }

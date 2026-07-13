"""Canonical thresholds for the integrity detectors — one authoritative place.

Every tunable number a detector uses is defined here, so the values have a
single source instead of being scattered through detector code. :func:`scan`
accepts a :class:`Thresholds` instance and defaults to these values; a caller
who knows their platform can tune them without touching detector logic.

The site's JavaScript port (``docs/boardcheck.js``) mirrors these numbers in its
``THRESHOLDS`` object, and ``tests/test_parity.py`` fails if the two ever drift
apart — so "change it in one place" is enforced across the Python and browser
implementations rather than trusted.

Provenance of the defaults — honest calibration disclosure. These are
field-informed engineering choices, not statistically derived cutoffs; the
project deliberately does not claim a fitted false-positive rate it has not
measured:

- ``self_ad_ratio`` **0.80**: three live boards measured ~95% agent
  self-advertisement; 0.80 sits well under that yet clears ordinary mixed
  boards. Lower it for a stricter read.
- ``budget_multiple`` **3.0**: a budget 3x the platform median is where
  "generous" starts reading as "bait" in the seeded listings observed in the
  field. Raise it on platforms with genuinely wide budget spreads.
- ``min_cluster`` **3** / ``window_seconds`` **1**: three listings sharing a
  one-second creation stamp is already past plausible independent arrival.
  Raise ``window_seconds``/``min_cluster`` on platforms that do legitimate bulk
  imports (which can look identical — a documented known false positive).

Changing a *default* here changes observable behavior and is a minor-version
event per SPEC.md; making them tunable (this module) did not change any default.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Thresholds:
    """Tunable detector thresholds. Instances are immutable; construct a new one
    to override, e.g. ``Thresholds(self_ad_ratio=0.9)``."""

    self_ad_ratio: float = 0.80  # AMS-003 fires at/above this share of self-ads
    budget_multiple: float = 3.0  # AMS-005: budget >= this * median, with 0 views
    min_cluster: int = 3  # AMS-002: this many listings in one window
    window_seconds: int = 1  # AMS-002: width of the batch-creation window

    def __post_init__(self) -> None:
        if not 0.0 < self.self_ad_ratio <= 1.0:
            raise ValueError("self_ad_ratio must be in (0, 1]")
        if self.budget_multiple <= 0:
            raise ValueError("budget_multiple must be > 0")
        if self.min_cluster < 2:
            raise ValueError("min_cluster must be >= 2")
        if self.window_seconds < 1:
            raise ValueError("window_seconds must be >= 1")


#: The canonical defaults, importable without constructing an instance.
DEFAULTS = Thresholds()

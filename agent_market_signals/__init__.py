"""agent_market_signals — detect deceptive signals in AI-agent marketplaces.

Dependency-free toolkit. See README.md for methodology and limitations.
"""

from .detectors import (
    Finding,
    Listing,
    batch_creation_clustering,
    high_budget_bait,
    scan,
    self_advertisement_ratio,
    unpaid_work_risk,
    view_application_inversion,
)

__all__ = [
    "Finding",
    "Listing",
    "batch_creation_clustering",
    "high_budget_bait",
    "scan",
    "self_advertisement_ratio",
    "unpaid_work_risk",
    "view_application_inversion",
]

__version__ = "0.1.0"

"""Detectors for deceptive signals in AI-agent marketplace listings.

Dependency-free (Python standard library only). Each detector operates on
normalized :class:`Listing` records and returns structured :class:`Finding`
objects. The patterns encoded here were observed first-hand while operating an
autonomous agent across live AI-agent marketplaces in the first half of 2026;
see README.md for methodology and honest limitations.

Design rules:
- A detector never invents data. If the fields it needs are absent (``None``),
  it stays silent rather than guessing — absence of evidence is not evidence.
- Findings are advisory signals, not verdicts. They flag patterns a human or a
  downstream system should weigh, and every finding explains its own reasoning.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from statistics import median
from typing import Optional

Severity = str  # "info" | "warn" | "high"


@dataclass
class Listing:
    """A normalized marketplace listing. Unknown fields stay ``None``.

    Only ``id`` and ``created_at`` are required; every signal degrades
    gracefully when the data it needs is missing.
    """

    id: str
    created_at: datetime
    views: Optional[int] = None
    applications: Optional[int] = None
    budget: Optional[float] = None
    poster_type: str = "unknown"  # "human" | "agent" | "unknown"
    is_self_advertisement: Optional[bool] = None
    has_escrow: Optional[bool] = None
    has_payment_evidence: Optional[bool] = None


@dataclass
class Finding:
    indicator: str
    severity: Severity
    detail: str
    listing_id: Optional[str] = None

    def as_dict(self) -> dict:
        return {
            "indicator": self.indicator,
            "severity": self.severity,
            "listing_id": self.listing_id,
            "detail": self.detail,
        }


# --------------------------------------------------------------------------
# Listing-level detectors
# --------------------------------------------------------------------------

def view_application_inversion(listing: Listing) -> Optional[Finding]:
    """Applications that exceed views.

    Applying to a listing ordinarily requires viewing it first, so
    applications should never exceed views. Applications with zero views is
    the starkest case and the one observed on seeded high-budget listings.
    """
    v, a = listing.views, listing.applications
    if v is None or a is None or a <= 0:
        return None
    if v == 0:
        return Finding(
            "view_application_inversion",
            "high",
            f"{a} application(s) with 0 views — applying requires viewing, "
            "so this count is arithmetically implausible and may be fabricated",
            listing.id,
        )
    if a > v:
        return Finding(
            "view_application_inversion",
            "warn",
            f"{a} applications exceed {v} views — anomalous engagement",
            listing.id,
        )
    return None


def unpaid_work_risk(listing: Listing) -> Optional[Finding]:
    """Priced work with neither escrow nor any payment-evidence mechanism.

    When a listing advertises a price but nothing guarantees payment, the
    money depends entirely on the poster's discretion after work is delivered
    — the structure behind accepted-but-unpaid work observed in the field.
    """
    if listing.budget is None or listing.budget <= 0:
        return None
    if listing.has_escrow is False and listing.has_payment_evidence is False:
        return Finding(
            "unpaid_work_risk",
            "warn",
            f"priced ({listing.budget:g}) with no escrow and no payment-evidence "
            "mechanism — payment depends solely on poster discretion after delivery",
            listing.id,
        )
    return None


# --------------------------------------------------------------------------
# Marketplace-level detectors (operate over a collection of listings)
# --------------------------------------------------------------------------

def batch_creation_clustering(
    listings: list[Listing], window_seconds: int = 1, min_cluster: int = 3
) -> list[Finding]:
    """Listings created within the same tight time window.

    Many listings sharing a creation timestamp to the second is a signature of
    automated batch seeding rather than organic, independently-arriving demand.
    """
    if window_seconds < 1:
        raise ValueError("window_seconds must be >= 1")
    buckets: dict[int, list[Listing]] = defaultdict(list)
    for listing in listings:
        bucket = int(listing.created_at.timestamp()) // window_seconds
        buckets[bucket].append(listing)

    findings: list[Finding] = []
    for group in buckets.values():
        if len(group) >= min_cluster:
            ids = ", ".join(sorted(g.id for g in group))
            findings.append(
                Finding(
                    "batch_creation_clustering",
                    "warn",
                    f"{len(group)} listings created within a {window_seconds}s "
                    f"window ({ids}) — consistent with automated seeding",
                )
            )
    return findings


def self_advertisement_ratio(
    listings: list[Listing], threshold: float = 0.8
) -> Optional[Finding]:
    """Share of listings that are agents advertising their own services.

    A board that is overwhelmingly agents marketing themselves — rather than
    buyers offering work — is a supply glut presented as demand. The ratio is
    computed only over listings whose type is known.
    """
    known = [l for l in listings if l.is_self_advertisement is not None]
    if not known:
        return None
    ratio = sum(1 for l in known if l.is_self_advertisement) / len(known)
    if ratio >= threshold:
        return Finding(
            "self_advertisement_ratio",
            "high",
            f"{ratio:.0%} of listings are agent self-advertisements (n={len(known)}) "
            "— supply glut marketed as demand",
        )
    return None


def high_budget_bait(
    listings: list[Listing], budget_multiple: float = 3.0
) -> list[Finding]:
    """Far-above-median budgets that have drawn zero views.

    A budget many times the platform norm that no one has viewed is bait: the
    large number attracts applicants while the zero views show no real buyer
    engagement. Needs at least three budgeted listings to establish a median.
    """
    budgets = [l.budget for l in listings if l.budget and l.budget > 0]
    if len(budgets) < 3:
        return []
    med = median(budgets)
    if med <= 0:
        return []

    findings: list[Finding] = []
    for listing in listings:
        if (
            listing.budget
            and listing.budget >= budget_multiple * med
            and listing.views == 0
        ):
            findings.append(
                Finding(
                    "high_budget_bait",
                    "warn",
                    f"budget {listing.budget:g} is >={budget_multiple:g}x the platform "
                    f"median ({med:g}) with 0 views — seeded high-budget bait",
                    listing.id,
                )
            )
    return findings


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

def scan(listings: list[Listing]) -> dict:
    """Run every detector and return findings plus a severity summary."""
    findings: list[Finding] = []

    for listing in listings:
        for detector in (view_application_inversion, unpaid_work_risk):
            result = detector(listing)
            if result is not None:
                findings.append(result)

    findings.extend(batch_creation_clustering(listings))
    ratio = self_advertisement_ratio(listings)
    if ratio is not None:
        findings.append(ratio)
    findings.extend(high_budget_bait(listings))

    summary = {"info": 0, "warn": 0, "high": 0}
    for finding in findings:
        summary[finding.severity] = summary.get(finding.severity, 0) + 1

    return {
        "listings_scanned": len(listings),
        "findings": [f.as_dict() for f in findings],
        "summary": summary,
    }

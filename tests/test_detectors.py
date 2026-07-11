"""Tests for the deceptive-signal detectors. Stdlib unittest — no deps.

Run:  python -m unittest discover -s tests
"""

import unittest
from datetime import datetime, timedelta

from agent_market_signals import detectors as d
from agent_market_signals.detectors import Listing

BASE = datetime(2026, 1, 14, 12, 0, 0)


def L(id, **kw):
    return Listing(id=id, created_at=kw.pop("created_at", BASE), **kw)


class TestViewApplicationInversion(unittest.TestCase):
    def test_applications_with_zero_views_is_high(self):
        f = d.view_application_inversion(L("a", views=0, applications=22))
        self.assertIsNotNone(f)
        self.assertEqual(f.severity, "high")

    def test_applications_exceed_views_is_warn(self):
        f = d.view_application_inversion(L("a", views=3, applications=10))
        self.assertEqual(f.severity, "warn")

    def test_normal_engagement_is_silent(self):
        # Many views, few applications — the ordinary, healthy shape.
        self.assertIsNone(d.view_application_inversion(L("a", views=100, applications=4)))

    def test_missing_data_is_silent(self):
        self.assertIsNone(d.view_application_inversion(L("a", views=None, applications=5)))
        self.assertIsNone(d.view_application_inversion(L("a", views=0, applications=0)))


class TestUnpaidWorkRisk(unittest.TestCase):
    def test_priced_without_escrow_or_evidence_flags(self):
        f = d.unpaid_work_risk(
            L("a", budget=6.0, has_escrow=False, has_payment_evidence=False)
        )
        self.assertEqual(f.severity, "warn")

    def test_escrow_present_is_silent(self):
        self.assertIsNone(
            d.unpaid_work_risk(
                L("a", budget=6.0, has_escrow=True, has_payment_evidence=False)
            )
        )

    def test_unknown_payment_fields_are_silent(self):
        # None (unknown) must not be treated as False (known-absent).
        self.assertIsNone(d.unpaid_work_risk(L("a", budget=6.0)))

    def test_no_budget_is_silent(self):
        self.assertIsNone(
            d.unpaid_work_risk(L("a", has_escrow=False, has_payment_evidence=False))
        )


class TestBatchCreationClustering(unittest.TestCase):
    def test_same_second_cluster_flags(self):
        listings = [L(f"n{i}", created_at=BASE) for i in range(6)]
        findings = d.batch_creation_clustering(listings)
        self.assertEqual(len(findings), 1)
        self.assertIn("6 listings", findings[0].detail)

    def test_spread_out_listings_are_silent(self):
        listings = [
            L(f"n{i}", created_at=BASE + timedelta(hours=i)) for i in range(6)
        ]
        self.assertEqual(d.batch_creation_clustering(listings), [])

    def test_below_min_cluster_is_silent(self):
        listings = [L(f"n{i}", created_at=BASE) for i in range(2)]
        self.assertEqual(d.batch_creation_clustering(listings), [])


class TestSelfAdvertisementRatio(unittest.TestCase):
    def test_high_self_ad_ratio_flags(self):
        listings = [L(f"ad{i}", is_self_advertisement=True) for i in range(9)]
        listings.append(L("job", is_self_advertisement=False))
        f = d.self_advertisement_ratio(listings)
        self.assertEqual(f.severity, "high")
        self.assertIn("90%", f.detail)

    def test_balanced_board_is_silent(self):
        listings = [L(f"ad{i}", is_self_advertisement=True) for i in range(3)]
        listings += [L(f"job{i}", is_self_advertisement=False) for i in range(7)]
        self.assertIsNone(d.self_advertisement_ratio(listings))

    def test_all_unknown_is_silent(self):
        listings = [L(f"n{i}") for i in range(5)]
        self.assertIsNone(d.self_advertisement_ratio(listings))


class TestHighBudgetBait(unittest.TestCase):
    def test_far_above_median_zero_views_flags(self):
        listings = [L(f"norm{i}", budget=10.0, views=5) for i in range(5)]
        listings.append(L("bait", budget=2000.0, views=0))
        findings = d.high_budget_bait(listings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].listing_id, "bait")

    def test_high_budget_with_views_is_silent(self):
        listings = [L(f"norm{i}", budget=10.0, views=5) for i in range(5)]
        listings.append(L("real", budget=2000.0, views=40))
        self.assertEqual(d.high_budget_bait(listings), [])

    def test_too_few_budgets_for_median_is_silent(self):
        listings = [L("a", budget=2000.0, views=0)]
        self.assertEqual(d.high_budget_bait(listings), [])


class TestScan(unittest.TestCase):
    def test_scan_aggregates_and_summarizes(self):
        listings = [L(f"ad{i}", is_self_advertisement=True) for i in range(9)]
        listings.append(L("bait", views=0, applications=20, budget=2000.0,
                          has_escrow=False, has_payment_evidence=False))
        listings += [L(f"n{i}", budget=10.0, views=5) for i in range(3)]
        report = d.scan(listings)
        self.assertEqual(report["listings_scanned"], len(listings))
        self.assertGreater(report["summary"]["high"], 0)
        indicators = {f["indicator"] for f in report["findings"]}
        self.assertIn("view_application_inversion", indicators)
        self.assertIn("self_advertisement_ratio", indicators)


if __name__ == "__main__":
    unittest.main()

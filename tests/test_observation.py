"""Tests for the privacy-preserving observation primitive.

The critical tests here are the *negative* ones: they assert that identifying
information can never appear in a shared observation, even when it is present in
the input.
"""

import json
import unittest
from datetime import datetime

from agent_market_signals import to_observation
from agent_market_signals.detectors import Listing

BASE = datetime(2026, 1, 14, 12, 0, 0)


def L(id, **kw):
    return Listing(id=id, created_at=kw.pop("created_at", BASE), **kw)


class TestObservationPrivacy(unittest.TestCase):
    def test_small_sample_is_refused(self):
        listings = [L(f"n{i}") for i in range(4)]  # below the k-anonymity floor
        self.assertIsNone(to_observation(listings))

    def test_observation_contains_no_identifiers(self):
        # Load identifying-looking values into the input, then prove none of
        # them survive into the shared observation.
        secret_id = "super-secret-platform-listing-9999"
        secret_budget = 424242.42
        secret_ts = datetime(2019, 3, 7, 8, 30, 0)
        listings = [
            L(
                secret_id,
                created_at=secret_ts,
                views=0,
                applications=25,
                budget=secret_budget,
                has_escrow=False,
                has_payment_evidence=False,
            )
        ]
        listings += [L(f"n{i}", views=3, applications=1) for i in range(9)]

        obs = to_observation(listings)
        blob = json.dumps(obs)
        self.assertNotIn(secret_id, blob)
        self.assertNotIn("424242", blob)
        self.assertNotIn("2019", blob)
        # And the exact sample size is bucketed, not verbatim.
        self.assertNotIn(str(len(listings)), obs.get("sample_size_bucket", ""))

    def test_observation_shape_is_minimal(self):
        listings = [L(f"n{i}", views=10, applications=2) for i in range(10)]
        obs = to_observation(listings)
        self.assertEqual(
            set(obs.keys()),
            {
                "schema_version",
                "sample_size_bucket",
                "views_tracked",
                "coverage_present",
                "indicators_fired",
            },
        )
        # coverage_present must be booleans (presence), never counts.
        self.assertTrue(all(isinstance(v, bool) for v in obs["coverage_present"].values()))

    def test_observation_reports_fired_indicators(self):
        # Give the ads real view counts so views are inferred tracked platform-wide;
        # then the zero-view job legitimately trips the inversion indicator.
        listings = [L(f"ad{i}", views=7, is_self_advertisement=True) for i in range(9)]
        listings.append(L("job", views=0, applications=20, is_self_advertisement=False))
        obs = to_observation(listings)
        self.assertIn("self_advertisement_ratio", obs["indicators_fired"])
        self.assertIn("view_application_inversion", obs["indicators_fired"])


if __name__ == "__main__":
    unittest.main()

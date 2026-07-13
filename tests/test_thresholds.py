"""The detector thresholds are tunable via a Thresholds override, with the
field-informed values as defaults. The parity test only exercises the defaults
(the site ships them), so these cover the tuning path itself."""

import unittest
from datetime import datetime, timezone

from agent_market_signals import Listing, Thresholds, scan

_TS = datetime(2026, 3, 1, 10, 0, 0, tzinfo=timezone.utc)


def _ids(report):
    return {f["id"] for f in report["findings"]}


class ThresholdsTest(unittest.TestCase):
    def test_min_cluster_tuning_changes_batch_finding(self):
        listings = [Listing(id=f"c{i}", created_at=_TS) for i in range(3)]
        self.assertIn("AMS-002", _ids(scan(listings)))  # default min_cluster=3
        self.assertNotIn("AMS-002", _ids(scan(listings, Thresholds(min_cluster=4))))

    def test_self_ad_ratio_tuning(self):
        # 3 of 4 known are self-ads = 0.75: below the 0.80 default, above 0.70.
        listings = [
            Listing(
                id=f"a{i}",
                created_at=datetime(2026, 3, 1, 10, i, 0, tzinfo=timezone.utc),
                is_self_advertisement=(i < 3),
            )
            for i in range(4)
        ]
        self.assertNotIn("AMS-003", _ids(scan(listings)))
        self.assertIn("AMS-003", _ids(scan(listings, Thresholds(self_ad_ratio=0.70))))

    def test_defaults_are_the_documented_values(self):
        d = Thresholds()
        self.assertEqual(
            (d.self_ad_ratio, d.budget_multiple, d.min_cluster, d.window_seconds),
            (0.80, 3.0, 3, 1),
        )

    def test_invalid_thresholds_rejected(self):
        for bad in (
            {"self_ad_ratio": 0},
            {"self_ad_ratio": 1.5},
            {"budget_multiple": 0},
            {"min_cluster": 1},
            {"window_seconds": 0},
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    Thresholds(**bad)


if __name__ == "__main__":
    unittest.main()

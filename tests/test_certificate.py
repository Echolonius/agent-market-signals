import unittest
from datetime import datetime, timezone
from agent_market_signals import Listing, scan, generate_certificate, upfront_fee_gating


class TestCertificateAndIndicators(unittest.TestCase):
    def test_upfront_fee_gating_detector(self):
        listing_bad = Listing(
            id="job-fee-1",
            created_at=datetime.now(timezone.utc),
            requires_upfront_fee=True,
            has_escrow=False,
        )
        finding = upfront_fee_gating(listing_bad)
        self.assertIsNotNone(finding)
        self.assertEqual(finding.indicator, "upfront_fee_gating")
        self.assertEqual(finding.severity, "high")

        listing_good = Listing(
            id="job-fee-2",
            created_at=datetime.now(timezone.utc),
            requires_upfront_fee=True,
            has_escrow=True,
        )
        self.assertIsNone(upfront_fee_gating(listing_good))

    def test_generate_certificate(self):
        listings = [
            Listing(id="1", created_at=datetime.now(timezone.utc), views=10, applications=1, has_escrow=True)
        ]
        scan_res = scan(listings)
        cert = generate_certificate(scan_res, platform_name="TestMarketplace")

        self.assertEqual(cert["platform_name"], "TestMarketplace")
        self.assertTrue(cert["is_compliant"])
        self.assertIn("BC-CERT-", cert["certificate_id"])
        self.assertIn("markdown", cert["badge"])
        self.assertIn("html", cert["badge"])


if __name__ == "__main__":
    unittest.main()

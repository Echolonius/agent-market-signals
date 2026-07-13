"""Guards for the two library<->site divergences an adversarial review surfaced:
host-independent timestamp parsing, and number/percent rendering that matches the
JavaScript port. The parity test runs in UTC on CI, so the timezone guarantee in
particular needs an explicit, host-independent check here."""

import unittest
from datetime import datetime, timezone

from agent_market_signals.detectors import _num, _pct, parse_created_at


class ParseCreatedAtTest(unittest.TestCase):
    def test_naive_and_dateonly_are_utc(self):
        expected = datetime(2026, 3, 1, tzinfo=timezone.utc)
        self.assertEqual(parse_created_at("2026-03-01"), expected)
        self.assertEqual(parse_created_at("2026-03-01T00:00:00"), expected)
        self.assertEqual(parse_created_at("2026-03-01T00:00:00Z"), expected)
        # Same absolute instant no matter the host timezone.
        self.assertEqual(
            parse_created_at("2026-03-01").timestamp(),
            parse_created_at("2026-03-01T00:00:00Z").timestamp(),
        )

    def test_explicit_offset_is_respected(self):
        # 2026-03-01T00:00:00+05:00 is 2026-02-28T19:00:00Z
        self.assertEqual(
            parse_created_at("2026-03-01T00:00:00+05:00"),
            datetime(2026, 2, 28, 19, tzinfo=timezone.utc),
        )


class RenderTest(unittest.TestCase):
    def test_num_matches_js_number_rendering(self):
        self.assertEqual(_num(5000000), "5000000")  # not "5e+06"
        self.assertEqual(_num(2500.0), "2500")
        self.assertEqual(_num(40), "40")
        self.assertEqual(_num(1234567.89), "1234567.89")
        self.assertEqual(_num(3.0), "3")
        self.assertEqual(_num(2.5), "2.5")

    def test_pct_is_half_up(self):
        self.assertEqual(_pct(33 / 40), 83)  # 82.5% -> 83 (JS Math.round), not 82
        self.assertEqual(_pct(7 / 8), 88)  # 87.5% -> 88
        self.assertEqual(_pct(1.0), 100)
        self.assertEqual(_pct(0.804), 80)


if __name__ == "__main__":
    unittest.main()

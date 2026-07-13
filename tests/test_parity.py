"""Cross-implementation parity: the browser detector (docs/boardcheck.js) must
produce the same findings as the Python reference (agent_market_signals.scan),
and the site's threshold constants must equal the Python defaults.

This is the guardrail behind "change it across everything correlated": if the
JS port and the Python reference ever diverge — an edited threshold, a changed
comparison, a dropped suppression — a case here fails and CI goes red. The
fixtures live in parity_fixtures.json and are shared by both runners.

If Node.js is not installed the JS half is skipped (so the pure-Python suite
still runs anywhere); CI installs Node so the check is real there.
"""

import json
import shutil
import subprocess
import unittest
from pathlib import Path

from agent_market_signals import DEFAULTS, Listing, scan

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
_FIXTURES = _HERE / "parity_fixtures.json"
_RUNNER = _HERE / "parity_runner.js"


def _py_canon(listings: list) -> dict:
    r = scan([Listing.from_dict(x) for x in listings])
    return {
        "verdict": r["verdict"],
        "views_tracked": r["views_tracked"],
        "summary": {k: r["summary"][k] for k in ("info", "warn", "high")},
        "findings": sorted(
            (f["id"], f["severity"], f["listing_id"], f["detail"])
            for f in r["findings"]
        ),
        "coverage": r["coverage"],
    }


class ParityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.node = shutil.which("node")
        cls.fixtures = json.loads(_FIXTURES.read_text())
        cls.js = None
        if cls.node:
            proc = subprocess.run(
                [cls.node, str(_RUNNER)], capture_output=True, text=True
            )
            if proc.returncode != 0:
                raise AssertionError(
                    "node parity_runner.js failed:\n" + proc.stderr
                )
            cls.js = json.loads(proc.stdout)

    def test_findings_parity(self) -> None:
        if not self.node:
            self.skipTest("node not found; browser-port parity not checked here")
        for case in self.fixtures["cases"]:
            name = case["name"]
            with self.subTest(case=name):
                py = _py_canon(case["listings"])
                raw = self.js[name]
                js = {
                    "verdict": raw["verdict"],
                    "views_tracked": raw["views_tracked"],
                    "summary": raw["summary"],
                    "findings": sorted(tuple(t) for t in raw["findings"]),
                    "coverage": raw["coverage"],
                }
                self.assertEqual(
                    py, js, f"Python/JS parity mismatch on case '{name}'"
                )

    def test_threshold_constants_match(self) -> None:
        if not self.node:
            self.skipTest("node not found; threshold-constant sync not checked here")
        jt = self.js["__thresholds"]
        self.assertEqual(jt["selfAdRatio"], DEFAULTS.self_ad_ratio)
        self.assertEqual(jt["budgetMultiple"], DEFAULTS.budget_multiple)
        self.assertEqual(jt["minCluster"], DEFAULTS.min_cluster)
        self.assertEqual(jt["windowSeconds"], DEFAULTS.window_seconds)


if __name__ == "__main__":
    unittest.main()

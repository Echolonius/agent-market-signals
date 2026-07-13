"use strict";
/* Runs the shared parity fixtures through docs/boardcheck.js and prints one
 * canonical JSON blob on stdout. tests/test_parity.py consumes it and compares
 * against the Python reference. Findings are emitted as [indicator, severity,
 * listing_id, detail] tuples — detail (the human-readable text) is included so
 * the site and the library are checked to render identical numbers/percentages,
 * not just the same finding identity. The Python side sorts both, so emission
 * order here does not matter. */
const path = require("path");
const bc = require(path.join(__dirname, "..", "docs", "boardcheck.js"));
const fixtures = require(path.join(__dirname, "parity_fixtures.json"));

function canon(r) {
  return {
    verdict: r.verdict,
    views_tracked: r.viewsTracked,
    summary: { info: r.summary.info, warn: r.summary.warn, high: r.summary.high },
    findings: r.findings.map(f => [f.i, f.s, f.id === undefined ? null : f.id, f.d]),
    coverage: r.coverage
  };
}

const out = { __thresholds: bc.THRESHOLDS };
for (const c of fixtures.cases) out[c.name] = canon(bc.scan(c.listings));
process.stdout.write(JSON.stringify(out));

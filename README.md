# agent-market-signals

**A dependency-free toolkit for detecting deceptive signals in AI-agent marketplaces.**

Agent marketplaces — where AI agents advertise services, bid on work, and get paid — are
growing fast, and so is the noise inside them: job boards that are mostly agents advertising
*themselves*, listings showing dozens of "applications" that nobody has viewed, priced work
that gets delivered and never paid. This library turns those patterns into small, auditable,
runnable checks so an agent operator, a marketplace, or a researcher can measure them instead
of guessing.

It encodes patterns observed first-hand while operating an autonomous agent across several
live marketplaces in the first half of 2026. The field notes behind it are written up in
[FIELD-REPORT](https://github.com/Echolonius/the-penniless-agent/blob/main/FIELD-REPORT-agent-marketplace-deception.md).

## What it checks

| Indicator | Fires when | Why it matters |
|---|---|---|
| `view_application_inversion` | applications exceed views (starkest: >0 applications, 0 views) | you must view a listing to apply, so this is arithmetically implausible — a sign of fabricated engagement |
| `batch_creation_clustering` | many listings share a creation timestamp to the second | signature of automated seeding, not organic demand |
| `self_advertisement_ratio` | most listings are agents advertising their own services | a supply glut presented to newcomers as demand |
| `unpaid_work_risk` | priced work with no escrow and no payment-evidence mechanism | payment depends entirely on poster discretion after delivery |
| `high_budget_bait` | a budget far above the platform median with zero views | a big number that attracts applicants while no real buyer is engaged |

Every check **stays silent when the data it needs is missing** — absence of evidence is never
treated as evidence. Findings are advisory signals for a human or a downstream system to weigh,
not verdicts, and each one explains its own reasoning.

## Install

No dependencies, no install step — Python 3.9+ standard library only. Clone and use.

## Use it as a library

```python
from datetime import datetime
from agent_market_signals import Listing, scan

listings = [
    Listing(id="job-1", created_at=datetime.fromisoformat("2026-01-14T12:00:00"),
            views=0, applications=24, budget=2500.0,
            has_escrow=False, has_payment_evidence=False),
    # ...
]
report = scan(listings)
print(report["summary"])          # {"info": 0, "warn": 1, "high": 1}
for f in report["findings"]:
    print(f["severity"], f["indicator"], f["detail"])
```

## Use it from the command line

```bash
python -m agent_market_signals examples/sample_listings.json
```

Prints a JSON report and exits `1` if any high-severity finding was raised (handy in CI or a
cron watcher), else `0`.

## Data format

Listings are normalized records; only `id` and `created_at` are required, and every other
field may be omitted (the relevant checks simply won't run). See [SCHEMA.md](SCHEMA.md).

## Honest scope and limitations

- **These are heuristics, not proof.** They flag patterns worth a human's attention. A flagged
  listing is not proven fraudulent, and an unflagged one is not proven clean.
- **It measures signals, it does not rank models.** This is deliberately *not* a benchmark of
  GPT / Claude / Gemini / Llama agents. A credible benchmark needs longitudinal, reproducible
  measurement; this toolkit is a piece of the data substrate one could build toward, not the
  benchmark itself. We would rather ship something true and small than something impressive and
  fabricated.
- **The thresholds are defaults, not laws.** `self_advertisement_ratio`'s 80%, `high_budget_bait`'s
  3× median, and the rest are starting points; tune them to your platform and say so when you do.
- **Contributions welcome.** New indicators grounded in real, describable observations — and
  counter-examples that show a detector is too aggressive — are equally valuable.

## Why this exists

The rules and norms for agent commerce are being written right now — by standards bodies,
platforms, and regulators — largely without ground truth from inside the marketplaces. Making
the deceptive patterns cheap to detect is a small way to push the ecosystem toward one where
honest signals are the default, so ordinary people can eventually trust an agent to do real
work and actually get paid. Free to use and quote with attribution.

## License

MIT — see [LICENSE](LICENSE).

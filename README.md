# agent-market-signals

**An open standard — and a dependency-free reference implementation — for auditing the
integrity of AI-agent marketplaces.**

Agent marketplaces — where AI agents advertise services, bid on work, and get paid — are
growing fast, and so is the noise inside them: job boards that are mostly agents advertising
*themselves*, listings showing dozens of "applications" that nobody has viewed, priced work
that gets delivered and never paid. This project turns those patterns into small, precise,
citable checks that **anyone on any side of the market can call upon** — a marketplace proving
its own board is clean, a buyer's agent vetting where to spend, a seller's agent deciding where
to work, a third-party auditor, a researcher, or a solo user who just told their agent to go
find work and wants to avoid the traps.

Two layers, so it is useful as more than a script:

- **[SPEC.md](SPEC.md)** — an implementation-neutral specification with stable indicator IDs
  (`AMS-001` … `AMS-005`) anyone can implement in any language or cite by ID.
- **This package** — a reference implementation of the spec in dependency-free Python.

It encodes patterns observed first-hand while operating an autonomous agent across several
live marketplaces in the first half of 2026. The field notes behind it are written up in the
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

Each indicator carries a stable ID so it can be cited precisely (e.g. "AMS-004 unpaid-work
risk"); the full definitions, severities, and known false positives live in [SPEC.md](SPEC.md).

## Install

No third-party dependencies — Python 3.9+ standard library only. Install straight from GitHub
(no package-registry account involved):

```bash
pip install git+https://github.com/Echolonius/agent-market-signals
```

Or just clone the repo and use it in place.

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
print(report["coverage"])         # how many listings carried each field
for f in report["findings"]:
    print(f["severity"], f["indicator"], f["detail"])
```

The report includes a `coverage` map (how many listings carried each field) and a
`views_tracked` flag, so an auditor can see how much was actually assessable — a clean scan of
sparse data is not a clean bill of health.

## Use it from the command line

```bash
python -m agent_market_signals examples/sample_listings.json
```

Prints a JSON report and exits `1` if any high-severity finding was raised (handy in CI or a
cron watcher), else `0`.

## Data format

Listings are normalized records; only `id` and `created_at` are required, and every other
field may be omitted (the relevant checks simply won't run). See [SCHEMA.md](SCHEMA.md).

## Improving over time (optional, privacy-first)

The checks get sharper as more people run them — but only through a design that never phones home
and never leaks anything. Running a scan sends nothing anywhere. *If* a user opts in, a minimal,
non-reversible summary (`to_observation()` — coarse buckets and boolean flags, no platform, no
listings, no identity) can be contributed via an ordinary pull request and reviewed by a human, so
thresholds can be tuned to reality and new patterns discovered without any automatic, poisonable,
data-hungry pipeline. The full design — including what we deliberately refuse to build — is in
[FLYWHEEL.md](FLYWHEEL.md).

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

## How this fits with existing work

The agent-trust space is active, and this project deliberately occupies a narrow, specific
niche rather than competing with the heavyweight efforts. Being honest about that is the point:

- **[ERC-8004](https://blog.thirdweb.com/erc-8004-explained-the-ethereum-standard-that-gives-ai-agents-on-chain-identity/)**
  (Ethereum Foundation, Google, Coinbase, MetaMask; mainnet Jan 2026) gives agents on-chain
  **identity and reputation registries** — it answers *"is this counterparty trustworthy?"* It is
  blockchain-based and about the agents. This project is orthogonal and complementary: it answers
  *"are this marketplace's own published signals honest?"*, needs no blockchain, and runs on any
  listing data. Its findings could *feed* a reputation system like ERC-8004; it does not replace one.
- **Agent Bazaar** and **Magentic Marketplace** (academic / Microsoft Research) are **simulation
  environments** for studying agentic markets. Agent Bazaar notably models "Sybil Deception"
  (deceptive agents flooding a market with fraudulent listings) and proposes detector agents.
  Those are research frameworks; this is a small, deployable implementation of similar detection
  ideas, grounded in first-hand field observation rather than simulation.
- **Fake-job-posting ML classifiers** target the human job market with models trained on listing
  text. This is agent-marketplace-specific, uses transparent arithmetic (not an opaque model), and
  is auditable line by line.

**Honest positioning:** the underlying *ideas* are not unprecedented — coordinated-listing / Sybil
detection appears in the research literature. What this adds is a *citable, implementation-neutral
specification* plus a *tiny, transparent, dependency-free, blockchain-free reference implementation*
that an operator can adopt in minutes and an agent can call at decision time. It is the "audit the
board's own signals" layer, complementary to the "identify and score the agents" layer the large
standards are building.

## Why this exists

The rules and norms for agent commerce are being written right now — by standards bodies,
platforms, and regulators — largely without ground truth from inside the marketplaces. Making
the deceptive patterns cheap to detect is a small way to push the ecosystem toward one where
honest signals are the default, so ordinary people can eventually trust an agent to do real
work and actually get paid. Free to use and quote with attribution.

## License

MIT — see [LICENSE](LICENSE).

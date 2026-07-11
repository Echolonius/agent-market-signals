# Agent Marketplace Integrity Signals — Specification v0.2

An open, implementation-neutral specification for detecting deceptive signals in
AI-agent marketplaces. Anyone — a marketplace operator, a buyer's or seller's agent,
a third-party auditor, a researcher, or a solo user telling their agent "go find me
work" — can implement or cite this specification to reason about marketplace integrity
in a shared vocabulary.

This document defines *what* the indicators are. The Python package in this repository
is a **reference implementation**; it is not the specification, and conforming
implementations may exist in any language.

## Status and scope

- **Version:** 0.2 (pre-1.0; indicator IDs are stable, thresholds and wording may change).
- **These are heuristics, not proof.** An indicator flags a pattern that merits human or
  system attention. A flagged listing is not proven deceptive; an unflagged one is not
  proven honest. Conforming implementations MUST NOT present findings as verdicts.
- **Neutral by design.** The specification names no platforms and endorses no parties. It
  describes patterns detectable from data a marketplace already publishes.

## Data model

A **listing** is a record with the following fields. Only `id` and `created_at` are
required; any other field MAY be absent, and indicators that need an absent field simply
do not run. For boolean fields, absent means *unknown* and MUST NOT be treated as `false`.

| Field | Type | Meaning |
|---|---|---|
| `id` | string | stable identifier |
| `created_at` | timestamp (ISO 8601) | creation time |
| `views` | integer | times viewed |
| `applications` | integer | applications/bids received |
| `budget` | number | advertised price |
| `poster_type` | `human` \| `agent` \| `unknown` | who posted |
| `is_self_advertisement` | boolean | listing is an agent marketing itself, not a buyer offering work |
| `has_escrow` | boolean | funds escrowed before work begins |
| `has_payment_evidence` | boolean | platform provides a verifiable record that priced work gets paid |

## Severity

`info` (context), `warn` (anomalous, weigh it), `high` (arithmetically implausible or
structurally exposed). Implementations MAY map these to their own scales but MUST preserve
the relative ordering.

## Environmental inference

Before evaluating listing-level indicators, an implementation SHOULD infer **`views_tracked`**:
true if any listing carries a positive view count. When false, the platform is presumed not
to expose views, and indicators whose logic depends on a zero-view reading (AMS-001 zero-view
case, AMS-005) MUST be suppressed to avoid a systematic false positive.

## Indicators

### AMS-001 — view/application inversion
**Fires when** applications exceed views. **`high`** when applications > 0 and views = 0
(and `views_tracked`); **`warn`** when applications > views > 0.
**Rationale:** applying ordinarily requires viewing, so applications cannot exceed views;
the inversion suggests fabricated engagement.
**Known false positives:** platforms that do not track views (handled by `views_tracked`);
bulk application imports.

### AMS-002 — batch creation clustering
**Fires when** a number of listings (default ≥ 3) share a creation timestamp within a tight
window (default 1 second). Severity `warn`.
**Rationale:** organic demand arrives independently; many listings created in the same second
indicate automated seeding.
**Known false positives:** legitimate bulk imports or platform migrations. Tunable via window
and minimum-cluster size.

### AMS-003 — self-advertisement ratio
**Fires when** the share of listings that are agent self-advertisements meets or exceeds a
threshold (default 80%), computed only over listings whose type is known. Severity `high`.
**Rationale:** a board that is overwhelmingly agents marketing themselves is a supply glut
presented to newcomers as demand.
**Known false positives:** directories that are explicitly agent catalogs (context-dependent;
tune or disable there).

### AMS-004 — unpaid-work risk
**Fires when** a listing advertises a positive budget while `has_escrow` and
`has_payment_evidence` are both explicitly `false`. Severity `warn`.
**Rationale:** priced work with no payment guarantee depends entirely on poster discretion
after delivery — the structure behind accepted-but-unpaid work.
**Known false positives:** none inherent; requires both fields to be known-false, not unknown.

### AMS-005 — high-budget bait
**Fires when** a listing's budget is at least a multiple (default 3×) of the platform median
budget and has zero views (requires `views_tracked` and ≥ 3 budgeted listings for a median).
Severity `warn`.
**Rationale:** a far-above-norm budget nobody has viewed attracts applicants while showing no
real buyer engagement.
**Known false positives:** genuinely large, newly-posted, not-yet-viewed listings; tune the
multiple to the platform.

## Conformance

An implementation conforms to v0.2 if it: (1) accepts listings in the data model above,
treating absent fields as unknown; (2) emits findings tagged with these indicator IDs and the
severity ordering; (3) performs the `views_tracked` suppression; and (4) presents findings as
advisory signals, not verdicts. Implementations MAY add their own indicators under a distinct
namespace.

## Related work

This specification is complementary to, not competitive with, agent **identity and reputation**
standards such as ERC-8004 (which score the trustworthiness of counterparties). Those ask "is this
agent trustworthy?"; this asks "are this marketplace's published signals honest?" The two compose:
integrity findings defined here can inform a reputation layer. Coordinated-listing / Sybil detection
also appears in academic frameworks (e.g. Agent Bazaar, Magentic Marketplace); this specification's
contribution is a deployable, implementation-neutral, dependency-free formalization grounded in field
observation. See the repository README for a fuller comparison.

## Evolution

Indicator IDs are stable and will not be reused. New indicators receive new IDs. Threshold and
wording changes are minor versions; removing or redefining an indicator is a major version. New
indicators must be grounded in real, describable observations, and counter-examples that show an
indicator is too aggressive are equally welcome — propose either via a repository issue or pull
request.

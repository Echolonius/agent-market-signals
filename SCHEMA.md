# Listing schema

A listing is a JSON object. Only `id` and `created_at` are required; every other field is
optional, and any check that needs a missing field simply does not run for that listing.

| Field | Type | Required | Meaning |
|---|---|---|---|
| `id` | string | yes | Stable identifier for the listing. |
| `created_at` | string (ISO 8601) | yes | When the listing was created. A trailing `Z` (UTC) is accepted. |
| `views` | integer | no | How many times the listing has been viewed. |
| `applications` | integer | no | How many applications/bids the listing has received. |
| `budget` | number | no | Advertised budget/price for the work. |
| `poster_type` | string | no | `"human"`, `"agent"`, or `"unknown"` (default). |
| `is_self_advertisement` | boolean | no | `true` if the listing is an agent advertising its own services rather than a buyer offering work. |
| `has_escrow` | boolean | no | Whether funds are escrowed before work begins. |
| `has_payment_evidence` | boolean | no | Whether the platform provides any verifiable record that priced work gets paid. |

**Unknown vs. false matters.** For boolean fields, `null`/omitted means *unknown* and is never
treated as `false`. For example, `unpaid_work_risk` fires only when escrow and payment-evidence
are both explicitly `false` — not when they are simply unrecorded.

## Example

```json
{
  "id": "job-1",
  "created_at": "2026-01-14T12:00:00Z",
  "views": 0,
  "applications": 24,
  "budget": 2500.0,
  "poster_type": "human",
  "is_self_advertisement": false,
  "has_escrow": false,
  "has_payment_evidence": false
}
```

See [`examples/sample_listings.json`](examples/sample_listings.json) for a full synthetic set.

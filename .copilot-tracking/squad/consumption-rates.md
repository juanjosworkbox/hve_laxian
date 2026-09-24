---
description: "Per-model token rates, dispatch-size estimator, and calibration factor for squad consumption estimates"
---

# Consumption Rates (verify against the current GitHub Copilot "Models and pricing" docs)

* Billing model: usage-based billing (UBB), token-metered, effective 2026-06-01.
* Observed-on: 2026-09-24. Source: https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing
* Credit conversion: 1 AI credit = $0.01 USD (fixed).
* All rates are USD per 1M tokens. Anthropic models bill a separate cache-write rate on top of cached input; models without one leave the column at 0.

## Per-model token rates in USD per 1M tokens (volatile, verify before commit)

| Model (as routed) | Tier     | Input | Cached | Cache write | Output | Notes                      |
| ----------------- | -------- | ----- | ------ | ----------- | ------ | -------------------------- |
| GPT-5.4 nano      | fast     | 0.20  | 0.02   | 0           | 1.25   | lightweight, read-heavy    |
| GPT-5.4 mini      | fast     | 0.75  | 0.075  | 0           | 4.50   | lightweight                |
| Claude Haiku 4.5  | fast     | 1.00  | 0.10   | 1.25        | 5.00   | lightweight reasoning      |
| Claude Sonnet 4.6 | default  | 3.00  | 0.30   | 3.75        | 15.00  | versatile                  |
| Claude Sonnet 5   | default  | 2.00  | 0.20   | 2.50        | 10.00  | versatile (promo pricing)  |
| GPT-5.4           | default  | 2.50  | 0.25   | 0           | 15.00  | versatile                  |
| Gemini 3.1 Pro    | default  | 2.00  | 0.20   | 0           | 12.00  | versatile                  |
| Claude Opus 4.8   | extended | 5.00  | 0.50   | 6.25        | 25.00  | high-capability reasoning  |
| Claude Opus 5     | extended | 5.00  | 0.50   | 6.25        | 25.00  | high-capability reasoning  |
| GPT-5.5           | extended | 5.00  | 0.50   | 0           | 30.00  | high-capability reasoning  |
| (additional)      |          |       |        |             |        | update when GitHub changes |

## Tier fallback rates (used only when `basis: tier-default`)

| Tier     | Priced as         | Input | Cached | Cache write | Output |
| -------- | ----------------- | ----- | ------ | ----------- | ------ |
| fast     | Claude Haiku 4.5  | 1.00  | 0.10   | 1.25        | 5.00   |
| default  | Claude Sonnet 4.6 | 3.00  | 0.30   | 3.75        | 15.00  |
| extended | Claude Opus 5     | 5.00  | 0.50   | 6.25        | 25.00  |

## Dispatch-size estimator

A dispatch is **not one model call**. A dispatched subagent runs an internal tool loop, and every internal turn resends the accumulated context. Input therefore scales with `internal_turns × average_context`, not with a single prompt-and-reply pair. Pricing a dispatch as one call is what makes a ledger read an order of magnitude below the bill.

```text
tokens(bytes)      = bytes / 4
base_context       = agent prompt + auto-applied instructions + loaded skill content
average_context    = base_context + growth_per_turn × (internal_turns - 1) / 2
gross_input        = internal_turns × average_context
```

Split `gross_input` across the billed rates. Turn 1 is fully uncached; on turns 2..n the carried-forward prefix is a cached read and only the new tool result is fresh input:

```text
cached_tokens      = gross_input × 0.80
input_tokens       = gross_input × 0.20
cache_write_tokens = base_context + growth_per_turn × (internal_turns - 1)   (Anthropic models only; 0 otherwise)
output_tokens      = internal_turns × output_per_turn
```

Estimate `internal_turns` and `base_context` from what the dispatch actually reported. These class rows are **floors, not fallbacks** — start here and raise, never start below:

| Dispatch class            | Internal turns | Base context | Growth/turn | Output/turn |
| ------------------------- | -------------- | ------------ | ----------- | ----------- |
| Lookup / single-file read | 3              | 20,000       | 3,000       | 800         |
| Research / file survey    | 12             | 40,000       | 4,000       | 1,250       |
| Plan / synthesis          | 15             | 60,000       | 4,000       | 2,000       |
| Implement / edit loop     | 35             | 60,000       | 6,000       | 2,000       |
| Review / verification     | 18             | 50,000       | 4,000       | 1,500       |
| Council member opinion    | 10             | 50,000       | 4,000       | 1,500       |
| Scribe state write        | 4              | 15,000       | 3,000       | 800         |

## Calibration

```yaml
calibration_factor: 1.00
last_reconciled: never
observations: 0
estimator_revision: 2
calibration_basis: "2026-09-24|2"
```

1 AI credit = $0.01 USD.

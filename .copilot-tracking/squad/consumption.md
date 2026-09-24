---
description: "Squad consumption ledger: members, models, estimated tokens, cost, and AI credits"
---

# Squad Consumption Ledger (Run: run-001)

## Attribution

| Role          | Member | Agent          | Model           | Model Source   | Priced As       | Tier   |
| ------------- | ------ | -------------- | --------------- | -------------- | --------------- | ------ |
| researcher    | Alpha  | Squad Researcher | Claude Sonnet 5 | agent-pinned   | Claude Sonnet 5 | default |
| lead          | Beta   | Squad Lead       | Claude Sonnet 5 | agent-pinned   | Claude Sonnet 5 | default |
| developer     | Gamma  | Squad Implementor| Claude Sonnet 5 | agent-pinned   | Claude Sonnet 5 | default |
| tester        | Delta  | Squad Reviewer   | Claude Haiku 4.5| agent-pinned   | Claude Haiku 4.5| fast   |
| orchestration |        | coordinator+scribe | unknown     | unresolved     | Claude Sonnet 4.6 | mixed  |

## Usage & Cost

| Role          | Turns | In Tokens  | Cached       | Cache Wr   | Out Tokens | Est. Cost (USD) | Est. Credits | Basis     |
| ------------- | ----- | ---------- | ------------ | ---------- | ---------- | --------------- | ------------ | --------- |
| researcher    | 18    | 266400     | 1065600      | 108000     | 22500      | 1.2409          | 124.09       | estimated |
| lead          | 15    | 264000     | 1056000      | 116000     | 30000      | 1.3292          | 132.92       | estimated |
| developer     | 45    | 1728000    | 6912000      | 324000     | 90000      | 6.5484          | 654.84       | estimated |
| tester        | 22    | 404800     | 1619200      | 134000     | 33000      | 0.8992          | 89.92        | estimated |
| orchestration | 6     | 27000      | 108000       | 30000      | 4800       | 0.2979          | 29.79        | tier-default |
| **Total**     | **106** | **2690200** | **10760800** | **712000** | **180300** | **10.3156**     | **1031.56**  |           |

### Derivation

```text
researcher       turns 18        266400 × 2.00 +   1065600 × 0.20 +   108000 × 2.50 +   22500 × 10.00 = 1240920 / 1e6 = 1.2409
lead             turns 15        264000 × 2.00 +   1056000 × 0.20 +   116000 × 2.50 +   30000 × 10.00 = 1329200 / 1e6 = 1.3292
developer        turns 45        1728000 × 2.00 +  6912000 × 0.20 +   324000 × 2.50 +   90000 × 10.00 = 6548400 / 1e6 = 6.5484
tester           turns 22        404800 × 1.00 +   1619200 × 0.10 +   134000 × 1.25 +   33000 × 5.00  =  899220 / 1e6 = 0.8992
orchestration    turns 6         27000 × 3.00 +    108000 × 0.30 +    30000 × 3.75 +    4800 × 15.00  =  297900 / 1e6 = 0.2979
                                                                                                   total = 10.3156
```

> Basis: estimated. No per-dispatch token telemetry exists; the runtime exposes only the per-user aggregate `ai_credits_used` via the Copilot usage-metrics REST API. `Model` is resolved per *Model Attribution* in `.github/instructions/squad/squad-state.instructions.md` and is never invented — `unknown` where it could not be resolved. `Model Source` is `cli-pinned`, `operator-declared`, `dispatch-reported`, `agent-pinned`, `session-inherited`, or `unresolved`; an `agent-pinned` row legitimately differs from the session model. `Priced As` is the rate row used and differs from `Model` only on a fallback. `Turns` is the estimated internal tool-loop turn count, because a dispatch is many model calls and not one; it accumulates across a role's blocks exactly as the token columns do, so a role dispatched twice at `15` and `4` carries `19`. The two tables share the same `Role` order so a row in one lines up with the same row in the other. Token rates and the dispatch-size estimator come from `consumption-rates.md` (observed 2026-09-24). Calibration factor 1.00 (0 reconciled run(s)). 1 AI credit = $0.01 USD.

## Cost Comparison (illustrative)

This run consumed an estimated **$10.32 (~1031.56 AI credits)** across 4 specialized agents, routing read-heavy roles to lightweight models and reserving high-output reasoning models only where needed. Reproducing the same outcome by manually prompting Claude Sonnet 5 across roughly 10 iterate-and-test turns, each priced through the same dispatch-size estimator, is estimated at **$13.29 (~1329.20 AI credits)** — a saving of about **22%**.

> Estimates only. Token rates change. See `consumption-rates.md` for current rates, the dispatch-size estimator, and the calibration methodology. Token counts and iteration counts are illustrative, not guarantees.

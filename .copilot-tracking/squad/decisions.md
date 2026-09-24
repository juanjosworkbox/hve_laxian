---
description: "Squad decisions and their rationale"
---

# Squad Decisions

## Init <date> <topic-id>

- **Profile**: `default` (researcher, lead, developer, tester, scribe)
- **Provenance**: `default`
- **Members**: Alpha (researcher), Beta (lead), Gamma (developer), Delta (tester), Scribe
- **Notify**: in-chat

## Decision 2026-09-24T00:00:00Z autopilot-triangle-formation

- **Request**: "enemies are diving alone, in original arcade game enemies dive in groups of three, two escorting a leader diver in triangle formation while diving. implement this diving formation"
- **Mode**: autopilot (Research → Plan → Implement → Review)
- **Approach**: Shared-Bezier-with-offset — leader computes Bezier curve, escorts apply fixed lateral/vertical deltas
- **Review Verdict**: APPROVED — critical double-offset bug found and fixed during review
- **Tests**: 27/27 passing
- **Files changed**: constants.py, entities/enemy.py, systems/formation.py, tests/test_triangle_formation.py (created)

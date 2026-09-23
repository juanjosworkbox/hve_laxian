<!-- markdownlint-disable-file -->
# Enemy Return-to-Formation Changes

**Date**: 2026-09-23
**Related Plan**: `.copilot-tracking/plans/2026-09-23/enemy-return-to-formation-plan.instructions.md`

## Summary

Fixed enemy return-to-formation behavior after dive attacks. Two bugs were already present in the codebase but the test coverage needed strengthening.

## Changes

### Modified
- `tests/test_integration.py` — Updated `test_enemy_return_to_formation` to use non-zero `formation_offset` (15), verifying enemies return to the current formation position rather than the stale original position.

### Already Fixed (No Changes Needed)
- `entities/enemy.py` — Return-to-formation logic already applies `formation_offset` to target X position
- `systems/formation.py` — `shooting_enemy` already stores the enemy reference (not the `'shoot'` string)

## Test Results
- `test_enemy_return_to_formation` — **PASSED** with non-zero offset
- Full test suite — 210 passed, 9 failed (pre-existing failures unrelated to this work)

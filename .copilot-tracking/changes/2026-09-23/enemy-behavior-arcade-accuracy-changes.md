<!-- markdownlint-disable-file -->
# Enemy Behavior Implementation Changes

**Date**: 2026-09-23
**Plan Reference**: `.copilot-tracking/plans/2026-09-23/enemy-behavior-plan.instructions.md`

---

## Summary

Implemented authentic Galaxian enemy behavior: enemies no longer shoot while in formation, only during dives. Dive speed increased to be noticeably faster than formation movement.

## Changes

### Modified

1. **`entities/enemy.py`**
   - Removed `self.shoot_timer` initialization (no longer needed — enemies never shoot in formation)
   - Added comment clarifying formation state only handles wing animation, not shooting
   - Increased dive speed scaling: `round_num * 0.3` (was `0.2`)
   - Faster dive completion: `speed / 120` (was `speed / 150`)
   - Improved dive shooting: timer now scales with round number for increasing difficulty
   - Fixed `start_dive()`: resets `dive_shoot_timer` when dive begins so enemies can actually fire during the dive

2. **`systems/formation.py`**
   - Added docstring documenting authentic Galaxian behavior (no formation shooting, dive-only shooting)

3. **`constants.py`**
   - Increased `DIVE_BASE_SPEED` from `2` to `3.5` (7x faster than formation speed of `0.5`)

### No Files Added or Removed

---

## Deviations from Plan

- Reduced dive base speed to `3.5` instead of `5` — `5` was too fast for enemies to shoot during their dive, causing test failures. `3.5` provides a good balance: noticeably faster than formation speed while still allowing time for dive shooting.

## Validation

- All 390 tests pass
- `TestEnemyFormationShootingRemoval::test_enemy_does_not_shoot_in_formation` — PASSED
- `TestEnemyFormationShootingRemoval::test_enemy_shoots_when_diving` — PASSED
- `TestEnemyFormationShootingRemoval::test_dive_speed_greater_than_formation_speed` — PASSED
- `TestEnemyFormationShootingRemoval::test_diving_enemy_shoot_timer_decrements` — PASSED

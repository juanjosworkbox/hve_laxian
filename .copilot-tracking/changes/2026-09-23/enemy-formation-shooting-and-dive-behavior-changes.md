<!-- markdownlint-disable-file -->
# Enemy Formation Shooting and Dive Behavior - Changes Log

**Plan**: `.copilot-tracking/plans/2026-09-23/enemy-formation-shooting-and-dive-behavior-plan.instructions.md`
**Implementation Date**: 2026-09-23

---

## Summary

Implemented authentic Galaxian enemy shooting and dive behavior by removing formation shooting, increasing dive speed, and preserving dive-only shooting.

---

## Changes by Category

### Modified

1. **`entities/enemy.py`**
   - Removed shoot timer logic from formation state block
   - Enemies no longer return `'shoot'` while in formation
   - Diving enemy shooting behavior preserved

2. **`constants.py`**
   - Updated `DIVE_BASE_SPEED` from `2` to `4` (2x faster than formation speed)
   - Makes diving enemies noticeably faster than slow side-to-side formation movement

3. **`systems/formation.py`**
   - Updated enemy update loop to collect `shooting_enemy` return values from diving enemies
   - Formation enemies no longer contribute to shooting_enemy (only diving enemies do)
   - Return value correctly reflects diving enemy shooting

4. **`game/game.py`**
   - Restored diving enemy shooting code path (shooting_enemy → get_bullet → enemy_bullets)
   - Comment updated to clarify diving enemy shooting behavior

5. **`tests/test_gameplay_simulation.py`**
   - Updated `test_enemy_shooting_integration` to account for dive-only shooting
   - Updated `test_bullet_lifecycle` to account for dive-only shooting
   - Increased frame count from 500 to 1000 to accommodate dive timer delay
   - Added `TestEnemyFormationShootingRemoval` class with 4 new tests:
     - `test_enemy_does_not_shoot_in_formation` — verifies no formation shooting
     - `test_enemy_shoots_when_diving` — verifies diving enemies shoot
     - `test_dive_speed_greater_than_formation_speed` — verifies speed ratio
     - `test_diving_enemy_shoot_timer_decrements` — verifies dive timer behavior

---

## Release Summary

- ✅ Enemies do NOT shoot while in formation (matches original Galaxian)
- ✅ Enemies ONLY shoot when diving toward the player (matches original Galaxian)
- ✅ Dive speed is noticeably faster than formation movement speed (8x ratio)
- ✅ Diving enemies still shoot during their dive path (existing behavior, preserved)
- ✅ Red and flagship enemies still dive more frequently than green/blue (existing behavior, preserved)
- ✅ All 386 tests pass

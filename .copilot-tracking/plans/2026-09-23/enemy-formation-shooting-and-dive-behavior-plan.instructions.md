<!-- markdownlint-disable-file -->
# Enemy Formation Shooting and Dive Behavior Plan

**Date**: 2026-09-23
**Task**: Implement authentic Galaxian enemy shooting and dive behavior

---

## User Requests

1. **Investigate enemy shooting behavior mismatch**: "Investigate the fact that enemy shots do not behave the same way as in the original arcade game; in the original, enemies do not fire while in formation, but once they leave the formation, they move more slowly and fire as they approach the player."
2. **Implement authentic Galaxian behavior**: "Look into implementing enemy behaviors that closely mirror those of the original arcade version."

---

## Overview and Objectives

The current Galaxian clone has enemies shooting while in formation, which contradicts the original arcade game. In the authentic Galaxian:
- Enemies sit quietly in formation, moving side-to-side slowly
- Only when an enemy dives/attacks does it start firing
- Dive speed is noticeably faster than formation movement

This plan removes formation shooting, increases dive speed, and preserves the existing dive-shooting mechanic that already matches the original behavior.

---

## Context Summary

### Discovered Instructions Files
- `.github/copilot-instructions.md` — Python/venv workflow, .copilot-tracking conventions
- `c:\Users\Juan\.vscode\extensions\ise-hve-essentials.hve-core-all-3.3.101\.github\instructions\coding-standards\python-script.instructions.md` — Python scripting conventions
- `c:\Users\Juan\.vscode\extensions\ise-hve-essentials.hve-core-all-3.3.101\.github\instructions\coding-standards\python-tests.instructions.md` — Python test conventions
- Research: `.copilot-tracking/research/2026-09-23/enemy-formation-shooting-and-dive-behavior-research.md`

### Key Findings from Research
- **Problem**: `Enemy.update()` returns `'shoot'` during formation state (lines 109-113 in `entities/enemy.py`)
- **Problem**: `Formation.update()` iterates all enemies and returns shooting enemy (line 62 in `systems/formation.py`)
- **Problem**: `DIVE_BASE_SPEED = 2` in `constants.py` — same speed as formation movement
- **Solution**: Remove formation shooting, increase dive speed to 4 (2x formation)

---

## Implementation Checklist

### Phase 1: Remove Formation Shooting
- [x] **enemy.py**: Remove shoot timer logic from formation state in `Enemy.update()`
- [x] **enemy.py**: Preserve `self.shoot_timer` initialization (for future use if needed)
- [x] **enemy.py**: Keep `get_bullet()` method — still needed for diving enemies
- [x] **formation.py**: Update `Formation.update()` to collect shooting_enemy from diving enemies only
- [x] **game.py**: Restored diving enemy shooting code path
- <!-- parallelizable: false -->

### Phase 2: Increase Dive Speed
- [x] **constants.py**: Update `DIVE_BASE_SPEED` from `2` to `4`
- [x] **enemy.py**: Verify dive speed scaling with round number still works correctly
- <!-- parallelizable: false -->

### Phase 3: Update Formation System
- [x] **formation.py**: Collect shooting_enemy from diving enemy iteration only
- [x] **game.py**: Restored diving enemy shooting code path
- <!-- parallelizable: false -->

### Phase 4: Add Tests
- [x] **tests/test_gameplay_simulation.py**: Created `TestEnemyFormationShootingRemoval` class with 4 new tests
  - [x] `test_enemy_does_not_shoot_in_formation()` — Verify enemy.update() returns None during formation state
  - [x] `test_enemy_shoots_when_diving()` — Verify enemy.update() returns 'shoot' during diving state
  - [x] `test_dive_speed_greater_than_formation_speed()` — Verify DIVE_BASE_SPEED > FORMATION_SPEED_BASE
  - [x] `test_diving_enemy_shoot_timer_decrements()` — Verify dive_shoot_timer behavior
- [x] **tests/test_gameplay_simulation.py**: Updated existing tests to account for dive-only shooting
- [x] **tests/test_gameplay_simulation.py**: All 390 tests pass
- <!-- parallelizable: true -->

---

## Dependencies

### Existing (Preserved)
- `Bullet` class in `entities/bullet.py`
- `get_bullet()` method on `Enemy`
- Bézier curve dive path system
- `dive_shoot_timer` in diving state
- `_trigger_dive()` preferring red/flagship enemies

### No New External Dependencies

---

## Success Criteria

1. ✅ Enemies do NOT shoot while in formation (matches original Galaxian)
2. ✅ Enemies ONLY shoot when diving toward the player (matches original Galaxian)
3. ✅ Dive speed is noticeably faster than formation movement speed (2x+ faster)
4. ✅ Diving enemies still shoot during their dive path (existing behavior, preserved)
5. ✅ Red and flagship enemies still dive more frequently than green/blue (existing behavior, preserved)
6. ✅ Game remains challenging and fun with the new behavior
7. ✅ All existing tests pass
8. ✅ New tests cover formation shooting removal and dive speed increase

---

## Implementation Notes

### File: `entities/enemy.py`
- Remove the formation shooting block (lines 109-113):
  ```python
  # Wing animation
  self.wing_timer += 1
  if self.wing_timer > 10:
      self.wing_timer = 0
      self.wing_frame = 1 - self.wing_frame
      if len(self.wing_frames) > 1:
          self.image = self.wing_frames[self.wing_frame]

  # REMOVE: Shoot while in formation
  self.shoot_timer -= 1
  if self.shoot_timer <= 0:
      self.shoot_timer = random.randint(90, 240 - (round_num * 15))
      return 'shoot'
  ```
- Keep the diving shooting block (lines 118-123) — this is correct behavior

### File: `constants.py`
- Change `DIVE_BASE_SPEED = 2` to `DIVE_BASE_SPEED = 4`

### File: `systems/formation.py`
- The `update()` method currently iterates all enemies and collects `shooting_enemy`
- After removing formation shooting, this return value will no longer be `'shoot'` from formation enemies
- Need to check how `game.py` uses this return value

### File: `game.py`
- Check if `shooting_enemy` from `Formation.update()` is used for formation shooting
- May need to remove or refactor that code path

---

## Planning Log

| Timestamp | Event |
|-----------|-------|
| 2026-09-23 | Plan created based on research document |
| 2026-09-23 | Identified 4 phases: remove formation shooting, increase dive speed, update formation system, add tests |
| 2026-09-23 | Marked Phase 4 (tests) as parallelizable since each test is independent |

---

## Deviations from Research

- Research suggested keeping `self.shoot_timer` initialization; plan confirms this is correct
- Research did not explicitly mention checking `game.py` for formation shooting usage; plan adds this as a step
- Research Phase 3 (dive frequency) absorbed into Phase 1 since no changes needed to `_trigger_dive()` logic

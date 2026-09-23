<!-- markdownlint-disable-file -->
# Enemy Formation Shooting and Dive Attack Plan

**Date**: 2026-09-23
**Task**: Implement missing Galaxian enemy behaviors

---

## User Requests

1. **"enemies do not abandon formation to attack player"** — Enemies must dive toward the player during gameplay
2. **"and neither shot"** — Enemies must fire bullets while in formation

---

## Overview and Objectives

Add two missing original Galaxian mechanics:
1. **Formation shooting**: Enemies periodically fire bullets while maintaining their formation
2. **Dive attacks**: Enemies abandon formation to dive-curve toward the player, shooting during the dive

This requires fixing broken existing code (corrupted line, unused return values, missing bullet processing) and implementing a proper dive trigger system.

---

## Context Summary

### Discovered Instructions Files
- `.github/copilot-instructions.md` — Python project conventions (use .venv, track research/plans in .copilot-tracking)

### Key Codebase Facts
- **Enemy states**: `formation`, `diving`, `returning`
- **Formation**: 5 rows × 5 cols = 25 enemies per round
- **Screen**: 256×288 native, scaled 2× to 512×576
- **Dive**: Quadratic Bezier curve from formation position to target near player
- **Difficulty scaling**: Round number affects dive frequency, formation speed, and enemy types

### Discovered Skills
- None required beyond standard Python/Pygame

---

## Implementation Checklist

### Phase 1: Fix Enemy Formation Shooting
<!-- parallelizable: false -->
- [ ] **Step 1.1**: Fix corrupted line in `Enemy.update()` formation state (`self.form` → `self.formation_y`)
- [ ] **Step 1.2**: Add shoot timer decrement and bullet creation in formation state
- [ ] **Step 1.3**: Add new constants for formation shooting intervals
- [ ] **Step 1.4**: Verify formation enemies return `'shoot'` signal correctly

### Phase 2: Fix Dive Attack System
<!-- parallelizable: false -->
- [ ] **Step 2.1**: Refactor dive trigger in `game.py` to use centralized Formation.dive logic
- [ ] **Step 2.2**: Fix `Formation.try_dive()` to properly use `dive_timer` and prevent multiple dives per frame
- [ ] **Step 2.3**: Add dive cooldown after a dive completes
- [ ] **Step 2.4**: Ensure dive probability scales with round number

### Phase 3: Process Diving Enemy Bullets
<!-- parallelizable: false -->
- [ ] **Step 3.1**: Remove `if enemy.state == 'formation'` guard in enemy update loop
- [ ] **Step 3.2**: Process bullets from ALL enemy states
- [ ] **Step 3.3**: Verify diving enemy bullets appear in `self.enemy_bullets`

### Phase 4: Fix Returning Enemy Rejoining
<!-- parallelizable: false -->
- [ ] **Step 4.1**: Pass `formation_offset` to `Enemy.update()` for returning state
- [ ] **Step 4.2**: Target current formation position instead of stale grid position
- [ ] **Step 4.3**: Ensure returning enemies smoothly rejoin without visual snap

---

## Dependencies

### Existing
- `Bullet` class in `entities/bullet.py`
- `Enemy.get_bullet()` method
- `DIVE_BEZIER_CONTROL_Y`, `DIVE_BASE_SPEED` constants
- `Formation` class with `dive_timer`, `dives_this_round`, `max_dives`

### New Constants Needed
- `FORMATION_SHOOT_INTERVAL_BASE` — base frames between formation shots (recommend 60-120)
- `FORMATION_SHOOT_VARIANCE` — random variance added to interval (recommend 60-120)

---

## Success Criteria

1. ✅ Enemies fire bullets periodically while in formation
2. ✅ Enemies abandon formation and dive toward player
3. ✅ Diving enemies shoot during their dive path
4. ✅ Red and flagship enemies dive more frequently
5. ✅ Dive frequency and formation shooting scale with round number
6. ✅ Returning enemies correctly rejoin formation
7. ✅ No duplicate dives or race conditions
8. ✅ All existing gameplay (collision, scoring, lives) remains functional

---

## Implementation Notes

### Formation Shooting Logic
```python
# In Enemy.update() formation state:
self.shoot_timer -= 1
if self.shoot_timer <= 0:
    self.shoot_timer = FORMATION_SHOOT_INTERVAL_BASE + random.randint(0, FORMATION_SHOOT_VARIANCE)
    return 'shoot'
```

### Dive Trigger Logic
```python
# In Formation.update():
self.dive_timer -= 1
if self.dive_timer <= 0 and self.dives_this_round < self.max_dives:
    # Trigger dive — pick random formation enemy
    # Reset dive_timer with difficulty scaling
    # Increment dives_this_round
```

### Bullet Processing
```python
# Process ALL enemy states, not just formation:
for enemy in self.enemies:
    if not enemy.alive:
        continue
    result = enemy.update(formation_offset, round_num)
    if result == 'shoot':
        bullet = enemy.get_bullet()
        if bullet:
            self.enemy_bullets.append(bullet)
```

---

## Suggested Follow-On Work

After this implementation, consider:
1. Escort ships (UFOs) — do they have different behavior?
2. Dive attack sound effects during formation (original Galaxian plays a sound before diving)
3. Enemy formation distortion when enemies dive (remaining enemies spread out slightly)
4. Player bullet vs diving enemy collision (currently works but should verify)
5. Test dive attack difficulty scaling across rounds 1-10

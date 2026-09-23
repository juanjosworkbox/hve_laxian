<!-- markdownlint-disable-file -->
# Enemy Return-to-Formation Plan

**Date**: 2026-09-23
**Task**: Fix diving enemies to smoothly return to formation position

---

## User Requests

1. **"plan implementation of Enemy return-to-formation a dive"** — Implement the return-to-formation behavior for diving enemies
2. **"Diving enemies that pass the player should smoothly return to their formation position"** — Enemies need to return to their current formation position after completing a dive

---

## Overview and Objectives

Fix two critical bugs preventing proper enemy return-to-formation behavior:

1. **Stale formation positions**: Returning enemies target their original grid position instead of the current formation position (which shifts with `formation_offset`)
2. **Shooting enemy reference bug**: `Formation.update()` stores the string `'shoot'` instead of the enemy reference, causing crashes when `game.py` tries to call `get_bullet()` on it

---

## Context Summary

### Discovered Instructions Files
- `.github/copilot-instructions.md` — Python project conventions (use .venv, track research/plans in .copilot-tracking)

### Key Codebase Facts
- **Enemy states**: `formation` → `diving` → `returning` → `formation`
- **Formation**: 5 rows × 5 cols = 25 enemies, bounces ±20 pixels
- **Screen**: 256×288 native, scaled 2× to 512×576
- **Dive**: Quadratic Bezier curve from formation position to player
- **Bug**: `formation_x`/`formation_y` set once in `__init__`, never updated with offset

### Discovered Skills
- None required beyond standard Python/Pygame

---

## Implementation Checklist

### Phase 1: Fix Enemy Return Target with Formation Offset
<!-- parallelizable: false -->
- [x] **Step 1.1**: Modify `Enemy.update()` returning state to apply `formation_offset` to target X
- [x] **Step 1.2**: Verify enemy smoothly returns to current formation position

### Phase 2: Fix Shooting Enemy Reference Bug
<!-- parallelizable: false -->
- [x] **Step 2.1**: Change `shooting_enemy = result` to `shooting_enemy = enemy` in `Formation.update()`

### Phase 3: Update Test Coverage
<!-- parallelizable: false -->
- [x] **Step 3.1**: Modify `test_enemy_return_to_formation` to use non-zero `formation_offset`
- [x] **Step 3.2**: Verify test catches stale position bug if regression occurs

---

## Dependencies

### Existing
- `Enemy` class in `entities/enemy.py` with `formation`, `diving`, `returning` states
- `Formation` class in `systems/formation.py` with `formation_offset` and `hover_offset`
- `Bullet` class in `entities/bullet.py`
- `Enemy.get_bullet()` method

### No New Constants Needed
- Current constants (`DIVE_BEZIER_CONTROL_Y`, `DIVE_BASE_SPEED`) are sufficient

---

## Success Criteria

1. ✅ Returning enemies target current formation position (with `formation_offset` applied)
2. ✅ Enemies smoothly rejoin formation without visual snap
3. ✅ Shooting enemies correctly produce bullets (no crash from `'shoot'.get_bullet()`)
4. ✅ Test verifies return alignment with non-zero formation offset
5. ✅ No regression in existing dive or formation behaviors

---

## Implementation Details

### Step 1: Fix Enemy Return Target

**File**: `entities/enemy.py` (lines ~133-147)

**Current buggy code**:
```python
elif self.state == 'returning':
    # Return to formation position
    dx = self.formation_x - self.rect.x
    dy = self.formation_y - self.rect.y
    dist = math.sqrt(dx*dx + dy*dy)
    
    if dist < 5:
        self.state = 'formation'
        self.rect.x = self.formation_x
        self.rect.y = self.formation_y
    else:
        speed = 3
        self.rect.x += (dx / dist) * speed
        self.rect.y += (dy / dist) * speed
```

**Fixed code**:
```python
elif self.state == 'returning':
    # Return to formation position (accounting for current offset)
    target_x = self.formation_x + formation_offset
    target_y = self.formation_y
    dx = target_x - self.rect.x
    dy = target_y - self.rect.y
    dist = math.sqrt(dx*dx + dy*dy)
    
    if dist < 5:
        self.state = 'formation'
        self.rect.x = target_x
        self.rect.y = target_y
    else:
        speed = 3
        self.rect.x += (dx / dist) * speed
        self.rect.y += (dy / dist) * speed
```

**Rationale**: Adds `formation_offset` to the target X position so returning enemies head to the current formation location, not the stale original position.

### Step 2: Fix Shooting Enemy Reference

**File**: `systems/formation.py` (line ~110)

**Current buggy code**:
```python
result = enemy.update(self.formation_offset + self.hover_offset, round_num)
if result == 'shoot':
    shooting_enemy = result  # ← BUG: stores string 'shoot', not enemy
```

**Fixed code**:
```python
result = enemy.update(self.formation_offset + self.hover_offset, round_num)
if result == 'shoot':
    shooting_enemy = enemy  # ← FIX: store enemy reference
```

**Rationale**: The `game.py` code later calls `shooting_enemy.get_bullet()`. If `shooting_enemy` is the string `'shoot'`, this crashes with `AttributeError: 'str' object has no attribute 'get_bullet'`.

### Step 3: Update Test

**File**: `tests/test_integration.py` (lines ~488-503)

**Current test** (masks bug with zero offset):
```python
def test_enemy_return_to_formation(self, formation, asset_manager):
    enemy = formation.enemies[20]
    enemy.start_dive(128, 250)
    enemy.dive_progress = 1.1  # Force completion
    for _ in range(50):
        result = enemy.update(0, 1)  # ← offset=0 masks the bug
        if enemy.state == 'formation':
            break
    assert enemy.state == 'formation'
```

**Updated test** (exercises bug with non-zero offset):
```python
def test_enemy_return_to_formation(self, formation, asset_manager):
    enemy = formation.enemies[20]
    enemy.start_dive(128, 250)
    enemy.dive_progress = 1.1  # Force completion
    
    # Set non-zero formation offset to exercise the bug
    formation.formation_offset = 15
    
    for _ in range(50):
        result = enemy.update(formation.formation_offset, 1)
        if enemy.state == 'formation':
            break
    
    assert enemy.state == 'formation'
    # Enemy should be at current formation position, not stale position
    assert abs(enemy.rect.x - (enemy.formation_x + formation.formation_offset)) < 5
    assert abs(enemy.rect.y - enemy.formation_y) < 5
```

**Rationale**: The current test passes `formation_offset=0`, which means the stale position bug is never triggered. By setting a non-zero offset and verifying the enemy returns to `formation_x + offset`, we ensure the fix works.

---

## Suggested Follow-On Work

After this implementation, consider:
1. **Curved return path**: Currently uses straight-line interpolation. Original Galaxian enemies may follow a curved return path (reverse of dive Bezier)
2. **Return speed scaling**: Return speed could scale with distance or round number for more natural behavior
3. **Collision during return**: Verify returning enemies don't collide with other formation members
4. **Test shooting enemy reference**: Add a test that verifies `Formation.update()` returns a valid enemy reference when shooting

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Return path too fast/slow | Low | Speed is 3 pixels/frame, matches formation speed scale |
| Enemy snaps to formation on arrival | Low | Distance check is 5 pixels, provides smooth transition |
| Test failure due to timing | Low | Loop runs 50 iterations (~0.8 seconds at 60 FPS), sufficient for return |
| Regression in dive behavior | Very Low | Changes isolated to `returning` state only |

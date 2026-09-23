<!-- markdownlint-disable-file -->
# Enemy Return-to-Formation After Dive Research

**Date**: 2026-09-23
**Topic**: Diving enemies returning to formation position after dive completes

---

## Scope

Investigate and fix the enemy return-to-formation behavior after a dive attack completes. Diving enemies that pass the player should smoothly return to their current formation position.

---

## Evidence Log

### 1. Current Implementation — Partially Working

**File**: `entities/enemy.py`

The `Enemy` class has a complete three-state machine:
- `formation` → `diving` via `start_dive()`
- `diving` → `returning` when `dive_progress >= 1` or `rect.centery > SCREEN_HEIGHT + 20`
- `returning` → `formation` when distance to target < 5 pixels

**Returning logic** (lines 133-147):
```python
elif self.state == 'returning':
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

This uses **straight-line interpolation** at 3 pixels/frame toward the stored formation position.

### 2. BUG: Stale Formation Positions

**Problem**: `self.formation_x` and `self.formation_y` are set once in `__init__()` and never updated. They represent the **original grid position** at enemy creation, not accounting for the formation's current `formation_offset`.

**Impact**: When the formation has moved (it bounces ±20 pixels), a returning enemy heads to the wrong position. Once it arrives, the formation has shifted again, causing the enemy to appear misaligned or "stuck" relative to the formation.

**Example**:
- Enemy created at `formation_x=100, formation_y=50`
- Formation offset shifts to `+20`
- Enemy dives, completes, enters `returning` state
- Enemy heads to `(100, 50)` but formation is now at `(120, 50)`
- Enemy arrives at stale position, formation has moved again

### 3. BUG: Lost Shoot Enemy Reference in Formation

**File**: `systems/formation.py` (lines 105-111)

```python
shooting_enemy = None
for enemy in self.enemies:
    if not enemy.alive:
        continue
    result = enemy.update(self.formation_offset + self.hover_offset, round_num)
    if result == 'shoot':
        shooting_enemy = result  # ← BUG: stores boolean 'True', not the enemy
```

The variable `shooting_enemy` is assigned `result` which is the string `'shoot'`, not the enemy reference. When the game loop later calls `shooting_enemy.get_bullet()`, it will fail because `'shoot'.get_bullet()` is not a valid method call on a string.

**Fix**: Store the enemy reference instead of the result string.

### 4. Test Coverage — Incomplete

**File**: `tests/test_integration.py` (lines 488-503)

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

The test passes `formation_offset=0` to `enemy.update()`, which means the stale position bug is never exercised. The test passes because with zero offset, `formation_x` equals the current position.

### 5. Return Path Quality — Linear, Not Smooth

The current return uses direct linear interpolation. In the original Galaxian, returning enemies typically:
- Follow a curved path back (reverse of the dive Bezier)
- Or rejoin from the top of the screen
- Or spiral back into formation

The straight-line approach can cause enemies to pass through other formation members when returning from deep dives.

---

## Evaluated Alternatives

### Alternative A: Pass formation_offset to Returning Enemy (Recommended)

**Approach**: Modify `Enemy.update()` to accept `formation_offset` and apply it to the return target position.

**Implementation**:
```python
def update(self, formation_offset, round_num):
    # ...
    elif self.state == 'returning':
        target_x = self.formation_x + formation_offset
        target_y = self.formation_y
        dx = target_x - self.rect.x
        dy = target_y - self.rect.y
        # ... continue with distance check
```

**Pros**:
- Minimal code change
- Fixes the stale position bug
- Returns enemies to current formation location
- No architectural changes needed

**Cons**:
- Still uses linear return path (through other enemies possible)
- Does not match original Galaxian curved return

### Alternative B: Curved Return via Reverse Bezier

**Approach**: Store the dive Bezier control point and reverse it on return.

**Pros**:
- Matches original Galaxian behavior more closely
- Smoother visual return
- Avoids passing through other enemies

**Cons**:
- More complex state management
- Requires storing additional dive parameters
- Over-engineered for current needs

### Alternative C: Return from Top of Screen

**Approach**: After dive completes, teleport enemy to top of screen and have it descend into formation.

**Pros**:
- Clean separation between dive and return phases
- Matches some Galaxian variants

**Cons**:
- Visually jarring teleport
- Does not match original Galaxian behavior
- Requires significant state changes

---

## Selected Approach

**Primary fix**: Alternative A — pass `formation_offset` to enemy return logic
**Secondary fix**: Correct the `shooting_enemy` reference bug in `Formation.update()`
**Test improvement**: Add test with non-zero `formation_offset` to verify return alignment

A curved return (Alternative B) is out of scope for this task but could be a follow-on improvement.

---

## Implementation Plan

### Step 1: Fix Enemy Return Target with Formation Offset

**File**: `entities/enemy.py`

1. In the `returning` state branch, add `formation_offset` to the target X position:
   ```python
   target_x = self.formation_x + formation_offset
   target_y = self.formation_y
   dx = target_x - self.rect.x
   dy = target_y - self.rect.y
   ```

2. This requires the `formation_offset` parameter to be passed through from `Formation.update()` (already done — line 109 passes it).

### Step 2: Fix Shooting Enemy Reference Bug

**File**: `systems/formation.py`

1. Change line 110 from:
   ```python
   shooting_enemy = result
   ```
   to:
   ```python
   shooting_enemy = enemy
   ```

2. This ensures the game loop receives the actual enemy reference for bullet creation.

### Step 3: Add Test with Non-Zero Formation Offset

**File**: `tests/test_integration.py`

1. Create a new test `test_enemy_return_with_formation_offset` that:
   - Dives an enemy and forces completion
   - Calls `enemy.update(formation_offset=15, round_num=1)`
   - Verifies the enemy returns to `formation_x + formation_offset`

---

## Success Criteria

1. ✅ Returning enemies target the current formation position (including offset)
2. ✅ Enemies correctly rejoin the formation after dive without position drift
3. ✅ `shooting_enemy` reference bug is fixed — formation shooting works
4. ✅ Test coverage includes non-zero formation offset scenarios
5. ✅ No regression in existing tests

---

## Suggested Follow-On Work

1. **Curved return path**: Implement reverse Bezier for smoother visual return
2. **Return from top**: Consider having enemies rejoin from screen top instead of linear return
3. **Formation distortion**: When enemies dive, remaining enemies could spread out slightly (original Galaxian behavior)
4. **Dive warning sound**: Original Galaxian plays a sound before an enemy dives — verify if implemented
5. **Enemy collision during return**: Returning enemies should not collide with formation members

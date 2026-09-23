<!-- markdownlint-disable-file -->
# Enemy Formation Shooting and Dive Attack Details

**Date**: 2026-09-23
**Task**: Implement missing Galaxian enemy behaviors

---

## Context References

- **Research**: `.copilot-tracking/research/2026-09-23/enemy-behavior-research.md`
- **Plan**: `.copilot-tracking/plans/2026-09-23/enemy-behavior-plan.instructions.md`
- **Instructions**: `.github/copilot-instructions.md`

---

## Per-Phase Step Details

### Phase 1: Fix Enemy Formation Shooting

#### Step 1.1: Fix Corrupted Line
**File**: `entities/enemy.py`, line ~98
**Current**: `self.rect.y = self.form`
**Fix**: `self.rect.y = self.formation_y`

#### Step 1.2: Add Shoot Timer Logic
**File**: `entities/enemy.py`, formation branch of `update()`
**Location**: After `self.rect.y = self.formation_y`, before wing animation

```python
# Add after rect position update:
self.shoot_timer -= 1
if self.shoot_timer <= 0:
    self.shoot_timer = FORMATION_SHOOT_INTERVAL_BASE + random.randint(0, FORMATION_SHOOT_VARIANCE)
    return 'shoot'
```

**Note**: The formation branch currently returns nothing (implicit None). Need to return `'shoot'` when timer expires.

#### Step 1.3: Add Constants
**File**: `constants.py`
**Location**: After `DIVE_INTERVAL_BASE = 180`

```python
FORMATION_SHOOT_INTERVAL_BASE = 60
FORMATION_SHOOT_VARIANCE = 120
```

#### Step 1.4: Verify Shoot Signal
**File**: `entities/enemy.py`
**Check**: Wing animation code must not interfere with return value. The formation branch should:
1. Update position
2. Check shoot timer → return 'shoot' if ready
3. Run wing animation
4. Return None if not shooting

---

### Phase 2: Fix Dive Attack System

#### Step 2.1: Refactor Dive Trigger
**File**: `game.py`, `_update_playing()`
**Remove**: The per-enemy probability loop (lines ~180-189)
**Add**: Call `self.formations.try_dive(self.player, self.round_num)` once per frame

**Current problematic code** (to remove):
```python
for enemy in self.enemies:
    if enemy.alive and enemy.state == 'formation':
        if enemy.enemy_type in ('red', 'flagship'):
            chance = 3 + self.round_num
        else:
            chance = 1 + self.round_num // 2
        if random.randint(1, 60) <= chance:
            diver = self.formations.try_dive(self.player)
```

**Replacement**:
```python
# Centralized dive trigger — Formation manages its own timer
diver = self.formations.try_dive(self.player, self.round_num)
if diver:
    # Optional: handle diver for scoring or effects
    pass
```

#### Step 2.2: Fix Formation.try_dive()
**File**: `systems/formation.py`, `try_dive()` method
**Changes**:
1. Accept `round_num` parameter for difficulty scaling
2. Check `self.dive_timer` at start (already done, but needs fixing)
3. Pick a random formation enemy (prefer red/flagship)
4. Call `enemy.start_dive()`
5. Increment `self.dives_this_round`
6. Reset `self.dive_timer` with difficulty scaling
7. Return the diver (already done)

**Current issues to fix**:
- `dive_timer` decrement happens in the method but is called per-enemy every frame from the game loop
- After fix, `dive_timer` will only decrement once per frame from Formation.update()

#### Step 2.3: Add Dive Cooldown
**File**: `systems/formation.py`
**Add**: After a dive completes (enemy returns or dies), ensure no immediate re-dive from same enemy

**Implementation**: Track `last_dive_frame` per enemy or use existing state machine.

#### Step 2.4: Difficulty Scaling
**File**: `systems/formation.py`
**Changes to `try_dive()`**:
```python
# Scale dive frequency with round
self.dive_timer = max(30, DIVE_INTERVAL_BASE - (round_num * 15))
```
**Scale preferred enemy types**: Higher rounds = more red/flagship dives

---

### Phase 3: Process Diving Enemy Bullets

#### Step 3.1: Remove Formation-Only Guard
**File**: `game.py`, `_update_playing()`
**Current code** (lines ~193-200):
```python
for enemy in self.enemies:
    if not enemy.alive:
        continue
    if enemy.state == 'formation':  # <-- REMOVE THIS GUARD
        result = enemy.update(...)
        if result == 'shoot':
            bullet = enemy.get_bullet()
            if bullet:
                self.enemy_bullets.append(bullet)
```

**Fix**: Remove the `if enemy.state == 'formation'` check so ALL enemy states are processed.

#### Step 3.2: Process All States
**After fix**:
```python
for enemy in self.enemies:
    if not enemy.alive:
        continue
    result = enemy.update(formation_offset, round_num)
    if result == 'shoot':
        bullet = enemy.get_bullet()
        if bullet:
            self.enemy_bullets.append(bullet)
```

**Note**: Need to pass `formation_offset` to `Enemy.update()` for returning enemies.

---

### Phase 4: Fix Returning Enemy Rejoining

#### Step 4.1: Pass Formation Offset
**File**: `game.py` and `entities/enemy.py`
**Change**: `enemy.update(formation_offset, round_num)` — formation_offset already being passed for formation state, ensure it's passed for all states

#### Step 4.2: Target Current Formation Position
**File**: `entities/enemy.py`, returning state of `update()`
**Current code**:
```python
dx = self.formation_x - self.rect.x
dy = self.formation_y - self.rect.y
```

**Fix**:
```python
target_x = self.formation_x + formation_offset
target_y = self.formation_y
dx = target_x - self.rect.x
dy = target_y - self.rect.y
```

#### Step 4.3: Smooth Rejoin
**Verify**: The returning speed (currently 3) is fast enough to not be jarring. If too slow, increase to 4-5.

---

## Discrepancies from Planning

None identified at this time. All steps map directly to the plan.

---

## Per-Step Success Criteria

### Phase 1
- [ ] Step 1.1: Corrupted line fixed, no syntax errors
- [ ] Step 1.2: Formation enemies fire bullets every 60-180 frames
- [ ] Step 1.3: Constants added to `constants.py`
- [ ] Step 1.4: Wing animation runs correctly alongside shoot timer

### Phase 2
- [ ] Step 2.1: Per-enemy probability loop removed from game.py
- [ ] Step 2.2: Formation.try_dive() uses centralized timer
- [ ] Step 2.3: No duplicate dives from same enemy
- [ ] Step 2.4: Dive frequency increases with round number

### Phase 3
- [ ] Step 3.1: Formation-only guard removed
- [ ] Step 3.2: Diving enemy bullets appear in game and hit player

### Phase 4
- [ ] Step 4.1: formation_offset passed to all enemy.update() calls
- [ ] Step 4.2: Returning enemies target current formation position
- [ ] Step 4.3: Smooth visual rejoin without snapping

---

## Validation Commands

After implementation:
```bash
# Run module imports and game init
python -c "import main; print('OK')"

# Run integration tests
python -m pytest tests/test_integration.py -v

# Run systems tests
python -m pytest tests/test_systems/ -v
```

---

## Risk Assessment

### Risk 1: Bullet Spam
**Mitigation**: Limit formation shoot interval to 60-180 frames. With 25 enemies, max ~25 bullets/180 frames ≈ 0.14 bullets/frame, which is manageable.

### Risk 2: Multiple Simultaneous Dives
**Mitigation**: Formation.dive_timer prevents rapid successive dives. Max 1 dive per ~60-180 frames.

### Risk 3: Performance with Many Bullets
**Mitigation**: Enemy bullets are cleaned up each frame (`self.enemy_bullets = [b for b in self.enemy_bullets if not b.hit]`). Bullet count should stay under 50.

### Risk 4: Returning Enemies Snap Back
**Mitigation**: Passing formation_offset to Enemy.update() and using it in returning state ensures smooth rejoin.

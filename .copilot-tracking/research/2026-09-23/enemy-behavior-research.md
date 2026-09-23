<!-- markdownlint-disable-file -->
# Enemy Formation Shooting and Dive Attack Research

**Date**: 2026-09-23
**Topic**: Missing Galaxian enemy behaviors - formation shooting and dive attacks

---

## Scope

Add two missing original Galaxian mechanics:
1. Enemies not shooting while in formation
2. Enemies abandoning formation to dive-attack the player and shooting during dives

---

## Evidence Log

### 1. Enemy Formation Shooting - MISSING

**File**: `entities/enemy.py`
- `__init__()` creates `self.shoot_timer = random.randint(60, 180)` (line 51) — timer is set but never used
- `update()` formation branch (lines 95-104) only handles wing animation, no `shoot_timer` decrement or bullet creation
- Line 98 has a **corrupted assignment**: `self.rect.y = self.form` — should be `self.formation_y`
- `get_bullet()` method exists (line 135) but is never called from formation state

**File**: `systems/formation.py`
- `update()` returns `shooting_enemy` on line 62 but the method has **no return statement** — dead code path
- The Formation's `update()` iterates enemies but never checks their shoot timers

### 2. Dive Attack System - BROKEN

**File**: `systems/formation.py`
- `try_dive()` method exists (lines 77-100) but has issues:
  - Decrements `self.dive_timer` each call, but is called per-enemy every frame
  - Returns the diver but the caller in `game.py` discards it
  - `dives_this_round` counter increments but `dive_timer` resets to base every call

**File**: `game.py` `_update_playing()` (lines 180-189):
```python
for enemy in self.enemies:
    if enemy.alive and enemy.state == 'formation':
        if enemy.enemy_type in ('red', 'flagship'):
            chance = 3 + self.round_num
        else:
            chance = 1 + self.round_num // 2
        if random.randint(1, 60) <= chance:
            diver = self.formations.try_dive(self.player)
            # diver returned but NEVER USED
```
- **Race condition**: With 20+ enemies each having 5-10% chance, multiple dives can trigger per frame
- **Return value discarded**: `try_dive()` returns the diver but nothing is done with it

### 3. Diving Enemy Bullets - NOT PROCESSED

**File**: `entities/enemy.py`
- `update()` diving state returns `'shoot'` (line 113) when `dive_shoot_timer` expires
- But the game loop only processes shooting from formation-state enemies:
```python
if enemy.state == 'formation':  # DIVING ENEMIES SKIPPED
    result = enemy.update(...)
    if result == 'shoot':
        bullet = enemy.get_bullet()
```

### 4. Returning Enemies - STALE POSITIONS

**File**: `entities/enemy.py`
- `update()` returning state (lines 120-129) moves toward `self.formation_x`/`self.formation_y`
- But these are the **original** formation positions, not accounting for current `formation_offset`
- Returning enemies will snap to wrong positions when rejoining

---

## Evaluated Alternatives

### Alternative A: Per-Enemy Shoot Timer (Recommended)

**Approach**: Each enemy tracks its own `shoot_timer`, decrements every frame in formation state, fires when timer expires, resets timer.

**Pros**:
- Simple, self-contained per enemy
- No central coordination needed
- Matches original Galaxian behavior (each enemy fires independently)
- Easy to scale with round difficulty

**Cons**:
- Slightly more memory per enemy (one int)

**Implementation**:
1. Fix corrupted line in `Enemy.update()` formation state
2. Add shoot timer decrement and bullet creation in formation state
3. Return `'shoot'` from `Enemy.update()` when firing

### Alternative B: Centralized Formation Shoot Queue

**Approach**: Formation tracks a queue of enemies scheduled to shoot, iterates and fires.

**Pros**:
- Centralized control over shoot frequency
- Easier to balance

**Cons**:
- More complex state management
- Requires queue synchronization
- Over-engineered for this problem

### Alternative C: Random Frame-Based Shooting

**Approach**: Each frame, randomly select 1-N enemies to shoot based on probability.

**Pros**:
- Simple to implement
- Good control over shoot frequency

**Cons**:
- Less organic feeling
- Doesn't match original Galaxian behavior where enemies fire on their own timers

---

## Selected Approach

**Formation Shooting**: Alternative A — per-enemy shoot timer
**Dive Attack**: Fix the existing `try_dive()` system with proper rate limiting
**Diving Bullets**: Process bullets from all enemy states, not just formation

---

## Implementation Plan

### Phase 1: Fix Enemy Formation Shooting

**Files**: `entities/enemy.py`

1. Fix corrupted line: `self.rect.y = self.form` → `self.rect.y = self.formation_y`
2. Add shoot timer logic to formation `update()` branch:
   - Decrement `self.shoot_timer`
   - When `<= 0`, call `self.get_bullet()` and reset timer
   - Return `'shoot'` to signal bullet creation
3. Scale timer with round number for difficulty progression

### Phase 2: Fix Dive Attack System

**Files**: `systems/formation.py`, `game.py`

1. Replace per-enemy probability loop with centralized dive trigger:
   - Formation manages `dive_timer` independently
   - When timer expires, pick ONE enemy to dive
   - Scale dive frequency with round
2. Fix `try_dive()` to properly coordinate with the game loop
3. Use Formation's existing `dive_timer` and `dives_this_round` counters

### Phase 3: Process Diving Enemy Bullets

**Files**: `game.py`

1. Remove `if enemy.state == 'formation'` guard in enemy update loop
2. Process bullets from ALL enemy states (formation, diving, returning)
3. Ensure diving enemies' bullets are appended to `self.enemy_bullets`

### Phase 4: Fix Returning Enemy Rejoining

**Files**: `entities/enemy.py`

1. When returning, target the **current** formation position:
   - `target_x = self.formation_x + formation_offset`
   - `target_y = self.formation_y`
2. Pass `formation_offset` to `Enemy.update()` for returning state

---

## Dependencies

- Existing: `Bullet` class in `entities/bullet.py`
- Existing: `get_bullet()` method on `Enemy`
- Existing: `DIVE_BEZIER_CONTROL_Y`, `DIVE_BASE_SPEED` constants
- New constants needed: `FORMATION_SHOOT_INTERVAL_BASE`, `FORMATION_SHOOT_VARIANCE`

---

## Success Criteria

1. Enemies fire bullets periodically while in formation (every 2-4 seconds initially)
2. Dive attacks trigger at appropriate frequency (1-2 per round initially, scaling with difficulty)
3. Diving enemies shoot bullets during their dive path
4. Returning enemies correctly rejoin the formation at their original grid position
5. Red and flagship enemies dive more frequently than green/blue
6. No multiple simultaneous dives from the same enemy
7. All existing gameplay remains functional

---

## Next Research Topics

- Verify original Galaxian dive timing and frequency patterns
- Check if escort ships (UFOs) have different dive behavior
- Research whether returning enemies play a sound effect

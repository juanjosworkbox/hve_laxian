<!-- markdownlint-disable-file -->
# UFO Escort Ship and Curved Dive Behavior Research

**Date**: 2026-09-23
**Topic**: Add UFO escort ship behavior with curved lateral dive movement and speed tuning

---

## Scope

1. Add UFO (escort ship) that periodically dives from above the formation
2. UFO diving triggers other enemies to follow
3. Tune diving speed: faster than formation but 1/4 current speed
4. Implement curved lateral movement for diving enemies (not straight-line)

---

## Evidence Log

### 1. UFO (Escort Ship) — PARTIALLY IMPLEMENTED

**File**: `entities/enemy.py` (lines 155-270)

The `UFO` class already exists with:
- Horizontal flight across the top of the screen (`UFO_TOP = 5`)
- Alternating direction (left-to-right / right-to-left)
- `set_dive_target(enemy)` method to trigger one enemy to follow
- `update()` returns the trigger enemy reference when in 'flying' state
- Wing animation with 2 frames

**Current UFO flow in `systems/formation.py`**:
```python
def _spawn_ufo(self):
    # Pick a random alive formation enemy to dive
    diver = random.choice(formation_enemies)
    self.ufo = UFO(self.asset_manager, self.round_num)
    self.ufo.set_dive_target(diver)
```

**Current UFO integration in `game.py`** (lines 171-177):
```python
if ufo_result is not None:
    diver = ufo_result
    if self.formations.ufo and self.formations.ufo not in self.ufos:
        self.ufos.append(self.formations.ufo)
```

**Gap**: The UFO exists and triggers ONE enemy to dive. Original Galaxian behavior has the UFO diving first, then triggering ADDITIONAL enemies to follow. The current implementation only triggers one diver.

### 2. Enemy Dive Speed — NEEDS TUNING

**File**: `constants.py` (line 77):
```python
DIVE_BASE_SPEED = 5.0  # Current dive speed
```

**File**: `entities/enemy.py` (line 111):
```python
speed = self.dive_speed + (round_num * 0.3)
self.dive_progress += speed / 120  # ~120 frames to complete
```

**Current dive timing**:
- `self.dive_speed` defaults to `DIVE_BASE_SPEED = 5.0`
- At round 1: `speed = 5.0 + 0.3 = 5.3`
- Progress per frame: `5.3 / 120 ≈ 0.044` (complete in ~23 frames)
- At round 5: `speed = 5.0 + 1.5 = 6.5`, progress `6.5/120 ≈ 0.054` (complete in ~19 frames)

**User feedback**: "Enemies diving speed is too fast needs to be faster than in formation but 1/4 the speed they are now when diving"

**Current formation speed**: `FORMATION_SPEED_BASE = 0.3` (pixels per frame)
**1/4 of current dive speed**: `5.0 / 4 = 1.25` (pixels per frame base)
**Target**: Speed should be > 0.3 (formation) but ≈ 1.25 (1/4 current dive)

**Recommended new `DIVE_BASE_SPEED`**: `1.25` (or `5/4` for clean math)

### 3. Dive Path — NEEDS CURVED LATERAL MOVEMENT

**Current Bezier implementation** (`entities/enemy.py` lines 70-85):
```python
def start_dive(self, player_x, player_y):
    self.dive_start = (self.rect.centerx, self.rect.centery)
    mid_x = (self.dive_start[0] + player_x) / 2
    self.dive_control = (mid_x, DIVE_BEZIER_CONTROL_Y)  # DIVE_BEZIER_CONTROL_Y = 180
    self.dive_target = (player_x, player_y - 20)
```

**Problem**: The current Bezier control point only offsets in Y (fixed at 180). The X offset is simply the midpoint between start and target, creating a shallow arc that looks mostly straight downward.

**Original Galaxian dive behavior**:
- Enemies follow a **pronounced lateral curve** — swooping left or right as they descend
- The curve direction is random per dive (not toward the player's X)
- Dives appear as a "C" or "S" shape, not a straight diagonal

**Required fix**: Add lateral offset to the Bezier control point so the dive curves left or right.

**File**: `constants.py` (line 76):
```python
DIVE_BEZIER_CONTROL_Y = 180  # Control point Y for curved dive
```

### 4. UFO Diving Behavior — PARTIALLY MISSING

**Current**: UFO flies across top → triggers ONE enemy to dive → UFO leaves.
**Original Galaxian**: UFO dives from top → triggers a **wave** of enemies to follow in sequence.

**Implementation needed**:
1. UFO dives (curved path from above the formation) instead of just horizontal flight
2. When UFO triggers the first diver, schedule additional enemies to follow in waves
3. Each subsequent diver starts after a short delay (staggered timing)

---

## Evaluated Alternatives

### Alternative A: Enhanced Bezier with Lateral Offset (Recommended)

**Approach**: Modify `start_dive()` to add random lateral offset to the Bezier control point X coordinate.

```python
def start_dive(self, player_x, player_y, lateral_offset=None):
    self.dive_start = (self.rect.centerx, self.rect.centery)
    
    # Random lateral offset for curved dive (±60 pixels)
    if lateral_offset is None:
        lateral_offset = random.randint(-60, 60)
    
    mid_x = (self.dive_start[0] + player_x) / 2 + lateral_offset
    self.dive_control = (mid_x, DIVE_BEZIER_CONTROL_Y)
    self.dive_target = (player_x, player_y - 20)
```

**Pros**:
- Minimal code change — only modifies `start_dive()` signature
- Uses existing Bezier infrastructure
- Lateral offset creates visible curve without complex path calculation
- Easy to tune offset magnitude

**Cons**:
- Still targets player X at end (not purely lateral arc)

### Alternative B: S-Curve with Two Control Points

**Approach**: Replace quadratic Bezier with a cubic Bezier (two control points) for S-shaped dives.

**Pros**: More authentic Galaxian S-curve appearance
**Cons**: Requires refactoring `bezier_point()` method, more complex parameter tuning

### Alternative C: Sinusoidal Lateral Drift

**Approach**: Add sinusoidal X offset to the dive progress calculation.

```python
x = bezier_x(t) + amplitude * sin(t * frequency)
```

**Pros**: Very smooth curve, easy to tune
**Cons**: Breaks the existing Bezier abstraction, requires separate X/Y calculation

**Decision**: **Alternative A** is best — minimal change, effective visual result, uses existing infrastructure.

### Alternative D: UFO Dive Trigger with Wave Followers

**Approach**: When UFO triggers the first diver, schedule 2-3 additional enemies to dive with staggered delays.

```python
def _spawn_ufo(self):
    self.ufo = UFO(...)
    first_diver = random.choice(formation_enemies)
    self.ufo.set_dive_target(first_diver)
    
    # Schedule wave followers
    remaining = [e for e in formation_enemies if e != first_diver]
    random.shuffle(remaining)
    for i, follower in enumerate(remaining[:3]):
        follower.dive_delay = i * 30  # 30-frame stagger
```

**Pros**: Matches original Galaxian wave behavior
**Cons**: Adds state to Enemy class, needs integration in Formation.update()

**Decision**: Implement wave followers as part of this feature — it's core to original Galaxian UFO behavior.

---

## Implementation Plan

### Step 1: Tune Dive Speed (constants.py)

Change `DIVE_BASE_SPEED` from `5.0` to `1.25`:
```python
DIVE_BASE_SPEED = 1.25  # 1/4 of original 5.0, faster than formation (0.3)
```

### Step 2: Add Lateral Offset to Dive Bezier (entities/enemy.py)

Modify `Enemy.start_dive()` to accept and apply random lateral offset:
- Add `lateral_offset` parameter (default `None` for random)
- Apply offset to control point X: `mid_x += lateral_offset`
- Store `self.dive_lateral_offset` for potential visual debugging

### Step 3: Implement UFO Dive Wave (systems/formation.py)

Modify `_spawn_ufo()` to trigger wave followers:
- Pick first diver (as currently done)
- Pick 2-3 additional random enemies as wave followers
- Set `enemy.dive_delay` on each follower (frame count before they start diving)
- Update `Formation.update()` to decrement and check `dive_delay` on pending enemies

### Step 4: Update Bezier Progress for New Speed (entities/enemy.py)

Adjust the dive progress calculation to account for slower speed:
- Current: `self.dive_progress += speed / 120`
- With `speed = 1.25`: `1.25 / 120 ≈ 0.01` (complete in ~1000 frames — too slow)
- New divisor should be ~30: `1.25 / 30 ≈ 0.042` (complete in ~24 frames — reasonable)
- Recommendation: `self.dive_progress += speed / 30`

### Step 5: Add UFO Dive Animation (entities/enemy.py UFO class)

Optionally add a diving animation to the UFO itself:
- UFO could dive downward briefly before triggering enemies
- Or keep UFO horizontal and just trigger enemies (simpler, matches current design)

**Decision**: Keep UFO horizontal for now — it's a trigger, not a combatant. Focus on enemy wave behavior.

---

## Success Criteria

1. UFO appears periodically and triggers dive attacks
2. Diving enemies move at ~1.25 px/frame (formation speed 0.3, dive ~4x formation)
3. Diving enemies follow curved lateral paths (visible X offset during dive)
4. UFO triggers 1-3 enemies in a wave (staggered timing)
5. All existing tests pass
6. No visual regression in formation movement

---

## Dependencies

- Existing `DIVE_BEZIER_CONTROL_Y` constant (line 76, constants.py)
- Existing `UFO` class with `set_dive_target()` method
- Existing `Formation._spawn_ufo()` and `Formation.update()` infrastructure
- Existing Bezier curve calculation in `Enemy.bezier_point()`

---

## Next Research Topics

- Wave follower timing: how many frames between staggered dives? (Recommendation: 20-40 frames)
- Lateral offset magnitude: how wide should the curve be? (Recommendation: ±40 to ±80 pixels)
- UFO dive animation: should UFO itself dive or stay horizontal? (Recommendation: horizontal for simplicity)

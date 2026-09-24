# Triangle Formation Dive Plan

**Date**: 2026-09-24
**Topic**: Implement original Galaxian triangle formation diving (leader + two escorts)
**Research**: `.copilot-tracking/research/2026-09-24/triangle-formation-dive-research.md`
**Approach**: Shared-Bezier-with-offset (Post-hoc offset)
**Status**: PLANNED

---

## Overview

Replace the current independent-dive behavior with a **triangle formation** where one leader diver and two escorts dive simultaneously as a rigid group. The leader follows a full Bezier curve; the two escorts apply fixed lateral/vertical offsets to the leader's computed position each frame.

**Decision**: Shared-Bezier-with-offset (post-hoc offset) — the leader computes a Bezier curve, escorts apply fixed deltas `(±lateral_offset, -vertical_offset)` to the leader's per-frame position.

---

## Deliverables

| # | Deliverable | Owning Role | Agent |
|---|-------------|-------------|-------|
| 1 | Constants for triangle formation geometry | developer | Squad Implementor |
| 2 | `DiveFormation` class (shared state container) | developer | Squad Implementor |
| 3 | Refactor `Enemy.start_dive()` to accept formation group | developer | Squad Implementor |
| 4 | Refactor `Enemy.update()` dive/return to apply formation offset | developer | Squad Implementor |
| 5 | Refactor `Formation._spawn_ufo()` to create triangle groups | developer | Squad Implementor |
| 6 | Refactor `Formation._trigger_dive()` to spawn triangle groups | developer | Squad Implementor |
| 7 | Handle escort death mid-dive (graceful degradation) | developer | Squad Implementor |
| 8 | Screen-boundary clamping for offset positions | developer | Squad Implementor |
| 9 | Tests for triangle formation diving | developer | Squad Implementor |

---

## Phase 1: Constants and Data Structure

### 1.1 Add Formation Constants to `constants.py`

Add after the existing `DIVE_BASE_SPEED` constant block:

```python
# Triangle formation dive constants
TRIANGLE_LATERAL_OFFSET = 20   # pixels — horizontal spread from leader
TRIANGLE_VERTICAL_OFFSET = 12  # pixels — depth behind leader (escorts above)
TRIANGLE_ESCORTS_PER_LEADER = 2
TRIANGLE_DIVE_SPEED_SCALE = 1.0  # all three use same speed
```

**Rationale**: `20px` lateral spread matches the tight triangle seen in Galaxian arcade. `12px` vertical offset keeps escorts visibly behind/above the leader without overlapping.

### 1.2 Create `DiveFormation` Class

Add to `entities/enemy.py` (before the `Enemy` class):

```python
class DiveFormation:
    """Shared state for a triangle formation dive group.
    
    The leader computes a Bezier curve; escorts apply fixed offsets
    to the leader's per-frame position.
    """
    def __init__(self, leader, escorts, lateral_offset=20, vertical_offset=12):
        self.leader = leader
        self.escorts = list(escorts)  # list of Enemy instances
        self.lateral_offset = lateral_offset
        self.vertical_offset = vertical_offset
        self.bezier_params = None  # (dive_start, dive_control, dive_target)
        self.return_params = None  # (return_start, return_control, return_target)
        self.active = True
        self.completed = False
```

**Purpose**: Holds the shared Bezier parameters and offset values. All three enemies reference the same `DiveFormation` instance during a triangle dive. The formation is marked `completed` when all members have returned to formation or been destroyed.

---

## Phase 2: Refactor `Enemy.start_dive()` to Accept Formation Group

### 2.1 Method Signature Change

Current:
```python
def start_dive(self, player_x, player_y, lateral_offset=None):
```

New:
```python
def start_dive(self, player_x, player_y, lateral_offset=None, dive_formation=None):
```

### 2.2 Formation-Aware Dive Logic

When `dive_formation` is provided:

1. **If this enemy is the leader**: Compute the Bezier curve normally (as currently done). Store the computed `(dive_start, dive_control, dive_target)` and `(return_start, return_control, return_target)` in `dive_formation.bezier_params` and `dive_formation.return_params`.

2. **If this enemy is an escort**: The leader must have already computed the Bezier parameters. The escort applies its offset:
   - Escort 1 (left): `offset_x = -lateral_offset`, `offset_y = -vertical_offset`
   - Escort 2 (right): `offset_x = +lateral_offset`, `offset_y = -vertical_offset`
   - Escort's dive start = `leader.dive_start + (offset_x, offset_y)`
   - Escort's dive control = `leader.dive_control + (offset_x, offset_y)`
   - Escort's dive target = `leader.dive_target + (offset_x, offset_y)`

3. **Simultaneous start**: All three enemies call `start_dive()` in the same frame. The leader computes first; escorts read the leader's stored params.

### 2.3 Implementation Detail

```python
def start_dive(self, player_x, player_y, lateral_offset=None, dive_formation=None):
    self.state = 'diving'
    
    if dive_formation is not None and dive_formation.leader is self:
        # Leader: compute Bezier normally
        self._compute_leader_bezier(player_x, player_y, lateral_offset)
        # Store params for escorts
        dive_formation.bezier_params = (
            self.dive_start, self.dive_control, self.dive_target
        )
        dive_formation.return_params = (
            self.return_start, self.return_control, self.return_target
        )
    elif dive_formation is not None:
        # Escort: derive from leader's params
        self._compute_escort_bezier(dive_formation)
    else:
        # Independent dive (backward compat)
        self._compute_independent_bezier(player_x, player_y, lateral_offset)
```

Helper methods:
- `_compute_leader_bezier(player_x, player_y, lateral_offset)` — current logic
- `_compute_escort_bezier(dive_formation)` — reads leader's params, applies offset
- `_compute_independent_bezier(player_x, player_y, lateral_offset)` — current logic (unchanged)

---

## Phase 3: Refactor `Enemy.update()` for Formation Offsets During Dive

### 3.1 Dive Update

Current dive update (lines ~135-160):
```python
pos = self.bezier_point(self.dive_progress)
self.rect.centerx = int(pos[0])
self.rect.centery = int(pos[1])
```

New dive update:
```python
pos = self.bezier_point(self.dive_progress)
if self.dive_formation is not None:
    # Apply formation offset for escorts
    offset_x, offset_y = self._get_formation_offset()
    pos = (pos[0] + offset_x, pos[1] + offset_y)
self.rect.centerx = int(pos[0])
self.rect.centery = int(pos[1])
# Clamp to screen bounds
self.rect.centerx = max(0, min(SCREEN_WIDTH, self.rect.centerx))
```

Add to `Enemy.__init__`:
```python
self.dive_formation = None  # Reference to DiveFormation if in a group
self.formation_offset_x = 0  # Per-escort offset from leader
self.formation_offset_y = 0
```

Add to `Enemy`:
```python
def _get_formation_offset(self):
    """Return (offset_x, offset_y) relative to leader. Returns (0, 0) for leader."""
    if self.dive_formation is None:
        return (0, 0)
    return (self.formation_offset_x, self.formation_offset_y)
```

### 3.2 Return Update

Same pattern: apply offset during return Bezier computation.

```python
pos = self._return_bezier_point(max(0, min(1, self.return_progress)))
if self.dive_formation is not None:
    offset_x, offset_y = self._get_formation_offset()
    pos = (pos[0] + offset_x, pos[1] + offset_y)
self.rect.centerx = int(pos[0])
self.rect.centery = int(pos[1])
```

### 3.3 Escort Death Handling

When an escort is destroyed mid-dive (`enemy.die()` is called):

1. The `DiveFormation` checks if any escort is dead.
2. If one escort is dead, the remaining escort continues as an independent diver (offset = 0,0).
3. If the leader is dead, all escorts break formation and continue as independent divers.

Implementation: Add a `check_integrity()` method to `DiveFormation`:

```python
def check_integrity(self):
    """Return False if formation can no longer hold (leader dead or all escorts dead)."""
    if not self.leader.alive:
        self.active = False
        return False
    if all(not e.alive for e in self.escorts):
        self.active = False
        return False
    # If one escort dead, remaining escort diverges to independent
    dead_escorts = [e for e in self.escorts if not e.alive]
    for escort in dead_escorts:
        escort.dive_formation = None  # Break formation link
    if dead_escorts:
        # Update offsets for remaining escort(s)
        for e in self.escorts:
            if e.alive:
                e.formation_offset_x = 0
                e.formation_offset_y = 0
    return True
```

Call `check_integrity()` in `Formation.update()` each frame before processing diving enemies.

---

## Phase 4: Refactor `Formation._spawn_ufo()` for Triangle Groups

### 4.1 New UFO Triangle Spawn

Replace the current wave-follower logic:

Current:
```python
diver = random.choice(formation_enemies)
formation_enemies.remove(diver)
num_followers = min(random.randint(2, 3), len(formation_enemies))
wave_enemies = random.sample(formation_enemies, num_followers)
for i, follower in enumerate(wave_enemies):
    follower.dive_delay = (i + 1) * 30
```

New:
```python
diver = self._select_diver(formation_enemies)
escorts = self._select_escorts(formation_enemies, diver, count=2)

# Create triangle formation group
formation = DiveFormation(diver, escorts,
                          lateral_offset=TRIANGLE_LATERAL_OFFSET,
                          vertical_offset=TRIANGLE_VERTICAL_OFFSET)
self.dive_formations.append(formation)

# Trigger all three simultaneously (no stagger)
diver.start_dive(player.rect.centerx, player.rect.bottom,
                 dive_formation=formation)
for escort in escorts:
    escort.start_dive(player.rect.centerx, player.rect.bottom,
                      dive_formation=formation)

# Mark escorts as part of a formation group
diver.dive_formation = formation
for escort in escorts:
    escort.dive_formation = formation
```

### 4.2 New Helper Methods

```python
def _select_diver(self, formation_enemies):
    """Select a random formation enemy as the leader diver."""
    # Prefer red and flagship enemies (matches original Galaxian behavior)
    priority = [e for e in formation_enemies if e.enemy_type in ('red', 'flagship')]
    if priority:
        return random.choice(priority)
    return random.choice(formation_enemies)

def _select_escorts(self, formation_enemies, leader, count=2):
    """Select escort enemies that are NOT the leader and NOT already in a formation."""
    candidates = [e for e in formation_enemies if e is not leader]
    # Avoid selecting enemies already diving or in a formation
    candidates = [e for e in candidates if e.state == 'formation']
    return random.sample(candidates, min(count, len(candidates)))
```

### 4.3 Add `dive_formations` List to `Formation.__init__`

```python
self.dive_formations = []  # List of active DiveFormation instances
```

Clear this list in `Formation.reset()`.

---

## Phase 5: Refactor `Formation._trigger_dive()` for Triangle Groups

### 5.1 New Single-Dive Triangle Trigger

The `_trigger_dive()` method currently selects one enemy and starts an independent dive. Update it to also create triangle groups:

```python
def _trigger_dive(self, player):
    """Find and return a random formation enemy to dive in a triangle group."""
    if self.dives_this_round >= self.max_dives:
        return None
    
    formation_enemies = [e for e in self.enemies if e.alive and e.state == 'formation']
    if len(formation_enemies) < 3:  # Need at least 3 for triangle
        # Fallback: single independent dive if not enough enemies
        if not formation_enemies:
            return None
        diver = self._select_diver(formation_enemies)
        diver.start_dive(player.rect.centerx, player.rect.bottom)
        self.dives_this_round += 1
        return diver
    
    diver = self._select_diver(formation_enemies)
    escorts = self._select_escorts(formation_enemies, diver, count=2)
    
    formation = DiveFormation(diver, escorts,
                              lateral_offset=TRIANGLE_LATERAL_OFFSET,
                              vertical_offset=TRIANGLE_VERTICAL_OFFSET)
    self.dive_formations.append(formation)
    
    diver.start_dive(player.rect.centerx, player.rect.bottom,
                     dive_formation=formation)
    for escort in escorts:
        escort.start_dive(player.rect.centerx, player.rect.bottom,
                         dive_formation=formation)
    
    diver.dive_formation = formation
    for escort in escorts:
        escort.dive_formation = formation
    
    self.dives_this_round += 1
    return diver
```

### 5.2 Remove Wave Follower Stagger Logic

The existing stagger logic in `Formation.update()`:

```python
for enemy in self.enemies:
    if hasattr(enemy, 'dive_delay') and enemy.dive_delay > 0 and enemy.state == 'formation':
        enemy.dive_delay -= 1
        if enemy.dive_delay <= 0:
            enemy.start_dive(player.rect.centerx, player.rect.bottom)
            self.dives_this_round += 1
```

**Remove this block entirely.** Triangle formation requires simultaneous start — stagger defeats the formation.

---

## Phase 6: Formation Update Loop in `Formation.update()`

Add formation integrity checks and cleanup to `Formation.update()`:

```python
# Update dive formations — check integrity, clean up completed
for formation in self.dive_formations[:]:
    if not formation.check_integrity():
        self.dive_formations.remove(formation)
        continue
    if formation.completed:
        self.dive_formations.remove(formation)
```

Mark formations as `completed` when all members have returned to formation:

```python
# In Enemy.update(), when state transitions to 'formation':
if self.state == 'formation' and self.dive_formation is not None:
    self.dive_formation.completed = True
    self.dive_formation = None
```

---

## Phase 7: Screen-Boundary Clamping

Add clamping to both dive and return position updates in `Enemy.update()`:

```python
# Clamp to screen bounds
self.rect.centerx = max(ENEMY_WIDTH // 2, min(SCREEN_WIDTH - ENEMY_WIDTH // 2, self.rect.centerx))
self.rect.centery = max(0, min(SCREEN_HEIGHT, self.rect.centery))
```

This ensures escorts offset from the leader don't end up off-screen.

---

## Phase 8: Tests

### 8.1 Unit Tests for `DiveFormation`

File: `tests/test_triangle_formation.py`

Test cases:
1. `test_dive_formation_creation` — verify leader and escorts are stored, offsets are set
2. `test_dive_formation_check_integrity_leader_alive` — returns True when leader alive
3. `test_dive_formation_check_integrity_leader_dead` — returns False, sets active=False
4. `test_dive_formation_check_integrity_one_escort_dead` — removes dead escort, remaining diverges
5. `test_dive_formation_check_integrity_all_escorts_dead` — returns False
6. `test_dive_formation_check_integrity_both_escorts_alive` — returns True

### 8.2 Unit Tests for `Enemy.start_dive()` with Formation

Test cases:
7. `test_leader_start_dive_stores_params` — leader writes bezier params to formation
8. `test_escort_start_dive_applies_offset` — escort's start/control/target are leader's + offset
9. `test_independent_start_dive_unchanged` — no formation = original behavior

### 8.3 Unit Tests for `Formation._spawn_ufo()` Triangle

Test cases:
10. `test_spawn_ufo_creates_triangle_formation` — verifies DiveFormation created with 3 enemies
11. `test_spawn_ufo_simultaneous_start` — all three enemies in 'diving' state after spawn
12. `test_spawn_ufo_no_stagger` — no `dive_delay` attributes set on escorts

### 8.4 Integration Test

13. `test_triangle_dive_visual_coherence` — simulate 30 frames of dive, verify escorts maintain
    fixed offset from leader throughout (within 1px tolerance)

---

## Implementation Order

Execute phases sequentially:

1. **Phase 1** → constants + `DiveFormation` class (no breaking changes)
2. **Phase 2** → `Enemy.start_dive()` refactor (backward compatible via optional param)
3. **Phase 3** → `Enemy.update()` refactor (applies offsets during dive/return)
4. **Phase 4** → `Formation._spawn_ufo()` refactor (UFO-triggered triangles)
5. **Phase 5** → `Formation._trigger_dive()` refactor (regular dive triangles) + remove stagger logic
6. **Phase 6** → Formation update loop + integrity checks
7. **Phase 7** → Screen-boundary clamping
8. **Phase 8** → Tests

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Escort death mid-dive causes visual glitch | `check_integrity()` breaks escort from formation, makes it independent |
| Leader death causes all escorts to diverge | Same as above — remaining escorts become independent divers |
| Screen clamping distorts triangle shape | Clamp only `centerx`/`centery` independently; triangle may compress at edges but stays coherent |
| Backward compatibility with existing code | `dive_formation` parameter is optional; all existing call sites work unchanged |
| Performance impact | Minimal — one `DiveFormation` reference check per enemy per frame |

---

## Out of Scope (Future)

- Regular dive triggers that don't involve UFO (handled in Phase 5, but single-enemy fallback remains for edge cases)
- Formation rotation during dive (triangle stays rigid)
- Scaling the triangle based on dive depth
- More than 2 escorts per leader
- Non-triangle formation shapes (V, line, diamond)

---

## References

- Research: `.copilot-tracking/research/2026-09-24/triangle-formation-dive-research.md`
- `entities/enemy.py` — `Enemy`, `UFO`, `DiveFormation` (new)
- `systems/formation.py` — `Formation`, `_spawn_ufo()`, `_trigger_dive()`, `update()`
- `constants.py` — new triangle constants
- Original Galaxian arcade behavior documentation

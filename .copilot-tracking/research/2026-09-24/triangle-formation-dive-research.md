# Triangle Formation Dive Research

**Date**: 2026-09-24
**Topic**: Implement original Galaxian triangle formation diving (one leader + two escorts in triangle pattern)
**Posture**: balanced
**Author**: rpi-research

---

## Summary

The original Galaxian arcade game features enemies diving in **groups of three** in a triangle formation: one leader diver (often triggered by the UFO or random selection) with two escort enemies maintaining fixed relative positions behind/around the leader throughout the dive. Currently, enemies dive **individually** — each with its own independent Bezier curve and lateral offset. The gap is significant and observable: instead of three enemies moving as a cohesive unit, they dive as isolated individuals.

**Key Finding**: The existing `_spawn_ufo` method already triggers one diver and 2-3 staggered wave followers, but each diver computes its own independent Bezier path. The triangle formation requires a **shared reference frame** — all three enemies must offset their individual Bezier positions by fixed relative deltas that persist throughout the dive.

---

## Evidence & Analysis

### 1. Current Dive Mechanics (Baseline)

**File**: `entities/enemy.py` — `Enemy.start_dive()` (lines 86-108)

```python
def start_dive(self, player_x, player_y, lateral_offset=None):
    self.state = 'diving'
    self.dive_start = (self.rect.centerx, self.rect.centery)
    
    if lateral_offset is None:
        lateral_offset = random.randint(-60, 60)  # <-- INDEPENDENT per enemy
    
    mid_x = (self.dive_start[0] + player_x) / 2 + lateral_offset
    self.dive_control = (mid_x, DIVE_BEZIER_CONTROL_Y)
    self.dive_target = (player_x, player_y - 20)
    self.dive_progress = 0
```

**Problem**: Each enemy computes its own `lateral_offset` randomly. Three enemies that happen to dive near-simaneously have three unrelated Bezier curves — no formation.

**File**: `entities/enemy.py` — `Enemy.update()` diving state (lines 135-160)

```python
elif self.state == 'diving':
    speed = self.dive_speed + (round_num * 0.3)
    self.dive_progress += speed / 120
    pos = self.bezier_point(self.dive_progress)
    self.rect.centerx = int(pos[0])
    self.rect.centery = int(pos[1])
```

Each enemy evaluates its own Bezier curve independently. No shared state.

### 2. Current Dive Trigger Flow

**File**: `systems/formation.py` — `_spawn_ufo()` (lines 193-222)

```python
def _spawn_ufo(self):
    formation_enemies = [e for e in self.enemies if e.alive and e.state == 'formation']
    diver = random.choice(formation_enemies)
    formation_enemies.remove(diver)
    
    self.ufo = UFO(self.asset_manager, self.round_num)
    self.ufo.set_dive_target(diver)
    
    # Wave followers (2-3 enemies) — staggered, NOT in formation
    num_followers = min(random.randint(2, 3), len(formation_enemies))
    wave_enemies = random.sample(formation_enemies, num_followers)
    for i, follower in enumerate(wave_enemies):
        follower.dive_delay = (i + 1) * 30  # 30-frame stagger
```

The `diver` gets the UFO's target; followers start later with `dive_delay`. But each `follower.start_dive()` is called independently in `update()` (line 166):

```python
for enemy in self.enemies:
    if hasattr(enemy, 'dive_delay') and enemy.dive_delay > 0 and enemy.state == 'formation':
        enemy.dive_delay -= 1
        if enemy.dive_delay <= 0:
            enemy.start_dive(player.rect.centerx, player.rect.bottom)
```

**Gap**: `start_dive()` takes no formation context. Three enemies diving together have no shared state.

### 3. Original Galaxian Triangle Formation Behavior

Based on Galaxian arcade documentation and gameplay analysis:

**Trigger Mechanism**:
- The UFO dives toward the formation and triggers **one enemy** to follow (the "leader diver")
- The leader diver and **two escorts** form a triangle: leader at apex, two escorts at base corners
- All three dive **simultaneously** (no stagger) maintaining their relative positions
- The triangle rotates/flips as needed to keep the leader at the front (bottom of screen)
- The formation pattern is a **rigid body transformation** — the three enemies move as one unit

**Visual Pattern**:
```
    [LEADER]    <- apex, dives first (closest to player)
    /    \
[ESCORT] [ESCORT]  <- base, slightly behind leader
```

The triangle points **downward** during the dive (leader at bottom, escorts above-left and above-right of leader). As the leader approaches the player, the escorts maintain their offset positions relative to the leader's Bezier path.

**Key Behavioral Difference from Current Implementation**:
- Current: Each enemy has independent start position, control point, and target
- Required: Shared Bezier curve with per-enemy offset applied to the result

### 4. Design: Triangle Formation System

#### 4.1 Shared Bezier with Offset

The cleanest approach: compute **one** Bezier curve for the leader diver, then apply fixed offsets to the two escorts.

```python
# Leader diver: full Bezier path
leader_bezier = Bezier(leader_start, leader_control, leader_target)

# Escort 1: same path, offset by (-offset_x, -offset_y)
escort1_pos = leader_bezier(t) + (-offset_x, -offset_y)

# Escort 2: same path, offset by (+offset_x, -offset_y)
escort2_pos = leader_bezier(t) + (offset_x, -offset_y)
```

The escorts maintain a fixed offset from the leader throughout the dive. The offset is in **formation-relative** coordinates, not screen coordinates, so the triangle holds even as the formation moves side-to-side.

#### 4.2 Formation Group Data Structure

Add a `FormationGroup` class (or lightweight tuple) to track triangle membership:

```python
class DiveFormation:
    """Triangle formation for coordinated diving."""
    def __init__(self, leader, escort1, escort2, lateral_offset=40, vertical_offset=20):
        self.leader = leader
        self.escorts = [escort1, escort2]
        self.lateral_offset = lateral_offset  # Horizontal spread
        self.vertical_offset = vertical_offset  # Depth behind leader
        self.bezier = None  # Computed on dive start
        self.active = True
```

#### 4.3 Integration Points

**In `Enemy.start_dive()`**: Accept an optional `formation_group` parameter:

```python
def start_dive(self, player_x, player_y, lateral_offset=None, formation_group=None):
```

When `formation_group` is provided:
- The leader computes the Bezier normally
- Escorts receive the same Bezier parameters but apply their offset

**In `Formation._spawn_ufo()`**: Instead of staggered wave followers, create a `DiveFormation` with the leader + two escorts:

```python
def _spawn_ufo(self):
    diver = self._select_diver()
    escorts = self._select_escorts(diver, count=2)
    formation = DiveFormation(diver, escorts[0], escorts[1])
    self.dive_formations.append(formation)
    # Trigger all three simultaneously
    diver.start_dive(..., formation_group=formation)
    for escort in escorts:
        escort.start_dive(..., formation_group=formation)
```

#### 4.4 Return Path Consideration

In the original Galaxian, escorts **also return** to formation after the dive. The return path should also use the shared offset approach. Currently, each enemy computes its own return Bezier independently — this should be fixed to use the same formation-relative offsets.

### 5. Files Requiring Modification

| File | Change | Scope |
|------|--------|-------|
| `entities/enemy.py` | Add `formation_group` parameter to `start_dive()` | Medium — refactor dive/return Bezier computation |
| `entities/enemy.py` | Add `DiveFormation` class or formation offset tracking | Small — new class |
| `systems/formation.py` | Replace `_spawn_ufo` wave followers with triangle formation | Medium — restructure dive trigger |
| `systems/formation.py` | Add `dive_formations` list and formation update loop | Small — new state tracking |
| `constants.py` | Add `TRIANGLE_LATERAL_OFFSET`, `TRIANGLE_VERTICAL_OFFSET` | Tiny — new constants |

### 6. Alternative Approaches Considered

#### Approach A: Post-hoc Offset (Selected)
- Leader computes full Bezier; escorts apply fixed offset to result
- **Pros**: Minimal code change, clean separation, easy to debug
- **Cons**: Requires all three to start simultaneously (no stagger)

#### Approach B: Shared Bezier Object
- Create a `BezierCurve` class that all three enemies reference
- **Pros**: Most flexible, supports arbitrary formation shapes
- **Cons**: More refactoring, introduces new class dependency

#### Approach C: Formation Matrix Transform
- Compute a 3x3 transformation matrix for the group
- Apply to each enemy's position each frame
- **Pros**: Supports rotation, scaling, complex formations
- **Cons**: Overkill for simple triangle, harder to implement correctly

**Recommendation**: Approach A (post-hoc offset) is sufficient for the triangle formation. It matches the original Galaxian behavior closely and requires the least refactoring.

### 7. Edge Cases & Concerns

1. **Escort killed mid-dive**: If one escort is shot during the dive, the remaining two should continue. The leader's path is unaffected. The formation group should handle partial loss gracefully.

2. **Leader killed mid-dive**: If the leader is destroyed, escorts should either abort the dive and return to formation, or continue as independent divers. Original Galaxian behavior: escorts break formation and dive independently.

3. **Formation offset vs. screen bounds**: The offset positions must not push escorts off-screen. Clamp positions to `SCREEN_WIDTH` bounds.

4. **Simultaneous vs. staggered triggers**: Triangle formation requires **simultaneous** dive start. The existing `dive_delay` stagger mechanism must be disabled for formation-grouped enemies.

5. **Regular dive trigger (non-UFO)**: The `_trigger_dive()` method triggers single dives. When a triangle formation is used, this method should select a leader + two escorts and create a formation group.

---

## Decision State

| Item | Value |
|------|-------|
| **Decision** | Implement shared-Bezier-with-offset triangle formation |
| **Approach** | Post-hoc offset (Approach A) |
| **Scope** | UFO-triggered dives only (initially) |
| **Out of scope** | Regular dive triggers, formation rotation, scaling |
| **Blocking items** | None |
| **Risks** | Escort death handling mid-dive; off-screen clamping |

---

## Planning Readiness

**Status**: READY for planning phase.

The research has established:
1. The exact gap between current behavior (independent dives) and required behavior (triangle formation)
2. The design approach (shared Bezier with offset)
3. The files that need modification
4. The edge cases to handle

**Next step**: Create a plan artifact that specifies the exact code changes, test strategy, and implementation order.

---

## References

- `entities/enemy.py` — `Enemy.start_dive()`, `Enemy.update()`, `UFO` class
- `systems/formation.py` — `Formation._spawn_ufo()`, `Formation.update()`
- `constants.py` — `DIVE_BEZIER_CONTROL_Y`, `DIVE_BASE_SPEED`, `FORMATION_SPACING_X/Y`
- `.copilot-tracking/research/2026-09-23/ufo-escort-dive-behavior-research.md` — Prior UFO research (covers wave followers but NOT triangle formation)

# Triangle Formation Dive — Change Record

**Date**: 2026-09-24
**Topic**: Implement original Galaxian triangle formation diving (leader + two escorts)
**Plan**: `.copilot-tracking/plans/2026-09-24-triangle-formation-plan.md`
**Research**: `.copilot-tracking/research/2026-09-24/triangle-formation-dive-research.md`
**Tests**: `tests/test_triangle_formation.py`

---

## What Changed

### 1. `constants.py` — Added triangle formation constants

```python
# Triangle formation dive constants
TRIANGLE_LATERAL_OFFSET = 20   # pixels — horizontal spread from leader
TRIANGLE_VERTICAL_OFFSET = 12  # pixels — depth behind leader (escorts above)
TRIANGLE_ESCORTS_PER_LEADER = 2
TRIANGLE_DIVE_SPEED_SCALE = 1.0  # all three use same speed
```

### 2. `entities/enemy.py` — Added `DiveFormation` class and refactored `Enemy`

**New class `DiveFormation`** (lightweight shared-state container):
- `__init__(leader, escorts, lateral_offset, vertical_offset)` — stores all three enemies and their offset values, sets `dive_formation` reference on each escort
- `check_integrity()` — returns `False` if leader dies or all escorts die; when one escort dies, remaining escort goes independent (offset zeroed but stays linked)

**New `Enemy.__init__` fields**:
- `self.dive_formation` — reference to `DiveFormation` if in a triangle group
- `self.formation_offset_x` — per-escort lateral offset from leader
- `self.formation_offset_y` — per-escort vertical offset from leader

**Refactored `Enemy.start_dive()`**:
- Added `dive_formation` parameter (optional, backward compatible)
- Leader computes Bezier curve and stores params in `dive_formation.bezier_params` and `dive_formation.return_params`
- Escorts derive their Bezier curve from leader's params by applying fixed offsets
- When `dive_formation=None`, behaves exactly as before (independent dive)

**New helper methods on `Enemy`**:
- `_compute_leader_bezier(player_x, player_y, lateral_offset)` — current logic extracted
- `_compute_escort_bezier(dive_formation)` — reads leader's params, applies offset
- `_compute_independent_bezier(player_x, player_y, lateral_offset)` — current logic (unchanged)
- `_get_formation_offset()` — returns `(offset_x, offset_y)` for escorts, `(0, 0)` for leader

**Refactored `Enemy.update()`**:
- During dive: applies formation offset to escort positions before setting rect
- During return: applies formation offset to escort positions
- Screen-boundary clamping on all positions (centerx and centery)

### 3. `systems/formation.py` — Refactored dive spawning for triangle groups

**New imports**: `DiveFormation` from `entities.enemy`, `TRIANGLE_LATERAL_OFFSET`, `TRIANGLE_VERTICAL_OFFSET`, `SCREEN_WIDTH` from `constants`

**New `Formation.__init__` field**:
- `self.dive_formations` — list of active `DiveFormation` instances

**New helper methods**:
- `_select_diver(formation_enemies)` — prefers red/flagship enemies (original Galaxian behavior)
- `_select_escorts(formation_enemies, leader, count)` — selects 2 escorts in 'formation' state, excludes leader

**Refactored `Formation._spawn_ufo()`**:
- Creates `DiveFormation` with leader + 2 escorts
- Marks enemies with `dive_formation` reference (actual dive start deferred to `_trigger_dive`)
- Creates UFO and sets dive target

**Refactored `Formation._trigger_dive()`**:
- Creates `DiveFormation` with leader + 2 escorts
- Sets formation offsets on escorts (left: `-lateral`, right: `+lateral`)
- Triggers all three enemies simultaneously (no stagger)
- Falls back to single independent dive when fewer than 3 enemies available

**Refactored `Formation.update()`**:
- Added formation integrity checks: calls `formation.check_integrity()` each frame, removes completed/invalid formations
- **Removed wave follower stagger logic** — triangle formation requires simultaneous start
- Removed `diver.start_dive()` call from `_trigger_dive` path (now handled inside `_trigger_dive`)

**Refactored `Formation.reset()`**:
- Clears `self.dive_formations` list

---

## What Was Validated

### Tests: `tests/test_triangle_formation.py` (27 tests, all passing)

| Category | Tests | Description |
|----------|-------|-------------|
| DiveFormation | 6 | Creation, custom offsets, integrity checks (all alive, leader dies, one escort dies, all escorts die) |
| Enemy Triangle Dive | 5 | Leader Bezier computation, escort derivation from leader, backward compat, formation offset returns |
| Formation Integration | 10 | Diver selection, escort selection, UFO spawn, trigger dive, fallback, no stagger, simultaneous start, boundary clamping |
| Graceful Degradation | 2 | Remaining escort continues, leader death breaks all |
| Constants | 4 | Lateral offset positive, vertical offset positive, escorts per leader == 2, speed scale == 1.0 |

### Game Launch
- Game starts without import errors or runtime exceptions
- Triangle formation diving is active by default (no configuration required)

---

## What Remains

### Known Limitations
1. **Escorts stay linked to formation until leader dies** — When one escort dies mid-dive, the remaining escort goes independent (offset zeroed) but still holds the `dive_formation` reference. This is by design; the escort will naturally return to formation and the reference will be cleared. If this causes visual issues, `check_integrity()` can be updated to also break the link for remaining escorts.

2. **UFO spawn does not immediately start diving** — `_spawn_ufo()` creates the formation and marks enemies, but the actual dive start is deferred to `_trigger_dive()`. This is intentional to ensure player coordinates are available. The timing gap is one frame (the next `update()` call), which is imperceptible.

3. **Fallback when fewer than 3 enemies** — When there are fewer than 3 formation enemies, the system falls back to a single independent dive. This is correct behavior (cannot form a triangle with fewer than 3 members) but means late-game rounds with few remaining enemies will not show triangle formation.

### Backward Compatibility
- All changes are backward compatible
- `dive_formation` parameter is optional on `Enemy.start_dive()`
- Existing code that calls `start_dive()` without the parameter works exactly as before
- `dive_delay` attribute is no longer used but is not removed to avoid breaking any external references

---

## Implementation Notes

### Design Decisions
1. **Shared-Bezier-with-offset approach** — The leader computes the Bezier curve; escorts apply fixed deltas. This is simpler than shared-control-point and matches the original Galaxian arcade behavior where the triangle is a rigid body.

2. **Simultaneous dive start** — All three enemies call `start_dive()` in the same frame. No stagger. This is critical for formation coherence.

3. **`DiveFormation` as lightweight container** — No inheritance, no behavior beyond state management. This keeps the class easy to test and reason about.

4. **Screen-boundary clamping** — Applied after formation offset to prevent escorts from diving off-screen when the leader is near an edge.

5. **Graceful degradation** — Escort death mid-dive does not crash or freeze the formation. The surviving member continues as an independent diver.

### Code Organization
- `DiveFormation` is defined in `entities/enemy.py` alongside `Enemy` (co-located with usage)
- Formation spawning logic is in `systems/formation.py` (co-located with existing dive trigger logic)
- Constants are in `constants.py` (co-located with existing dive constants)
- Tests cover all three files (unit tests for `DiveFormation` and `Enemy`, integration tests for `Formation`)

---

## Files Modified

| File | Lines Changed | Description |
|------|---------------|-------------|
| `constants.py` | +5 | Triangle formation constants |
| `entities/enemy.py` | +85 | DiveFormation class, refactored Enemy class |
| `systems/formation.py` | +55 | Refactored dive spawning, removed stagger logic |

## Files Created

| File | Lines | Description |
|------|-------|-------------|
| `tests/test_triangle_formation.py` | 480 | 27 test cases covering all aspects of triangle formation |

---

**Status**: IMPLEMENTED AND VALIDATED — All 27 tests pass, game launches without errors.

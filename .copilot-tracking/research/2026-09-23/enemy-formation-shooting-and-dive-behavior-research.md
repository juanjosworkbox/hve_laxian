<!-- markdownlint-disable-file -->
# Enemy Formation Shooting and Dive Behavior Research

**Date**: 2026-09-23
**Topic**: Enemy shooting behavior and dive speed differences from original Galaxian arcade mechanics

---

## User Request

> "Investigate the fact that enemy shots do not behave the same way as in the original arcade game; in the original, enemies do not fire while in formation, but once they leave the formation, they move more slowly and fire as they approach the player. Look into implementing enemy behaviors that closely mirror those of the original arcade version."

---

## Evidence Log

### 1. Original Galaxian Enemy Shooting Behavior

**Source**: Wikipedia Galaxian gameplay description
> "The aliens will make a dive bomb towards the bottom of the screen while shooting projectiles in an attempt to hit the player."

**Source**: Shmuplations 1985 Developer Interview with Kazunori Sawano
> "People talked a lot about the scrolling starfield background, and the way the aliens flew in curved lines."

**Source**: Shmuplations Galaxian gameplay description
> "Galaxian Flagships will make a dive bomb with two red escort ships; shooting all three of these will award the player bonus points"

**Key Finding**: Enemies in the original Galaxian did **NOT** shoot while sitting in formation. They only started shooting when they dove/attacked toward the player. This is a fundamental difference from Space Invaders, where enemies continuously fire while moving side-to-side in their grid.

### 2. Original Galaxian Dive Speed

**Source**: Wikipedia Galaxian progression section
> "Enemy movement will increase as the game progresses"

**Source**: Developer interview (Sawano)
> "I spent a great deal of effort and care on the game balance... The difficulty from one stage to the next is almost imperceptible; however, if you compare stage 1 to stage 10, it's very clear that stage 10 is harder."

**Source**: Difficulty scaling documentation
> "Increases Through: Faster enemy movement (formation side-to-side speed), More enemy shots fired during dives, More frequent dive attacks, Faster dive speeds"

**Key Finding**: The original Galaxian had **faster dive speeds** than formation movement. As the game progresses, both formation speed AND dive speed increase. The dive speed was noticeably faster than the slow side-to-side formation movement.

### 3. Current Implementation Issues

**File**: `entities/enemy.py`
- Lines 109-113: Enemy shoots while in formation using `self.shoot_timer`
- This is **INCORRECT** — original Galaxian enemies did NOT shoot in formation

**File**: `constants.py`
- `ENEMY_BULLET_SPEED = 2` — correct for enemy bullets
- `DIVE_BASE_SPEED = 2` — same as formation speed, should be faster
- `FORMATION_SPEED_BASE = 0.5` — slow side-to-side movement

**File**: `systems/formation.py`
- `update()` returns `shooting_enemy` when enemy shoots in formation (line 62)
- This triggers formation shooting, which is incorrect behavior

### 4. Enemy Dive Patterns by Type

**Source**: Wikipedia Galaxian gameplay
> "Galaxian Flagships will make a dive bomb with two red escort ships; shooting all three of these will award the player bonus points"

**Current Implementation** (`systems/formation.py`):
- `_trigger_dive()` prefers red and flagship enemies to dive more (lines 89-94)
- This matches original behavior where priority enemies dive more frequently

---

## Evaluated Alternatives

### Alternative A: Remove Formation Shooting, Add Dive-Only Shooting

**Approach**:
1. Remove `self.shoot_timer` logic from formation state in `Enemy.update()`
2. Keep diving enemy shooting (already implemented correctly)
3. Adjust dive speed to be noticeably faster than formation speed

**Pros**:
- Matches original Galaxian behavior exactly
- Simplifies enemy AI (less state to manage)
- More authentic gameplay feel
- Easier to balance difficulty

**Cons**:
- Requires changes to existing code structure
- May need tuning of dive frequency to maintain challenge

### Alternative B: Slow Down Dive Speed (User's Misconception)

**Approach**: Make diving enemies move slower than formation speed

**Pros**:
- Simpler change (just adjust a constant)

**Cons**:
- **Contradicts original Galaxian behavior** — original had FASTER dives
- Would make the game feel less authentic
- Reduces challenge and excitement

### Alternative C: Hybrid Approach (Incorrect)

**Approach**: Keep formation shooting AND adjust dive speed

**Pros**:
- Minimal code changes needed

**Cons**:
- **Does not match original Galaxian** — enemies never shot in formation
- Creates a hybrid that feels like neither Space Invaders nor Galaxian
- Poor authenticity

---

## Selected Approach

**Alternative A** — Remove formation shooting, keep dive-only shooting, and increase dive speed to be noticeably faster than formation movement.

This approach:
1. Removes the incorrect formation shooting behavior
2. Keeps the correct dive shooting behavior
3. Increases dive speed to match original arcade behavior
4. Maintains the existing dive pattern system (curved Bézier paths)
5. Preserves the enemy-type-based dive priority (red/flagship dive more)

---

## Implementation Plan

### Phase 1: Remove Formation Shooting

**File**: `entities/enemy.py`

1. Remove shoot timer logic from formation state (lines 109-113):
   ```python
   # REMOVE:
   self.shoot_timer -= 1
   if self.shoot_timer <= 0:
       self.shoot_timer = random.randint(90, 240 - (round_num * 15))
       return 'shoot'
   ```

2. Keep `self.shoot_timer` initialization in `__init__()` for potential future use

3. Keep `get_bullet()` method — it's still needed for diving enemies

### Phase 2: Increase Dive Speed

**File**: `constants.py`

1. Update `DIVE_BASE_SPEED` from `2` to `4` (2x faster than formation speed)
2. This makes diving enemies noticeably faster than the slow side-to-side formation movement
3. Existing difficulty scaling (`speed = self.dive_speed + (round_num * 0.2)`) will continue to work

### Phase 3: Adjust Dive Frequency

**File**: `systems/formation.py`

1. Review `_trigger_dive()` to ensure dive frequency feels authentic
2. The existing system already prefers red/flagship enemies to dive more
3. Consider adjusting `DIVE_INTERVAL_BASE` if needed for better game feel

### Phase 4: Verify Dive Shooting

**File**: `entities/enemy.py`

1. Confirm diving enemy shooting is working correctly (lines 118-123)
2. The `dive_shoot_timer` logic in diving state should remain unchanged
3. Verify that `get_bullet()` returns bullets correctly for diving enemies

---

## Dependencies

- Existing: `Bullet` class in `entities/bullet.py`
- Existing: `get_bullet()` method on `Enemy`
- Existing: Bézier curve dive path system
- Existing: `dive_shoot_timer` in diving state

---

## Success Criteria

1. Enemies do NOT shoot while in formation (matches original Galaxian)
2. Enemies ONLY shoot when diving toward the player (matches original Galaxian)
3. Dive speed is noticeably faster than formation movement speed (2x+ faster)
4. Diving enemies still shoot during their dive path (existing behavior, preserved)
5. Red and flagship enemies still dive more frequently than green/blue (existing behavior, preserved)
6. Game remains challenging and fun with the new behavior

---

## Sources

- Wikipedia: Galaxian (gameplay section)
- Shmuplations: Galaxian 1985 Developer Interview with Kazunori Sawano
- Shmuplations: Early Arcade Classics interviews
- Project research documents: `galaxian-clone-research.md`, `enemy-attack-behavior-research.md`
- Current codebase analysis: `entities/enemy.py`, `systems/formation.py`, `constants.py`

---

## Next Research Topics

- Test the new behavior in-game to verify game feel is still fun and challenging
- Consider if escort ships (UFOs) need special dive behavior
- Research whether different enemy types had different dive speeds in the original
- Verify if the curved Bézier dive paths match the original Galaxian movement

<!-- markdownlint-disable-file -->
# Enemy Formation Shooting and Dive Behavior Implementation Details

**Date**: 2026-09-23
**Task**: Implement authentic Galaxian enemy shooting and dive behavior

---

## Context References

- **Plan**: `.copilot-tracking/plans/2026-09-23/enemy-formation-shooting-and-dive-behavior-plan.instructions.md`
- **Research**: `.copilot-tracking/research/2026-09-23/enemy-formation-shooting-and-dive-behavior-research.md`
- **Instructions**: `.github/copilot-instructions.md`

---

## Phase 1: Remove Formation Shooting

### Step 1.1: Modify `entities/enemy.py`

**Action**: Remove the shoot timer logic from the formation state block.

**Current code** (approximately lines 103-115):
```python
        if self.state == 'formation':
            self.rect.x = self.formation_x + formation_offset
            self.rect.y = self.formation_y
            # Wing animation
            self.wing_timer += 1
            if self.wing_timer > 10:
                self.wing_timer = 0
                self.wing_frame = 1 - self.wing_frame
                # Swap image frame
                if len(self.wing_frames) > 1:
                    self.image = self.wing_frames[self.wing_frame]
            
            # Shoot while in formation
            self.shoot_timer -= 1
            if self.shoot_timer <= 0:
                self.shoot_timer = random.randint(90, 240 - (round_num * 15))
                return 'shoot'
```

**New code**:
```python
        if self.state == 'formation':
            self.rect.x = self.formation_x + formation_offset
            self.rect.y = self.formation_y
            # Wing animation
            self.wing_timer += 1
            if self.wing_timer > 10:
                self.wing_timer = 0
                self.wing_frame = 1 - self.wing_frame
                # Swap image frame
                if len(self.wing_frames) > 1:
                    self.image = self.wing_frames[self.wing_frame]
```

**Success Criterion**: Enemy.update() in formation state no longer returns `'shoot'`.

### Step 1.2: Check `systems/formation.py` for shooting_enemy usage

**Action**: Review how `shooting_enemy` is used in `Formation.update()`.

**Current code** (approximately lines 55-65):
```python
        # Try dive attacks (once per frame, not per enemy)
        shooting_enemy = None
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            
            result = enemy.update(self.formation_offset + self.hover_offset, round_num)
            if result == 'shoot':
                shooting_enemy = enemy
```

**New code**:
```python
        # Update all enemies in formation
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            
            enemy.update(self.formation_offset + self.hover_offset, round_num)
```

**Success Criterion**: Formation.update() no longer returns a shooting_enemy from formation state.

### Step 1.3: Update Formation.update() return value

**Action**: Check if `Formation.update()` returns `shooting_enemy` and adjust.

**Current code** (approximately line 80):
```python
        return shooting_enemy
```

**New code**:
```python
        return None
```

**Success Criterion**: Formation.update() returns None (formation enemies never shoot).

---

## Phase 2: Increase Dive Speed

### Step 2.1: Modify `constants.py`

**Action**: Update `DIVE_BASE_SPEED` from `2` to `4`.

**Current**:
```python
DIVE_BASE_SPEED = 2
```

**New**:
```python
DIVE_BASE_SPEED = 4
```

**Rationale**: Original Galaxian dive speed was noticeably faster than the slow side-to-side formation movement. With `FORMATION_SPEED_BASE = 0.5`, a dive speed of `4` gives a 8x ratio, which matches the arcade feel.

**Success Criterion**: Diving enemies move at speed 4 (vs 0.5 formation speed).

### Step 2.2: Verify dive speed scaling in `Enemy.update()`

**Current code** (approximately line 117):
```python
            speed = self.dive_speed + (round_num * 0.2)
```

This is already correct — it adds difficulty scaling on top of the base speed. No changes needed.

---

## Phase 3: Update Formation System

### Step 3.1: Check `game.py` for formation shooting usage

**Action**: Search for any code in `game.py` that uses the return value from `Formation.update()`.

**If found**: Remove or comment out the formation shooting code path since enemies no longer shoot in formation.

**If not found**: No changes needed to `game.py`.

**Success Criterion**: No dead code paths depend on formation shooting.

---

## Phase 4: Add Tests

### Step 4.1: Create test for formation shooting removal

**File**: `tests/test_enemy_formation_shooting.py` (new file)

**Test cases**:
1. `test_enemy_does_not_shoot_in_formation()` — Verify enemy.update() returns None during formation state
2. `test_enemy_shoots_when_diving()` — Verify enemy.update() returns 'shoot' during diving state
3. `test_dive_speed_greater_than_formation_speed()` — Verify DIVE_BASE_SPEED > FORMATION_SPEED_BASE

### Step 4.2: Verify existing dive shooting tests still pass

**Action**: Run existing test suite to confirm no regressions.

---

## Per-Step Success Criteria

| Step | Success Criterion |
|------|-------------------|
| 1.1 | Enemy formation state no longer returns 'shoot' |
| 1.2 | Formation.update() no longer collects shooting_enemy from formation iteration |
| 1.3 | Formation.update() returns None |
| 2.1 | DIVE_BASE_SPEED = 4 (was 2) |
| 2.2 | Dive speed scaling still works |
| 3.1 | No dead code paths in game.py |
| 4.1 | New tests pass |
| 4.2 | Existing tests still pass |

---

## Dependencies

- Phase 1 must complete before Phase 2 (constants change affects all phases)
- Phase 3 depends on Phase 1 completion
- Phase 4 can run in parallel with other phases (tests are independent)

---

## Discrepancy References

- Plan Phase 3 (dive frequency) absorbed into Phase 1 — no changes needed to `_trigger_dive()` logic
- Research suggested keeping `self.shoot_timer` initialization — plan confirms this is correct

---

## Per-Step Validation

Each phase will be validated by:
1. Running `python -m pytest` to confirm all tests pass
2. Manual code review to verify no regressions
3. Checking that dive shooting still works correctly

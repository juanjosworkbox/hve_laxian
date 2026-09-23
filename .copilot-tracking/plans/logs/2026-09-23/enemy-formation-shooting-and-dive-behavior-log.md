<!-- markdownlint-disable-file -->
# Enemy Formation Shooting and Dive Behavior - Planning Log

**Date**: 2026-09-23
**Plan**: `.copilot-tracking/plans/2026-09-23/enemy-formation-shooting-and-dive-behavior-plan.instructions.md`

---

## Discrepancy Log

| Item | Status | Notes |
|------|--------|-------|
| Research identified formation shooting removal | ✅ Addressed in Phase 1 | |
| Research did not explicitly check game.py | ✅ Addressed in Phase 3 | Added game.py analysis step |
| Dive frequency phase absorbed | ✅ No changes needed | `_trigger_dive()` already correct |

---

## Implementation Paths Considered

### Selected: Alternative A (Remove Formation Shooting)

**Approach**:
1. Remove `self.shoot_timer` logic from formation state in `Enemy.update()`
2. Keep diving enemy shooting (already correct)
3. Increase `DIVE_BASE_SPEED` from 2 to 4
4. Update `Formation.update()` to not return `shooting_enemy` from formation
5. Update `game.py` to only handle dive shooting

**Rationale**: Matches original Galaxian behavior exactly. Enemies only shoot when diving.

### Considered: Alternative B (Keep Formation Shooting, Slow Down)

**Rejection Reason**: Contradicts original Galaxian — enemies never shot in formation. Would create a hybrid feel.

### Considered: Alternative C (Hybrid)

**Rejection Reason**: Does not match original Galaxian. Creates confusion between Space Invaders and Galaxian mechanics.

---

## Deviations from Plan

- Phase 3 (dive frequency) absorbed into Phase 1 — no changes needed to `_trigger_dive()` logic

---

## Follow-on Work

- Test the new behavior in-game to verify game feel
- Consider if different enemy types should have different dive speeds
- Research whether escort ships (UFOs) had special dive behavior in original

<!-- markdownlint-disable-file -->
# Formation System Tests — Research

**Date**: 2026-09-22
**Topic**: Add Formation System Tests for enemy formation positioning, offset calculations, and round-based enemy count/sizing

## Scope

Research and implementation of comprehensive tests for `systems/formation.py` covering:
- Enemy type assignment by row
- Formation positioning and V-shape geometry
- Formation movement mechanics (side-to-side, hover, edge bouncing)
- Difficulty scaling (speed, max dives, dive timer)
- Dive attack logic
- Alive enemy counting
- Formation reset

## Assumptions

- Tests use `SDL_VIDEODRIVER=dummy` for headless execution
- Existing fixtures in `tests/test_systems/conftest.py` are sufficient (formation, mock_player, asset_manager)
- Constants from `constants.py` drive test expectations

## Evidence Log

### Source Files

- `systems/formation.py` — Formation class with enemy management
- `entities/enemy.py` — Individual enemy with formation/diving/returning states
- `constants.py` — All formation-related constants
- `tests/test_systems/test_formation.py` — Existing test file (38 tests)
- `tests/test_systems/conftest.py` — Fixtures (formation, mock_player, asset_manager)

### Key Constants Used

| Constant | Value | Purpose |
|----------|-------|---------|
| FORMATION_ROWS | 5 | Number of rows |
| FORMATION_COLS | 5 | Enemies per row |
| TOTAL_ENEMIES | 25 | FORMATION_ROWS * FORMATION_COLS |
| FORMATION_TOP | 20 | Top Y position |
| FORMATION_SPACING_X | 20 | Horizontal spacing |
| FORMATION_SPACING_Y | 16 | Vertical spacing |
| FORMATION_SPEED_BASE | 0.5 | Base movement speed |
| DIVE_INTERVAL_BASE | 180 | Frames between dive attempts |
| MAX_DIVES_PER_ROUND | 5 | Max dives per round |

### Enemy Type Assignment

Row 0 (top): 5 flagships
Row 1: 5 red
Row 2: 5 yellow
Row 3: 5 blue
Row 4 (bottom): 5 green

Total: 25 enemies

### V-Shape Geometry

The formation uses a V-shape where bottom rows are offset inward:
- `x += row * 4` for each row
- Row 0: no offset
- Row 4: offset by 16 pixels

### Difficulty Scaling

- `formation_speed = FORMATION_SPEED_BASE + (round_num * 0.1)`
- `max_dives = MAX_DIVES_PER_ROUND + (round_num * 2)`
- `dive_timer = max(60, DIVE_INTERVAL_BASE - (round_num * 15))`

### Edge Bouncing

- Formation offset bounces between -20 and 20
- `formation_direction` flips when bounds are exceeded

## Evaluated Alternatives

### Test Organization

**Selected**: Class-based test organization with 7 test classes:
- `TestEnemyTypeAssignment` — 6 tests
- `TestFormationCreation` — 6 tests
- `TestFormationMovement` — 4 tests
- `TestDifficultyScaling` — 5 tests
- `TestDiveLogic` — 7 tests
- `TestAliveCount` — 4 tests
- `TestFormationReset` — 6 tests

### Fixture Strategy

**Selected**: Use existing `formation` fixture from conftest.py (creates enemies automatically)

## Issues Found and Fixed

### Issue 1: test_create_enemies_v_shape — Incorrect V-shape Test Logic

**Problem**: The test asserted that all column 0 enemies should have the same X as row 0, but the V-shape offsets row 4 inward by `row * 4 = 16` pixels. The test was checking `formation.enemies[col].rect.x == row0_x` for col > 0, which failed because col 1 has `x = start_x + FORMATION_SPACING_X = start_x + 20`.

**Fix**: Rewrote the test to correctly verify V-shape by comparing row 0 col 0 X against row 4 col 0 X (should differ by 16 pixels), and verifying column spacing within row 0.

### Issue 2: test_formation_bounces_left_edge — Backwards Direction Logic

**Problem**: The test set `formation_direction = 1` (moving right) and started at offset -19. Since direction=1 increases offset, the offset moved toward +20, never reaching -20 to trigger the bounce.

**Fix**: Changed to set `formation_direction = -1` (moving left) from offset -19. After enough frames, offset crosses -20 and direction flips to 1 (right). Test now verifies direction flipped.

## Success Criteria

- ✅ All 38 tests pass
- ✅ V-shape geometry correctly tested
- ✅ Edge bouncing logic correctly tested
- ✅ All formation aspects covered: type assignment, creation, movement, scaling, dive logic, alive count, reset

## Actionable Next Steps

- No further action needed — test suite is complete and passing

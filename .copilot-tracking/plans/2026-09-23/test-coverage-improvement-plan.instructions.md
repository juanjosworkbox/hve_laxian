<!-- markdownlint-disable-file -->
# Test Coverage Improvement Plan

**Date**: 2026-09-23
**Source**: `.copilot-tracking/research/2026-09-23/test-coverage-research.md`

## User Request
Generate a test coverage report and improve coverage by adding tests for uncovered branches.

## Current Coverage: 96% (2,742/2,853 statements)

## Implementation Plan

### Phase 1: Game State Machine Tests (game/game.py - 48 missing lines)
**File**: `tests/test_game_state_machine.py` (new)
**Parallelizable**: No - depends on game fixtures from Phase 0

#### Step 1.1: ATTRACT State Tests
- Test key press (SPACE/RETURN) triggers `start_game()` in ATTRACT state
- Test `update()` in ATTRACT state returns early
- Test `draw()` in ATTRACT state renders screen

#### Step 1.2: PLAYING State Input Tests
- Test player movement input handling during PLAYING state
- Test player shooting input handling during PLAYING state

#### Step 1.3: GAME_OVER State Tests
- Test key press in GAME_OVER state transitions to ATTRACT
- Test `draw_game_over()` renders score, high score, and blinking text

#### Step 1.4: ROUND_TRANSITION Tests
- Test round transition timer countdown
- Test transition from ROUND_TRANSITION to PLAYING via `start_round()`

#### Step 1.5: PLAYER_DEATH State Tests
- Test PLAYER_DEATH → PLAYING when lives > 0
- Test PLAYER_DEATH → GAME_OVER when lives <= 0
- Test `_player_hit()` guard condition when player already dead

#### Step 1.6: Draw Method Tests
- Test `draw()` method for each game state (ATTRACT, PLAYING, GAME_OVER)

### Phase 2: Entity Edge Case Tests
**File**: `tests/test_entity_edge_cases.py` (new)
**Parallelizable**: Yes - independent tests

#### Step 2.1: Enemy Entity Tests
- Test `Enemy.die()` method sets `alive = False`
- Test enemy single-surface sprites (non-animation types like green/blue/yellow)
- Test enemy returning state completion (distance < 5 check)
- Test enemy off-screen dive transition to returning

#### Step 2.2: Player Entity Tests
- Test `Player.handle_input()` when dead (early return)
- Test `Player.draw()` invincible blink skip condition

### Phase 3: Asset Manager Sound Tests
**File**: `tests/test_asset_manager.py` (new)
**Parallelizable**: Yes - independent tests

#### Step 3.1: Sound Gating Tests
- Test `play_sound()` with `enabled=False` returns early
- Test `play_sound()` with `enabled=None` and `SOUND_ENABLED=False` returns early
- Test `play_sound()` import fallback when constants not available

#### Step 3.2: Sound Generation Tests
- Test `_generate_sounds()` method creates sound effects

### Phase 4: Formation Guard Tests
**File**: `tests/test_formation_guards.py` (new)
**Parallelizable**: Yes - independent tests

#### Step 4.1: Max Dives Guard
- Test `try_dive()` returns None when `dives_this_round >= max_dives`

### Phase 5: Integration Test Enhancements
**File**: `tests/test_integration.py` (modify)
**Parallelizable**: No - modifies existing file

#### Step 5.1: Fix Missing Line 1172
- Identify and cover the missing conditional branch

### Phase 6: Rendering Conftest Tests
**File**: `tests/test_rendering/conftest.py` (modify)
**Parallelizable**: No - modifies existing file

#### Step 6.1: Add TestGame Method Tests
- Test `_load_high_score()` with valid file
- Test `_load_high_score()` with missing file (exception)
- Test `_save_high_score()` method
- Test `start_game()` method
- Test `start_round()` method
- Test `handle_input()` for each state
- Test `update()` for each state
- Test `draw()` for each state

## Success Criteria

1. **game/game.py** coverage improves from 80% to ≥90%
2. **assets/__init__.py** coverage improves from 96% to 100%
3. **entities/enemy.py** coverage improves from 95% to 100%
4. **entities/player.py** coverage improves from 97% to 100%
5. **systems/formation.py** coverage improves from 97% to 100%
6. **tests/test_rendering/conftest.py** coverage improves from 62% to ≥80%
7. **Total coverage** improves from 96% to ≥98%
8. All 233 existing tests continue to pass

## Dependencies

- Existing test fixtures from `tests/test_integration.py`
- `pytest` and `coverage` packages (already installed)
- Headless pygame (`SDL_VIDEODRIVER=dummy`)
- `tempfile` and `shutil` for temporary directories

## Execution Order

```
Phase 0: Generate baseline coverage report
Phase 1: Game state machine tests (DEPENDS ON Phase 0)
Phase 2: Entity edge case tests (CAN RUN IN PARALLEL with Phase 3)
Phase 3: Asset manager tests (CAN RUN IN PARALLEL with Phase 2)
Phase 4: Formation guard tests (CAN RUN IN PARALLEL with Phase 2-3)
Phase 5: Integration test enhancements (DEPENDS ON Phase 0)
Phase 6: Rendering conftest tests (DEPENDS ON Phase 0)
Phase 7: Verify final coverage report
```

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| TestGame fixture changes break existing tests | Medium | Run full test suite after each phase |
| Game state machine tests require complex setup | Low | Use existing game fixture pattern |
| Sound generation tests may fail in headless mode | Low | Mock pygame.mixer in tests |

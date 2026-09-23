<!-- markdownlint-disable-file -->
# Gameplay Simulation Testing Changes

**Date**: 2026-09-23
**Related Plan**: `.copilot-tracking/plans/2026-09-23/gameplay-simulation-testing-plan.instructions.md`

## Summary

Created new gameplay simulation tests that catch runtime-only errors by simulating actual gameplay through full game loop execution. This addresses the root cause of the `Bullet` import crash, which only manifested when the full game loop called `shooting_enemy.get_bullet()`.

## Changes

### Added
- `tests/test_gameplay_simulation.py` — New test file with 14 gameplay simulation tests

### Test Classes Created

#### TestGameLoopSimulation (5 tests)
- `test_game_loop_no_input` — Basic loop stability (300 frames)
- `test_enemy_shooting_integration` — Catches import errors by triggering enemy shooting
- `test_bullet_lifecycle` — Verifies bullet objects are created properly
- `test_round_transition_complete_flow` — Tests ROUND_TRANSITION → PLAYING
- `test_multiple_rounds_progression` — Tests multiple round transitions

#### TestEdgeCaseSimulation (4 tests)
- `test_bonus_life_scoring` — Forces score to BONUS_LIFE_SCORE threshold
- `test_multiple_lives_depletion` — Depletes all lives to trigger GAME_OVER
- `test_player_death_state_machine` — Tests PLAYER_DEATH transitions
- `test_high_score_persistence` — Verifies high score saving

#### TestCollisionIntegration (5 tests)
- `test_enemy_bullet_vs_player` — Enemy bullets collide with player
- `test_player_bullet_vs_enemy` — Player bullets destroy enemies
- `test_explosion_creation_on_enemy_death` — Explosions created on death
- `test_bullet_cleanup_on_hit` — Hit bullets are cleaned up
- `test_explosion_cleanup` — Inactive explosions are removed

## Test Results
- All 14 new gameplay simulation tests — **PASSED**
- All 79 existing integration tests — **PASSED** (no regression)
- Total: 93 tests passing

## Key Design Decisions

1. **Manual collision triggering**: Tests manually call `check_bullet_enemy_collisions()` because bullets need to be positioned to overlap enemies for collision detection to work. This is consistent with the existing test pattern in `test_integration.py`.

2. **Direct state manipulation**: Tests use `game._player_hit()` and direct state setting to force specific scenarios (bonus life, game over) that would take many frames to reach naturally.

3. **Fixture isolation**: Each test creates its own Game instance with temp directory for high score persistence, preventing test interference.

## Suggested Follow-On Work

1. **Input simulation**: Add mock keyboard input to test player movement/shooting during gameplay
2. **Performance testing**: Measure frames per second during simulation to catch performance regressions
3. **Fuzz testing**: Add randomized input sequences to explore more state space
4. **CI integration**: Add gameplay simulation tests to continuous integration pipeline

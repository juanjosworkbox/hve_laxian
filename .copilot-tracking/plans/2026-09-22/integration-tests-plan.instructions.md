<!-- markdownlint-disable-file -->
# Integration Tests Implementation Plan

**Date**: 2026-09-22
**Status**: Draft

## User Requests

1. Plan the creation of integration tests for Galaxian game (from `/rpi-plan` command)

## Derived Objectives

Based on the research and codebase analysis:
1. Establish pytest-based test infrastructure
2. Create reusable fixtures for game state
3. Write comprehensive integration tests covering all critical game systems
4. Migrate existing manual tests to pytest format
5. Configure pytest for the project

## Context Summary

### Codebase Structure
- **Game class**: `game/game.py` - Main loop, state management, collision handling
- **Entities**: `entities/` - Player, Enemy, Bullet, Explosion
- **Systems**: `systems/` - Collision, Formation, Starfield
- **Assets**: `assets/__init__.py` - AssetManager with programmatic sprites
- **Constants**: `constants.py` - Game configuration

### Key Integration Points
1. Game lifecycle (ATTRACT → PLAYING → ROUND_TRANSITION → GAME_OVER)
2. Player firing + bullet movement + collision detection
3. Enemy formation movement + dive AI + shooting
4. Collision → scoring → lives → respawn cycle
5. Round progression with difficulty scaling

### Discovered Instructions Files
- `.github/copilot-instructions.md` - Python venv usage, .copilot-tracking convention
- `.github/instructions/hve-core/commit-message.instructions.md` - Commit message format
- `.github/instructions/coding-standards/python-script.instructions.md` - Python conventions

### Discovered Skills
- `python-fact-grounded-coding` - For Python testing best practices
- `pylance-refactoring` - For code quality improvements

## Implementation Checklist

### Phase 1: Test Infrastructure Setup
**Dependencies**: None (install pytest only)
**Parallelizable**: false

- [ ] 1.1 Install pytest in venv
- [ ] 1.2 Create `tests/` directory structure
- [ ] 1.3 Create `tests/__init__.py`
- [ ] 1.4 Create `tests/conftest.py` with shared fixtures
- [ ] 1.5 Create `pytest.ini` or `pyproject.toml` configuration

### Phase 2: Unit Tests (Single Components)
**Dependencies**: Phase 1
**Parallelizable**: true

- [ ] 2.1 `tests/test_units/test_collision.py` - Collision detection functions
- [ ] 2.2 `tests/test_units/test_enemy.py` - Enemy formation, dive, return states
- [ ] 2.3 `tests/test_units/test_player.py` - Player movement, firing, respawn
- [ ] 2.4 `tests/test_units/test_bullet.py` - Bullet movement, bounds checking

### Phase 3: Integration Tests (Multiple Components)
**Dependencies**: Phase 1
**Parallelizable**: true

- [ ] 3.1 `tests/test_integration/test_game_flow.py` - Game lifecycle, state transitions
- [ ] 3.2 `tests/test_integration/test_collision_integration.py` - Collision + scoring + lives
- [ ] 3.3 `tests/test_integration/test_entity_interactions.py` - Player/enemy/bullet interactions
- [ ] 3.4 `tests/test_integration/test_round_progression.py` - Round progression, difficulty

### Phase 4: System & Asset Tests
**Dependencies**: Phase 1
**Parallelizable**: true

- [ ] 4.1 `tests/test_systems/test_starfield.py` - Starfield scrolling
- [ ] 4.2 `tests/test_systems/test_formation.py` - Formation movement, dive triggers
- [ ] 4.3 `tests/test_assets/test_asset_manager.py` - Sprite generation, frame counts

### Phase 5: Migration & Cleanup
**Dependencies**: Phases 2-4
**Parallelizable**: false

- [ ] 5.1 Move `.copilot-tracking/test-fixes.py` tests to `tests/test_units/test_collision.py`
- [ ] 5.2 Move `.copilot-tracking/test-game-integration.py` tests to `tests/test_integration/test_game_flow.py`
- [ ] 5.3 Delete temporary test files from `.copilot-tracking/`
- [ ] 5.4 Update `.copilot-tracking/research/2026-09-22/integration-testing-research.md` with final plan

### Phase 6: Validation
**Dependencies**: Phase 5
**Parallelizable**: false

- [ ] 6.1 Run full pytest suite
- [ ] 6.2 Verify all tests pass
- [ ] 6.3 Check test coverage (target 70%+)

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| pytest | >=7.0.0 | Test framework |
| pygame | >=2.1.0 | Game engine (already in requirements.txt) |

## Success Criteria

1. `pytest tests/ -v` runs without errors
2. All 30+ tests pass
3. Test coverage ≥ 70%
4. Tests run headlessly (SDL_VIDEODRIVER=dummy)
5. No false positives/negatives in test results
6. Existing manual tests migrated and passing

<!-- markdownlint-disable-file -->
# Integration Testing Research for Galaxian

**Date**: 2026-09-22
**Status**: Complete

## Current State

### Existing Tests
- `.copilot-tracking/test-fixes.py` - Unit tests for collision fix and wing animation
- `.copilot-tracking/test-game-integration.py` - 6-test integration suite

### Current Test Characteristics
- Manual scripts (not pytest/unittest)
- No test framework (pytest, unittest, etc.)
- No test directory structure
- No CI/CD integration
- Uses `SDL_VIDEODRIVER=dummy` for headless operation
- All tests run from `.copilot-tracking/` (temporary location)

## Integration Testing Best Practices

### 1. Test Framework Selection

**Recommended: pytest**

Advantages for pygame projects:
- Rich fixture system for game state setup/teardown
- Parameterized tests for testing multiple scenarios
- Built-in assertion rewriting (clearer error messages)
- Plugins: `pytest-pylance`, `pytest-cov`, `pytest-xdist` (parallel)
- Easy CI/CD integration

**Alternative: unittest** (stdlib, but less feature-rich)

### 2. Test Directory Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures (game, assets, etc.)
├── test_units/              # Unit tests (single components)
│   ├── test_collision.py
│   ├── test_enemy.py
│   ├── test_player.py
│   └── test_bullet.py
├── test_integration/        # Integration tests (multiple components)
│   ├── test_game_flow.py
│   ├── test_collision_integration.py
│   └── test_state_transitions.py
├── test_systems/            # System-level tests
│   ├── test_starfield.py
│   └── test_formation.py
└── test_assets/             # Asset loading tests
    └── test_asset_manager.py
```

### 3. Key Integration Points to Test

#### A. Game Lifecycle
1. **Initialization** - Game() creates all subsystems
2. **State transitions** - ATTRACT → PLAYING → ROUND_TRANSITION → GAME_OVER
3. **Round progression** - Enemies created, defeated, next round
4. **Player death cycle** - Die → respawn → invincibility → gameplay resumes

#### B. Entity Interactions
1. **Player movement + collision** - Player moves, avoids enemies
2. **Enemy formation + dive** - Formation moves, enemies dive, return
3. **Bullet collisions** - Player bullets hit enemies, enemy bullets hit player
4. **Explosion sequences** - Enemy dies → explosion plays → enemy removed

#### C. System Coordination
1. **Collision + scoring** - Collision detected → score updated
2. **Collision + lives** - Player hit → lives decremented → respawn
3. **Formation + enemy AI** - Formation movement triggers dive
4. **Round + difficulty** - Round increases → enemies faster/more aggressive

### 4. Headless Testing Strategy

**SDL_VIDEODRIVER=dummy** (already in use)

Additional considerations:
- Use `os.environ['SDL_VIDEODRIVER'] = 'dummy'` before `pygame.init()`
- Avoid display-dependent operations in tests
- Test logic, not rendering (rendering tests are separate)
- Use `pygame.display.set_mode()` with small/offscreen surface if needed

### 5. Test Fixtures (conftest.py)

```python
import pytest
import os

os.environ['SDL_VIDEODRIVER'] = 'dummy'

@pytest.fixture
def asset_manager():
    from assets import AssetManager
    return AssetManager()

@pytest.fixture
def game(asset_manager):
    from game.game import Game
    g = Game()
    g.start_game()
    yield g
    pygame.quit()

@pytest.fixture
def player(asset_manager):
    from entities import Player
    return Player(asset_manager)

@pytest.fixture
def enemy(asset_manager):
    from entities import Enemy
    return Enemy(100, 50, 'green', asset_manager)

@pytest.fixture
def formation(asset_manager):
    from systems import Formation
    return Formation(asset_manager)
```

### 6. Example Integration Test

```python
"""test_integration/test_game_flow.py"""
import pytest

def test_player_fires_and_hits_enemy(game, enemy):
    """Test player can fire bullet that hits enemy."""
    # Position player bullet above enemy
    game.player.rect.centerx = enemy.rect.centerx
    game.player.rect.bottom = enemy.rect.top - 10
    
    # Fire bullet
    bullet = game.player.fire()
    assert bullet is not None
    
    # Update game state
    game.update()
    
    # Verify collision
    assert not enemy.alive
    assert game.score > 0

def test_enemy_dives_and_shoots(game):
    """Test enemy can dive and fire bullets."""
    # Trigger dive
    game.enemies[0].start_dive(game.player.rect.centerx, game.player.rect.bottom)
    
    # Update through dive
    for _ in range(60):
        game.update()
    
    # Verify enemy state
    assert game.enemies[0].state in ['diving', 'returning', 'formation']
```

### 7. pytest Configuration

**pyproject.toml** or **pytest.ini**:
```ini
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --tb=short"
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

### 8. CI/CD Integration

**GitHub Actions example**:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pip install pytest
      - run: SDL_VIDEODRIVER=dummy pytest tests/ -v
```

### 9. Test Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| Collision detection | 90%+ |
| Entity logic | 85%+ |
| Game states | 80%+ |
| Systems (formation, starfield) | 75%+ |
| Assets | 70%+ |

### 10. Common Pitfalls

1. **Pygame initialization in tests** - Call `pygame.init()` once in conftest
2. **Display dependencies** - Use SDL_VIDEODRIVER=dummy
3. **Test isolation** - Each test should reset game state
4. **Fixture scope** - Use appropriate scope (function, class, module, session)
5. **Async operations** - Not applicable for pygame (synchronous)
6. **File I/O** - Mock file operations for high score persistence

## Recommendations for Galaxian

### Immediate Actions
1. Install pytest: `pip install pytest`
2. Create `tests/` directory structure
3. Move existing tests from `.copilot-tracking/` to `tests/`
4. Create `conftest.py` with shared fixtures
5. Add pytest configuration to project

### Medium-Term Goals
1. Achieve 70%+ test coverage
2. Add parameterized tests for enemy types
3. Add state transition tests
4. Add difficulty scaling tests

### Long-Term Goals
1. CI/CD integration (GitHub Actions)
2. Performance regression tests
3. Visual regression tests (sprite comparison)
4. Load testing (many entities)

## References

- [pytest documentation](https://docs.pytest.org/)
- [pygame testing best practices](https://www.pygame.org/wiki/Test)
- [Headless pygame testing](https://www.pygame.org/wiki/HeadlessMode)
- [Test-driven development for games](https://gameprogrammingpatterns.com/test.html)

<!-- markdownlint-disable-file -->
# Gameplay Simulation Testing Plan

**Date**: 2026-09-23
**Task**: Create tests that simulate gameplay to catch runtime-only errors

---

## User Requests

1. **"implement tests were you simulate playing to find errors only ocurring when playing"** — Create gameplay simulation tests that catch runtime-only errors like the `Bullet` import crash

---

## Overview and Objectives

Create a new test file `tests/test_gameplay_simulation.py` that simulates actual gameplay by running the game loop for multiple frames. This will catch errors that only manifest during full game execution, such as:
- Missing imports that cause NameError (like the `Bullet` import issue)
- State machine transitions that aren't exercised by unit tests
- Edge cases in scoring, lives, and round transitions

---

## Context Summary

### Discovered Instructions Files
- `.github/copilot-instructions.md` — Python project conventions (use .venv, track research/plans in .copilot-tracking)

### Key Codebase Facts
- **Game loop**: `Game.update()` → `Game._update_playing()` runs every frame
- **Enemy shooting**: `Formation.update()` returns `shooting_enemy`, then `shooting_enemy.get_bullet()` is called
- **Test structure**: Existing tests in `tests/test_integration.py` use unit testing approach
- **Bug pattern**: The `Bullet` import error was only triggered when the full game loop called `shooting_enemy.get_bullet()`

### Discovered Research
- `.copilot-tracking/research/2026-09-23/gameplay-simulation-testing-research.md` — Detailed analysis of coverage gaps and recommended test structure

---

## Implementation Checklist

### Phase 1: Create Game Loop Simulation Tests
<!-- parallelizable: false -->
- [x] **Step 1.1**: Create `tests/test_gameplay_simulation.py`
- [x] **Step 1.2**: Implement `TestGameLoopSimulation` class with:
  - `test_game_loop_no_input` — Basic loop stability (300 frames)
  - `test_enemy_shooting_integration` — Catches import errors by triggering enemy shooting
  - `test_bullet_lifecycle` — Verifies bullet objects are created properly
  - `test_round_transition_complete_flow` — Tests ROUND_TRANSITION → PLAYING

### Phase 2: Add Edge Case Tests
<!-- parallelizable: false -->
- [x] **Step 2.1**: Implement `TestEdgeCaseSimulation` class with:
  - `test_bonus_life_scoring` — Force score to BONUS_LIFE_SCORE
  - `test_multiple_lives_depletion` — Deplete all lives to trigger GAME_OVER
  - `test_player_death_state_machine` — Test PLAYER_DEATH transitions

### Phase 3: Add Collision Integration Tests
<!-- parallelizable: false -->
- [x] **Step 3.1**: Implement `TestCollisionIntegration` class with:
  - `test_enemy_bullet_vs_player` — Enemy bullets collide with player
  - `test_player_bullet_vs_enemy` — Player bullets destroy enemies
  - `test_explosion_creation_on_enemy_death` — Explosions created on death

---

## Dependencies

### Existing
- `Game` class in `game/game.py` with full update loop
- `Formation` class in `systems/formation.py` with enemy AI
- `Enemy` class in `entities/enemy.py` with shooting behavior
- `Bullet` class in `entities/bullet.py`
- `AssetManager` class in `assets/__init__.py`
- Existing test fixtures in `tests/test_integration.py`

### No New Constants Needed
- Existing constants (`BONUS_LIFE_SCORE`, `STARTING_LIVES`, `TOTAL_ENEMIES`) are sufficient

---

## Success Criteria

1. ✅ Tests simulate full game loop (300+ frames) without crashes
2. ✅ Tests exercise enemy shooting path (catches import errors like `Bullet` NameError)
3. ✅ Tests verify bullet lifecycle (creation, update, collision)
4. ✅ Tests cover state transitions (PLAYING → ROUND_TRANSITION → PLAYING)
5. ✅ Tests force edge cases (bonus life, game over, multiple deaths)
6. ✅ All new tests pass without modification to game code
7. ✅ No regression in existing 79 integration tests

---

## Implementation Details

### Step 1: Create Test File

**File**: `tests/test_gameplay_simulation.py`

**Imports**:
```python
import pytest
import pygame
import os
import sys
import tempfile
import shutil

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from constants import (
    BONUS_LIFE_SCORE, STARTING_LIVES, ENEMY_BULLET_SPEED,
    PLAYER_BULLET_SPEED, TOTAL_ENEMIES, GameState,
)
from entities import Bullet
from game.game import Game
```

**Test Class 1: `TestGameLoopSimulation`**

```python
class TestGameLoopSimulation:
    """Full game loop tests that catch runtime-only errors."""
    
    @pytest.fixture
    def game(self):
        """Provide a fresh Game instance."""
        temp_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        g = Game()
        yield g
        
        g._save_high_score()
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_game_loop_no_input(self, game):
        """Test game loop runs without crashes (no input)."""
        game.start_game()
        
        for _ in range(300):
            game.update()
        
        assert game.state == GameState.PLAYING
    
    def test_enemy_shooting_integration(self, game):
        """Test enemy shooting creates bullets (catches import errors)."""
        game.start_game()
        
        for _ in range(500):
            game.update()
            if game.enemy_bullets:
                break
        
        assert len(game.enemy_bullets) > 0, "Enemy should have shot"
    
    def test_bullet_lifecycle(self, game):
        """Test enemy bullets are created with correct type."""
        game.start_game()
        
        for _ in range(500):
            game.update()
            if game.enemy_bullets:
                break
        
        assert len(game.enemy_bullets) > 0
        assert isinstance(game.enemy_bullets[0], Bullet)
        assert game.enemy_bullets[0].bullet_type == 'enemy'
    
    def test_round_transition_complete_flow(self, game):
        """Test ROUND_TRANSITION → PLAYING state transition."""
        game.start_game()
        
        # Clear all enemies to trigger round completion
        for enemy in game.enemies:
            enemy.alive = False
        
        game.update()
        assert game.state == GameState.ROUND_TRANSITION
        
        # Wait for transition timer (120 frames)
        for _ in range(120):
            game.update()
        
        assert game.state == GameState.PLAYING
        assert game.round_num == 2
```

**Test Class 2: `TestEdgeCaseSimulation`**

```python
class TestEdgeCaseSimulation:
    """Tests that force edge cases rarely reached in normal play."""
    
    @pytest.fixture
    def game(self):
        """Provide a fresh Game instance."""
        temp_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        g = Game()
        yield g
        
        g._save_high_score()
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_bonus_life_scoring(self, game):
        """Test bonus life awarded at BONUS_LIFE_SCORE."""
        game.start_game()
        game.score = BONUS_LIFE_SCORE - 1
        game.bonus_awarded = False
        initial_lives = game.lives
        
        # Kill an enemy to trigger score update
        enemy = game.enemies[0]
        enemy.alive = False
        
        # Simulate bullet collision to trigger score
        bullet = Bullet(
            enemy.rect.centerx, enemy.rect.bottom + 10,
            0, PLAYER_BULLET_SPEED, 'player', game.asset_manager
        )
        game.player.bullet = bullet
        
        game.update()
        
        assert game.lives == initial_lives + 1
        assert game.bonus_awarded is True
    
    def test_multiple_lives_depletion(self, game):
        """Test GAME_OVER after all lives lost."""
        game.start_game()
        initial_lives = STARTING_LIVES
        
        # Deplete all lives
        for _ in range(initial_lives):
            game._player_hit()
            for _ in range(90):
                game.update()
                if game.state != GameState.PLAYER_DEATH:
                    break
        
        assert game.state == GameState.GAME_OVER
    
    def test_player_death_state_machine(self, game):
        """Test PLAYER_DEATH → PLAYING transition when lives remain."""
        game.start_game()
        
        # Lose one life
        game._player_hit()
        assert game.state == GameState.PLAYER_DEATH
        
        # Wait for death animation (90 frames)
        for _ in range(90):
            game.update()
            if game.state != GameState.PLAYER_DEATH:
                break
        
        # Should return to PLAYING if lives remain
        assert game.state == GameState.PLAYING
        assert game.lives == STARTING_LIVES - 1
```

**Test Class 3: `TestCollisionIntegration`**

```python
class TestCollisionIntegration:
    """Tests that verify collision detection in full game loop."""
    
    @pytest.fixture
    def game(self):
        """Provide a fresh Game instance."""
        temp_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        g = Game()
        yield g
        
        g._save_high_score()
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_enemy_bullet_vs_player(self, game):
        """Test enemy bullets collide with player."""
        game.start_game()
        
        # Create enemy bullet at player position
        bullet = Bullet(
            game.player.rect.centerx,
            game.player.rect.top,
            0, ENEMY_BULLET_SPEED, 'enemy', game.asset_manager
        )
        game.enemy_bullets.append(bullet)
        
        game.update()
        
        # Bullet should hit player and be removed or marked hit
        assert bullet.hit or game.state == GameState.PLAYER_DEATH
    
    def test_player_bullet_vs_enemy(self, game):
        """Test player bullets destroy enemies."""
        game.start_game()
        
        enemy = game.enemies[0]
        initial_score = game.score
        
        # Fire bullet at enemy position
        bullet = Bullet(
            enemy.rect.centerx, enemy.rect.bottom + 10,
            0, PLAYER_BULLET_SPEED, 'player', game.asset_manager
        )
        game.player.bullet = bullet
        
        game.update()
        
        assert not enemy.alive or game.score > initial_score
    
    def test_explosion_creation_on_enemy_death(self, game):
        """Test explosions are created when enemies die."""
        game.start_game()
        
        initial_explosions = len(game.explosions)
        
        # Kill an enemy by forcing death
        enemy = game.enemies[0]
        enemy.alive = False
        
        # Simulate collision
        bullet = Bullet(
            enemy.rect.centerx, enemy.rect.bottom + 10,
            0, PLAYER_BULLET_SPEED, 'player', game.asset_manager
        )
        game.player.bullet = bullet
        
        game.update()
        
        assert len(game.explosions) > initial_explosions
```

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Tests too slow | Low | 300-500 frames at 60 FPS = 5-8 seconds max per test |
| Tests too brittle | Low | Use deterministic state forcing, not timing-dependent assertions |
| Tests mask real bugs | Low | Tests verify specific conditions, not just "no crash" |
| Duplicate existing tests | Medium | Review existing tests before implementation, avoid overlap |

---

## Suggested Follow-On Work

1. **Input simulation**: Add mock keyboard input to test player movement/shooting
2. **Performance testing**: Measure frames per second during simulation
3. **Visual regression**: Use pygame surface comparison to verify rendering
4. **Fuzz testing**: Random input sequences to explore state space
5. **CI integration**: Add gameplay simulation tests to continuous integration

<!-- markdownlint-disable-file -->
# Gameplay Simulation Testing Research

**Date**: 2026-09-23
**Topic**: Simulating gameplay to catch runtime-only errors

---

## Problem Statement

Errors like `NameError: name 'Bullet' is not defined` in `Enemy.get_bullet()` are not caught by existing unit tests because they only exercise isolated methods. The crash only occurs when the full game loop executes:

```
Game.update() → Game._update_playing()
  → Formation.update() → returns shooting_enemy
  → shooting_enemy.get_bullet()  # ← CRASH: Bullet not imported
```

---

## Evidence Log

### 1. Existing Test Coverage — Unit Tests Only

**File**: `tests/test_integration.py`

Tests are organized into classes that exercise individual components:
- `TestGameLifecycle` — State transitions, but uses manual state setting
- `TestPlayerEnemyInteractions` — Collision detection in isolation
- `TestEnemyBehavior` — Enemy state machines directly
- `TestPlayerEntity` — Player movement/shooting directly
- `TestFormationEnemyCreation` — Enemy grid creation only

**Gap**: No test simulates actual gameplay by running the game loop for multiple frames with input.

### 2. Existing Test Coverage — Rendering Tests

**Files**: `tests/test_rendering/*.py`

Tests verify sprite rendering, blitting, text positions, and surface operations. These are visual tests that don't exercise game logic paths.

### 3. Existing Test Coverage — Systems Tests

**Files**: `tests/test_systems/*.py`

Tests verify formation movement, starfield behavior, and collision detection in isolation. They don't test the full update loop.

### 4. The Specific Crash Pattern

The `Bullet` import error was only triggered when:
1. Game is in PLAYING state
2. Formation.update() finds an enemy that returns 'shoot'
3. Game._update_playing() calls `shooting_enemy.get_bullet()`
4. Enemy.get_bullet() references `Bullet` without importing it

This path is never exercised by existing tests because:
- `TestEnemyBehavior.test_enemy_shoot_during_dive()` calls `enemy.update(0, 1)` directly
- It never calls `Formation.update()` which returns the shooting enemy
- It never calls `shooting_enemy.get_bullet()` through the game loop

### 5. Game Loop Complexity

**File**: `game/game.py` — `_update_playing()` method (lines 143-191)

The playing state update path includes:
1. Player movement and shooting
2. Formation update (enemy AI, diving, shooting)
3. Enemy bullet creation and update
4. Enemy bullet vs player collision
5. Player-enemy collision
6. Player bullet vs enemy collision
7. Score accumulation and bonus life
8. Explosion creation
9. Bullet cleanup
10. Round completion check

Each of these paths can contain errors that only manifest during actual gameplay.

---

## Analysis of Coverage Gaps

### Critical Gaps (Cause Crashes)

| Gap | Risk | Example |
|-----|------|---------|
| No full game loop simulation | Import errors, missing references | `Bullet` not imported in enemy.py |
| No enemy shooting integration test | Shooting path never exercised | `shooting_enemy.get_bullet()` crash |
| No bullet lifecycle test | Bullet update/cleanup errors | Bullet objects not created properly |

### Medium Gaps (Cause Logic Errors)

| Gap | Risk | Example |
|-----|------|---------|
| No bonus life scoring test | Score edge cases | Bonus life at BONUS_LIFE_SCORE |
| No round transition complete test | State machine gaps | ROUND_TRANSITION → PLAYING flow |
| No multiple lives depletion test | Game over flow | PLAYER_DEATH → GAME_OVER |

### Low Gaps (Quality Issues)

| Gap | Risk | Example |
|-----|------|---------|
| No player input simulation | Input handling errors | Keyboard/mouse not tested in loop |
| No enemy bullet collision test | Collision bugs | Enemy bullets vs player |
| No explosion cleanup test | Memory/performance | Explosions not removed |

---

## Evaluated Alternatives

### Alternative A: Full Game Loop Simulation Tests (Recommended)

**Approach**: Create tests that instantiate a Game, call `start_game()`, then run the game loop for N frames with simulated input (or no input). This exercises the full update path including enemy shooting, collisions, and state transitions.

**Implementation**:
```python
def test_full_gameplay_simulation(game):
    """Simulate 300 frames of gameplay to catch runtime errors."""
    game.start_game()
    
    for _ in range(300):
        game.handle_input()  # No input, just update
        game.update()        # Full game loop
    
    # If we reach here, no crashes occurred
    assert game.state in (GameState.PLAYING, GameState.ROUND_TRANSITION)
```

**Pros**:
- Catches import errors, missing references, NameErrors
- Exercises full game loop including enemy shooting
- Simple to implement and maintain
- Fast execution (no rendering needed)

**Cons**:
- Doesn't test actual player input handling
- Doesn't verify visual correctness
- May not trigger rare state transitions without input

### Alternative B: Mock Input Simulation

**Approach**: Create a mock input system that simulates keyboard/mouse events during gameplay tests.

**Implementation**:
```python
def test_player_shooting_during_gameplay(game):
    """Simulate player shooting while enemies dive."""
    game.start_game()
    
    for _ in range(100):
        # Simulate player moving and shooting
        mock_keys = {pygame.K_SPACE: True}  # Space = shoot
        game._keys = mock_keys  # Mock key state
        game.handle_input()
        game.update()
```

**Pros**:
- Tests actual input handling code paths
- Can force specific scenarios (player shoots, moves left/right)

**Cons**:
- More complex to implement
- Requires mocking pygame.key.get_pressed()
- Doesn't add much value over Alternative A for catching crashes

### Alternative C: Property-Based Testing

**Approach**: Use randomized input sequences to explore the state space.

**Implementation**:
```python
def test_random_gameplay(game):
    """Test with random input sequences."""
    game.start_game()
    
    for _ in range(200):
        # Random key combinations
        keys = {k: random.choice([True, False]) for k in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE]}
        game._keys = keys
        game.handle_input()
        game.update()
```

**Pros**:
- Explores many code paths
- May find edge cases

**Cons**:
- Non-deterministic (tests may pass/fail inconsistently)
- Complex to debug failures
- Over-engineered for crash detection

---

## Selected Approach

**Primary**: Alternative A — Full game loop simulation tests

**Rationale**: The `Bullet` import error demonstrates that the most effective way to catch runtime-only errors is to exercise the full game loop. Alternative A is simple, deterministic, and directly addresses the root cause of this class of bugs.

**Secondary**: Add specific integration tests for:
- Enemy shooting through the full game loop
- Bullet lifecycle (creation, update, collision, cleanup)
- Bonus life scoring edge case
- Round transition complete flow

---

## Recommended Test Structure

### File: `tests/test_gameplay_simulation.py`

```python
class TestGameLoopSimulation:
    """Full game loop tests that catch runtime-only errors."""
    
    def test_game_loop_no_input(self, game):
        """Test game loop runs without crashes (no input)."""
        game.start_game()
        for _ in range(300):
            game.update()
        assert game.state == GameState.PLAYING
    
    def test_enemy_shooting_integration(self, game):
        """Test enemy shooting creates bullets (catches import errors)."""
        game.start_game()
        # Run enough frames for formation to trigger shooting
        for _ in range(500):
            game.update()
            if game.enemy_bullets:
                break
        assert len(game.enemy_bullets) > 0, "Enemy should have shot"
    
    def test_bullet_lifecycle(self, game):
        """Test enemy bullets are created, updated, and cleaned up."""
        game.start_game()
        # Force enemy to shoot
        for enemy in game.enemies:
            if enemy.alive:
                enemy.shoot_timer = 0
                break
        
        game.update()
        assert len(game.enemy_bullets) > 0
        assert isinstance(game.enemy_bullets[0], Bullet)
    
    def test_round_transition_complete_flow(self, game):
        """Test ROUND_TRANSITION → PLAYING state transition."""
        game.start_game()
        # Clear all enemies
        for enemy in game.enemies:
            enemy.alive = False
        
        game.update()
        assert game.state == GameState.ROUND_TRANSITION
        
        # Wait for transition timer
        for _ in range(120):
            game.update()
        
        assert game.state == GameState.PLAYING
        assert game.round_num == 2


class TestEdgeCaseSimulation:
    """Tests that force edge cases rarely reached in normal play."""
    
    def test_bonus_life_scoring(self, game):
        """Test bonus life awarded at BONUS_LIFE_SCORE."""
        game.start_game()
        game.score = BONUS_LIFE_SCORE - 1
        game.bonus_awarded = False
        
        # Kill an enemy to trigger score update
        # (Implementation details TBD)
        
        assert game.lives == STARTING_LIVES + 1
        assert game.bonus_awarded is True
    
    def test_multiple_lives_depletion(self, game):
        """Test GAME_OVER after all lives lost."""
        game.start_game()
        
        # Deplete all lives
        for _ in range(STARTING_LIVES + 1):
            game._player_hit()
            for _ in range(90):
                game.update()
        
        assert game.state == GameState.GAME_OVER
    
    def test_player_death_state_machine(self, game):
        """Test PLAYER_DEATH → PLAYING or GAME_OVER transitions."""
        game.start_game()
        
        # Lose one life
        game._player_hit()
        for _ in range(90):
            game.update()
        
        # Should return to PLAYING if lives remain
        assert game.state == GameState.PLAYING


class TestCollisionIntegration:
    """Tests that verify collision detection in full game loop."""
    
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
        # Bullet should hit player and be removed
        assert bullet.hit or game.state == GameState.PLAYER_DEATH
    
    def test_player_bullet_vs_enemy(self, game):
        """Test player bullets destroy enemies."""
        game.start_game()
        
        enemy = game.enemies[0]
        initial_lives = game.lives
        initial_score = game.score
        
        # Fire bullet at enemy
        game.player.bullet = Bullet(
            game.player.rect.centerx,
            enemy.rect.top - 10,
            0, -PLAYER_BULLET_SPEED, 'player', game.asset_manager
        )
        
        game.update()
        
        assert not enemy.alive or game.score > initial_score
    
    def test_explosion_creation_on_enemy_death(self, game):
        """Test explosions are created when enemies die."""
        game.start_game()
        
        initial_explosions = len(game.explosions)
        
        # Kill an enemy
        enemy = game.enemies[0]
        enemy.alive = False  # Force death
        
        # Trigger collision check
        bullet = Bullet(
            enemy.rect.centerx, enemy.rect.bottom + 10,
            0, PLAYER_BULLET_SPEED, 'player', game.asset_manager
        )
        game.player.bullet = bullet
        
        game.update()
        
        assert len(game.explosions) > initial_explosions
```

---

## Implementation Plan

### Step 1: Create `tests/test_gameplay_simulation.py`

1. Add imports (pytest, pygame, Game, Bullet, constants)
2. Implement `TestGameLoopSimulation` class with:
   - `test_game_loop_no_input` — Basic loop stability
   - `test_enemy_shooting_integration` — Catches import errors
   - `test_bullet_lifecycle` — Verifies bullet objects
   - `test_round_transition_complete_flow` — State machine coverage

### Step 2: Add Edge Case Tests

1. Implement `TestEdgeCaseSimulation` class with:
   - `test_bonus_life_scoring` — Score edge case
   - `test_multiple_lives_depletion` — Game over flow
   - `test_player_death_state_machine` — Death animation

### Step 3: Add Collision Integration Tests

1. Implement `TestCollisionIntegration` class with:
   - `test_enemy_bullet_vs_player` — Enemy shooting path
   - `test_player_bullet_vs_enemy` — Player shooting path
   - `test_explosion_creation_on_enemy_death` — Explosion cleanup

### Step 4: Update `.copilot-tracking/` Artifacts

1. Update research document with findings
2. Create implementation plan
3. Update changes log after implementation

---

## Success Criteria

1. ✅ Tests simulate full game loop (300+ frames)
2. ✅ Tests exercise enemy shooting path (catches import errors)
3. ✅ Tests verify bullet lifecycle (creation, update, collision)
4. ✅ Tests cover state transitions (PLAYING → ROUND_TRANSITION → PLAYING)
5. ✅ Tests force edge cases (bonus life, game over, multiple deaths)
6. ✅ All new tests pass without modification to game code
7. ✅ No regression in existing 79 integration tests

---

## Suggested Follow-On Work

1. **Input simulation**: Add mock keyboard input to test player movement/shooting
2. **Performance testing**: Measure frames per second during simulation
3. **Visual regression**: Use pygame surface comparison to verify rendering
4. **Fuzz testing**: Random input sequences to explore state space
5. **CI integration**: Add gameplay simulation tests to continuous integration

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Tests too slow | Low | 300 frames at 60 FPS = 5 seconds max |
| Tests too brittle | Low | Use deterministic state forcing, not timing |
| Tests mask real bugs | Low | Tests verify specific conditions, not just "no crash" |
| Duplicate existing tests | Medium | Review existing tests before implementation |

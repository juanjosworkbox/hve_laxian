<!-- markdownlint-disable-file -->
# Test Coverage Research - Galaxian Game

**Date**: 2026-09-23
**Status**: Complete

## Coverage Summary

| Metric | Value |
|--------|-------|
| Total Statements | 2,853 |
| Missing | 111 |
| **Coverage** | **96%** |

## File-Level Coverage Breakdown

### 100% Coverage Files
- `constants.py` - 54 stmts, 0 missing
- `entities/__init__.py` - 4 stmts, 0 missing
- `entities/bullet.py` - 29 stmts, 0 missing
- `entities/explosion.py` - 22 stmts, 0 missing
- `game/__init__.py` - 1 stmt, 0 missing
- `systems/__init__.py` - 3 stmts, 0 missing
- `systems/collision.py` - 28 stmts, 0 missing
- `systems/starfield.py` - 23 stmts, 0 missing
- `tests/test_gameplay_simulation.py` - 201 stmts, 0 missing
- `tests/test_sprites.py` - 112 stmts, 0 missing
- `tests/test_surfaces.py` - 160 stmts, 0 missing
- `tests/test_text_rendering.py` - 136 stmts, 0 missing
- `tests/test_systems/test_formation.py` - 204 stmts, 0 missing
- `tests/test_systems/conftest.py` - 35 stmts, 0 missing

### High Coverage (95-99%)
- `assets/__init__.py` - 96% (6 missing)
- `entities/enemy.py` - 95% (5 missing)
- `entities/player.py` - 97% (2 missing)
- `systems/formation.py` - 97% (3 missing)
- `tests/test_integration.py` - 99% (1 missing)
- `tests/test_rendering/test_blitting.py` - 98% (3 missing)
- `tests/test_rendering/test_draw_methods.py` - 99% (1 missing)
- `tests/test_systems/test_starfield.py` - 99% (1 missing)

### Needs Improvement (<95%)
- `game/game.py` - 80% (48 missing)
- `tests/test_rendering/conftest.py` - 62% (41 missing)

## Missing Coverage Analysis

### game/game.py (80% - 48 lines missing)

**Lines 69-70**: `_load_high_score` exception handling
```python
except:
    return 0
```
- Missing: File read exceptions (permission, malformed data)

**Lines 99**: `handle_input` for ATTRACT state
- Missing: Testing key press in ATTRACT state triggers `start_game()`

**Lines 104-112**: `handle_input` for PLAYING state
- Missing: Player movement input handling during PLAYING state

**Lines 116-119**: `handle_input` for GAME_OVER state
- Missing: Key press in GAME_OVER state transitions to ATTRACT

**Lines 127**: `update` ATTRACT state early return
- Missing: Testing ATTRACT state update path

**Line 154**: `update` ROUND_TRANSITION state
- Missing: Round transition timer decrement and state change

**Lines 179**: `update` PLAYER_DEATH state with lives remaining
- Missing: Transition from PLAYER_DEATH to PLAYING when lives > 0

**Lines 183-199**: `update` PLAYER_DEATH state game over path
- Missing: Transition from PLAYER_DEATH to GAME_OVER when lives <= 0

**Line 214**: `_update_playing` early return when player is None
- Missing: Guard clause for None player

**Line 291**: `_player_hit` guard condition
- Missing: Early return when player already dead in PLAYER_DEATH state

**Line 295**: `_player_hit` explosion creation
- Missing: Player death explosion with asset_manager parameter

**Lines 359-361**: `draw` ATTRACT state
- Missing: Attract screen drawing path

**Lines 365-380**: `draw_game_over`
- Missing: Game over screen rendering (score, high score, blinking text)

### assets/__init__.py (96% - 6 lines missing)

**Lines 181, 186-188**: `play_sound` enabled=False and SOUND_ENABLED import path
```python
if enabled is False:
    return
if enabled is None:
    try:
        from constants import SOUND_ENABLED
        if not SOUND_ENABLED:
            return
    except ImportError:
        pass
```
- Missing: Sound disable gating and import fallback

**Lines 276-278**: `_generate_sounds` method
- Missing: Sound generation code path

### entities/enemy.py (95% - 5 lines missing)

**Lines 33-34**: `__init__` else branch for non-list sprites
```python
else:
    self.wing_frames = [raw_image]
```
- Missing: Single surface (non-animation) enemy sprite handling

**Line 82**: `update` returning state distance check
```python
if dist < 5:
```
- Missing: Formation return completion condition

**Line 95**: `update` off-screen dive check
```python
if self.state == 'diving' and self.rect.centery > SCREEN_HEIGHT + 30:
```
- Missing: Off-screen dive transition to returning

**Line 153**: `die` method
- Missing: Enemy death state change

### entities/player.py (97% - 2 lines missing)

**Line 25**: `handle_input` early return when not alive
```python
if not self.alive:
    return
```
- Missing: Input handling on dead player

**Line 108**: `draw` blink condition
```python
if self.respawn_timer % 6 < 3:
```
- Missing: Invincible blinking draw skip

### systems/formation.py (97% - 3 lines missing)

**Lines 128, 133, 139**: `try_dive` guard conditions
```python
if self.dives_this_round >= self.max_dives:
    return None
```
- Missing: Max dives exceeded guard path

### tests/test_integration.py (99% - 1 line missing)

**Line 1172**: Missing test code path in integration tests
- Likely a conditional branch in a test helper or fixture

### tests/test_rendering/conftest.py (62% - 41 lines missing)

**Lines 83-88, 91-98, 105-106, 112-114, 120, 128-130, 137-171**: TestGame class methods
- Missing: `_load_high_score`, `_save_high_score`, `start_game`, `start_round`, `handle_input`, `update`, `draw` methods in TestGame fixture

### tests/test_rendering/test_blitting.py (98% - 3 lines missing)

**Lines 14-20**: Test helper functions
- Missing: `_make_checker` helper usage

### tests/test_rendering/test_draw_methods.py (99% - 1 line missing)

**Line 11**: Test class/module level
- Likely a single conditional branch

### tests/test_systems/test_starfield.py (99% - 1 line missing)

**Line 245**: Single missing line
- Likely a conditional in star drawing test

## Recommendations

### Priority 1: Critical Game Logic Paths (game.py)
1. **ATTRACT state handling** - Test key press triggers game start
2. **GAME_OVER state handling** - Test key press returns to ATTRACT
3. **ROUND_TRANSITION** - Test timer countdown and round start
4. **PLAYER_DEATH transitions** - Test both lives remaining and game over paths
5. **draw_game_over** - Test game over screen rendering
6. **draw ATTRACT** - Test attract screen rendering

### Priority 2: Entity Edge Cases
1. **Enemy die() method** - Test death state change
2. **Player handle_input when dead** - Test no-op on dead player
3. **Player draw blinking** - Test invincible blink skip
4. **Enemy single-surface sprites** - Test non-animation enemy types
5. **Enemy returning state completion** - Test formation return

### Priority 3: Asset Manager
1. **play_sound with enabled=False** - Test sound disable
2. **play_sound SOUND_ENABLED import** - Test import fallback
3. **_generate_sounds** - Test sound generation

### Priority 4: Formation Guards
1. **try_dive max dives exceeded** - Test early return when max dives reached

## Testing Strategy

The missing coverage falls into two categories:
1. **Game state machine paths** - The Game.update() and Game.handle_input() methods have multiple state branches that aren't fully tested
2. **Edge case guards** - Early returns and exception handlers that are rarely triggered in normal test flows

Recommendations focus on adding targeted tests for each uncovered branch rather than refactoring existing tests.

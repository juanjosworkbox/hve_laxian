<!-- markdownlint-disable-file -->
# Sound System Research - Galaxian Game

**Date**: 2026-09-22  
**Status**: Complete  
**Difficulty**: Simple

## Overview

Research into adding/improving sound effects for the Galaxian clone game.

## Current State

The game already has a **programmatic sound system** using `pygame.mixer.Sound`. Sounds are generated in `AssetManager._generate_sounds()` using sine wave synthesis with `array` module.

### Currently Implemented Sounds

| Sound Name | Description | Frequency | Duration | Where Played |
|------------|-------------|-----------|----------|--------------|
| `shoot` | Player fire | 880 Hz beep | 0.1s | `game.py:handle_input()` |
| `explosion` | Enemy destroyed | 200 Hz with decay | 0.3s | `game.py:_update_playing()` |
| `player_death` | Player destroyed | Descending 880→100 Hz | 0.5s | `game.py:_player_hit()` |
| `dive` | Enemy starts dive | Rising 300→900 Hz | 0.2s | `enemy.py:start_dive()` |
| `bonus` | Bonus life arpeggio | C5-E5-G5-C6 | 0.4s | `game.py:_update_playing()` |

### Sound Generation Code Location

- **File**: `assets/__init__.py` — `_generate_sounds()` method (lines ~170-220)
- **Sample Rate**: 22050 Hz
- ** mixer Config**: `pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)` in `Game.__init__()`

### Missing Integration

The `SOUND_ENABLED` constant exists in `constants.py` but is **never checked** before playing sounds. All sound calls proceed unconditionally.

## Code Quality Issues Found

1. **Dead code in `_generate_sounds()`**: Lines creating unused `pygame.mixer.Sound` objects before the `import array`
2. **Variable shadowing**: `freq` variable used for both `pygame.mixer.Sound` object and frequency calculation in `player_death` sound
3. **No volume control**: All sounds use default amplitude (no way to adjust relative loudness)
4. **No sound priority/grouping**: `channels=1` means only one sound plays at a time — overlapping sounds will cut each other off
5. **No mute/toggle functionality**: No `SOUND_ENABLED` check anywhere in the codebase

## Recommended New Sounds

Based on classic Galaxian arcade behavior and gameplay gaps:

| Sound | Description | Priority |
|-------|-------------|----------|
| `enemy_fire` | Enemy bullet sound | High — enemies shoot but no sound |
| `round_start` | Fanfare when round begins | Medium — adds atmosphere |
| `game_over` | Descending sad tone | Medium — feedback for game end |
| `coin_insert` | Arcade coin sound | Low — for attract mode |
| `1up` | Standard life sound | Low — bonus uses arpeggio already |
| `enemy_hit` | Different explosion variant | Low — optional variety |

## Implementation Approaches

### Option A: Enhanced Programmatic Synthesis (Recommended)
**Pros**: No external files needed, consistent with current architecture, small footprint  
**Cons**: Limited sound quality, all synthesized

**Changes**:
- Fix `channels=1` → `channels=8` or `channels=16` for overlapping sounds
- Add `SOUND_ENABLED` checks to all `sound.play()` calls
- Implement `play_sound(name)` helper with enable check
- Add missing sounds: `enemy_fire`, `round_start`, `game_over`
- Clean up dead code and variable shadowing

### Option B: External Audio Files
**Pros**: Higher quality, more realistic sounds  
**Cons**: Requires asset files, more complex loading logic

**Changes**:
- Add `pygame.mixer.Sound.load()` for WAV/OGG files
- Create `sounds/` directory with generated audio
- Update `requirements.txt` if using additional decoders

### Option C: Hybrid (Best of Both)
**Pros**: Use external files when available, fall back to synthesis  
**Cons**: More complex code path

## Dependency Impact

- **Current**: `pygame>=2.1.0` already includes `pygame.mixer` — **no new dependencies needed**
- **For external audio**: `pygame` supports WAV natively; OGG/MP3 may need `pygame.mixer` SDL audio backends (already included in standard pygame installs)

## Architecture Notes

Sound calls are currently scattered across:
- `game.py`: `handle_input()`, `_update_playing()`, `_player_hit()`
- `enemy.py`: `start_dive()`

A centralized `SoundManager` class could be introduced, but for the current scope, enhancing `AssetManager` with sound helpers is sufficient and less invasive.

## Next Steps

1. **Fix mixer channels** — increase from 1 to 8+ for overlapping sounds
2. **Add `SOUND_ENABLED` gating** — check the constant before every `sound.play()`
3. **Implement `AssetManager.play_sound(name)`** — helper method with enable check
4. **Add missing sounds** — `enemy_fire`, `round_start`, `game_over`
5. **Clean up** — remove dead code, fix variable shadowing

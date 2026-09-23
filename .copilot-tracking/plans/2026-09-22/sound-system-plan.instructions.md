<!-- markdownlint-disable-file -->
# Sound System Enhancement Plan - Galaxian Game

**Date**: 2026-09-22  
**Status**: Ready for Implementation  
**Difficulty**: Medium

---

## User Request

> "plan adding sounds to the game"

## Overview

Enhance the Galaxian game's sound system by fixing critical mixer limitations, adding missing sound effects, and implementing proper sound enable/disable gating.

## Objectives

1. Fix pygame.mixer to support multiple overlapping sounds
2. Add SOUND_ENABLED constant gating to all sound playback
3. Implement centralized `play_sound()` helper in AssetManager
4. Add missing enemy bullet fire sound
5. Clean up dead code and variable shadowing bugs
6. (Optional) Add round_start fanfare and game_over tone

---

## Implementation Checklist

### Phase 1: Core Mixer Fix & Helper Method
- [ ] Change `channels=1` to `channels=8` in `Game.__init__()` pygame.mixer.init()
- [ ] Add `play_sound(name, enabled=None)` method to `AssetManager` with SOUND_ENABLED check
- [ ] Fix dead code in `_generate_sounds()` (remove unused pygame.mixer.Sound.__new__() calls)
- [ ] Fix variable shadowing (`freq` used for both Sound object and frequency calculation)
- [ ] **Files**: `game/game.py`, `assets/__init__.py`

### Phase 2: Add Missing Sounds
- [ ] Add `enemy_fire` sound: short downward sweep (600→200 Hz, 0.08s)
- [ ] Add `round_start` sound: ascending fanfare (C4-E4-G4-C5, 0.5s)
- [ ] Add `game_over` sound: descending sad tone (440→100 Hz, 0.8s)
- [ ] Wire `enemy_fire` to enemy bullet creation in `enemy.py` or `game.py`
- [ ] Wire `round_start` to `Game.start_round()` method
- [ ] Wire `game_over` to `Game._save_high_score()` or game over state transition
- [ ] **Files**: `assets/__init__.py`, `entities/enemy.py`, `game/game.py`

### Phase 3: Apply SOUND_ENABLED Gating
- [ ] Replace all `sound.play()` calls with `self.asset_manager.play_sound('sound_name')`
- [ ] Ensure all existing sounds (shoot, explosion, player_death, dive, bonus) use the helper
- [ ] Add toggle mechanism (e.g., key binding or settings)
- [ ] **Files**: `game/game.py`, `entities/enemy.py`

### Phase 4: Validation
- [ ] Test all sounds play correctly
- [ ] Test overlapping sounds (enemy bullets + player shooting)
- [ ] Test SOUND_ENABLED toggle works
- [ ] Verify no regression in game behavior
- [ ] **Command**: `python -m pytest tests/ -v` (if applicable)

---

## Dependencies

- **pygame>=2.1.0** — already includes pygame.mixer (no new dependencies)
- **Existing research**: `.copilot-tracking/research/2026-09-22/sound-system-research.md`

---

## Success Criteria

1. ✅ All 5 existing sounds (shoot, explosion, player_death, dive, bonus) still play correctly
2. ✅ 3 new sounds added (enemy_fire, round_start, game_over)
3. ✅ Multiple sounds can play simultaneously (channels=8)
4. ✅ SOUND_ENABLED constant gates all sound playback
5. ✅ No dead code or variable shadowing in sound generation
6. ✅ Sound helper method centralizes enable/disable logic

---

## Parallelization

**Not parallelizable** — phases must execute in order due to dependencies:
- Phase 1 must complete before Phase 3 (helper method needed for gating)
- Phase 2 must complete before Phase 3 (new sounds needed before wiring)
- Phase 4 validates all previous phases

---

## Notes

- Approach: **Option A (Enhanced Programmatic Synthesis)** — consistent with current architecture
- No external audio files needed
- Sound generation uses sine wave synthesis with array module (already in place)

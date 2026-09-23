<!-- markdownlint-disable-file -->
# Collision Bug Fix + Wing Flap Animation Research

**Date**: 2026-09-22
**Status**: Complete

## Issues Identified

### Issue 1: Undefined `bullet_rect` in `check_bullet_player_collisions` (Critical Bug)

**File**: `systems/collision.py`, line 27

**Problem**: The function `check_bullet_player_collisions` references `bullet_rect` which is never defined. The `player_rect` is defined on line 23, but the collision check on line 27 uses `bullet_rect.colliderect(player_rect)` instead of `bullet.get_rect().colliderect(player_rect)`.

**Impact**: This causes an `UnboundLocalError` whenever an enemy bullet is checked against the player, preventing the player from taking damage properly or potentially crashing the game.

**Fix**: Replace `bullet_rect` with `bullet.get_rect()` inside the loop.

### Issue 2: No Animated Wing Frames for Dragonfly Enemies (Visual Upgrade)

**Current State**:
- `Enemy` class has `wing_frame` and `wing_timer` attributes (lines 47-48 of `enemy.py`)
- `Enemy.update()` toggles `wing_frame` between 0 and 1 during formation state (lines 95-98)
- `_create_enemy_sprite()` in `assets/__init__.py` creates only ONE static sprite
- `Enemy.draw()` always blits `self.image` without frame switching

**Problem**: The wing animation infrastructure exists in the Enemy class but the asset manager provides only a single static sprite frame, so no wing flap animation is visible.

**Fix**:
1. Modify `_create_enemy_sprite()` to create two frames:
   - Frame 0: wings raised (polygon points angled upward)
   - Frame 1: wings lowered (polygon points angled downward)
2. Store both frames in `self._wing_frames` list on AssetManager
3. In `Enemy.__init__`, store reference to wing frames
4. In `Enemy.update()`, swap `self.image` based on `wing_frame`
5. In `Enemy.draw()`, use the current frame image

## Files to Modify

| File | Change |
|------|--------|
| `systems/collision.py` | Fix undefined `bullet_rect` reference |
| `assets/__init__.py` | Create two wing animation frames |
| `entities/enemy.py` | Use wing frames during update/draw |

## Dependencies

- pygame>=2.1.0 (for surface rendering)
- No new dependencies required

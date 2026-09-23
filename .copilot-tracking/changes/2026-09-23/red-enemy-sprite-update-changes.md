# Red Enemy Sprite Update - Changes

## Date
2026-09-23

## Summary of Changes
Updated the red enemy (second row from top) to use pixel-extracted frames from the PNG sprite sheet instead of procedural drawing, and fixed the animation cycle to use all 4 frames.

## Changes by Category

### Modified
- `assets/__init__.py` - Replaced `_create_red_enemy_sprite()` with PNG-extracted pixel data (10x10 frames)
- `entities/enemy.py` - Fixed wing animation cycle to use modulo-based frame rotation instead of toggle (0↔1)

## Additional Notes
- All 4 frames are now 10x10 pixels, matching the original arcade sprite size
- Animation cycles through all 4 frames (0→1→2→3→0...) instead of just 2 frames (0↔1)
- 390 tests pass

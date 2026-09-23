# Red Enemy Sprite Redesign - Suggested Next Work

**Date:** 2026-09-23

---

## 1. What Was Completed

The second row (red) enemy sprite has been redesigned to match the successive animation frames from `second_row_enemy_animation.png`. The new 4-frame wing flapping animation uses the correct colors (red body, yellow wing tips, blue wing bases) and replaces the generic 2-frame sprite.

---

## 2. Suggested Next Work

Based on the sprite redesign and codebase analysis:

1. **Add visual test for red enemy sprite frames** - Create a test that renders all 4 red enemy frames to a surface and compares pixel data against the PNG to verify visual accuracy
2. **Apply same PNG-based approach to other enemy rows** - Green, blue, and yellow enemies still use generic `_create_enemy_sprite()` with simple wing flaps; consider extracting their frames from their respective PNGs if available
3. **Add animation speed configuration for red enemy** - The wing animation timer could be tuned per-enemy-type to make the red enemy's flapping faster/slower than other enemies for visual distinction
4. **Verify red enemy looks correct in-game** - Run the game with SDL_VIDEODRIVER=directx to visually inspect the new sprite in formation and during dive animations
5. **Add coverage for _create_red_enemy_sprite method** - Current test coverage reports don't include the new method; add to coverage analysis

---

## 3. Priority Order

1. **Verify in-game** (highest priority - visual confirmation)
2. **Add animation speed configuration** (tweak flapping rate)
3. **Apply PNG approach to other rows** (consistency across all enemies)
4. **Add visual test** (automated verification)
5. **Update coverage** (documentation)

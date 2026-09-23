<!-- markdownlint-disable-file -->
# Player Sprite Redraw Plan

**Date**: 2026-09-23

## User Request

- Redraw player sprite to match samples/player.png as closely as possible

## Implementation Approach

### Files to Modify

1. **constants.py** - Update PLAYER_WIDTH (12→13) and PLAYER_HEIGHT (12→16)
2. **assets/__init__.py** - Replace `_create_player_sprite()` with pixel-by-pixel recreation

### Pixel-by-Pixel Recreation Strategy

Use averaged representative colors instead of 14 individual colors:

| Representative Color | Approximate RGB | Usage |
|---------------------|----------------|-------|
| BLACK | (0, 0, 0) | Outline/background |
| RED | (223, 0, 0) | Cockpit/accents |
| TEAL | (0, 195, 216) | Main body |
| GRAY | (195, 195, 216) | Wings/details |

## Success Criteria

- Player sprite matches samples/player.png pixel-for-pixel
- Constants updated to reflect new dimensions
- Game runs without errors

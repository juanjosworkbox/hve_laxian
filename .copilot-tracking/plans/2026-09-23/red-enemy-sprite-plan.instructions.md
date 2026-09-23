# Red Enemy Sprite Redesign Plan

**Date:** 2026-09-23  
**Task:** Redesign the second row (red) enemy sprite to match successive animation frames from `second_row_enemy_animation.png`

---

## User Requests

1. Change the second from the top row enemy sprite (red enemies) to be redrawn as similar as possible to the successive animation from `second_row_enemy_animation.png`

---

## Context Summary

### Discovered Instructions Files
- `.github/copilot-instructions.md` - Python/pygame project conventions
- `assets/__init__.py` - AssetManager with sprite generation methods
- `entities/enemy.py` - Enemy class with wing animation frame handling
- `constants.py` - ENEMY_WIDTH=10, ENEMY_HEIGHT=10

### Research Document
- `.copilot-tracking/research/2026-09-23/second-row-enemy-sprite-research.md` - Complete PNG analysis

### Key Findings
- PNG is 58x8 pixels with 4 distinct animation frames
- Each frame ~11px wide, showing wing flapping animation
- Colors: Red body (224,0,0), Yellow wing tips (224,213,0), Blue wing bases (0,86,206), Dark (11,0,0)
- Current implementation uses generic `_create_enemy_sprite((255, 50, 50))` with simple 2-frame wing flap

---

## Implementation Checklist

### Phase 1: Add _create_red_enemy_sprite() Method
- [x] Create new method in AssetManager with 4 animation frames
- [x] Use pygame.draw to recreate dragonfly-like alien with correct colors
- [x] Each frame shows different wing position (raised → intermediate-down → lowered → intermediate-up)

### Phase 2: Update Registration
- [x] Replace `self.sprites['enemy_red'] = self._create_enemy_sprite((255, 50, 50))` with `self.sprites['enemy_red'] = self._create_red_enemy_sprite()`

### Phase 3: Verify Enemy Class Compatibility
- [x] Enemy class already handles list of frames via `isinstance(raw_image, list)` check
- [x] No changes needed to enemy.py - 4 frames work with existing animation logic

---

## Dependencies

- `pygame>=2.1.0` for Surface and drawing primitives
- `Pillow>=10.0.0` (already in requirements.txt, used for PNG analysis)
- Existing ENEMY_WIDTH/HEIGHT constants (10x10)

---

## Success Criteria

1. ✅ Red enemies use new 4-frame sprite matching PNG appearance
2. ✅ Frames show wing flapping animation (raised → down → lowered → up)
3. ✅ Sprite dimensions remain 10x10 (ENEMY_WIDTH/HEIGHT)
4. ✅ Animation cycles smoothly through all 4 frames
5. ✅ All existing tests pass

---

## Implementation Details

### Frame Animation Pattern
The 4 frames create a natural wing-flapping cycle:
- Frame 0: Wings raised (start position)
- Frame 1: Wings intermediate-down (beginning flap down)
- Frame 2: Wings fully lowered (bottom of flap)
- Frame 3: Wings intermediate-up (returning to start)

### Color Palette (Exact from PNG)
| Color | RGB | Usage |
|-------|-----|-------|
| Red (body) | (224, 0, 0) | Main dragonfly body |
| Yellow (wing tips) | (224, 213, 0) | Wing tips and antennae |
| Blue (wing base) | (0, 86, 206) | Wing attachment points |
| Dark | (11, 0, 0) | Shadow/detail areas |
| Black | (0, 0, 0) | Outline/background |

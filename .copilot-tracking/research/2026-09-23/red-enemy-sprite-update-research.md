# Red Enemy Sprite Update - Research

## Date
2026-09-23

## Summary
Updated the second row from top enemy (red enemy) to use pixel-extracted frames from the PNG sprite sheet `samples/second_row_enemy_animation.png` instead of procedurally drawn shapes. Also fixed the animation cycle to use all 4 frames instead of just cycling between frames 0 and 1.

## Findings

### Sprite Sheet Structure
- **File**: `samples/second_row_enemy_animation.png`
- **Size**: 58x8 pixels
- **Frames**: 4 frames stored side-by-side
  - Frame 0: columns 0-13 (14px wide)
  - Frame 1: columns 14-28 (15px wide)
  - Frame 2: columns 29-43 (15px wide)
  - Frame 3: columns 44-57 (14px wide)
- **Color palette**: Red body (224,0,0), yellow wing tips (224,213,0), blue wing bases (0,86,206), dark accents (11,0,0)

### Previous Issues
1. **Animation truncated**: The red enemy had 4 frames generated but only cycled through frames 0 and 1 (2-frame loop)
2. **Procedural generation**: The `_create_red_enemy_sprite()` method used `pygame.draw` primitives instead of actual PNG pixel data

### Changes Made

#### assets/__init__.py
- Replaced `_create_red_enemy_sprite()` method with pixel-extracted frames from PNG
- Each frame is now 10x10 pixels (matching original arcade size)
- Uses `pygame.Surface.set_at()` to set exact pixel colors from the PNG

#### entities/enemy.py
- Fixed animation cycle in `Enemy.update()` method
- Changed `self.wing_frame = 1 - self.wing_frame` to `self.wing_frame = (self.wing_frame + 1) % len(self.wing_frames)`
- This allows all 4 frames to be used for red enemy animation

## Validation
- All 4 frames are 10x10 pixels ✓
- All enemy types load correctly ✓
- Game initialization succeeds ✓

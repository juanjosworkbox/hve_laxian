# Second Row Enemy Sprite Redesign Research

**Date:** 2026-09-23  
**Task:** Redesign the second row (red) enemy sprite to match successive animation frames from `second_row_enemy_animation.png`

---

## 1. User Request

> "Research changing second from the top row enemy sprite so you redraw it as similar as possible to the successive animation of successive left to right sprites of the png image second_row_enemy_animation.png"

---

## 2. Task Overview

The second row of the Galaxian formation contains **red enemies** (row=1, types="red"). Currently, these enemies use the generic `_create_enemy_sprite()` method with simple wing-flap animation. The PNG file `samples/second_row_enemy_animation.png` contains **5 successive animation frames** showing the red enemy in different wing positions across the formation columns.

---

## 3. Current Implementation

### 3.1 Enemy Type Assignment (systems/formation.py)

```python
def _assign_enemy_types(self):
    types = []
    # Row 0 (top): 5 flagships
    for _ in range(5):
        types.append('flagship')
    # Row 1: 5 red
    for _ in range(5):
        types.append('red')  # <-- SECOND ROW = RED ENEMIES
    # Row 2: 5 yellow
    for _ in range(5):
        types.append('yellow')
    # Row 3: 5 blue
    for _ in range(5):
        types.append('blue')
    # Row 4 (bottom): 5 green
    for _ in range(5):
        types.append('green')
    return types
```

### 3.2 Current Red Enemy Sprite (assets/__init__.py)

```python
def _create_enemy_sprite(self, color):
    """Create dragonfly alien enemy sprite with two wing animation frames."""
    # Frame 0: wings raised (flap up)
    surface0 = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(surface0, color, (4, 2, 2, 6))  # body
    pygame.draw.polygon(surface0, color, [(0, 3), (4, 3), (4, 5)])  # left wing
    pygame.draw.polygon(surface0, color, [(10, 3), (6, 3), (6, 5)])  # right wing
    pygame.draw.line(surface0, color, (4, 2), (3, 0), 1)  # left antenna
    pygame.draw.line(surface0, color, (6, 2), (7, 0), 1)  # right antenna
    
    # Frame 1: wings lowered (flap down)
    surface1 = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(surface1, color, (4, 2, 2, 6))  # body
    pygame.draw.polygon(surface1, color, [(0, 5), (4, 3), (4, 5)])  # left wing
    pygame.draw.polygon(surface1, color, [(10, 5), (6, 3), (6, 5)])  # right wing
    pygame.draw.line(surface1, color, (4, 2), (3, 0), 1)  # left antenna
    pygame.draw.line(surface1, color, (6, 2), (7, 0), 1)  # right antenna
    
    return [surface0, surface1]
```

### 3.3 Current Sprite Registration

```python
# In _generate_sprites():
self.sprites['enemy_green'] = self._create_enemy_sprite((0, 255, 0))
self.sprites['enemy_blue'] = self._create_enemy_sprite((0, 100, 255))
self.sprites['enemy_yellow'] = self._create_enemy_sprite((255, 255, 0))
self.sprites['enemy_red'] = self._create_enemy_sprite((255, 50, 50))  # <-- GENERIC
self.sprites['enemy_flagship'] = self._create_flagship_sprite()
self.sprites['enemy_escort'] = self._create_escort_sprite()
```

---

## 4. PNG Analysis Results

### 4.1 Image Properties

- **File:** `samples/second_row_enemy_animation.png`
- **Size:** 58 x 8 pixels
- **Mode:** RGBA
- **Content:** 5 successive animation frames of red enemy

### 4.2 Frame Structure

The PNG contains **5 distinct enemy sprites** arranged horizontally, each approximately 10-11 pixels wide with gaps between them. These represent the successive left-to-right animation frames.

**Frame positions (approximate):**
- Frame 1: columns 0-10 (width ~11px)
- Frame 2: columns 15-25 (width ~11px)  
- Frame 3: columns 30-40 (width ~11px)
- Frame 4: columns 47-57 (width ~11px)

### 4.3 Color Palette

The enemy sprites use these colors:
- **Red body:** `(224, 0, 0)` and `(213, 0, 0)` - main dragonfly body
- **Yellow wings/antennae:** `(224, 213, 0)` - wing tips and antennae
- **Blue wing base:** `(0, 86, 206)` and `(0, 91, 217)` - wing attachment points
- **Dark accent:** `(11, 0, 0)` - shadow/detail areas
- **Black:** `(0, 0, 0)` - outline/background

### 4.4 Sprite Anatomy (from pixel data)

Each frame shows a **dragonfly-like alien** with:
- **Red body** (center): ~5-6 pixels wide
- **Yellow wing tips** (top): extending outward
- **Blue wing base** (middle): connecting body to wings
- **Dark accents** (bottom): body details

---

## 5. Research Findings

### 5.1 Key Observations

1. **The PNG contains 5 frames** showing the red enemy in different wing positions across the formation
2. **Each frame is ~10-11 pixels wide** with slight variations in wing position
3. **The animation shows wing flapping** - wings move up/down between frames
4. **Colors are consistent** across frames: red body, yellow wing tips, blue wing bases

### 5.2 Frame-by-Frame Analysis

**Frame 1 (cols 0-10):**
- Red body at center
- Yellow wing tips at top-left and top-right
- Blue wing bases connecting to body

**Frame 2 (cols 15-25):**
- Similar structure but wings slightly lower
- Red body unchanged
- Yellow wing tips shifted downward

**Frame 3 (cols 30-40):**
- Wings in intermediate position
- Blue wing bases more visible

**Frame 4 (cols 47-57):**
- Wings returning to raised position
- Completes the flapping cycle

### 5.3 Implementation Approach

To redraw the second row enemy sprite to match the PNG:

1. **Create a new method** `_create_red_enemy_sprite()` in `AssetManager`
2. **Extract 4-5 distinct frames** from the PNG pixel data
3. **Each frame should be 10x10 pixels** (matching current ENEMY_WIDTH/HEIGHT)
4. **Use the exact colors** from the PNG: red body, yellow wing tips, blue wing bases
5. **Register as `enemy_red`** in the sprites dictionary

---

## 6. Recommended Implementation

### 6.1 New AssetManager Method

```python
def _create_red_enemy_sprite(self):
    """Create red enemy sprite from second_row_enemy_animation.png frames.
    
    Returns a list of 4 animation frames showing wing flapping.
    Colors extracted from PNG:
    - Red body: (224, 0, 0)
    - Yellow wing tips: (224, 213, 0)
    - Blue wing bases: (0, 86, 206)
    """
    # Load the PNG and extract frames
    img_path = os.path.join(os.path.dirname(__file__), '..', 'samples', 
                           'second_row_enemy_animation.png')
    img = pygame.image.load(img_path).convert_alpha()
    
    # Extract 4 frames (10x10 each) from the 58x8 PNG
    # Frame positions based on pixel analysis
    frames = []
    frame_positions = [(0, 0), (15, 0), (30, 0), (47, 0)]
    
    for x, y in frame_positions:
        # Create 10x10 surface and blit from PNG
        frame = pygame.Surface((10, 10), pygame.SRCALPHA)
        frame.blit(img, (0, 0), (x, y, 10, 8))
        # Scale to 10x10 if needed
        frames.append(pygame.transform.scale(frame, (10, 10)))
    
    return frames
```

### 6.2 Alternative: Manual Pixel Drawing

If loading from PNG isn't preferred, manually recreate from pixel data:

```python
def _create_red_enemy_sprite(self):
    """Create red enemy sprite with wing animation frames."""
    RED = (224, 0, 0)
    YELLOW = (224, 213, 0)
    BLUE = (0, 86, 206)
    DARK = (11, 0, 0)
    
    frames = []
    
    # Frame 0: wings raised
    surface0 = pygame.Surface((10, 10), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(surface0, RED, (3, 2, 4, 6))
    # Wing tips (yellow)
    pygame.draw.polygon(surface0, YELLOW, [(0, 2), (3, 2), (3, 4)])
    pygame.draw.polygon(surface0, YELLOW, [(10, 2), (7, 2), (7, 4)])
    # Wing bases (blue)
    pygame.draw.polygon(surface0, BLUE, [(1, 4), (3, 4), (3, 6)])
    pygame.draw.polygon(surface0, BLUE, [(9, 4), (7, 4), (7, 6)])
    frames.append(surface0)
    
    # Frame 1: wings slightly lower
    surface1 = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.rect(surface1, RED, (3, 2, 4, 6))
    pygame.draw.polygon(surface1, YELLOW, [(0, 3), (3, 3), (3, 5)])
    pygame.draw.polygon(surface1, YELLOW, [(10, 3), (7, 3), (7, 5)])
    pygame.draw.polygon(surface1, BLUE, [(1, 5), (3, 5), (3, 7)])
    pygame.draw.polygon(surface1, BLUE, [(9, 5), (7, 5), (7, 7)])
    frames.append(surface1)
    
    # ... continue for frames 2-3
    
    return frames
```

### 6.3 Registration Update

```python
# In _generate_sprites():
# Replace:
# self.sprites['enemy_red'] = self._create_enemy_sprite((255, 50, 50))
# With:
self.sprites['enemy_red'] = self._create_red_enemy_sprite()
```

---

## 7. Success Criteria

1. **Red enemies use the new sprite** with 4+ animation frames
2. **Frames match the PNG** in appearance (red body, yellow wing tips, blue wing bases)
3. **Animation cycles smoothly** through all frames during formation movement
4. **Sprite dimensions remain 10x10** (ENEMY_WIDTH/HEIGHT)
5. **All existing tests pass** (enemy type assignment, formation layout, etc.)

---

## 8. Dependencies

- `pygame` for image loading and surface manipulation
- `Pillow` (optional) for PNG frame extraction analysis
- Existing `ENEMY_WIDTH = 10` and `ENEMY_HEIGHT = 10` constants

---

## 10. Implementation Plan

### 10.1 Extracted Frame Data

The PNG contains **4 distinct animation frames** (not 5 as initially suspected), each 11x8 pixels:

| Frame | Columns | Width | Height | Description |
|-------|---------|-------|--------|-------------|
| 0 | 0-10 | 11px | 8px | Wings raised (initial) |
| 1 | 15-25 | 11px | 8px | Wings intermediate-down |
| 2 | 30-40 | 11px | 8px | Wings fully lowered |
| 3 | 47-57 | 11px | 8px | Wings intermediate-up |

### 10.2 Color Palette (Exact from PNG)

| Color | RGB | Usage |
|-------|-----|-------|
| Red (body) | `(224, 0, 0)` / `(213, 0, 0)` | Main dragonfly body |
| Dark red | `(11, 0, 0)` | Shadow/detail areas |
| Yellow (wing tips) | `(224, 213, 0)` | Wing tips and antennae |
| Orange-red | `(224, 11, 0)` | Wing body gradient |
| Blue (wing base) | `(0, 86, 206)` / `(0, 91, 217)` | Wing attachment points |
| Dark blue | `(0, 87, 206)` / `(0, 4, 11)` | Wing shadow areas |
| Black | `(0, 0, 0)` | Outline/background |

### 10.3 Generated Code Location

Complete pygame-compatible sprite generation code has been extracted to:
- **File:** `generated_sprites/red_enemy_sprite_code.py`
- **Function:** `create_red_enemy_sprite()`
- **Returns:** List of 4 pygame Surface objects (11x8px each, will be scaled to 10x10)

### 10.4 Required Changes

1. **Add `_create_red_enemy_sprite()` method** to `AssetManager` class in `assets/__init__.py`
2. **Replace registration** from `self.sprites['enemy_red'] = self._create_enemy_sprite((255, 50, 50))` to `self.sprites['enemy_red'] = self._create_red_enemy_sprite()`
3. **Update Enemy class** in `entities/enemy.py` to handle 4 frames instead of 2 for red enemies
4. **Adjust wing animation timer** to cycle through all 4 frames smoothly

### 10.5 Animation Behavior

The 4 frames create a **smooth wing-flapping animation**:
- Frame 0 → Frame 1 → Frame 2 → Frame 1 → Frame 0 (loop)
- This creates a natural "down-up-down" wing motion
- Each frame transition should occur every 5-10 game frames (based on current wing_timer)

---

## 11. Next Steps

1. **Implement `_create_red_enemy_sprite()`** in `assets/__init__.py` using the generated pixel data
2. **Test animation** in formation display
3. **Verify all tests pass** (enemy type assignment, formation layout, etc.)
4. **Update research document** with test results

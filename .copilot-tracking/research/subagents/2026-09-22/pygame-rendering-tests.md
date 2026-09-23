# Pygame Rendering Tests Research

## Research Topics

1. How to run pygame without a display (software renderer, offscreen rendering)
2. How to capture and verify screen content (pixel colors, surface contents)
3. How to test that blitting works correctly (verify sprite is on surface at expected rect)
4. How to test text rendering (verify font.render() output)
5. pytest fixtures and patterns for rendering tests
6. Pygame-specific testing libraries or approaches
7. How to verify the game's specific draw methods work correctly

---

## Research Findings

### 1. Headless Pygame Rendering Approaches

#### 1.1 SDL_VIDEODRIVER=software (Recommended)

**Problem**: The current game uses `SDL_VIDEODRIVER=dummy` which disables all video output. UI/Rendering tests require a real (but headless) video driver.

**Solution**: Use `SDL_VIDEODRIVER=software` to enable a pure software renderer with no display dependency.

```python
import os
os.environ['SDL_VIDEODRIVER'] = 'software'  # Before pygame.init()
import pygame
```

**Comparison of drivers**:
| Driver | Rendering | Display Needed | Pixel Access |
|--------|-----------|----------------|--------------|
| `dummy` | No | No | No (cannot create surfaces) |
| `software` | Yes | No | Yes (full) |
| `windib` (Windows) | Yes | No | Yes (full) |
| `directx` (Windows) | Yes | No | Limited |

**Key insight**: `SDL_VIDEODRIVER=software` is the best choice for headless rendering tests on Windows. It creates a fully functional software renderer that can create Surfaces, blit sprites, render fonts, and access pixel data — all without a physical display.

**Alternative**: `SDL_VIDEODRIVER=windib` also works headlessly on Windows and may be faster in some cases.

#### 1.2 Offscreen Surface Rendering (Game Architecture)

The Galaxian game already uses an offscreen surface pattern:
- `self.surface` — 256x288 native resolution surface (offscreen)
- `self.screen` — 512x564 display surface (scaled from surface)
- `Game.draw()` fills `self.surface`, then scales it to `self.screen`, then flips

**Testing advantage**: Tests can render directly to `self.surface` (the offscreen surface) without needing display mode at all. This is the cleanest approach:

```python
# Create surface without display mode
surface = pygame.Surface((256, 288))
surface.fill((0, 0, 0))  # Black background
surface.blit(some_sprite, (50, 50))
# Verify pixels on surface directly
```

### 2. Capturing and Verifying Screen Content

#### 2.1 pygame.surfarray (Recommended — NumPy-based)

**`pygame.surfarray.array3d(surface)`** — Returns a (width, height, 3) NumPy array of RGB values:

```python
import pygame.surfarray
import numpy as np

# Convert surface to RGB array
rgb_array = pygame.surfarray.array3d(surface)
# Shape: (256, 288, 3) for the Galaxian surface

# Check if a specific pixel is white (255, 255, 255)
pixel_color = rgb_array[x, y]  # Returns [R, G, B]
assert tuple(pixel_color) == (255, 255, 255), f"Expected white, got {pixel_color}"

# Check if any pixel matches a color
white_mask = np.all(rgb_array == [255, 255, 255], axis=2)
assert np.any(white_mask), "Expected white pixels not found"

# Count non-black pixels (sprites drawn)
non_black = np.count_nonzero(np.any(rgb_array > 0, axis=2))
assert non_black > 0, "No sprites were drawn"
```

**`pygame.surfarray.array2d(surface)`** — Returns a 2D array of mapped pixel integers:

```python
# Convert surface to 2D mapped array
mapped = pygame.surfarray.array2d(surface)
# Access pixel: mapped[x, y] returns mapped integer
```

#### 2.2 pygame.PixelArray (Direct pixel access)

```python
with pygame.PixelArray(surface) as pxarray:
    # Check pixel at (x, y)
    pixel = pxarray[x, y]
    expected = surface.map_rgb((255, 255, 255))
    assert pixel == expected

    # Check a region
    region = pxarray[10:20, 10:20]
    # Returns a 2D PixelArray slice

    # Replace colors
    pxarray.replace((0, 0, 0), (128, 128, 128))

    # Extract a color (creates mask)
    mask = pxarray.extract((255, 0, 0))
```

#### 2.3 Surface.get_at() (Single pixel — slower)

```python
# Get single pixel color
color = surface.get_at((x, y))  # Returns pygame.Color
assert tuple(color) == (255, 255, 255, 255)  # RGBA

# Check multiple pixels (slower but simple)
for x, y in expected_sprite_region:
    color = surface.get_at((x, y))
    assert color != (0, 0, 0, 255), f"Sprite pixel at ({x},{y}) is black"
```

#### 2.4 Surface.get_view() (Modern buffer access — pygame 1.9.2+)

```python
# Get RGB plane directly
rgb_view = surface.get_view('3')  # Returns BufferProxy
# Convert to numpy:
import numpy as np
rgb_array = np.asarray(rgb_view).reshape(surface.get_width(), surface.get_height(), 3)
```

### 3. Testing Blitting Correctly

#### 3.1 Verify Sprite Appears on Surface

```python
def test_sprite_blitted_at_position(game):
    """Verify a sprite is drawn at the expected rect position."""
    # Get surface before and after draw
    before = pygame.surfarray.array3d(game.surface)

    # Draw the game (sprites should appear)
    game.draw()

    after = pygame.surfarray.array3d(game.surface)

    # Get player rect position
    player_rect = game.player.rect

    # Check that pixels at player position differ from black background
    player_region = after[player_rect.y:player_rect.bottom,
                          player_rect.x:player_rect.right]
    non_black = np.count_nonzero(np.any(player_region > 0, axis=2))
    assert non_black > 0, f"Player sprite not found at rect {player_rect}"
```

#### 3.2 Verify Sprite Image Content

```python
def test_player_sprite_correct_image(game):
    """Verify the player sprite uses the correct asset image."""
    player = game.player
    sprite = player.image

    # Create a test surface and blit the sprite
    test_surface = pygame.Surface((256, 288))
    test_surface.fill((0, 0, 0))  # Black background
    test_surface.blit(sprite, (50, 100))

    # Get the sprite's bounding rect (non-black pixels)
    bounding_rect = sprite.get_bounding_rect()

    # Verify sprite is not empty
    assert bounding_rect.width > 0 and bounding_rect.height > 0

    # Verify sprite dimensions match expected
    assert sprite.get_width() == 12  # PLAYER_WIDTH
    assert sprite.get_height() == 12  # PLAYER_HEIGHT
```

#### 3.3 Verify Blit Rect Position

```python
def test_enemy_positions_in_formation(game):
    """Verify enemies are blitted at their formation positions."""
    from constants import FORMATION_TOP, FORMATION_SPACING_X, FORMATION_SPACING_Y

    for i, enemy in enumerate(game.enemies):
        expected_x = FORMATION_TOP + (i % 5) * FORMATION_SPACING_X
        expected_y = FORMATION_TOP + (i // 5) * FORMATION_SPACING_Y

        assert enemy.rect.x == expected_x, \
            f"Enemy at index {i} has x={enemy.rect.x}, expected {expected_x}"
        assert enemy.rect.y == expected_y, \
            f"Enemy at index {i} has y={enemy.rect.y}, expected {expected_y}"
```

#### 3.4 Verify Colorkey Transparency

```python
def test_colorkey_transparency(surface, sprite, colorkey):
    """Verify transparent pixels are not drawn."""
    surface.blit(sprite, (0, 0))
    array = pygame.surfarray.array3d(surface)

    # Check that colorkey pixels on sprite are not present on destination
    # (they should remain the background color)
```

### 4. Testing Text Rendering

#### 4.1 Verify Font.render() Output

```python
def test_font_render_text(font, text, expected_color):
    """Verify text renders with expected properties."""
    rendered = font.render(text, True, expected_color)

    # Verify rendered surface dimensions
    expected_width, expected_height = font.size(text)
    assert rendered.get_width() == expected_width
    assert rendered.get_height() == expected_height

    # Verify text is not blank (has non-black pixels)
    array = pygame.surfarray.array3d(rendered)
    non_black = np.count_nonzero(np.any(array > 0, axis=2))
    assert non_black > 0, "Text rendered as blank"

    # Verify background is transparent or expected
    # (check corners for transparency/background)
    if rendered.get_flags() & pygame.SRCALPHA:
        top_left = rendered.get_at((0, 0))
        assert top_left.a == 0, "Expected transparent background"
```

#### 4.2 Verify HUD Text Content and Position

```python
def test_hud_score_position(game):
    """Verify score text is rendered at top-left of HUD."""
    # Draw HUD
    game._draw_hud()

    # Get surface array
    array = pygame.surfarray.array3d(game.surface)

    # Score text should have non-black pixels near (5, 5)
    # Check a small region where score text appears
    hud_region = array[5:15, 5:25]
    non_black = np.count_nonzero(np.any(hud_region > 0, axis=2))
    assert non_black > 0, "HUD score text not rendered"
```

#### 4.3 Verify Font Properties

```python
def test_font_bold_attribute(font):
    """Verify bold rendering is applied."""
    assert font.bold is True

    regular = font.render("test", False, (255, 255, 255))
    font.set_bold(True)
    bold = font.render("test", False, (255, 255, 255))
    assert bold.get_width() > regular.get_width(), "Bold text should be wider"
```

### 5. Pytest Fixtures and Patterns

#### 5.1 Game Fixtures

```python
import pytest
import os
import pygame

os.environ['SDL_VIDEODRIVER'] = 'software'

@pytest.fixture
def pygame_init():
    """Initialize and finalize pygame for each test."""
    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
    yield
    pygame.quit()

@pytest.fixture
def asset_manager():
    """Provide a fresh AssetManager."""
    from assets import AssetManager
    return AssetManager()

@pytest.fixture
def game(pygame_init, asset_manager):
    """Provide a fresh Game instance with mocked display."""
    from game.game import Game
    from constants import SCREEN_WIDTH, SCREEN_HEIGHT, DISPLAY_WIDTH, DISPLAY_HEIGHT

    # Create game without display
    game = Game.__new__(Game)  # Bypass __init__ display creation
    pygame.init()
    pygame.mixer.init()

    # Set up game state manually
    game.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    game.clock = pygame.time.Clock()
    game.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    game.asset_manager = asset_manager
    game.starfield = None  # Set up as needed
    game.state = None
    game.round_num = 1
    game.score = 0
    game.lives = 3
    game.high_score = 0
    game.player = None
    game.enemies = []
    game.enemy_bullets = []
    game.explosions = []
    # ... etc
    return game

@pytest.fixture
def black_surface():
    """Provide a black 256x288 surface (Galaxian native resolution)."""
    return pygame.Surface((256, 288))

@pytest.fixture
def sample_sprite(asset_manager):
    """Provide a sample enemy sprite for testing."""
    return asset_manager.sprites['enemy_green'][0]
```

#### 5.2 Surface Comparison Helper

```python
@pytest.fixture
def surface_comparator():
    """Provide a helper for comparing surface contents."""
    class SurfaceComparator:
        def __init__(self, surface):
            self.surface = surface
            self.array = pygame.surfarray.array3d(surface)

        def pixel_at(self, x, y):
            return tuple(self.array[x, y])

        def has_non_black_pixels(self, x1, y1, x2, y2):
            region = self.array[y1:y2, x1:x2]
            return np.any(region > 0)

        def count_non_black(self, x1, y1, x2, y2):
            region = self.array[y1:y2, x1:x2]
            return np.count_nonzero(np.any(region > 0, axis=2))

        def compare_regions(self, other, x1, y1, x2, y2, tolerance=5):
            """Compare pixel regions with tolerance for anti-aliasing."""
            region1 = self.array[y1:y2, x1:x2]
            region2 = other.array[y1:y2, x1:x2]
            diff = np.abs(region1.astype(int) - region2.astype(int))
            return np.all(diff <= tolerance)

    return SurfaceComparator
```

### 6. Pygame-Specific Testing Libraries

#### 6.1 pygame.tests (Official Test Suite)

Pygame ships with its own test suite (`pygame.tests`), but it's designed for testing pygame itself, not games built with pygame. It uses subprocess isolation and custom test runners.

#### 6.2 No Specialized Library Found

After research, no dedicated "pytest-pygame" library was found on PyPI or GitHub. The community standard is to use:
- `pytest` for test organization
- `pygame.surfarray` for pixel verification
- `SDL_VIDEODRIVER=software` for headless operation
- Custom fixtures for game state management

#### 6.3 Recommended Test Structure

```
tests/
    __init__.py
    test_rendering/
        __init__.py
        test_draw_methods.py      # Game.draw(), _draw_*() methods
        test_blitting.py           # Sprite blitting verification
        test_text_rendering.py     # Font.render(), HUD text
        test_surfaces.py           # Surface creation, scaling
    test_entities/
        __init__.py
        test_player.py             # Player.draw()
        test_enemy.py              # Enemy.draw()
    test_assets/
        __init__.py
        test_asset_generation.py   # Programmatic sprite creation
    conftest.py                    # Shared fixtures
```

### 7. Verifying Galaxian-Specific Draw Methods

#### 7.1 Game.draw() Method

```python
def test_game_draw_populates_surface(game):
    """Test that Game.draw() draws to the offscreen surface."""
    game.state = GameState.ATTRACT
    game.draw()

    # Surface should have non-black pixels (title text, etc.)
    array = pygame.surfarray.array3d(game.surface)
    non_black = np.count_nonzero(np.any(array > 0, axis=2))
    assert non_black > 0, "Game.draw() did not render anything"

def test_game_draw_scales_to_screen(game):
    """Test that Game.draw() scales surface to display size."""
    game.draw()

    # Screen should be scaled version of surface
    screen_array = pygame.surfarray.array3d(game.screen)
    surface_array = pygame.surfarray.array3d(game.surface)

    assert screen_array.shape == (DISPLAY_WIDTH, DISPLAY_HEIGHT, 3)
    assert surface_array.shape == (SCREEN_WIDTH, SCREEN_HEIGHT, 3)
```

#### 7.2 _draw_attract() Method

```python
def test_draw_attract_shows_title(game):
    """Test attract mode renders title text."""
    game.state = GameState.ATTRACT
    game._draw_attract()

    array = pygame.surfarray.array3d(game.surface)

    # Title "GALAXIAN" should be rendered in WHITE near top center
    # Check for white pixels in title area
    title_region = array[50:80, 80:180]  # Approximate title position
    white_mask = np.all(title_region == [255, 255, 255], axis=2)
    assert np.any(white_mask), "Title text not rendered in white"
```

#### 7.3 _draw_hud() Method

```python
def test_draw_hud_shows_score(game):
    """Test HUD renders score text."""
    game.score = 1234
    game.high_score = 5678
    game.lives = 3
    game.round_num = 2
    game.state = GameState.PLAYING

    game._draw_hud()

    array = pygame.surfarray.array3d(game.surface)

    # Score text at (5, 5) should have non-black pixels
    assert game.surface.has_non_black_pixels(5, 5, 40, 15)

def test_draw_hud_shows_lives(game):
    """Test HUD renders lives count."""
    game.lives = 2
    game._draw_hud()

    # Lives text at bottom-left should have non-black pixels
    array = pygame.surfarray.array3d(game.surface)
    lives_region = array[270:280, 5:25]
    assert np.any(np.any(lives_region > 0, axis=2)), "Lives text not rendered"
```

#### 7.4 Entity.draw() Methods

```python
def test_player_draw_blits_sprite(game):
    """Test Player.draw() blits the player sprite."""
    game.player.alive = True
    game.player.invincible = False
    game.player.draw(game.surface)

    array = pygame.surfarray.array3d(game.surface)
    rect = game.player.rect

    # Check for non-black pixels in player rect area
    player_region = array[rect.y:rect.bottom, rect.x:rect.right]
    non_black = np.count_nonzero(np.any(player_region > 0, axis=2))
    assert non_black > 0, "Player sprite not blitted"

def test_player_draw_skips_when_dead(game):
    """Test Player.draw() does nothing when player is dead."""
    game.player.alive = False
    game.surface.fill((255, 0, 0))  # Red background
    game.player.draw(game.surface)

    # Surface should remain unchanged (red)
    array = pygame.surfarray.array3d(game.surface)
    assert np.all(array == [255, 0, 0]), "Player.draw() modified surface while dead"

def test_enemy_draw_uses_correct_sprite(game, asset_manager):
    """Test Enemy.draw() uses the correct type-specific sprite."""
    enemy = Enemy(50, 50, 'green', asset_manager)
    enemy.draw(game.surface)

    array = pygame.surfarray.array3d(game.surface)
    # Green enemy should render with green-dominant colors
    enemy_region = array[50:60, 50:60]
    green_dominant = np.any(enemy_region[:, :, 1] > enemy_region[:, :, 0], axis=1)
    assert np.any(green_dominant), "Green enemy sprite not rendered correctly"
```

#### 7.5 Round Transition and Game Over

```python
def test_draw_round_transition(game):
    """Test round transition overlay renders."""
    game.round_num = 3
    game.state = GameState.ROUND_TRANSITION
    game.round_transition_timer = 60
    game.draw()

    array = pygame.surfarray.array3d(game.surface)

    # Semi-transparent overlay should be present
    # Check for non-black pixels in center (ROUND 3 text)
    center_region = array[130:160, 80:180]
    non_black = np.count_nonzero(np.any(center_region > 0, axis=2))
    assert non_black > 0, "Round transition text not rendered"

def test_draw_game_over(game):
    """Test game over screen renders."""
    game.score = 9999
    game.state = GameState.GAME_OVER
    game.draw()

    array = pygame.surfarray.array3d(game.surface)

    # "GAME OVER" in RED should be rendered
    go_region = array[90:120, 70:150]
    red_mask = (go_region[:, :, 0] > 200) & (go_region[:, :, 1] < 100) & (go_region[:, :, 2] < 100)
    assert np.any(red_mask), "GAME OVER text not rendered in red"
```

### 8. Testing Programmatic Sprite Generation

```python
def test_player_sprite_dimensions():
    """Test player sprite is 12x12 as defined in constants."""
    from assets import AssetManager
    am = AssetManager()
    sprite = am.sprites['player']
    assert sprite.get_width() == 12
    assert sprite.get_height() == 12

def test_enemy_sprite_animation_frames():
    """Test enemy sprites have wing animation frames."""
    from assets import AssetManager
    am = AssetManager()
    enemy_frames = am.sprites['enemy_green']
    assert isinstance(enemy_frames, list)
    assert len(enemy_frames) == 2  # Two wing frames
    for frame in enemy_frames:
        assert frame.get_width() == 10
        assert frame.get_height() == 10

def test_flagship_sprite_dimensions():
    """Test flagship sprite is 14x14."""
    from assets import AssetManager
    am = AssetManager()
    sprite = am.sprites['enemy_flagship']
    if isinstance(sprite, list):
        for s in sprite:
            assert s.get_width() == 14
            assert s.get_height() == 14
    else:
        assert sprite.get_width() == 14
        assert sprite.get_height() == 14

def test_bullet_sprite_colors():
    """Test bullet sprites have expected colors."""
    from assets import AssetManager
    am = AssetManager()

    # Player bullet should be white
    player_bullet = am.sprites['player_bullet']
    assert player_bullet.get_width() == 2
    assert player_bullet.get_height() == 6

    # Enemy bullet should be reddish
    enemy_bullet = am.sprites['enemy_bullet']
    assert enemy_bullet.get_width() == 2
    assert enemy_bullet.get_height() == 4
```

### 9. Testing Surface Scaling (Transform)

```python
def test_surface_scaling_preserves_colors():
    """Test that scaling the surface preserves pixel colors."""
    pygame.init()
    surface = pygame.Surface((256, 288))
    surface.fill((255, 0, 0))  # Red

    scaled = pygame.transform.scale(surface, (512, 564))

    # Pixel at center of scaled surface should still be red
    center_pixel = scaled.get_at((256, 282))
    assert tuple(center_pixel)[:3] == (255, 0, 0), "Color not preserved during scaling"

    pygame.quit()

def test_scaled_dimensions():
    """Test scaled surface has correct dimensions."""
    pygame.init()
    surface = pygame.Surface((256, 288))
    scaled = pygame.transform.scale(surface, (512, 564))

    assert scaled.get_width() == 512
    assert scaled.get_height() == 564

    pygame.quit()
```

### 10. Key Implementation Recommendations

#### 10.1 Use `SDL_VIDEODRIVER=software` Instead of `dummy`

```python
# In conftest.py or test file header:
import os
os.environ['SDL_VIDEODRIVER'] = 'software'  # BEFORE pygame.init()
```

This enables full rendering capabilities while remaining headless.

#### 10.2 Test Offscreen Surface Directly

Since Galaxian uses an offscreen surface pattern, test `game.surface` (256x288) directly:

```python
def test_hud_rendered_on_offscreen_surface(game):
    game._draw_hud()
    array = pygame.surfarray.array3d(game.surface)
    # Verify HUD pixels on offscreen surface
```

#### 10.3 Use NumPy for Efficient Pixel Verification

```python
import numpy as np
import pygame.surfarray

array = pygame.surfarray.array3d(surface)

# Count non-black pixels
non_black = np.count_nonzero(np.any(array > 0, axis=2))

# Check for specific color in region
region = array[y1:y2, x1:x2]
white_mask = np.all(region == [255, 255, 255], axis=2)
has_white = np.any(white_mask)

# Check for red (GAME OVER text)
red_mask = (region[:, :, 0] > 200) & (region[:, :, 1] < 100) & (region[:, :, 2] < 100)
has_red = np.any(red_mask)
```

#### 10.4 Handle Timer-Dependent Rendering

For blinking text and invincibility flashing, set known timer states:

```python
def test_blinking_start_text(game):
    game.attract_timer = 0  # Visible
    game._draw_attract()
    array = pygame.surfarray.array3d(game.surface)
    assert np.count_nonzero(np.any(array > 0, axis=2)) > 0

    game.attract_timer = 50  # Hidden (50 % 60 = 50, which is >= 40)
    game._draw_attract()
    # Verify start text region is black
```

### 11. Test File Structure

```
tests/
├── __init__.py
├── conftest.py                  # Shared fixtures (pygame, game, surfaces)
├── test_integration.py          # Existing integration tests
├── test_rendering/              # NEW: UI/Rendering tests
│   ├── __init__.py
│   ├── test_draw_methods.py     # Game.draw(), _draw_*() methods
│   ├── test_blitting.py         # Sprite blitting verification
│   ├── test_text_rendering.py   # Font.render(), HUD text
│   ├── test_surfaces.py         # Surface creation, scaling
│   └── test_sprites.py          # Programmatic sprite generation
├── test_entities/
│   ├── __init__.py
│   ├── test_player.py           # Player.draw() with blitting
│   ├── test_enemy.py            # Enemy.draw() with blitting
│   ├── test_bullet.py           # Bullet.draw() with blitting
│   └── test_explosion.py        # Explosion.draw() animation
└── test_systems/
    ├── __init__.py
    └── test_starfield.py        # Starfield.draw() rendering
```

### 12. Dependencies

No new dependencies required. The project already has:
- `pytest` (for test framework)
- `numpy` (for pixel array operations)
- `pygame` (for rendering)

### 13. CI/CD Considerations

For CI/CD environments:
- `SDL_VIDEODRIVER=software` works in headless CI
- Font rendering may vary by OS (Arial may not be available on Linux CI)
- Consider using `pygame.font.init()` explicitly before font creation
- Test font availability: `pygame.font.get_fonts()` returns available fonts

### 14. Summary

This research provides a complete blueprint for adding UI/Rendering tests to the Galaxian game:

1. **Switch from `dummy` to `software` SDL driver** for headless rendering
2. **Use `pygame.surfarray` with NumPy** for efficient pixel verification
3. **Test offscreen surface directly** rather than scaled display surface
4. **Create dedicated test files** for draw methods, blitting, text rendering, and sprite generation
5. **Use pytest fixtures** for reusable game state setup
6. **Handle timer-dependent rendering** by setting known timer values
7. **No new dependencies required** — uses existing pytest, numpy, and pygame

---

**Status**: Complete
**Date**: 2026-09-22
**Next Steps**: Create test files in `tests/test_rendering/` directory structure

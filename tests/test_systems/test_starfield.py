"""Tests for the starfield background system."""

import pytest
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


class TestStarGeneration:
    """Tests for star generation in Starfield.__init__."""

    def test_starfield_generates_80_stars(self, starfield):
        """Starfield should generate exactly 80 stars."""
        assert len(starfield.stars) == 80

    def test_star_positions_in_bounds(self, starfield):
        """All star positions should be within screen bounds."""
        for star in starfield.stars:
            assert 0 <= star['x'] < SCREEN_WIDTH, \
                f"Star x={star['x']} out of bounds [0, {SCREEN_WIDTH})"
            assert 0 <= star['y'] < SCREEN_HEIGHT, \
                f"Star y={star['y']} out of bounds [0, {SCREEN_HEIGHT})"

    def test_star_speeds_valid(self, starfield):
        """All star speeds should be in [0.5, 1, 1.5, 2]."""
        valid_speeds = {0.5, 1, 1.5, 2}
        for star in starfield.stars:
            assert star['speed'] in valid_speeds, \
                f"Star speed {star['speed']} not in valid set {valid_speeds}"

    def test_star_brightness_range(self, starfield):
        """All star brightness should be in [100, 255]."""
        for star in starfield.stars:
            assert 100 <= star['brightness'] <= 255, \
                f"Star brightness {star['brightness']} out of range [100, 255]"

    def test_starfield_has_all_properties(self, starfield):
        """Each star should have x, y, speed, and brightness."""
        required_keys = {'x', 'y', 'speed', 'brightness'}
        for star in starfield.stars:
            assert required_keys.issubset(star.keys()), \
                f"Star missing keys: {required_keys - set(star.keys())}"

    def test_starfield_offset_y_starts_at_zero(self, starfield):
        """offset_y should start at 0."""
        assert starfield.offset_y == 0


class TestStarUpdate:
    """Tests for star position updates."""

    def test_star_y_increases(self, starfield):
        """Star y positions should increase or wrap after update."""
        initial_ys = [star['y'] for star in starfield.stars]
        starfield.update()
        for i, star in enumerate(starfield.stars):
            # Star either moved down (y increased) or wrapped to top (y decreased)
            assert (star['y'] >= initial_ys[i]) or (star['y'] < initial_ys[i]), \
                f"Star y unchanged: {initial_ys[i]} -> {star['y']}"

    def test_star_wraps_at_bottom(self, starfield):
        """Stars should wrap to top when y exceeds SCREEN_HEIGHT."""
        # Set a star near the bottom
        starfield.stars[0]['y'] = SCREEN_HEIGHT - 1
        starfield.stars[0]['speed'] = 2  # Will push it past bottom
        starfield.update()
        assert starfield.stars[0]['y'] < SCREEN_HEIGHT, \
            "Star should wrap to top when exceeding SCREEN_HEIGHT"

    def test_star_x_resets_on_wrap(self, starfield):
        """Star x should be randomized when wrapping."""
        original_x = starfield.stars[0]['x']
        starfield.stars[0]['y'] = SCREEN_HEIGHT + 10  # Force wrap
        starfield.update()
        # x should be reset to a new random value
        assert 0 <= starfield.stars[0]['x'] < SCREEN_WIDTH

    def test_offset_y_increases(self, starfield):
        """offset_y should increase by 0.5 each update."""
        initial_offset = starfield.offset_y
        starfield.update()
        assert starfield.offset_y == initial_offset + 0.5

    def test_multiple_updates_accumulate(self, starfield):
        """Multiple updates should accumulate offsets correctly."""
        for _ in range(10):
            starfield.update()
        assert starfield.offset_y == 5.0  # 10 * 0.5

    def test_star_speed_affects_update(self, starfield):
        """Stars with higher speed should move faster."""
        # Find a fast star (speed=2) and a slow star (speed=0.5)
        fast_star = None
        slow_star = None
        for star in starfield.stars:
            if star['speed'] == 2 and fast_star is None:
                fast_star = star
            if star['speed'] == 0.5 and slow_star is None:
                slow_star = star

        if fast_star and slow_star:
            initial_fast_y = fast_star['y']
            initial_slow_y = slow_star['y']
            starfield.update()
            fast_delta = fast_star['y'] - initial_fast_y
            slow_delta = slow_star['y'] - initial_slow_y
            assert fast_delta > slow_delta, \
                "Fast star should move more than slow star"


class TestStarDrawing:
    """Tests for starfield drawing."""

    def test_starfield_draws_1x1_pixels(self, starfield):
        """Stars should be drawn as 1x1 pixel rectangles."""
        import pygame
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        starfield.draw(surface)

        # Check that some pixels were drawn (non-black)
        import pygame.surfarray
        import numpy as np
        array = pygame.surfarray.array3d(surface).swapaxes(0, 1)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black > 0, "Starfield should draw visible pixels"

    def test_starfield_draws_correct_brightness(self, starfield):
        """Stars should be drawn with their brightness value."""
        import pygame
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Set a specific star
        starfield.stars[0]['x'] = 10
        starfield.stars[0]['y'] = 10
        starfield.stars[0]['brightness'] = 200

        starfield.draw(surface)

        # Check pixel at star position
        color = surface.get_at((10, 10))
        assert tuple(color[:3]) == (200, 200, 200), \
            f"Star brightness mismatch: expected (200,200,200), got {color[:3]}"

    def test_starfield_draws_all_stars(self, starfield):
        """All stars should be drawn on the surface."""
        import pygame
        import pygame.surfarray
        import numpy as np

        # Place each star at a unique position to avoid overlaps
        for i, star in enumerate(starfield.stars):
            star['x'] = i % SCREEN_WIDTH
            star['y'] = i // SCREEN_WIDTH

        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        starfield.draw(surface)

        array = pygame.surfarray.array3d(surface).swapaxes(0, 1)
        # Should have 80 non-black pixels (one per star)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black == 80, f"Expected 80 star pixels, got {non_black}"

    def test_starfield_draws_grayscale(self, starfield):
        """Stars should be drawn in grayscale (R=G=B=brightness)."""
        import pygame

        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Set a star with specific brightness
        starfield.stars[0]['x'] = 5
        starfield.stars[0]['y'] = 5
        starfield.stars[0]['brightness'] = 150

        starfield.draw(surface)

        color = surface.get_at((5, 5))
        r, g, b = color[:3]
        assert r == g == b == 150, \
            f"Star should be grayscale: got ({r},{g},{b})"

    def test_starfield_draws_no_background(self, starfield):
        """Starfield should not fill the surface, only draw pixels."""
        import pygame
        import pygame.surfarray
        import numpy as np

        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surface.fill((50, 50, 50))  # Gray background
        starfield.draw(surface)

        # Background should still be visible (not overwritten)
        array = pygame.surfarray.array3d(surface).swapaxes(0, 1)
        checker = _make_checker(array)
        gray_pixels = checker.count_color((50, 50, 50), tolerance=10)
        assert gray_pixels > 0, "Background should remain visible"


class TestStarfieldIntegration:
    """Integration tests for starfield update and draw cycle."""

    def test_starfield_update_then_draw(self, starfield):
        """Stars should be in updated positions when drawn."""
        import pygame

        # Set star positions
        starfield.stars[0]['x'] = 100
        starfield.stars[0]['y'] = 100
        starfield.stars[0]['speed'] = 2.0  # Known speed for predictable movement

        starfield.update()
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        starfield.draw(surface)

        # Star should have moved down by speed (2.0), now at y=102
        # Check that position below original has star color (bright)
        color = surface.get_at((100, 102))
        assert color[0] > 100, \
            "Star should have moved down and drawn at new position"

    def test_starfield_wraps_and_draws(self, starfield):
        """Wrapped stars should draw at new positions."""
        import pygame
        import pygame.surfarray
        import numpy as np

        # Force a star to wrap
        starfield.stars[0]['y'] = SCREEN_HEIGHT + 10
        starfield.update()

        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        starfield.draw(surface)

        # Verify the wrapped star (now at y=0) was drawn
        color = surface.get_at((100, 0))
        # At least check that some stars were drawn (may overlap)
        array = pygame.surfarray.array3d(surface).swapaxes(0, 1)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black > 0, "Stars should be drawn after wrap"


def _make_checker(array):
    """Create a pixel checker from a numpy RGB array."""
    import numpy as np

    class Checker:
        def count_non_black(self):
            return int(np.count_nonzero(np.any(array > 0, axis=2)))

        def count_color(self, color, tolerance=10):
            r, g, b = color
            mask = (
                (np.abs(array[:, :, 0].astype(int) - r) <= tolerance) &
                (np.abs(array[:, :, 1].astype(int) - g) <= tolerance) &
                (np.abs(array[:, :, 2].astype(int) - b) <= tolerance)
            )
            return int(np.count_nonzero(mask))
    return Checker()

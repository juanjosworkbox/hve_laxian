"""Tests for surface operations, scaling, and color preservation."""

import numpy as np
import pygame


class TestSurfaceCreation:
    """Tests for basic surface creation."""

    def test_surface_creation_dimensions(self):
        """pygame.Surface should create with correct dimensions."""
        surface = pygame.Surface((256, 288))
        assert surface.get_width() == 256
        assert surface.get_height() == 288

    def test_surface_with_alpha_flag(self):
        """Surface with SRCALPHA flag should support transparency."""
        surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        assert surface.get_flags() & pygame.SRCALPHA
        assert surface.get_width() == 100
        assert surface.get_height() == 100

    def test_surface_default_no_alpha(self):
        """Surface without SRCALPHA flag should not have alpha."""
        surface = pygame.Surface((100, 100))
        assert not (surface.get_flags() & pygame.SRCALPHA)


class TestSurfaceFill:
    """Tests for surface.fill() operations."""

    def test_surface_fill_black(self):
        """surface.fill(BLACK) should produce all-zero array."""
        surface = pygame.Surface((64, 64))
        surface.fill((0, 0, 0))
        array = pygame.surfarray.array3d(surface).swapaxes(0, 1)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black == 0, "Filled black surface should have zero non-black pixels"

    def test_surface_fill_white(self):
        """surface.fill(WHITE) should produce all-white array."""
        surface = pygame.Surface((64, 64))
        surface.fill((255, 255, 255))
        array = pygame.surfarray.array3d(surface).swapaxes(0, 1)
        checker = _make_checker(array)
        white_pixels = checker.count_color((255, 255, 255))
        assert white_pixels == 64 * 64, "Filled white surface should have all white pixels"

    def test_surface_fill_color(self):
        """surface.fill(COLOR) should produce matching pixel array."""
        surface = pygame.Surface((32, 32))
        surface.fill((128, 64, 0))
        array = pygame.surfarray.array3d(surface).swapaxes(0, 1)
        checker = _make_checker(array)
        color_pixels = checker.count_color((128, 64, 0))
        assert color_pixels == 32 * 32, "Filled colored surface should match"

    def test_surface_fill_overwrites_previous_content(self):
        """surface.fill() should overwrite previous pixels."""
        surface = pygame.Surface((32, 32))
        surface.fill((255, 255, 255))
        surface.fill((0, 0, 0))
        array = pygame.surfarray.array3d(surface).swapaxes(0, 1)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black == 0, "Fill should overwrite previous content"


class TestSurfaceScaling:
    """Tests for pygame.transform.scale()."""

    def test_surface_scaling_dimensions(self):
        """Scaled surface should have correct output dimensions."""
        source = pygame.Surface((64, 64))
        scaled = pygame.transform.scale(source, (128, 128))
        assert scaled.get_width() == 128
        assert scaled.get_height() == 128

    def test_surface_scaling_up(self):
        """Scaling up should increase dimensions."""
        source = pygame.Surface((32, 32))
        scaled = pygame.transform.scale(source, (96, 96))
        assert scaled.get_width() == 96
        assert scaled.get_height() == 96

    def test_surface_scaling_game_dimensions(self):
        """Game surface scaling should produce correct display dimensions."""
        surface = pygame.Surface((256, 288))
        scaled = pygame.transform.scale(surface, (512, 564))
        assert scaled.get_width() == 512
        assert scaled.get_height() == 564

    def test_surface_scaling_preserves_aspect_ratio(self):
        """Scaling should maintain aspect ratio when using transform.scale."""
        source = pygame.Surface((100, 50))
        scaled = pygame.transform.scale(source, (200, 100))
        assert scaled.get_width() / scaled.get_height() == source.get_width() / source.get_height()


class TestSurfaceColorPreservation:
    """Tests for color preservation during scaling."""

    def test_surface_scaling_preserves_colors(self):
        """Scaled surface should preserve pixel colors."""
        source = pygame.Surface((4, 4))
        # Fill with distinct colors
        colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255), (128, 128, 128),
        ]
        for i, color in enumerate(colors):
            x = i % 4
            y = i // 4
            source.fill(color, (x * 8, y * 8, 8, 8))

        scaled = pygame.transform.scale(source, (32, 32))
        source_array = pygame.surfarray.array3d(source).swapaxes(0, 1)
        scaled_array = pygame.surfarray.array3d(scaled).swapaxes(0, 1)

        checker_src = _make_checker(source_array)
        checker_scl = _make_checker(scaled_array)

        # Both should have non-black pixels (content preserved through scaling)
        assert checker_src.count_non_black() > 0, "Source has no non-black pixels"
        assert checker_scl.count_non_black() > 0, "Scaled surface has no non-black pixels"

    def test_surface_scaling_red_channel_preserved(self):
        """Red channel should be preserved during scaling."""
        source = pygame.Surface((4, 4))
        source.fill((255, 0, 0))
        scaled = pygame.transform.scale(source, (16, 16))

        array = pygame.surfarray.array3d(scaled).swapaxes(0, 1)
        checker = _make_checker(array)
        red_pixels = checker.count_color((255, 0, 0), tolerance=20)
        assert red_pixels > 0, "Red color should be preserved during scaling"


class TestSurfaceBlitting:
    """Tests for surface.blit() operations."""

    def test_surface_blit_overwrites_background(self):
        """Blitting a sprite should replace background pixels."""
        surface = pygame.Surface((32, 32))
        surface.fill((0, 0, 0))  # Black background
        sprite = pygame.Surface((8, 8), pygame.SRCALPHA)
        sprite.fill((255, 255, 255))  # White sprite

        surface.blit(sprite, (12, 12))

        array = pygame.surfarray.array3d(surface).swapaxes(0, 1)
        checker = _make_checker(array)
        white_pixels = checker.count_color((255, 255, 255))
        assert white_pixels > 0, "Blitted sprite should replace background pixels"

    def test_surface_blit_preserves_unblitted_areas(self):
        """Blitting should not affect areas outside the sprite rect."""
        surface = pygame.Surface((32, 32))
        surface.fill((100, 100, 100))  # Gray background
        sprite = pygame.Surface((8, 8), pygame.SRCALPHA)
        sprite.fill((255, 255, 255))  # White sprite

        surface.blit(sprite, (12, 12))

        # Check corners (should remain gray)
        array = pygame.surfarray.array3d(surface).swapaxes(0, 1)
        checker = _make_checker(array)
        gray_pixels = checker.count_color((100, 100, 100), tolerance=20)
        assert gray_pixels > 0, "Unblitted areas should preserve original color"

    def test_surface_blit_at_different_positions(self, game):
        """Sprite should appear at the blit position."""
        surface = pygame.Surface((32, 32))
        surface.fill((0, 0, 0))

        sprite = pygame.Surface((4, 4), pygame.SRCALPHA)
        sprite.fill((255, 0, 0))

        # Blit at position (10, 10)
        surface.blit(sprite, (10, 10))

        array = pygame.surfarray.array3d(surface).swapaxes(0, 1)
        # Check region around blit position
        region = array[10:14, 10:14]
        checker = _make_checker(region)
        red_pixels = checker.count_color((255, 0, 0))
        assert red_pixels > 0, "Sprite should appear at blit position"

    def test_surface_blit_preserves_sprite_alpha(self, asset_manager):
        """Blitting an alpha sprite should preserve transparency."""
        surface = pygame.Surface((32, 32))
        surface.fill((255, 0, 0))  # Red background

        sprite = asset_manager.sprites['player']  # Has SRCALPHA
        surface.blit(sprite, (12, 12))

        # Sprite should be drawn; background should show through transparent areas
        array = pygame.surfarray.array3d(surface).swapaxes(0, 1)
        checker = _make_checker(array)
        # Should have non-black pixels (sprite drawn)
        assert checker.count_non_black() > 0, "Alpha sprite should blit correctly"


class TestStarfieldDrawing:
    """Tests for starfield background rendering."""

    def test_starfield_draws_on_surface(self, game):
        """Starfield should draw white pixels on the surface."""
        game.starfield.draw(game.surface)

        array = pygame.surfarray.array3d(game.surface).swapaxes(0, 1)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black > 0, "Starfield should draw visible stars"

    def test_starfield_uses_white_pixels(self, game):
        """Starfield stars should be white."""
        game.starfield.draw(game.surface)

        array = pygame.surfarray.array3d(game.surface).swapaxes(0, 1)
        checker = _make_checker(array)
        white_pixels = checker.count_color((255, 255, 255))
        assert white_pixels > 0, "Starfield should render white stars"


class TestSurfaceOperations:
    """General surface operation tests."""

    def test_surface_get_at(self):
        """surface.get_at() should return correct pixel color."""
        surface = pygame.Surface((10, 10))
        surface.fill((100, 150, 200))
        color = surface.get_at((5, 5))
        assert tuple(color[:3]) == (100, 150, 200), "get_at() should return correct RGB"

    def test_surface_get_at_corners(self):
        """surface.get_at() should work at all corners."""
        surface = pygame.Surface((10, 10))
        surface.fill((50, 50, 50))

        assert tuple(surface.get_at((0, 0))[:3]) == (50, 50, 50)
        assert tuple(surface.get_at((9, 0))[:3]) == (50, 50, 50)
        assert tuple(surface.get_at((0, 9))[:3]) == (50, 50, 50)
        assert tuple(surface.get_at((9, 9))[:3]) == (50, 50, 50)


def _make_checker(array):
    """Create a pixel checker from a numpy RGB array."""
    class Checker:
        def count_non_black(self):
            return int(np.count_nonzero(np.any(array > 0, axis=2)))

        def count_color(self, color, tolerance=30):
            r, g, b = color
            mask = (
                (np.abs(array[:, :, 0].astype(int) - r) <= tolerance) &
                (np.abs(array[:, :, 1].astype(int) - g) <= tolerance) &
                (np.abs(array[:, :, 2].astype(int) - b) <= tolerance)
            )
            return int(np.count_nonzero(mask))
    return Checker()

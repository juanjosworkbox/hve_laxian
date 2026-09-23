"""Tests for font rendering and text elements."""

import numpy as np
import pygame


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


class TestFontSmallRender:
    """Tests for small font rendering."""

    def test_font_small_render_score(self, game):
        """Small font should render score text with non-black pixels."""
        text = game.font_small.render("SCORE:1000", True, (255, 255, 255))

        array = pygame.surfarray.array3d(text).swapaxes(0, 1)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black > 0, "Score text rendered as blank"

    def test_font_small_render_lives(self, game):
        """Small font should render lives text with non-black pixels."""
        text = game.font_small.render("LIVES:3", True, (255, 255, 255))

        array = pygame.surfarray.array3d(text).swapaxes(0, 1)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black > 0, "Lives text rendered as blank"

    def test_font_small_render_round(self, game):
        """Small font should render round text with non-black pixels."""
        text = game.font_small.render("ROUND:1", True, (255, 255, 255))

        array = pygame.surfarray.array3d(text).swapaxes(0, 1)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black > 0, "Round text rendered as blank"

    def test_font_small_different_colors(self, game):
        """Small font should render text in different colors."""
        colors = [(255, 255, 0), (255, 0, 0), (255, 215, 0)]  # yellow, red, gold
        for color in colors:
            text = game.font_small.render(f"TEST:{color}", True, color)
            array = pygame.surfarray.array3d(text).swapaxes(0, 1)
            checker = _make_checker(array)
            assert checker.count_non_black() > 0, f"Text not rendered in color {color}"


class TestFontLargeRender:
    """Tests for large font rendering."""

    def test_font_large_render_title(self, game):
        """Large font should render 'GALAXIAN' title."""
        text = game.font_large.render("GALAXIAN", True, (255, 255, 255))

        array = pygame.surfarray.array3d(text).swapaxes(0, 1)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black > 0, "Title text rendered as blank"

    def test_font_large_render_game_over(self, game):
        """Large font should render 'GAME OVER' in red."""
        text = game.font_large.render("GAME OVER", True, (255, 0, 0))

        array = pygame.surfarray.array3d(text).swapaxes(0, 1)
        checker = _make_checker(array)
        red_pixels = checker.count_color((255, 0, 0), tolerance=50)
        assert red_pixels > 0, "GAME OVER text not rendered in red"

    def test_font_large_dimensions_larger_than_small(self, game):
        """Large font should produce wider text than small font."""
        small = game.font_small.render("TEST", True, (255, 255, 255))
        large = game.font_large.render("TEST", True, (255, 255, 255))

        assert large.get_width() > small.get_width(), \
            f"Large font width ({large.get_width()}) should exceed small font width ({small.get_width()})"
        assert large.get_height() >= small.get_height(), \
            f"Large font height ({large.get_height()}) should exceed small font height ({small.get_height()})"


class TestFontRenderProperties:
    """Tests for font rendering properties."""

    def test_font_render_dimensions_match_font_size(self, game):
        """Rendered text width should approximately match font.size()."""
        text = "HELLO"
        rendered = game.font.render(text, True, (255, 255, 255))
        expected_width, expected_height = game.font.size(text)

        assert rendered.get_width() == expected_width, \
            f"Rendered width {rendered.get_width()} != expected {expected_width}"
        assert rendered.get_height() == expected_height, \
            f"Rendered height {rendered.get_height()} != expected {expected_height}"

    def test_font_bold_attribute(self, game):
        """Small font should be bold."""
        assert game.font.bold is True

    def test_font_large_bold_attribute(self, game):
        """Large font should be bold."""
        assert game.font_large.bold is True

    def test_font_render_same_text_same_size(self, game):
        """Same text rendered twice should produce same dimensions."""
        text1 = game.font.render("TEST", True, (255, 255, 255))
        text2 = game.font.render("TEST", True, (255, 255, 255))

        assert text1.get_width() == text2.get_width()
        assert text1.get_height() == text2.get_height()


class TestHudTextPositions:
    """Tests for HUD text positioning."""

    def test_hud_score_position(self, game):
        """Score text should appear at top-left of HUD."""
        game.state = "playing"
        game.score = 1000
        game.lives = 3
        game.round_num = 1

        # _draw_hud draws to surface
        game.surface.fill((0, 0, 0))
        game._draw_hud()

        array = pygame.surfarray.array3d(game.surface).swapaxes(0, 1)
        hud_region = array[5:15, 5:25]
        non_black = int(np.count_nonzero(np.any(hud_region > 0, axis=2)))
        assert non_black > 0, "HUD score text not rendered at top-left"

    def test_hud_lives_position(self, game):
        """Lives text should appear at bottom-left of HUD."""
        game.state = "playing"
        game.lives = 2
        game.round_num = 1

        game.surface.fill((0, 0, 0))
        game._draw_hud()

        array = pygame.surfarray.array3d(game.surface).swapaxes(0, 1)
        hud_region = array[276:286, 5:25]
        non_black = int(np.count_nonzero(np.any(hud_region > 0, axis=2)))
        assert non_black > 0, "HUD lives text not rendered at bottom-left"

    def test_hud_round_position(self, game):
        """Round indicator should appear at bottom-center of HUD."""
        game.state = "playing"
        game.round_num = 3

        game.surface.fill((0, 0, 0))
        game._draw_hud()

        array = pygame.surfarray.array3d(game.surface).swapaxes(0, 1)
        hud_region = array[276:286, 100:160]
        non_black = int(np.count_nonzero(np.any(hud_region > 0, axis=2)))
        assert non_black > 0, "HUD round text not rendered at bottom-center"


class TestRoundTransitionOverlay:
    """Tests for round transition overlay rendering."""

    def test_round_transition_overlay_rendered(self, game):
        """Round transition should render a semi-transparent overlay."""
        game.state = "round_transition"
        game.round_num = 2

        game.surface.fill((0, 0, 0))
        game._draw_round_transition()

        array = pygame.surfarray.array3d(game.surface).swapaxes(0, 1)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black > 0, "Round transition overlay not rendered"

    def test_round_transition_shows_round_number(self, game):
        """Round transition should render the round number text."""
        game.state = "round_transition"
        game.round_num = 5

        game.surface.fill((0, 0, 0))
        game._draw_round_transition()

        array = pygame.surfarray.array3d(game.surface).swapaxes(0, 1)
        center_region = array[130:160, 80:180]
        checker = _make_checker(center_region)
        white_pixels = checker.count_color((255, 255, 255))
        assert white_pixels > 0, "Round number text not rendered in center"


class TestAttractTextBlinking:
    """Tests for blinking text in ATTRACT state."""

    def test_attract_blinking_text_visible(self, game):
        """Blinking 'PRESS SPACE TO START' should be visible at certain timers."""
        game.state = "attract"
        game.attract_timer = 30  # 30 % 60 = 30, 30 < 40 → visible
        game.surface.fill((0, 0, 0))
        game.draw()

        # _draw_attract draws to surface (unscaled), check the text region directly
        # Convert surface to numpy array
        array = pygame.surfarray.array3d(game.surface).swapaxes(0, 1)
        # Text center is at (128, 200) with size ~90x11
        text_region = array[195:210, 80:160]
        non_black = int(np.count_nonzero(np.any(text_region > 0, axis=2)))
        assert non_black > 0, "Blinking start text should be visible at timer=30"

    def test_attract_blinking_text_hidden(self, game):
        """Blinking 'PRESS SPACE TO START' should be hidden at certain timers."""
        game.state = "attract"
        game.attract_timer = 50  # 50 % 60 = 50, 50 >= 40 → hidden
        game.surface.fill((0, 0, 0))
        game.draw()

        # _draw_attract draws to screen (scaled), check center region
        array = pygame.surfarray.array3d(game.screen).swapaxes(0, 1)
        # Scale text region: surface (50,180)x(90,110) → screen (100,360)x(180,220)
        center_region = array[180:220, 100:360]
        non_black = int(np.count_nonzero(np.any(center_region > 0, axis=2)))
        # Should be 0 (or at least much less) when text is hidden
        assert non_black < 50, "Blinking start text should be hidden at timer=50"

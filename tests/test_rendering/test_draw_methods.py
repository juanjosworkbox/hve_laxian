"""Tests for Game.draw() and _draw_*() state methods."""

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


class TestGameDrawAttract:
    """Tests for ATTRACT state rendering."""

    def test_game_draw_attract_populates_surface(self, game):
        """ATTRACT state should render title text on the screen surface."""
        game.state = "attract"
        game.attract_timer = 30  # so blinking text is visible (30 % 60 = 30, 30 < 40)

        # Draw
        game.draw()

        # Check screen surface has non-black pixels (title, messages rendered)
        array = pygame.surfarray.array3d(game.screen).swapaxes(0, 1)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black > 0, "ATTRACT state did not render any visible content"

    def test_attract_shows_title_text(self, game):
        """ATTRACT state should render 'GALAXIAN' title text."""
        game.state = "attract"
        game.attract_timer = 30
        game.surface.fill((0, 0, 0))
        game.draw()

        # Title text should be white — check screen surface for white pixels
        array = pygame.surfarray.array3d(game.screen).swapaxes(0, 1)
        checker = _make_checker(array)
        white_pixels = checker.count_color((255, 255, 255))
        assert white_pixels > 0, "Title text (white) not rendered"


class TestGameDrawPlaying:
    """Tests for PLAYING state rendering."""

    def test_game_draw_playing_shows_entities(self, game):
        """PLAYING state should render player, enemies, and HUD."""
        from entities import Player
        from entities import Enemy

        game.state = "playing"
        game.player = Player(game.asset_manager)
        game.player.rect.centerx = 128
        game.player.rect.bottom = 264

        game.enemies = [
            Enemy(40, 20, 'green', game.asset_manager, row=0, col=0),
            Enemy(60, 20, 'blue', game.asset_manager, row=0, col=1),
        ]

        game.surface.fill((0, 0, 0))
        game.draw()

        # Screen should have non-black pixels from entities + HUD
        array = pygame.surfarray.array3d(game.screen).swapaxes(0, 1)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black > 0, "PLAYING state did not render any visible content"

    def test_game_draw_playing_shows_hud(self, game):
        """PLAYING state should render HUD text (score, lives, round)."""
        from entities import Player

        game.state = "playing"
        game.player = Player(game.asset_manager)
        game.player.rect.centerx = 128
        game.player.rect.bottom = 264

        game.surface.fill((0, 0, 0))
        game.draw()

        # HUD text is white — check for white pixels in HUD regions
        array = pygame.surfarray.array3d(game.screen).swapaxes(0, 1)
        checker = _make_checker(array)
        white_pixels = checker.count_color((255, 255, 255))
        assert white_pixels > 0, "HUD text not rendered"


class TestGameDrawRoundTransition:
    """Tests for ROUND_TRANSITION state rendering."""

    def test_game_draw_round_transition_shows_overlay(self, game):
        """ROUND_TRANSITION should render semi-transparent overlay + text."""
        from entities import Player

        game.state = "round_transition"
        game.round_num = 2
        game.player = Player(game.asset_manager)

        game.surface.fill((0, 0, 0))
        game.draw()

        # Screen should have non-black pixels from overlay and text
        array = pygame.surfarray.array3d(game.screen).swapaxes(0, 1)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black > 0, "ROUND_TRANSITION state did not render"


class TestGameDrawGameOver:
    """Tests for GAME_OVER state rendering."""

    def test_game_draw_game_over_shows_text(self, game):
        """GAME_OVER should render 'GAME OVER' in red."""
        game.state = "game_over"
        game.score = 1500
        game.attract_timer = 30

        # _draw_game_over draws to surface
        game.surface.fill((0, 0, 0))
        game._draw_game_over()

        array = pygame.surfarray.array3d(game.surface).swapaxes(0, 1)
        checker = _make_checker(array)
        # Use wider tolerance because scaling interpolation may affect exact red
        red_pixels = checker.count_color((255, 0, 0), tolerance=100)
        assert red_pixels > 0, "GAME OVER text (red) not rendered"

    def test_game_over_shows_score(self, game):
        """GAME_OVER should render score text."""
        game.state = "game_over"
        game.score = 2500
        game.attract_timer = 30

        game.surface.fill((0, 0, 0))
        game.draw()

        array = pygame.surfarray.array3d(game.screen).swapaxes(0, 1)
        checker = _make_checker(array)
        white_pixels = checker.count_color((255, 255, 255))
        assert white_pixels > 0, "Score text (white) not rendered"


class TestGameDrawScaling:
    """Tests for surface scaling in Game.draw()."""

    def test_game_draw_scales_surface_to_screen(self, game):
        """Game.draw() should scale surface to screen dimensions."""
        game.state = "attract"
        game.attract_timer = 30

        game.draw()

        # Screen should be scaled version of surface
        assert game.screen.get_width() == 512, f"Screen width should be 512, got {game.screen.get_width()}"
        assert game.screen.get_height() == 564, f"Screen height should be 564, got {game.screen.get_height()}"

    def test_game_draw_dimensions(self, game):
        """Surface should be 256x288, screen should be 512x564."""
        assert game.surface.get_width() == 256
        assert game.surface.get_height() == 288
        assert game.screen.get_width() == 512
        assert game.screen.get_height() == 564

    def test_surface_scaling_preserves_content(self, game):
        """Scaled screen should contain content from surface."""
        game.state = "attract"
        game.attract_timer = 30
        game.draw()

        # Both surface and screen should have non-black pixels
        surface_array = pygame.surfarray.array3d(game.surface).swapaxes(0, 1)
        screen_array = pygame.surfarray.array3d(game.screen).swapaxes(0, 1)

        surface_count = int(np.count_nonzero(np.any(surface_array > 0, axis=2)))
        screen_count = int(np.count_nonzero(np.any(screen_array > 0, axis=2)))

        assert surface_count > 0, "Surface has no rendered content"
        assert screen_count > 0, "Screen has no scaled content"

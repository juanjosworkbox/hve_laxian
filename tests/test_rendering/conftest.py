"""Pytest fixtures for rendering tests.

Uses SDL_VIDEODRIVER=windib for Windows headless rendering.
"""

import os
import sys
import pytest
import tempfile
import shutil

# Set software renderer BEFORE any pygame imports
# Use windib for Windows headless rendering (software is not available on this platform)
os.environ['SDL_VIDEODRIVER'] = 'windib'

import pygame
import pygame.surfarray
import numpy as np

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


# ─── Session-scoped fixtures ───────────────────────────────────────────────────

@pytest.fixture(scope='session')
def pygame_init():
    """Initialize pygame and mixer for the test session."""
    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
    yield
    pygame.quit()


@pytest.fixture(scope='session')
def asset_manager(pygame_init):
    """Provide a shared AssetManager instance."""
    from assets import AssetManager
    return AssetManager()


# ─── Function-scoped fixtures ──────────────────────────────────────────────────

@pytest.fixture
def game(asset_manager):
    """Provide a fresh Game instance with temp high-score directory."""
    temp_dir = tempfile.mkdtemp()
    # Patch the high-score file path
    from game import Game
    from constants import GameState

    class TestGame(Game):
        def __init__(self, asset_mgr):
            # Skip parent __init__'s pygame.init() — already done
            self.screen = pygame.display.set_mode((512, 564))
            self.clock = pygame.time.Clock()
            self.surface = pygame.Surface((256, 288))
            self.asset_manager = asset_mgr
            from systems.starfield import Starfield
            self.starfield = Starfield()
            self.state = GameState.ATTRACT
            self.round_num = 1
            self.score = 0
            self.lives = 3
            self.high_score = 0
            self.player = None
            self.enemies = []
            self.enemy_bullets = []
            self.explosions = []
            from systems.formation import Formation
            self.formations = Formation(asset_mgr)
            self.round_transition_timer = 0
            self.player_death_timer = 0
            self.attract_timer = 0
            self.bonus_awarded = False
            self.font = pygame.font.SysFont('arial,monospace', 8, bold=True)
            self.font_small = pygame.font.SysFont('arial,monospace', 6)
            self.font_large = pygame.font.SysFont('arial,monospace', 14, bold=True)
            self._temp_dir = temp_dir

        def _load_high_score(self):
            path = os.path.join(self._temp_dir, 'highscore.txt')
            try:
                with open(path, 'r') as f:
                    return int(f.read().strip())
            except Exception:
                return 0

        def _save_high_score(self):
            if self.score > self.high_score:
                self.high_score = self.score
                path = os.path.join(self._temp_dir, 'highscore.txt')
                try:
                    with open(path, 'w') as f:
                        f.write(str(self.high_score))
                except Exception:
                    pass

    g = TestGame(asset_manager)
    yield g
    # Cleanup temp directory
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass


@pytest.fixture
def black_surface():
    """Provide a 256x288 black surface for testing."""
    surface = pygame.Surface((256, 288))
    surface.fill((0, 0, 0))
    return surface


@pytest.fixture
def sample_sprite(asset_manager):
    """Provide a sample enemy sprite."""
    return asset_manager.sprites['enemy_green'][0]


# ─── Helper fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def surface_array():
    """Helper function to convert surface to numpy RGB array."""
    def _to_array(surface):
        return pygame.surfarray.array3d(surface).swapaxes(0, 1)
    return _to_array


@pytest.fixture
def pixel_checker():
    """Helper class for pixel-level assertions."""

    class Checker:
        def __init__(self, surface):
            self.surface = surface
            self.array = pygame.surfarray.array3d(surface).swapaxes(0, 1)

        def count_non_black(self):
            """Count pixels that are not black."""
            return int(np.count_nonzero(np.any(self.array > 0, axis=2)))

        def has_color(self, color, tolerance=30):
            """Check if any pixel matches the color within tolerance."""
            r, g, b = color
            mask = (
                (np.abs(self.array[:, :, 0].astype(int) - r) <= tolerance) &
                (np.abs(self.array[:, :, 1].astype(int) - g) <= tolerance) &
                (np.abs(self.array[:, :, 2].astype(int) - b) <= tolerance)
            )
            return bool(np.any(mask))

        def count_color(self, color, tolerance=30):
            """Count pixels matching the color within tolerance."""
            r, g, b = color
            mask = (
                (np.abs(self.array[:, :, 0].astype(int) - r) <= tolerance) &
                (np.abs(self.array[:, :, 1].astype(int) - g) <= tolerance) &
                (np.abs(self.array[:, :, 2].astype(int) - b) <= tolerance)
            )
            return int(np.count_nonzero(mask))

        def region_non_black(self, x, y, w, h):
            """Count non-black pixels in a region."""
            region = self.array[y:y+h, x:x+w]
            return int(np.count_nonzero(np.any(region > 0, axis=2)))

    return Checker

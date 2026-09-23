"""Pytest fixtures for system tests.

Uses SDL_VIDEODRIVER=dummy for headless logic tests.
"""

import os
import sys
import pytest

# Set dummy driver BEFORE any pygame imports
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame

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
def formation(asset_manager):
    """Provide a fresh Formation instance."""
    from systems.formation import Formation
    f = Formation(asset_manager)
    f.create_enemies()
    return f


@pytest.fixture
def starfield():
    """Provide a fresh Starfield instance."""
    from systems.starfield import Starfield
    return Starfield()


@pytest.fixture
def mock_player():
    """Provide a mock player rect for dive tests."""
    class MockPlayer:
        class Rect:
            centerx = 128
            bottom = 264
        rect = Rect()
    return MockPlayer()

"""Tests for sprite generation and dimensions."""

import numpy as np
import pygame


class TestPlayerSprite:
    """Tests for the player ship sprite."""

    def test_player_sprite_dimensions(self, asset_manager):
        """Player sprite should be 13x16 pixels."""
        sprite = asset_manager.sprites['player']
        assert sprite.get_width() == 13
        assert sprite.get_height() == 16

    def test_player_sprite_has_alpha(self, asset_manager):
        """Player sprite should have an alpha channel."""
        sprite = asset_manager.sprites['player']
        assert sprite.get_flags() & pygame.SRCALPHA

    def test_player_sprite_not_empty(self, asset_manager):
        """Player sprite should have non-black pixels."""
        sprite = asset_manager.sprites['player']
        test_surface = pygame.Surface((13, 16))
        test_surface.blit(sprite, (0, 0))
        array = pygame.surfarray.array3d(test_surface).swapaxes(0, 1)
        non_black = int(pygame.surfarray.array3d(test_surface).swapaxes(0, 1).shape[0] *
                        pygame.surfarray.array3d(test_surface).swapaxes(0, 1).shape[1])
        assert non_black > 0


class TestEnemySprite:
    """Tests for enemy dragonfly sprites."""

    def test_enemy_sprite_animation_frames(self, asset_manager):
        """Enemy sprites should have 2 animation frames (red has 4)."""
        for key in ['enemy_green', 'enemy_blue', 'enemy_yellow']:
            frames = asset_manager.sprites[key]
            assert isinstance(frames, list), f"{key} should be a list of frames"
            assert len(frames) == 2, f"{key} should have 2 frames, got {len(frames)}"
        # Red enemy has 4 frames from second_row_enemy_animation.png
        red_frames = asset_manager.sprites['enemy_red']
        assert isinstance(red_frames, list), "enemy_red should be a list of frames"
        assert len(red_frames) == 4, f"enemy_red should have 4 frames, got {len(red_frames)}"

    def test_enemy_sprite_frame_dimensions(self, asset_manager):
        """Each enemy animation frame should be 10x10 pixels."""
        for key in ['enemy_green', 'enemy_blue', 'enemy_yellow', 'enemy_red']:
            frames = asset_manager.sprites[key]
            for i, frame in enumerate(frames):
                assert frame.get_width() == 10, f"{key} frame {i} width should be 10"
                assert frame.get_height() == 10, f"{key} frame {i} height should be 10"

    def test_enemy_frames_are_different(self, asset_manager):
        """Wing animation frames should differ (wings raised vs lowered)."""
        frames = asset_manager.sprites['enemy_green']
        array0 = pygame.surfarray.array3d(frames[0]).swapaxes(0, 1)
        array1 = pygame.surfarray.array3d(frames[1]).swapaxes(0, 1)
        # Frames should not be identical
        assert not np.array_equal(array0, array1), "Wing animation frames should differ"

    def test_all_enemy_types_have_frames(self, asset_manager):
        """All enemy types should have animation frames."""
        for key in ['enemy_green', 'enemy_blue', 'enemy_yellow', 'enemy_red']:
            assert key in asset_manager.sprites
            frames = asset_manager.sprites[key]
            assert len(frames) > 0


class TestFlagshipSprite:
    """Tests for the flagship (Galboss) sprite."""

    def test_flagship_sprite_dimensions(self, asset_manager):
        """Flagship sprite should be 14x14 pixels."""
        sprite = asset_manager.sprites['enemy_flagship']
        assert isinstance(sprite, list), "Flagship should be a list of frames"
        for i, frame in enumerate(sprite):
            assert frame.get_width() == 14, f"Flagship frame {i} width should be 14"
            assert frame.get_height() == 14, f"Flagship frame {i} height should be 14"

    def test_flagship_has_animation_frames(self, asset_manager):
        """Flagship should have 2 animation frames."""
        frames = asset_manager.sprites['enemy_flagship']
        assert len(frames) == 2


class TestEscortSprite:
    """Tests for the escort ship sprite."""

    def test_escort_sprite_dimensions(self, asset_manager):
        """Escort sprite should be 10x10 pixels."""
        sprite = asset_manager.sprites['enemy_escort']
        assert isinstance(sprite, list), "Escort should be a list of frames"
        for i, frame in enumerate(sprite):
            assert frame.get_width() == 10, f"Escort frame {i} width should be 10"
            assert frame.get_height() == 10, f"Escort frame {i} height should be 10"

    def test_escort_has_animation_frames(self, asset_manager):
        """Escort should have 2 animation frames."""
        frames = asset_manager.sprites['enemy_escort']
        assert len(frames) == 2


class TestBulletSprites:
    """Tests for bullet sprites."""

    def test_player_bullet_dimensions(self, asset_manager):
        """Player bullet should be 2x6 pixels."""
        sprite = asset_manager.sprites['player_bullet']
        assert sprite.get_width() == 2
        assert sprite.get_height() == 6

    def test_enemy_bullet_dimensions(self, asset_manager):
        """Enemy bullet should be 2x4 pixels."""
        sprite = asset_manager.sprites['enemy_bullet']
        assert sprite.get_width() == 2
        assert sprite.get_height() == 4

    def test_player_bullet_color(self, asset_manager):
        """Player bullet should be whitish."""
        sprite = asset_manager.sprites['player_bullet']
        assert sprite.get_width() > 0 and sprite.get_height() > 0

    def test_enemy_bullet_color(self, asset_manager):
        """Enemy bullet should be reddish."""
        sprite = asset_manager.sprites['enemy_bullet']
        assert sprite.get_width() > 0 and sprite.get_height() > 0


class TestExplosionSprite:
    """Tests for explosion animation sprites."""

    def test_explosion_sprite_dimensions(self, asset_manager):
        """Explosion frames should be 10x10 pixels."""
        frames = asset_manager.sprites['explosion']
        assert isinstance(frames, list)
        for i, frame in enumerate(frames):
            assert frame.get_width() == 10, f"Explosion frame {i} width should be 10"
            assert frame.get_height() == 10, f"Explosion frame {i} height should be 10"

    def test_explosion_has_multiple_frames(self, asset_manager):
        """Explosion should have multiple animation frames."""
        frames = asset_manager.sprites['explosion']
        assert len(frames) > 1, f"Explosion should have multiple frames, got {len(frames)}"

    def test_player_explosion_dimensions(self, asset_manager):
        """Player explosion should be 12x12 pixels."""
        frames = asset_manager.sprites['player_explode']
        assert isinstance(frames, list)
        for i, frame in enumerate(frames):
            assert frame.get_width() == 12, f"Player explosion frame {i} width should be 12"
            assert frame.get_height() == 12, f"Player explosion frame {i} height should be 12"


class TestStarSprite:
    """Tests for the star UI sprite."""

    def test_star_sprite_exists(self, asset_manager):
        """Star sprite should exist in assets."""
        assert 'star' in asset_manager.sprites

    def test_star_sprite_dimensions(self, asset_manager):
        """Star sprite should be 2x2 pixels."""
        sprite = asset_manager.sprites['star']
        assert sprite.get_width() == 2
        assert sprite.get_height() == 2


class TestAllSprites:
    """General tests for all sprites."""

    def test_all_sprites_have_dimensions(self, asset_manager):
        """All sprites should have width and height greater than 0."""
        for name, sprite in asset_manager.sprites.items():
            if isinstance(sprite, list):
                for i, frame in enumerate(sprite):
                    assert frame.get_width() > 0, f"{name}[{i}] has zero width"
                    assert frame.get_height() > 0, f"{name}[{i}] has zero height"
            else:
                assert sprite.get_width() > 0, f"{name} has zero width"
                assert sprite.get_height() > 0, f"{name} has zero height"

    def test_all_sprites_have_alpha(self, asset_manager):
        """All sprites should have an alpha channel."""
        for name, sprite in asset_manager.sprites.items():
            if isinstance(sprite, list):
                for i, frame in enumerate(sprite):
                    assert frame.get_flags() & pygame.SRCALPHA, f"{name}[{i}] missing alpha"
            else:
                assert sprite.get_flags() & pygame.SRCALPHA, f"{name} missing alpha"

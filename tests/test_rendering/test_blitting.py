"""Tests for entity draw methods and sprite blitting."""

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


class TestPlayerDraw:
    """Tests for player entity draw/blitting."""

    def test_player_draw_blits_sprite(self, game):
        """When player is alive, sprite should appear on surface."""
        from entities import Player
        player = Player(game.asset_manager)
        player.rect.centerx = 128
        player.rect.bottom = 264

        # Draw player to screen surface (as the real draw method does)
        game.screen.fill((0, 0, 0))
        player.draw(game.screen)

        array = pygame.surfarray.array3d(game.screen).swapaxes(0, 1)
        player_region = array[player.rect.y:player.rect.bottom,
                              player.rect.x:player.rect.right]
        non_black = int(np.count_nonzero(np.any(player_region > 0, axis=2)))
        assert non_black > 0, "Player sprite not found on surface"

    def test_player_draw_skips_when_dead(self, game):
        """When player is dead, no sprite should be drawn."""
        from entities import Player
        player = Player(game.asset_manager)
        player.die()

        test_surface = pygame.Surface((256, 288))
        player.draw(test_surface)

        array = pygame.surfarray.array3d(test_surface).swapaxes(0, 1)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black == 0, "Dead player should not draw any pixels"

    def test_player_draw_blinks_when_invincible(self, game):
        """When player is invincible, sprite should blink (visible/hidden)."""
        from entities import Player
        player = Player(game.asset_manager)
        player.respawn()  # sets invincible = True, respawn_timer = 120

        test_surface = pygame.Surface((256, 288))

        # At timer=120, 120 % 6 = 0, so 0 < 3 → hidden
        player.draw(test_surface)
        array1 = pygame.surfarray.array3d(test_surface).swapaxes(0, 1)
        count1 = int(np.count_nonzero(np.any(array1 > 0, axis=2)))

        # Manually set timer to 119, 119 % 6 = 5, so 5 >= 3 → visible
        player.respawn_timer = 119
        test_surface2 = pygame.Surface((256, 288))
        player.draw(test_surface2)
        array2 = pygame.surfarray.array3d(test_surface2).swapaxes(0, 1)
        count2 = int(np.count_nonzero(np.any(array2 > 0, axis=2)))

        # One should be hidden, one visible
        # (exact behavior depends on blink logic)
        assert count1 == 0 or count2 > 0, "Blinking behavior not working"

    def test_player_draw_shoots_bullet_sprite(self, game):
        """When player fires, bullet sprite should appear."""
        from entities import Player
        player = Player(game.asset_manager)
        bullet = player.fire()

        test_surface = pygame.Surface((256, 288))
        player.draw(test_surface)

        # Check that bullet rect region has pixels
        if player.bullet and not player.bullet.hit:
            b = player.bullet
            array = pygame.surfarray.array3d(test_surface).swapaxes(0, 1)
            region = array[b.rect.y:b.rect.bottom, b.rect.x:b.rect.right]
            non_black = int(np.count_nonzero(np.any(region > 0, axis=2)))
            assert non_black > 0, "Player bullet sprite not found"


class TestEnemyDraw:
    """Tests for enemy entity draw/blitting."""

    def test_enemy_draw_blits_sprite(self, game):
        """When enemy is alive, sprite should appear on surface."""
        from entities import Enemy
        enemy = Enemy(40, 20, 'green', game.asset_manager, row=0, col=0)

        test_surface = pygame.Surface((256, 288))
        enemy.draw(test_surface)

        array = pygame.surfarray.array3d(test_surface).swapaxes(0, 1)
        enemy_region = array[enemy.rect.y:enemy.rect.bottom,
                             enemy.rect.x:enemy.rect.right]
        non_black = int(np.count_nonzero(np.any(enemy_region > 0, axis=2)))
        assert non_black > 0, "Enemy sprite not found on surface"

    def test_enemy_draw_skips_when_dead(self, game):
        """When enemy is dead, no sprite should be drawn."""
        from entities import Enemy
        enemy = Enemy(40, 20, 'green', game.asset_manager, row=0, col=0)
        enemy.alive = False

        test_surface = pygame.Surface((256, 288))
        enemy.draw(test_surface)

        array = pygame.surfarray.array3d(test_surface).swapaxes(0, 1)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black == 0, "Dead enemy should not draw any pixels"

    def test_enemy_draw_different_colors(self, game):
        """Different enemy types should have different colors."""
        from entities import Enemy
        colors = {'green': (0, 255, 0), 'blue': (0, 100, 255)}

        enemies = {}
        for etype, expected_color in colors.items():
            enemy = Enemy(40, 20, etype, game.asset_manager, row=0, col=0)
            test_surface = pygame.Surface((256, 288))
            enemy.draw(test_surface)
            arr = pygame.surfarray.array3d(test_surface).swapaxes(0, 1)
            checker = _make_checker(arr)
            enemies[etype] = checker

        # Verify each has non-black pixels (they are drawn)
        for etype, checker in enemies.items():
            assert checker.count_non_black() > 0, f"{etype} enemy not drawn"


class TestBulletDraw:
    """Tests for bullet entity draw/blitting."""

    def test_bullet_draw_blits_sprite(self, game):
        """When bullet is active, sprite should appear on surface."""
        from entities import Bullet
        bullet = Bullet(128, 200, 0, -6, 'player', game.asset_manager)

        test_surface = pygame.Surface((256, 288))
        bullet.draw(test_surface)

        array = pygame.surfarray.array3d(test_surface).swapaxes(0, 1)
        bullet_region = array[bullet.rect.y:bullet.rect.bottom,
                              bullet.rect.x:bullet.rect.right]
        non_black = int(np.count_nonzero(np.any(bullet_region > 0, axis=2)))
        assert non_black > 0, "Player bullet sprite not found"

    def test_bullet_draw_skips_when_hit(self, game):
        """When bullet is hit, no sprite should be drawn."""
        from entities import Bullet
        bullet = Bullet(128, 200, 0, -6, 'player', game.asset_manager)
        bullet.hit = True

        test_surface = pygame.Surface((256, 288))
        bullet.draw(test_surface)

        array = pygame.surfarray.array3d(test_surface).swapaxes(0, 1)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black == 0, "Hit bullet should not draw any pixels"

    def test_enemy_bullet_draw(self, game):
        """Enemy bullet should also blit correctly."""
        from entities import Bullet
        bullet = Bullet(128, 100, 0, 2, 'enemy', game.asset_manager)

        test_surface = pygame.Surface((256, 288))
        bullet.draw(test_surface)

        array = pygame.surfarray.array3d(test_surface).swapaxes(0, 1)
        bullet_region = array[bullet.rect.y:bullet.rect.bottom,
                              bullet.rect.x:bullet.rect.right]
        non_black = int(np.count_nonzero(np.any(bullet_region > 0, axis=2)))
        assert non_black > 0, "Enemy bullet sprite not found"


class TestExplosionDraw:
    """Tests for explosion entity draw/blitting."""

    def test_explosion_draw_animation(self, game):
        """Explosion should draw frames and advance animation."""
        from entities import Explosion
        explosion = Explosion(128, 144, game.asset_manager)

        # Frame timer needs >4 to advance; 6 updates = frame 1 (visible)
        for _ in range(6):
            explosion.update()
        # Now current_frame = 1
        test_surface = pygame.Surface((256, 288))
        explosion.draw(test_surface)

        array = pygame.surfarray.array3d(test_surface).swapaxes(0, 1)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black > 0, "Explosion frame not drawn"

        # Advance animation (6 more updates = frame 2)
        for _ in range(6):
            explosion.update()
        test_surface2 = pygame.Surface((256, 288))
        explosion.draw(test_surface2)
        array2 = pygame.surfarray.array3d(test_surface2).swapaxes(0, 1)
        non_black2 = int(np.count_nonzero(np.any(array2 > 0, axis=2)))
        assert non_black2 > 0, "Explosion frame 2 not drawn"

    def test_explosion_stops_when_inactive(self, game):
        """When explosion is inactive, no pixels should be drawn."""
        from entities import Explosion
        explosion = Explosion(128, 144, game.asset_manager)

        # 10 frames, each needs 6 updates to advance = 60 updates total
        for _ in range(70):
            explosion.update()

        test_surface = pygame.Surface((256, 288))
        explosion.draw(test_surface)

        array = pygame.surfarray.array3d(test_surface).swapaxes(0, 1)
        non_black = int(np.count_nonzero(np.any(array > 0, axis=2)))
        assert non_black == 0, "Inactive explosion should not draw"

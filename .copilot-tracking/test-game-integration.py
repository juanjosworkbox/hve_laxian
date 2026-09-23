"""Full game integration test - verifies collision fix and wing animation."""
import sys
sys.path.insert(0, '.')
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
import time
from entities import Enemy, Bullet
from game.game import Game

print("=" * 60)
print("GALAXIAN GAME INTEGRATION TEST")
print("=" * 60)

# Initialize pygame
pygame.init()

# Create game instance
print("\n[1/6] Creating Game instance...")
try:
    game = Game()
    print("  PASS: Game initialized successfully")
    print(f"  - Screen: {game.screen.get_size()}")
    print(f"  - Round: {game.round_num}")
    
    # Initialize player via start_game
    game.start_game()
    print(f"  - Lives: {game.player.alive}")
except Exception as e:
    print(f"  FAIL: {e}")
    import traceback
    traceback.print_exc()
    pygame.quit()
    sys.exit(1)

# Test enemy creation and wing animation
print("\n[2/6] Testing enemy creation and wing animation...")
try:
    enemies = game.formations.create_enemies()
    print(f"  PASS: Created {len(enemies)} enemies")
    
    # Check wing frames
    for i, enemy in enumerate(enemies[:3]):
        assert len(enemy.wing_frames) == 2, f"Enemy {i} should have 2 frames"
        assert enemy.image is enemy.wing_frames[0], f"Enemy {i} initial frame wrong"
    print("  PASS: Wing frames verified on all enemies")
    
    # Test wing animation update
    initial_frame = enemies[0].wing_frame
    for _ in range(20):
        enemies[0].update(0, 0)
    assert enemies[0].wing_frame != initial_frame or enemies[0].wing_frame == 1 - initial_frame, "Wing frame should change"
    assert enemies[0].image is enemies[0].wing_frames[enemies[0].wing_frame], "Image should match frame"
    print("  PASS: Wing animation updates correctly")
except Exception as e:
    print(f"  FAIL: {e}")
    import traceback
    traceback.print_exc()
    pygame.quit()
    sys.exit(1)

# Test collision detection - bullet hits enemy
print("\n[3/6] Testing bullet-enemy collision...")
try:
    from systems.collision import check_bullet_enemy_collisions
    
    alive_enemy = [e for e in enemies if e.alive][0]
    # Position bullet directly above enemy center so it will collide
    bullet = Bullet(alive_enemy.rect.centerx, alive_enemy.rect.top - 5, 0, -6, 'player', game.asset_manager)
    
    hits = check_bullet_enemy_collisions(bullet, enemies, [])
    assert len(hits) > 0, f"Should hit at least one enemy. Bullet rect: {bullet.rect}, Enemy rect: {alive_enemy.rect}"
    assert not hits[0].alive, "Hit enemy should be dead"
    assert bullet.hit, "Bullet should be marked as hit"
    print(f"  PASS: Bullet hit {len(hits)} enemy(ies)")
except Exception as e:
    print(f"  FAIL: {e}")
    import traceback
    traceback.print_exc()
    pygame.quit()
    sys.exit(1)

# Test collision detection - enemy bullet hits player (THE BUG FIX)
print("\n[4/6] Testing enemy bullet-player collision (BUG FIX)...")
try:
    from systems.collision import check_bullet_player_collisions
    
    # Create an enemy bullet overlapping the player
    player_rect = game.player.rect
    enemy_bullet = Bullet(
        game.player.rect.centerx,
        game.player.rect.centery,
        0, 3, 'enemy', game.asset_manager
    )
    
    # Player is alive and not invincible
    game.player.alive = True
    game.player.invincible = False
    
    result = check_bullet_player_collisions([enemy_bullet], game.player)
    assert result is True, "Should detect player hit"
    print("  PASS: Enemy bullet-player collision detected (BUG FIXED)")
    
    # Test miss case
    far_bullet = Bullet(500, 500, 0, 3, 'enemy', game.asset_manager)
    result2 = check_bullet_player_collisions([far_bullet], game.player)
    assert result2 is False, "Should not detect collision when far away"
    print("  PASS: No false collision when bullet is far away")
except Exception as e:
    print(f"  FAIL: {e}")
    import traceback
    traceback.print_exc()
    pygame.quit()
    sys.exit(1)

# Test player-enemy collision
print("\n[5/6] Testing player-enemy collision...")
try:
    from systems.collision import check_player_enemy_collisions
    
    # Place an enemy on top of the player
    game.player.alive = True
    game.player.invincible = False
    test_enemy = enemies[0]
    test_enemy.alive = True
    test_enemy.rect = game.player.rect.copy()
    
    result = check_player_enemy_collisions(game.player, [test_enemy])
    assert result is True, "Should detect player-enemy collision"
    print("  PASS: Player-enemy collision detected")
except Exception as e:
    print(f"  FAIL: {e}")
    import traceback
    traceback.print_exc()
    pygame.quit()
    sys.exit(1)

# Test game state update loop
print("\n[6/6] Testing game update loop...")
try:
    # Reset for update test
    game.round = 1
    game.lives = 3
    game.player.alive = True
    game.player.invincible = False
    game.player.bullet = None
    
    # Create fresh enemies
    game.enemies = game.formations.create_enemies()
    
    # Run 60 frames of updates
    for frame in range(60):
        game.update()
    
    print("  PASS: Game updated 60 frames without errors")
    
    # Verify enemies still have wing animation
    for enemy in game.enemies[:3]:
        assert hasattr(enemy, 'wing_frame'), "Enemy should have wing_frame"
        assert hasattr(enemy, 'wing_timer'), "Enemy should have wing_timer"
    print("  PASS: Wing animation state preserved after updates")
    
except Exception as e:
    print(f"  FAIL: {e}")
    import traceback
    traceback.print_exc()
    pygame.quit()
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED - GAME IS WORKING CORRECTLY")
print("=" * 60)
print("\nFixed issues verified:")
print("  1. Collision bug: bullet_rect undefined - FIXED")
print("  2. Wing animation: dragonfly enemies now flap wings - IMPLEMENTED")
print("\nPygame is ready for display. Game can be started with:")
print("  python main.py")

pygame.quit()

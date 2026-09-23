"""Verify collision fix and wing animation."""
import sys
sys.path.insert(0, '.')
import pygame
from assets import AssetManager
from entities.enemy import Enemy
from entities.bullet import Bullet
from systems.collision import check_bullet_enemy_collisions, check_bullet_player_collisions

pygame.init()

am = AssetManager()

# Test 1: Wing frames
em = am.sprites['enemy_green']
assert isinstance(em, list) and len(em) == 2, "Enemy should have 2 frames"
print("PASS: Enemy has 2 wing frames")

# Test 2: Enemy initialization with wing frames
e = Enemy(50, 50, 'green', am)
assert len(e.wing_frames) == 2, "Enemy should have 2 wing frames"
assert e.image is e.wing_frames[0], "Initial image should be frame 0"
print("PASS: Enemy initialized with wing frames")

# Test 3: Collision - bullet hits enemy
b = Bullet(50, 100, 0, -5, 'player', am)
hits = check_bullet_enemy_collisions(b, [e], [])
assert len(hits) == 1, "Should hit enemy"
assert not e.alive, "Enemy should be dead"
print("PASS: Bullet-enemy collision works")

# Test 4: Collision - bullet misses enemy (no crash)
e2 = Enemy(100, 100, 'blue', am)
b2 = Bullet(50, 50, 0, -5, 'player', am)
hits2 = check_bullet_enemy_collisions(b2, [e2], [])
assert len(hits2) == 0, "Should miss enemy"
assert e2.alive, "Enemy should still be alive"
print("PASS: Bullet-enemy miss works")

# Test 5: Collision - enemy bullet vs player (the bug fix)
class MockPlayer:
    def __init__(self):
        self.alive = True
        self.invincible = False
        self._rect = pygame.Rect(100, 100, 12, 12)
    def get_rect(self):
        return self._rect

p = MockPlayer()
eb = Bullet(105, 105, 0, 3, 'enemy', am)
result = check_bullet_player_collisions([eb], p)
assert result is True, "Should detect collision"
print("PASS: Enemy bullet-player collision works (BUG FIX)")

# Test 6: Collision - enemy bullet misses player
eb2 = Bullet(200, 200, 0, 3, 'enemy', am)
result2 = check_bullet_player_collisions([eb2], p)
assert result2 is False, "Should miss player"
print("PASS: Enemy bullet-player miss works (BUG FIX)")

print("\nALL TESTS PASSED!")

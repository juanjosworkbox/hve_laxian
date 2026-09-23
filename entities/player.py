"""Player ship (Galaxip)."""
import pygame
from constants import (
    PLAYER_SPEED, PLAYER_BULLET_SPEED, PLAYER_Y,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_RESPAWN_INVINCIBLE_FRAMES,
    SCREEN_WIDTH, WHITE, RED
)
from .bullet import Bullet

class Player:
    def __init__(self, asset_manager):
        self.image = asset_manager.sprites['player']
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = PLAYER_Y
        self.speed = PLAYER_SPEED
        self.asset_manager = asset_manager
        self.bullet = None
        self.respawn_timer = 0
        self.invincible = False
        self.alive = True
    
    def handle_input(self, keys):
        if not self.alive:
            return
        
        # Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        
        # Clamp to screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
    
    def fire(self):
        """Fire bullet if none exists."""
        if not self.alive or self.bullet is not None:
            return None
        
        bullet = Bullet(
            self.rect.centerx, self.rect.top,
            0, -PLAYER_BULLET_SPEED,
            'player',
            self.asset_manager
        )
        self.bullet = bullet
        return bullet
    
    def update(self):
        if not self.alive:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.respawn()
            return
        
        if self.bullet:
            self.bullet.update()
            if self.bullet.rect.top < 0:
                self.bullet = None
            elif self.bullet.hit:
                self.bullet = None
        else:
            if self.invincible:
                self.invincible = False
    
    def respawn(self):
        self.alive = True
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = PLAYER_Y
        self.bullet = None
        self.invincible = True
        self.respawn_timer = PLAYER_RESPAWN_INVINCIBLE_FRAMES
    
    def die(self):
        self.alive = False
        self.bullet = None
        self.respawn_timer = PLAYER_RESPAWN_INVINCIBLE_FRAMES
    
    def draw(self, screen):
        if not self.alive:
            return
        
        # Blink when invincible
        if self.invincible:
            if self.respawn_timer % 6 < 3:
                return
        
        screen.blit(self.image, self.rect)
        
        if self.bullet and not self.bullet.hit:
            self.bullet.draw(screen)
    
    def get_rect(self):
        return self.rect
    
    def check_collision(self, enemies):
        """Check if player collides with any enemy."""
        if not self.alive or self.invincible:
            return False
        
        player_rect = self.get_rect()
        for enemy in enemies:
            if enemy.alive and player_rect.colliderect(enemy.rect):
                return True
        return False

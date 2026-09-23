"""Bullets for player and enemies."""
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Bullet:
    def __init__(self, x, y, dx, dy, bullet_type, asset_manager):
        if bullet_type == 'player':
            self.image = asset_manager.sprites['player_bullet']
            self.speed = 6
        else:
            self.image = asset_manager.sprites['enemy_bullet']
            self.speed = 2
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.dx = dx
        self.dy = dy
        self.bullet_type = bullet_type
        self.hit = False
        self.asset_manager = asset_manager
    
    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        # Check bounds
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.hit = True
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.hit = True
    
    def draw(self, screen):
        if not self.hit:
            screen.blit(self.image, self.rect)
    
    def get_rect(self):
        return self.rect

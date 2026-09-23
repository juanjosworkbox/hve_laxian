"""Explosion animations."""
import pygame

class Explosion:
    def __init__(self, x, y, asset_manager, size=10):
        self.frames = asset_manager.sprites['explosion']
        self.current_frame = 0
        self.rect = self.frames[0].get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.asset_manager = asset_manager
        self.frame_timer = 0
        self.active = True
        self.size = size
    
    def update(self):
        self.frame_timer += 1
        if self.frame_timer > 4:  # Frame speed
            self.frame_timer = 0
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.active = False
    
    def draw(self, screen):
        if self.active and self.current_frame < len(self.frames):
            screen.blit(self.frames[self.current_frame], self.rect)

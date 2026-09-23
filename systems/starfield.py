"""Animated starfield background."""
import random
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Starfield:
    """Scrolling starfield background."""
    
    def __init__(self):
        self.stars = []
        self._generate_stars()
        self.offset_y = 0
    
    def _generate_stars(self):
        """Generate random stars."""
        self.stars = []
        for _ in range(80):
            self.stars.append({
                'x': random.randint(0, SCREEN_WIDTH - 1),
                'y': random.randint(0, SCREEN_HEIGHT - 1),
                'speed': random.choice([0.5, 1, 1.5, 2]),
                'brightness': random.randint(100, 255),
            })
    
    def update(self):
        """Update star positions."""
        self.offset_y += 0.5
        
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > SCREEN_HEIGHT:
                star['y'] = 0
                star['x'] = random.randint(0, SCREEN_WIDTH - 1)
    
    def draw(self, screen):
        """Draw all stars."""
        for star in self.stars:
            color = star['brightness']
            screen.fill((color, color, color), (int(star['x']), int(star['y']), 1, 1))

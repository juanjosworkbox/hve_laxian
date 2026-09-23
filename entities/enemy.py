"""Enemy ships with formation and dive AI."""
import pygame
import math
import random
from constants import (
    ENEMY_WIDTH, ENEMY_HEIGHT, ENEMY_BULLET_SPEED,
    FORMATION_TOP, FORMATION_SPACING_X, FORMATION_SPACING_Y,
    FORMATION_ROWS, FORMATION_COLS, TOTAL_ENEMIES,
    DIVE_BEZIER_CONTROL_Y, DIVE_BASE_SPEED,
    ENEMY_POINTS, SCREEN_WIDTH, SCREEN_HEIGHT,
    UFO_POINTS, UFO_WIDTH, UFO_HEIGHT, UFO_SPEED,
    UFO_TOP, UFO_APPEAR_INTERVAL_BASE, UFO_APPEAR_INTERVAL_MIN,
)
from .bullet import Bullet

class Enemy:
    """Individual enemy with formation and dive behaviors."""
    
    def __init__(self, x, y, enemy_type, asset_manager, row=0, col=0):
        # Assign sprite based on type
        sprite_map = {
            'green': 'enemy_green',
            'blue': 'enemy_blue',
            'yellow': 'enemy_yellow',
            'red': 'enemy_red',
            'flagship': 'enemy_flagship',
            'escort': 'enemy_escort',
        }
        raw_image = asset_manager.sprites[sprite_map[enemy_type]]
        # Handle wing animation frames (list) vs single surface
        if isinstance(raw_image, list):
            self.wing_frames = raw_image
            self.image = self.wing_frames[0]
        else:
            self.wing_frames = [raw_image]
            self.image = self.wing_frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.enemy_type = enemy_type
        self.asset_manager = asset_manager
        self.alive = True
        self.state = 'formation'  # formation, diving, returning
        
        # Formation position
        self.formation_x = x
        self.formation_y = y
        self.row = row
        self.col = col
        
        # Dive properties
        self.dive_speed = DIVE_BASE_SPEED
        self.dive_angle = 0
        self.dive_start = None
        self.dive_control = None
        self.dive_target = None
        self.dive_progress = 0
        self.dive_shoot_timer = random.randint(30, 90)
        self.dive_delay = 0  # Staggered wave follower delay (frames)
        
        # Return path properties (curved Bezier return)
        self.return_start = None
        self.return_control = None
        self.return_target = None
        self.return_progress = 0
        
        # Animation
        self.wing_frame = 0
        self.wing_timer = 0
    
    def start_dive(self, player_x, player_y, lateral_offset=None):
        """Start a curved dive toward the player with lateral swooping movement."""
        self.state = 'diving'
        self.dive_start = (self.rect.centerx, self.rect.centery)
        
        # Random lateral offset for curved dive (±60 pixels)
        if lateral_offset is None:
            lateral_offset = random.randint(-60, 60)
        
        # Control point for bezier curve - offset from midpoint for lateral curve
        mid_x = (self.dive_start[0] + player_x) / 2 + lateral_offset
        self.dive_control = (mid_x, DIVE_BEZIER_CONTROL_Y)
        self.dive_target = (player_x, player_y - 20)
        self.dive_progress = 0
        
        # Store return path data (reverse of dive, curving back to formation)
        # Return from dive target back to start, with control point above
        self.return_start = (self.dive_target[0], self.dive_target[1])
        self.return_control = ((self.dive_start[0] + self.dive_target[0]) / 2, -20)
        self.return_target = (self.dive_start[0], self.dive_start[1])
        self.return_progress = 0
        
        # Reset shoot timer so enemy can fire during dive
        self.dive_shoot_timer = random.randint(15, 40)
        
        # Play dive sound
        sound = self.asset_manager.get_sound('dive')
        if sound:
            sound.play()
    
    def bezier_point(self, t):
        """Calculate position on quadratic bezier curve."""
        if self.dive_start is None or self.dive_target is None:
            return (self.rect.centerx, self.rect.centery)
        
        x0, y0 = self.dive_start
        x1, y1 = self.dive_control
        x2, y2 = self.dive_target
        
        t = max(0, min(1, t))
        x = (1 - t)**2 * x0 + 2 * (1 - t) * t * x1 + t**2 * x2
        y = (1 - t)**2 * y0 + 2 * (1 - t) * t * y1 + t**2 * y2
        return (x, y)
    
    def _return_bezier_point(self, t):
        """Calculate position on quadratic bezier curve for return path."""
        if self.return_start is None or self.return_target is None:
            return (self.rect.centerx, self.rect.centery)
        
        x0, y0 = self.return_start
        x1, y1 = self.return_control
        x2, y2 = self.return_target
        
        t = max(0, min(1, t))
        x = (1 - t)**2 * x0 + 2 * (1 - t) * t * x1 + t**2 * x2
        y = (1 - t)**2 * y0 + 2 * (1 - t) * t * y1 + t**2 * y2
        return (x, y)
    
    def update(self, formation_offset, round_num):
        if not self.alive:
            return
        
        if self.state == 'formation':
            self.rect.x = self.formation_x + formation_offset
            self.rect.y = self.formation_y
            # Wing animation only — original Galaxian enemies do NOT shoot in formation
            # They only fire when diving toward the player
            self.wing_timer += 1
            if self.wing_timer > 10:
                self.wing_timer = 0
                self.wing_frame = (self.wing_frame + 1) % len(self.wing_frames)
                # Swap image frame
                if len(self.wing_frames) > 1:
                    self.image = self.wing_frames[self.wing_frame]
        
        elif self.state == 'diving':
            # Update bezier progress — slower dive (1/4 speed) takes ~4x longer than before
            speed = self.dive_speed + (round_num * 0.3)
            self.dive_progress += speed / 120  # ~77 frames to complete at base speed
            pos = self.bezier_point(self.dive_progress)
            self.rect.centerx = int(pos[0])
            self.rect.centery = int(pos[1])
            
            # Shoot during dive — matches original Galaxian behavior
            # Enemies fire as they approach the player during the dive
            self.dive_shoot_timer -= 1
            if self.dive_shoot_timer <= 0:
                # Shoot interval scales with round (harder rounds = faster shooting)
                base_interval = random.randint(20, 50)
                reduction = min(20, round_num * 3)
                self.dive_shoot_timer = max(10, base_interval - reduction)
                return 'shoot'
            
            # Check if dive is complete (past player)
            if self.dive_progress >= 1 or self.rect.centery > SCREEN_HEIGHT + 20:
                self.state = 'returning'
                self.dive_progress = 0
        
        elif self.state == 'returning':
            # Return to formation using curved Bezier path (reverse of dive)
            # Update target to account for current formation offset
            target_x = self.formation_x + formation_offset
            target_y = self.formation_y
            
            # Update return target to current formation position
            self.return_target = (target_x, target_y)
            
            # Progress along return curve (slower than dive for smooth return)
            return_speed = 2.0 + (round_num * 0.2)
            self.return_progress += return_speed / 60  # ~60 frames to return
            
            # Calculate curved return position using Bezier
            pos = self._return_bezier_point(max(0, min(1, self.return_progress)))
            self.rect.centerx = int(pos[0])
            self.rect.centery = int(pos[1])
            
            # Check if return is complete
            if self.return_progress >= 1:
                self.state = 'formation'
                self.rect.x = target_x
                self.rect.y = target_y
                self.return_progress = 0
        
        # Check if enemy is off screen and needs to return
        if self.state == 'diving' and self.rect.centery > SCREEN_HEIGHT + 30:
            self.state = 'returning'
        
        return None
    
    def get_bullet(self, pos=None):
        """Create enemy bullet."""
        x = pos[0] if pos else self.rect.centerx
        y = pos[1] if pos else self.rect.bottom
        self.asset_manager.play_sound('enemy_fire')
        return Bullet(x, y, 0, ENEMY_BULLET_SPEED, 'enemy', self.asset_manager)
    
    def die(self):
        self.alive = False
    
    def draw(self, screen):
        if not self.alive:
            return
        screen.blit(self.image, self.rect)


class UFO:
    """Escort ship (UFO) that dives toward the formation and triggers enemies.
    
    Original Galaxian behavior:
    - A UFO periodically dives from above the screen toward the formation
    - During its dive, it triggers one random enemy to follow
    - After triggering, it flies horizontally across the top of the screen
    - The UFO does not shoot; it's purely a behavioral trigger
    - The UFO is worth 100 points
    """
    
    def __init__(self, asset_manager, round_num=1):
        self.asset_manager = asset_manager
        self.alive = True
        self.state = 'diving'  # diving, flying, leaving
        self.rect = pygame.Rect(0, UFO_TOP, UFO_WIDTH, UFO_HEIGHT)
        
        # Direction: alternate left-to-right and right-to-left
        self.direction = random.choice([-1, 1])
        if self.direction == -1:
            # Right to left
            self.rect.x = SCREEN_WIDTH + 10
        else:
            # Left to right
            self.rect.x = -UFO_WIDTH - 10
        
        # Dive properties - UFO dives from above the screen
        self.dive_start = (self.rect.centerx, -UFO_HEIGHT)  # Start above screen
        self.dive_target = (self.rect.centerx, UFO_TOP + 20)  # End near formation top
        mid_x = (self.dive_start[0] + self.dive_target[0]) / 2
        lateral_offset = random.randint(-40, 40)
        self.dive_control = (mid_x + lateral_offset, -30)  # Control point above screen
        self.dive_progress = 0
        self.dive_speed = 2.0  # UFO dive speed
        
        # Flight properties
        self.speed = UFO_SPEED + (round_num * 0.1)
        self.trigger_enemy = None
        self.has_triggered = False
        
        # Wing animation
        self.wing_frame = 0
        self.wing_timer = 0
        self.wing_frames = [
            asset_manager.sprites['ufo_frame0'],
            asset_manager.sprites['ufo_frame1'],
        ]
        self.image = self.wing_frames[0]
    
    def update(self):
        """Update UFO position and state."""
        if not self.alive:
            return None
        
        # Animation
        self.wing_timer += 1
        if self.wing_timer > 8:
            self.wing_timer = 0
            self.wing_frame = 1 - self.wing_frame
            self.image = self.wing_frames[self.wing_frame]
        
        # State machine
        if self.state == 'diving':
            # Move along curved dive path using Bezier
            self.dive_progress += self.dive_speed / 60  # ~60 frames to complete dive
            
            # Calculate Bezier position
            t = max(0, min(1, self.dive_progress))
            x0, y0 = self.dive_start
            x1, y1 = self.dive_control
            x2, y2 = self.dive_target
            
            x = (1 - t)**2 * x0 + 2 * (1 - t) * t * x1 + t**2 * x2
            y = (1 - t)**2 * y0 + 2 * (1 - t) * t * y1 + t**2 * y2
            
            self.rect.x = int(x)
            self.rect.y = int(y)
            
            # Trigger enemy during dive (only once)
            if not self.has_triggered and self.trigger_enemy is not None:
                self.has_triggered = True
                return self.trigger_enemy
            
            # Check if dive is complete
            if self.dive_progress >= 1:
                self.state = 'flying'
        
        elif self.state == 'flying':
            # Normal flight speed (horizontal)
            self.rect.x += self.direction * self.speed
        
        elif self.state == 'leaving':
            # Move off screen
            self.rect.x += self.direction * self.speed
        
        # Check if off screen (flying or leaving)
        if self.state in ('flying', 'leaving') and \
           ((self.direction == 1 and self.rect.left > SCREEN_WIDTH) or
            (self.direction == -1 and self.rect.right < 0)):
            self.state = 'leaving'
        
        if self.state == 'leaving' and \
           ((self.direction == 1 and self.rect.left > SCREEN_WIDTH + 20) or
            (self.direction == -1 and self.rect.right < -20)):
            self.alive = False
            return 'gone'
        
        return None
    
    def set_dive_target(self, enemy):
        """Set the enemy that will dive when the UFO appears."""
        self.trigger_enemy = enemy
    
    def draw(self, screen):
        """Draw the UFO."""
        if not self.alive:
            return
        screen.blit(self.image, self.rect)

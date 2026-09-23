"""Enemy formation system."""
import random
import pygame
from constants import (
    FORMATION_TOP, FORMATION_SPACING_X, FORMATION_SPACING_Y,
    FORMATION_ROWS, FORMATION_COLS, TOTAL_ENEMIES,
    ENEMY_WIDTH, ENEMY_HEIGHT,
    FORMATION_SPEED_BASE, MAX_DIVES_PER_ROUND,
    DIVE_INTERVAL_BASE, UFO_APPEAR_INTERVAL_BASE, UFO_APPEAR_INTERVAL_MIN,
)
from entities.enemy import Enemy, UFO

class Formation:
    """Manages the enemy formation movement and dive triggers.
    
    Original Galaxian behavior:
    - Enemies do NOT shoot while in formation
    - Enemies only shoot when diving toward the player
    - Dives are faster than formation movement
    """
    
    def __init__(self, asset_manager):
        self.asset_manager = asset_manager
        self.enemies = []
        self.formation_offset = 0
        self.formation_direction = 1
        self.formation_speed = FORMATION_SPEED_BASE
        self.hover_offset = 0
        self.hover_direction = 1
        self.dive_timer = DIVE_INTERVAL_BASE
        self.dives_this_round = 0
        self.max_dives = MAX_DIVES_PER_ROUND
        self.round_num = 1
        self.enemy_types = self._assign_enemy_types()
        
        # UFO (escort ship) state
        self.ufo = None
        self.ufo_timer = UFO_APPEAR_INTERVAL_BASE
        self.ufo_interval = UFO_APPEAR_INTERVAL_BASE
    
    def _assign_enemy_types(self):
        """Assign enemy types based on row (original Galaxian pattern)."""
        types = []
        # Row 0 (top): 5 flagships
        for _ in range(5):
            types.append('flagship')
        # Row 1: 5 red
        for _ in range(5):
            types.append('red')
        # Row 2: 5 yellow
        for _ in range(5):
            types.append('yellow')
        # Row 3: 5 blue
        for _ in range(5):
            types.append('blue')
        # Row 4 (bottom): 5 green
        for _ in range(5):
            types.append('green')
        return types
    
    def create_enemies(self):
        """Create all enemies in V-shaped formation."""
        self.enemies = []
        self.formation_offset = 0
        self.dives_this_round = 0
        self.dive_timer = DIVE_INTERVAL_BASE
        self.ufo = None
        self.ufo_timer = UFO_APPEAR_INTERVAL_BASE
        
        # Calculate formation center
        total_width = (FORMATION_COLS - 1) * FORMATION_SPACING_X
        start_x = (256 - total_width) / 2  # 256 = SCREEN_WIDTH
        
        # V-shape: offset each row slightly inward
        for row in range(FORMATION_ROWS):
            for col in range(FORMATION_COLS):
                x = start_x + col * FORMATION_SPACING_X
                y = FORMATION_TOP + row * FORMATION_SPACING_Y
                
                # V-shape offset: rows toward bottom move inward slightly
                v_offset = row * 4
                x += v_offset
                
                enemy_type = self.enemy_types[row * FORMATION_COLS + col]
                enemy = Enemy(x, y, enemy_type, self.asset_manager, row, col)
                self.enemies.append(enemy)
        
        return self.enemies
    
    def update(self, round_num, player=None):
        """Update formation movement and trigger dives."""
        self.round_num = round_num
        
        # Update difficulty parameters
        self.formation_speed = FORMATION_SPEED_BASE + (round_num * 0.1)
        self.max_dives = MAX_DIVES_PER_ROUND + (round_num * 2)
        self.dive_interval = max(60, DIVE_INTERVAL_BASE - (round_num * 15))
        self.ufo_interval = max(UFO_APPEAR_INTERVAL_MIN, 
                                UFO_APPEAR_INTERVAL_BASE - (round_num * 50))
        
        # Reset dive timer when round changes
        if self.dive_timer > self.dive_interval:
            self.dive_timer = self.dive_interval
        
        # Side-to-side movement with hover
        self.formation_offset += self.formation_speed * self.formation_direction
        self.hover_offset += 0.3 * self.hover_direction
        
        # Bounce off edges
        if self.formation_offset > 20:
            self.formation_direction = -1
        elif self.formation_offset < -20:
            self.formation_direction = 1
        
        if abs(self.hover_offset) > 3:
            self.hover_direction = -self.hover_direction
        
        # Update all enemies (diving enemies may shoot; formation enemies do not shoot)
        shooting_enemy = None
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            
            result = enemy.update(self.formation_offset + self.hover_offset, round_num)
            if result == 'shoot':
                shooting_enemy = enemy
        
        # Trigger dive attacks (once per frame, not per enemy)
        if player is not None:
            self.dive_timer -= 1
            if self.dive_timer <= 0:
                diver = self._trigger_dive(player)
                if diver:
                    diver.start_dive(player.rect.centerx, player.rect.bottom)
                    self.dives_this_round += 1
                    self.dive_timer = max(30, DIVE_INTERVAL_BASE // 2 - (round_num * 10))
            
            # Process wave follower dive delays
            for enemy in self.enemies:
                if hasattr(enemy, 'dive_delay') and enemy.dive_delay > 0 and enemy.state == 'formation':
                    enemy.dive_delay -= 1
                    if enemy.dive_delay <= 0:
                        enemy.start_dive(player.rect.centerx, player.rect.bottom)
                        self.dives_this_round += 1
        
        # Update UFO if it exists
        ufo_result = None
        if self.ufo is not None:
            ufo_result = self.ufo.update()
            if ufo_result == 'gone':
                self.ufo = None
        
        # Spawn UFO on timer
        if self.ufo is None and player is not None:
            self.ufo_timer -= 1
            if self.ufo_timer <= 0:
                self._spawn_ufo()
                self.ufo_timer = self.ufo_interval
        
        return shooting_enemy, ufo_result
    
    def _trigger_dive(self, player):
        """Find and return a random formation enemy to dive."""
        if self.dives_this_round >= self.max_dives:
            return None
        
        # Find a random alive enemy that's in formation
        formation_enemies = [e for e in self.enemies if e.alive and e.state == 'formation']
        if not formation_enemies:
            return None
        
        # Prefer red and flagship enemies to dive more
        priority = [e for e in formation_enemies if e.enemy_type in ('red', 'flagship')]
        if priority:
            return random.choice(priority)
        return random.choice(formation_enemies)
    
    def _spawn_ufo(self):
        """Spawn a UFO and trigger a wave of enemies to dive.
        
        Original Galaxian behavior:
        - UFO flies across the top of the screen
        - When it appears, one enemy dives immediately to follow it
        - Additional enemies follow in a staggered wave (2-3 followers)
        """
        if not self.enemies:
            return
        
        # Pick a random alive formation enemy to dive first
        formation_enemies = [e for e in self.enemies if e.alive and e.state == 'formation']
        if not formation_enemies:
            return
        
        diver = random.choice(formation_enemies)
        formation_enemies.remove(diver)
        
        # Create UFO and set the dive target
        self.ufo = UFO(self.asset_manager, self.round_num)
        self.ufo.set_dive_target(diver)
        
        # Schedule wave followers (2-3 enemies diving with staggered delays)
        num_followers = min(random.randint(2, 3), len(formation_enemies))
        wave_enemies = random.sample(formation_enemies, num_followers)
        for i, follower in enumerate(wave_enemies):
            follower.dive_delay = (i + 1) * 30  # 30-frame stagger between followers
        
        # Play UFO sound
        sound = self.asset_manager.get_sound('ufo_appear')
        if sound:
            sound.play()
    
    def try_dive(self, player):
        """Try to trigger a dive attack."""
        if self.dives_this_round >= self.max_dives:
            return None
        
        self.dive_timer -= 1
        if self.dive_timer > 0:
            return None
        
        # Find a random alive enemy that's in formation
        formation_enemies = [e for e in self.enemies if e.alive and e.state == 'formation']
        if not formation_enemies:
            return None
        
        # Prefer red and flagship enemies to dive more
        priority = [e for e in formation_enemies if e.enemy_type in ('red', 'flagship')]
        if priority:
            diver = random.choice(priority)
        else:
            diver = random.choice(formation_enemies)
        
        diver.start_dive(player.rect.centerx, player.rect.bottom)
        self.dives_this_round += 1
        self.dive_timer = DIVE_INTERVAL_BASE
        
        return diver
    
    def alive_count(self):
        """Count alive enemies."""
        return sum(1 for e in self.enemies if e.alive)
    
    def reset(self, round_num=1):
        """Reset formation for new round."""
        self.round_num = round_num
        self.formation_offset = 0
        self.formation_direction = 1
        self.hover_offset = 0
        self.hover_direction = 1
        self.dives_this_round = 0
        self.dive_timer = DIVE_INTERVAL_BASE
        self.ufo = None
        self.ufo_timer = UFO_APPEAR_INTERVAL_BASE

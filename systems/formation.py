"""Enemy formation system."""
import random
import pygame
from constants import (
    FORMATION_TOP, FORMATION_SPACING_X, FORMATION_SPACING_Y,
    FORMATION_ROWS, FORMATION_COLS, TOTAL_ENEMIES,
    ENEMY_WIDTH, ENEMY_HEIGHT,
    FORMATION_SPEED_BASE, MAX_DIVES_PER_ROUND,
    DIVE_INTERVAL_BASE, UFO_APPEAR_INTERVAL_BASE, UFO_APPEAR_INTERVAL_MIN,
    TRIANGLE_LATERAL_OFFSET, TRIANGLE_VERTICAL_OFFSET,
    SCREEN_WIDTH,
)
from entities.enemy import Enemy, UFO, DiveFormation

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
        
        # Triangle formation dive tracking
        self.dive_formations = []  # List of active DiveFormation instances
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
        
        # Update dive formations — check integrity, clean up completed
        for formation in self.dive_formations[:]:
            if not formation.check_integrity():
                self.dive_formations.remove(formation)
                continue
            if formation.completed:
                self.dive_formations.remove(formation)
        
        # Trigger dive attacks (once per frame, not per enemy)
        if player is not None:
            self.dive_timer -= 1
            if self.dive_timer <= 0:
                diver = self._trigger_dive(player)
                if diver:
                    self.dives_this_round += 1
                    self.dive_timer = max(30, DIVE_INTERVAL_BASE // 2 - (round_num * 10))
        
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
        """Find and return a random formation enemy to dive in a triangle group.
        
        Selects a leader diver and two escorts, then triggers all three
        simultaneously in triangle formation. Falls back to single independent
        dive if fewer than 3 enemies are available.
        """
        if self.dives_this_round >= self.max_dives:
            return None
        
        formation_enemies = [e for e in self.enemies if e.alive and e.state == 'formation']
        if len(formation_enemies) < 3:
            # Fallback: single independent dive if not enough enemies
            if not formation_enemies:
                return None
            diver = self._select_diver(formation_enemies)
            diver.start_dive(player.rect.centerx, player.rect.bottom)
            self.dives_this_round += 1
            return diver
        
        diver = self._select_diver(formation_enemies)
        escorts = self._select_escorts(formation_enemies, diver, count=2)
        
        formation = DiveFormation(diver, escorts,
                                  lateral_offset=TRIANGLE_LATERAL_OFFSET,
                                  vertical_offset=TRIANGLE_VERTICAL_OFFSET)
        self.dive_formations.append(formation)
        
        # Set formation offsets for escorts
        for i, escort in enumerate(escorts):
            if i == 0:
                escort.formation_offset_x = -TRIANGLE_LATERAL_OFFSET
            else:
                escort.formation_offset_x = TRIANGLE_LATERAL_OFFSET
            escort.formation_offset_y = -TRIANGLE_VERTICAL_OFFSET
        
        diver.start_dive(player.rect.centerx, player.rect.bottom,
                         dive_formation=formation)
        for escort in escorts:
            escort.start_dive(player.rect.centerx, player.rect.bottom,
                             dive_formation=formation)
        
        self.dives_this_round += 1
        return diver
    
    def _spawn_ufo(self):
        """Spawn a UFO and create a triangle formation dive group.
        
        Creates the formation and marks the leader and escorts.
        The actual dive start happens in _trigger_dive when player
        coordinates are available.
        """
        if not self.enemies:
            return
        
        # Pick a random alive formation enemy to dive first
        formation_enemies = [e for e in self.enemies if e.alive and e.state == 'formation']
        if not formation_enemies:
            return
        
        diver = self._select_diver(formation_enemies)
        escorts = self._select_escorts(formation_enemies, diver, count=2)
        
        # Create triangle formation group (but don't start diving yet)
        formation = DiveFormation(diver, escorts,
                                  lateral_offset=TRIANGLE_LATERAL_OFFSET,
                                  vertical_offset=TRIANGLE_VERTICAL_OFFSET)
        self.dive_formations.append(formation)
        
        # Mark enemies as part of formation (dive will start in _trigger_dive)
        diver.dive_formation = formation
        for escort in escorts:
            escort.dive_formation = formation
        
        # Create UFO and set the dive target
        self.ufo = UFO(self.asset_manager, self.round_num)
        self.ufo.set_dive_target(diver)
        
        # Play UFO sound
        sound = self.asset_manager.get_sound('ufo_appear')
        if sound:
            sound.play()
    
    def _select_diver(self, formation_enemies):
        """Select a random formation enemy as the leader diver.
        
        Prefers red and flagship enemies (matches original Galaxian behavior).
        """
        priority = [e for e in formation_enemies if e.enemy_type in ('red', 'flagship')]
        if priority:
            return random.choice(priority)
        return random.choice(formation_enemies)
    
    def _select_escorts(self, formation_enemies, leader, count=2):
        """Select escort enemies that are NOT the leader and NOT already in a formation.
        
        Only enemies in 'formation' state can be selected as escorts.
        """
        candidates = [e for e in formation_enemies if e is not leader and e.state == 'formation']
        actual_count = min(count, len(candidates))
        if actual_count < count:
            # Not enough escorts available — return what we can
            pass
        return random.sample(candidates, actual_count) if candidates else []
    
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

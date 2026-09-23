"""Asset management for Galaxian clone."""
import pygame
import os
import math

class AssetManager:
    """Manages all game assets including sprites and sounds."""
    
    def __init__(self):
        self.sprites = {}
        self.sounds = {}
        self._generate_sprites()
        self._generate_sounds()
    
    def _generate_sprites(self):
        """Generate all game sprites programmatically."""
        # Player ship (Galaxip) - 12x12
        self.sprites['player'] = self._create_player_sprite()
        self.sprites['player_explode'] = self._create_explosion_sprites(12, 12)
        
        # Enemies - 10x10
        self.sprites['enemy_green'] = self._create_enemy_sprite((0, 255, 0))
        self.sprites['enemy_blue'] = self._create_enemy_sprite((0, 100, 255))
        self.sprites['enemy_yellow'] = self._create_enemy_sprite((255, 255, 0))
        self.sprites['enemy_red'] = self._create_enemy_sprite((255, 50, 50))
        self.sprites['enemy_flagship'] = self._create_flagship_sprite()
        self.sprites['enemy_escort'] = self._create_escort_sprite()
        
        # Bullets
        self.sprites['player_bullet'] = self._create_bullet_sprite((255, 255, 255), 2, 6)
        self.sprites['enemy_bullet'] = self._create_bullet_sprite((255, 100, 100), 2, 4)
        
        # Explosion frames
        self.sprites['explosion'] = self._create_explosion_sprites(10, 10)
        
        # UI elements
        self.sprites['star'] = self._create_star_sprite()
        
        # UFO (escort ship) - 14x10
        self.sprites['ufo_frame0'] = self._create_ufo_sprite(0)
        self.sprites['ufo_frame1'] = self._create_ufo_sprite(1)
    
    def _create_player_sprite(self):
        """Create player ship sprite from samples/player.png pixel data.
        
        Recreates the 13x16 pixel sprite with accurate colors:
        - Red (224,0,0): cockpit/accents
        - Teal (0,195,217): main body
        - Gray (195,195,217): wings/details
        - Black (0,0,0): outline/background
        """
        surface = pygame.Surface((13, 16), pygame.SRCALPHA)
        
        # Most common exact colors from PNG pixel data
        RED = (224, 0, 0)
        TEAL = (0, 195, 217)
        GRAY = (195, 195, 217)
        BLACK = (0, 0, 0)
        
        # Pixel grid: B=Black, R=Red, T=Teal, G=Gray
        grid = [
            "BBBBBRRRBBBBB",  # y=0
            "BBBBRRRRRBBBB",  # y=1
            "BBBRRRRRRRBBB",  # y=2
            "BBBRRRRRRRBBB",  # y=3
            "BBBRBBRBBRBBB",  # y=4
            "BGBBBTRTBBBGB",  # y=5
            "BGBBBTRTBBBGB",  # y=6
            "GGGBBTRTBBGGG",  # y=7
            "GTGBTTRTTBGTG",  # y=8
            "GTGTTTRTTTGTG",  # y=9
            "GTTTTTRTTTTTG",  # y=10
            "GTGTBTRTBTGTG",  # y=11
            "GTGBBTBTBBGTG",  # y=12
            "GTGBBTBTBBGTG",  # y=13
            "GGGBBBBBBBGGG",  # y=14
            "BGBBBBBBBBBGB",  # y=15
        ]
        
        color_map = {'B': BLACK, 'R': RED, 'T': TEAL, 'G': GRAY}
        
        for y, row in enumerate(grid):
            for x, char in enumerate(row):
                surface.set_at((x, y), color_map[char])
        
        return surface
    
    def _create_enemy_sprite(self, color):
        """Create dragonfly alien enemy sprite with two wing animation frames."""
        # Frame 0: wings raised (flap up)
        surface0 = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(surface0, color, (4, 2, 2, 6))
        pygame.draw.polygon(surface0, color, [
            (0, 3), (4, 3), (4, 5)
        ])
        pygame.draw.polygon(surface0, color, [
            (10, 3), (6, 3), (6, 5)
        ])
        pygame.draw.line(surface0, color, (4, 2), (3, 0), 1)
        pygame.draw.line(surface0, color, (6, 2), (7, 0), 1)
        
        # Frame 1: wings lowered (flap down)
        surface1 = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(surface1, color, (4, 2, 2, 6))
        pygame.draw.polygon(surface1, color, [
            (0, 5), (4, 3), (4, 5)
        ])
        pygame.draw.polygon(surface1, color, [
            (10, 5), (6, 3), (6, 5)
        ])
        pygame.draw.line(surface1, color, (4, 2), (3, 0), 1)
        pygame.draw.line(surface1, color, (6, 2), (7, 0), 1)
        
        return [surface0, surface1]
    
    def _create_flagship_sprite(self):
        """Create Galboss flagship sprite with wing animation frames."""
        # Frame 0: wings raised
        surface0 = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(surface0, (255, 50, 50), (3, 2, 8, 10))
        pygame.draw.polygon(surface0, (255, 100, 100), [
            (0, 4), (3, 4), (3, 7)
        ])
        pygame.draw.polygon(surface0, (255, 100, 100), [
            (14, 4), (11, 4), (11, 7)
        ])
        pygame.draw.circle(surface0, (255, 255, 0), (7, 5), 2)
        pygame.draw.polygon(surface0, (255, 200, 200), [
            (5, 2), (7, 0), (9, 2)
        ])
        
        # Frame 1: wings lowered
        surface1 = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(surface1, (255, 50, 50), (3, 2, 8, 10))
        pygame.draw.polygon(surface1, (255, 100, 100), [
            (0, 6), (3, 4), (3, 7)
        ])
        pygame.draw.polygon(surface1, (255, 100, 100), [
            (14, 6), (11, 4), (11, 7)
        ])
        pygame.draw.circle(surface1, (255, 255, 0), (7, 5), 2)
        pygame.draw.polygon(surface1, (255, 200, 200), [
            (5, 2), (7, 0), (9, 2)
        ])
        
        return [surface0, surface1]
    
    def _create_escort_sprite(self):
        """Create escort ship sprite with wing animation frames."""
        # Frame 0: wings raised
        surface0 = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(surface0, (255, 100, 100), (3, 1, 4, 8))
        pygame.draw.polygon(surface0, (255, 150, 150), [
            (0, 3), (3, 3), (3, 5)
        ])
        pygame.draw.polygon(surface0, (255, 150, 150), [
            (10, 3), (7, 3), (7, 5)
        ])
        
        # Frame 1: wings lowered
        surface1 = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(surface1, (255, 100, 100), (3, 1, 4, 8))
        pygame.draw.polygon(surface1, (255, 150, 150), [
            (0, 5), (3, 3), (3, 5)
        ])
        pygame.draw.polygon(surface1, (255, 150, 150), [
            (10, 5), (7, 3), (7, 5)
        ])
        
        return [surface0, surface1]
    
    def _create_ufo_sprite(self, frame=0):
        """Create UFO (escort ship) sprite with two animation frames.
        
        The UFO is a small saucer-shaped craft that flies across the top
        of the screen and triggers enemies to dive.
        """
        if frame == 0:
            # Frame 0: wings up
            surface = pygame.Surface((14, 10), pygame.SRCALPHA)
            # Dome
            pygame.draw.ellipse(surface, (255, 255, 100), (5, 0, 4, 4))
            # Body
            pygame.draw.ellipse(surface, (200, 200, 50), (2, 3, 10, 5))
            # Lights
            pygame.draw.circle(surface, (255, 255, 0), (4, 6), 1)
            pygame.draw.circle(surface, (255, 255, 0), (7, 6), 1)
            pygame.draw.circle(surface, (255, 255, 0), (10, 6), 1)
        else:
            # Frame 1: wings down
            surface = pygame.Surface((14, 10), pygame.SRCALPHA)
            # Dome
            pygame.draw.ellipse(surface, (255, 255, 100), (5, 1, 4, 3))
            # Body (flattened)
            pygame.draw.ellipse(surface, (200, 200, 50), (1, 4, 12, 4))
            # Lights
            pygame.draw.circle(surface, (255, 255, 0), (4, 6), 1)
            pygame.draw.circle(surface, (255, 255, 0), (7, 6), 1)
            pygame.draw.circle(surface, (255, 255, 0), (10, 6), 1)
        
        return surface
    
    def _create_bullet_sprite(self, color, width, height):
        """Create bullet sprite."""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, color, (0, 0, width, height))
        return surface
    
    def _create_explosion_sprites(self, size, frames=4):
        """Create explosion animation frames."""
        explosions = []
        for i in range(frames):
            surface = pygame.Surface((size, size), pygame.SRCALPHA)
            radius = int(size * (i + 1) / frames / 2)
            if radius > 0:
                pygame.draw.circle(surface, (255, 200, 0), (size // 2, size // 2), radius)
                pygame.draw.circle(surface, (255, 100, 0), (size // 2, size // 2), radius - 2)
            explosions.append(surface)
        return explosions
    
    def _create_star_sprite(self):
        """Create a small star for background."""
        surface = pygame.Surface((2, 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, (255, 255, 255), (1, 1), 1)
        return surface
    
    def get_sound(self, name):
        """Get a sound effect."""
        return self.sounds.get(name)
    
    def play_sound(self, name, enabled=None):
        """Play a sound effect with optional SOUND_ENABLED gating.
        
        Args:
            name: Sound effect name (e.g., 'shoot', 'explosion')
            enabled: If True, always play. If False, never play.
                     If None, checks SOUND_ENABLED constant.
        """
        # Determine if sound should play
        if enabled is False:
            return
        if enabled is None:
            try:
                from constants import SOUND_ENABLED
                if not SOUND_ENABLED:
                    return
            except ImportError:
                pass  # No constant found, play anyway
        
        sound = self.sounds.get(name)
        if sound:
            sound.play()
    
    def _generate_sounds(self):
        """Generate sound effects using pygame.mixer."""
        try:
            import array
            sample_rate = 22050
            
            # Player shoot - high frequency beep
            data = array.array('h', [0] * int(sample_rate * 0.1))
            for i in range(len(data)):
                t = i / sample_rate
                data[i] = int(1000 * math.sin(2 * math.pi * 880 * t))
            self.sounds['shoot'] = pygame.mixer.Sound(buffer=data)
            
            # Enemy explosion - noise burst
            data = array.array('h', [0] * int(sample_rate * 0.3))
            for i in range(len(data)):
                t = i / sample_rate
                data[i] = int(500 * math.sin(2 * math.pi * 200 * t) * (1 - t / 0.3))
            self.sounds['explosion'] = pygame.mixer.Sound(buffer=data)
            
            # Player death - descending tone
            data = array.array('h', [0] * int(sample_rate * 0.5))
            for i in range(len(data)):
                t = i / sample_rate
                current_freq = 880 - 700 * (t / 0.5)
                data[i] = int(800 * math.sin(2 * math.pi * max(current_freq, 100) * t))
            self.sounds['player_death'] = pygame.mixer.Sound(buffer=data)
            
            # Enemy dive - rising tone
            data = array.array('h', [0] * int(sample_rate * 0.2))
            for i in range(len(data)):
                t = i / sample_rate
                current_freq = 300 + 600 * (t / 0.2)
                data[i] = int(600 * math.sin(2 * math.pi * current_freq * t))
            self.sounds['dive'] = pygame.mixer.Sound(buffer=data)
            
            # Bonus - ascending arpeggio
            data = array.array('h', [0] * int(sample_rate * 0.4))
            for i in range(len(data)):
                t = i / sample_rate
                if t < 0.1:
                    current_freq = 523  # C5
                elif t < 0.2:
                    current_freq = 659  # E5
                elif t < 0.3:
                    current_freq = 784  # G5
                else:
                    current_freq = 1047  # C6
                data[i] = int(800 * math.sin(2 * math.pi * current_freq * t))
            self.sounds['bonus'] = pygame.mixer.Sound(buffer=data)
            
            # Enemy fire - short downward sweep
            data = array.array('h', [0] * int(sample_rate * 0.08))
            for i in range(len(data)):
                t = i / sample_rate
                current_freq = 600 - 400 * (t / 0.08)
                data[i] = int(600 * math.sin(2 * math.pi * max(current_freq, 50) * t))
            self.sounds['enemy_fire'] = pygame.mixer.Sound(buffer=data)
            
            # Round start - ascending fanfare
            data = array.array('h', [0] * int(sample_rate * 0.5))
            for i in range(len(data)):
                t = i / sample_rate
                if t < 0.125:
                    current_freq = 262  # C4
                elif t < 0.25:
                    current_freq = 330  # E4
                elif t < 0.375:
                    current_freq = 392  # G4
                else:
                    current_freq = 524  # C5
                data[i] = int(800 * math.sin(2 * math.pi * current_freq * t))
            self.sounds['round_start'] = pygame.mixer.Sound(buffer=data)
            
            # Game over - descending sad tone
            data = array.array('h', [0] * int(sample_rate * 0.8))
            for i in range(len(data)):
                t = i / sample_rate
                current_freq = 440 - 340 * (t / 0.8)
                data[i] = int(700 * math.sin(2 * math.pi * max(current_freq, 50) * t))
            self.sounds['game_over'] = pygame.mixer.Sound(buffer=data)
            
        except Exception:
            # If sound generation fails, sounds will be None
            pass

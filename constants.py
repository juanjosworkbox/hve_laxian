"""Galaxian clone constants."""

# Screen dimensions (original hardware resolution)
SCREEN_WIDTH = 256
SCREEN_HEIGHT = 288
SCREEN_SCALE = 2
DISPLAY_WIDTH = SCREEN_WIDTH * SCREEN_SCALE
DISPLAY_HEIGHT = SCREEN_HEIGHT * SCREEN_SCALE
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
GOLD = (255, 215, 0)

# Player constants
PLAYER_SPEED = 3  # pixels per frame
PLAYER_BULLET_SPEED = 6
PLAYER_Y = SCREEN_HEIGHT - 24
PLAYER_WIDTH = 13
PLAYER_HEIGHT = 16
PLAYER_RESPAWN_INVINCIBLE_FRAMES = 120  # 2 seconds at 60 FPS

# Enemy constants
ENEMY_WIDTH = 10
ENEMY_HEIGHT = 10
ENEMY_BULLET_SPEED = 2
FORMATION_TOP = 20
FORMATION_SPACING_X = 20
FORMATION_SPACING_Y = 16
FORMATION_ROWS = 5
FORMATION_COLS = 5
TOTAL_ENEMIES = FORMATION_ROWS * FORMATION_COLS  # 25
FORMATION_SPEED_BASE = 0.3  # Slower side-to-side formation movement (original arcade)

# Enemy point values
ENEMY_POINTS = {
    "green": 100,
    "blue": 150,
    "yellow": 200,
    "red": 300,
    "flagship": 400,
    "escort": 200,
}

# UFO (escort ship) constants
UFO_POINTS = 100
UFO_WIDTH = 14
UFO_HEIGHT = 10
UFO_SPEED = 1  # pixels per frame
UFO_TOP = 5  # Y position from top of screen
UFO_APPEAR_INTERVAL_BASE = 600  # frames between UFO appearances
UFO_APPEAR_INTERVAL_MIN = 300  # minimum interval (harder rounds)
UFO_TRAVEL_LEFT_TO_RIGHT = True  # direction flag

# Scoring
BONUS_LIFE_SCORE = 4000
BONUS_ENEMY_SCORE = 5000
ENEMY_DIVE_BONUS = 50

# Lives
STARTING_LIVES = 3

# Dive constants
DIVE_BEZIER_CONTROL_Y = 180  # control point Y for curved dive
DIVE_BASE_SPEED = 1.25  # 1/4 of original 5.0, ~4x formation speed (0.3)
MAX_DIVES_PER_ROUND = 5  # increases with round

# Difficulty scaling
FORMATION_SPEED_BASE = 0.3
DIVE_SPEED_BASE = 2
DIVE_INTERVAL_BASE = 180  # frames between dive attempts

# Sound
SOUND_ENABLED = True

# Game states
class GameState:
    ATTRACT = "attract"
    PLAYING = "playing"
    ROUND_TRANSITION = "round_transition"
    GAME_OVER = "game_over"
    PLAYER_DEATH = "player_death"

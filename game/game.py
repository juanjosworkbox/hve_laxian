"""Main Game class for Galaxian clone."""
import pygame
import sys
import random
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, DISPLAY_WIDTH, DISPLAY_HEIGHT,
    FPS, BLACK, WHITE, GOLD, GREEN, RED, YELLOW,
    STARTING_LIVES, PLAYER_Y, BONUS_LIFE_SCORE,
    ENEMY_POINTS, UFO_POINTS, GameState,
)
from assets import AssetManager
from entities import Player, Enemy, Bullet, Explosion, UFO as UFOEntity
from systems import Formation, Starfield
from systems.collision import check_bullet_enemy_collisions, check_player_enemy_collisions, check_bullet_player_collisions

class Game:
    """Main Galaxian game class."""
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=8, buffer=512)
        
        self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_caption("GALAXIAN")
        self.clock = pygame.time.Clock()
        
        # Offscreen surface for native resolution
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.asset_manager = AssetManager()
        self.starfield = Starfield()
        
        self.state = GameState.ATTRACT
        self.round_num = 1
        self.score = 0
        self.lives = STARTING_LIVES
        self.high_score = self._load_high_score()
        
        self.player = None
        self.enemies = []
        self.enemy_bullets = []
        self.explosions = []
        self.formations = Formation(self.asset_manager)
        self.ufos = []
        
        self.round_transition_timer = 0
        self.player_death_timer = 0
        self.attract_timer = 0
        self.bonus_awarded = False
        
        self.font = pygame.font.SysFont('arial,monospace', 8, bold=True)
        self.font_small = pygame.font.SysFont('arial,monospace', 6)
        self.font_large = pygame.font.SysFont('arial,monospace', 14, bold=True)
    
    def _load_high_score(self):
        """Load high score from file."""
        try:
            with open('highscore.txt', 'r') as f:
                return int(f.read().strip())
        except:
            return 0
    
    def _save_high_score(self):
        """Save high score to file."""
        if self.score > self.high_score:
            self.high_score = self.score
            try:
                with open('highscore.txt', 'w') as f:
                    f.write(str(self.high_score))
            except:
                pass
            self.asset_manager.play_sound('game_over')
    
    def start_game(self):
        """Start a new game."""
        self.score = 0
        self.lives = STARTING_LIVES
        self.round_num = 1
        self.bonus_awarded = False
        self.start_round()
        self.state = GameState.PLAYING
    
    def start_round(self):
        """Start a new round."""
        self.formations.reset(self.round_num)
        self.enemies = self.formations.create_enemies()
        self.enemy_bullets = []
        self.explosions = []
        self.ufos = []
        self.player = Player(self.asset_manager)
        self.state = GameState.PLAYING
        self.asset_manager.play_sound('round_start')
    
    def handle_input(self):
        """Handle keyboard input."""
        keys = pygame.key.get_pressed()
        
        if self.state == GameState.ATTRACT:
            # Any key or coin start
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN] or keys[pygame.K_1]:
                self.start_game()
            return
        
        if self.state == GameState.PLAYING:
            # Player movement
            self.player.handle_input(keys)
            
            # Player shooting
            if keys[pygame.K_SPACE]:
                bullet = self.player.fire()
                if bullet:
                    sound = self.asset_manager.get_sound('shoot')
                    if sound:
                        sound.play()
        
        elif self.state == GameState.GAME_OVER:
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                self.state = GameState.ATTRACT
                self.round_num = 1
                self.score = 0
                self.asset_manager.play_sound('game_over')
    
    def update(self):
        """Update game state."""
        self.starfield.update()
        self.attract_timer += 1
        
        if self.state == GameState.ATTRACT:
            return
        
        if self.state == GameState.PLAYING:
            self._update_playing()
        
        elif self.state == GameState.ROUND_TRANSITION:
            self.round_transition_timer -= 1
            if self.round_transition_timer <= 0:
                self.start_round()
        
        elif self.state == GameState.PLAYER_DEATH:
            self.player_death_timer -= 1
            if self.player_death_timer <= 0:
                if self.lives > 0:
                    self.state = GameState.PLAYING
                else:
                    self._save_high_score()
                    self.state = GameState.GAME_OVER
        
        # Update explosions
        for explosion in self.explosions:
            explosion.update()
        self.explosions = [e for e in self.explosions if e.active]
    
    def _update_playing(self):
        """Update playing state."""
        if not self.player:
            return
        
        # Update player
        self.player.update()
        
        # Update formation and handle diving enemy shooting
        result = self.formations.update(self.round_num, self.player)
        shooting_enemy = result[0] if result else None
        ufo_result = result[1] if len(result) > 1 else None
        
        if shooting_enemy:
            bullet = shooting_enemy.get_bullet()
            if bullet:
                self.enemy_bullets.append(bullet)
        
        # Handle UFO from formation
        if ufo_result is not None:
            diver = ufo_result
            # UFO triggered a dive - the diver is already set in UFO
            # Add UFO to the game's UFO list
            if self.formations.ufo and self.formations.ufo not in self.ufos:
                self.ufos.append(self.formations.ufo)
        
        # Check enemy bullets vs player
        if self.player.alive:
            for bullet in self.enemy_bullets:
                bullet.update()
                if bullet.hit:
                    continue
                # Check collision with player
                if self.player.get_rect().colliderect(bullet.get_rect()):
                    bullet.hit = True
                    self._player_hit()
        
        # Check player-enemy collision (only if player alive)
        if self.player.alive and self.player.check_collision(self.enemies):
            self._player_hit()
        
        # Check player bullet vs enemies
        if self.player.bullet and not self.player.bullet.hit:
            hit_enemies = check_bullet_enemy_collisions(self.player.bullet, self.enemies, self.explosions)
            for enemy in hit_enemies:
                points = ENEMY_POINTS.get(enemy.enemy_type, 100)
                self.score += points
                
                # Create explosion
                explosion = Explosion(enemy.rect.centerx, enemy.rect.centery, self.asset_manager)
                self.explosions.append(explosion)
                
                # Play sound
                self.asset_manager.play_sound('explosion')
                
                # Check for bonus life
                if self.score >= BONUS_LIFE_SCORE and not self.bonus_awarded:
                    self.lives += 1
                    self.bonus_awarded = True
                    self.asset_manager.play_sound('bonus')
        
        # Check player bullet vs UFOs
        if self.player.bullet and not self.player.bullet.hit:
            for ufo in self.ufos:
                if ufo.alive and self.player.bullet.get_rect().colliderect(ufo.rect):
                    self.player.bullet.hit = True
                    # Score UFO
                    self.score += UFO_POINTS
                    # Create explosion at UFO position
                    explosion = Explosion(ufo.rect.centerx, ufo.rect.centery, self.asset_manager)
                    self.explosions.append(explosion)
                    # Play sound
                    self.asset_manager.play_sound('explosion')
                    # Remove UFO
                    ufo.alive = False
                    break
        
        # Clean up hit bullets
        self.enemy_bullets = [b for b in self.enemy_bullets if not b.hit]
        
        # Update and clean up UFOs
        for ufo in self.ufos:
            ufo_result = ufo.update()
            if ufo_result == 'gone':
                ufo.alive = False
        self.ufos = [ufo for ufo in self.ufos if ufo.alive]
        
        # Check if round is cleared
        if self.formations.alive_count() == 0:
            self.round_num += 1
            self.round_transition_timer = 120  # 2 second transition
            self.state = GameState.ROUND_TRANSITION
    
    def _player_hit(self):
        """Handle player death."""
        # Guard: if player is already dead and in PLAYER_DEATH state, don't reprocess
        if not self.player.alive and self.state == GameState.PLAYER_DEATH:
            return
        
        self.lives -= 1
        self.player.die()
        
        # Create explosion
        explosion = Explosion(self.player.rect.centerx, self.player.rect.centery, self.asset_manager, 12)
        self.explosions.append(explosion)
        
        # Play sound
        self.asset_manager.play_sound('player_death')
        
        self.player_death_timer = 90  # 1.5 seconds
        self.state = GameState.PLAYER_DEATH
    
    def draw(self):
        """Draw the game."""
        # Clear offscreen surface
        self.surface.fill(BLACK)
        
        # Draw starfield
        self.starfield.draw(self.surface)
        
        if self.state == GameState.ATTRACT:
            self._draw_attract()
        elif self.state in (GameState.PLAYING, GameState.ROUND_TRANSITION, GameState.PLAYER_DEATH):
            self._draw_playing()
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()
        
        # Scale to display size
        scaled = pygame.transform.scale(self.surface, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.screen.blit(scaled, (0, 0))
        
        pygame.display.flip()
    
    def _draw_attract(self):
        """Draw attract mode."""
        # Title
        title = self.font_large.render("GALAXIAN", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 60))
        self.surface.blit(title, title_rect)
        
        # Message
        msg = "WE ARE THE GALAXIANS"
        message = self.font.render(msg, True, YELLOW)
        msg_rect = message.get_rect(center=(SCREEN_WIDTH//2, 120))
        self.surface.blit(message, msg_rect)
        
        msg2 = "MISSION: DESTROY ALIENS"
        message2 = self.font.render(msg2, True, RED)
        msg2_rect = message2.get_rect(center=(SCREEN_WIDTH//2, 140))
        self.surface.blit(message2, msg2_rect)
        
        # Blinking start text
        if self.attract_timer % 60 < 40:
            start = self.font.render("PRESS SPACE TO START", True, GREEN)
            start_rect = start.get_rect(center=(SCREEN_WIDTH//2, 200))
            self.surface.blit(start, start_rect)
        
        # High score
        hs = self.font.render(f"HIGH SCORE: {self.high_score}", True, WHITE)
        hs_rect = hs.get_rect(center=(SCREEN_WIDTH//2, 240))
        self.surface.blit(hs, hs_rect)
    
    def _draw_playing(self):
        """Draw playing state."""
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.surface)
        
        # Draw player
        if self.player:
            self.player.draw(self.surface)
        
        # Draw enemy bullets
        for bullet in self.enemy_bullets:
            bullet.draw(self.surface)
        
        # Draw explosions
        for explosion in self.explosions:
            explosion.draw(self.surface)
        
        # Draw HUD
        self._draw_hud()
        
        # Round transition overlay
        if self.state == GameState.ROUND_TRANSITION:
            self._draw_round_transition()
    
    def _draw_round_transition(self):
        """Draw round transition screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.surface.blit(overlay, (0, 0))
        
        text = self.font_large.render(f"ROUND {self.round_num}", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.surface.blit(text, text_rect)
    
    def _draw_game_over(self):
        """Draw game over screen."""
        # Game over text
        go = self.font_large.render("GAME OVER", True, RED)
        go_rect = go.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.surface.blit(go, go_rect)
        
        # Score
        score = self.font.render(f"SCORE: {self.score}", True, WHITE)
        score_rect = score.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.surface.blit(score, score_rect)
        
        # High score
        hs = self.font.render(f"HIGH SCORE: {self.high_score}", True, GOLD)
        hs_rect = hs.get_rect(center=(SCREEN_WIDTH//2, 180))
        self.surface.blit(hs, hs_rect)
        
        # Blinking start text
        if self.attract_timer % 60 < 40:
            start = self.font.render("PRESS SPACE TO CONTINUE", True, WHITE)
            start_rect = start.get_rect(center=(SCREEN_WIDTH//2, 230))
            self.surface.blit(start, start_rect)
    
    def _draw_hud(self):
        """Draw HUD elements."""
        # Score (top left)
        score_text = self.font_small.render(f"SCORE:{self.score}", True, WHITE)
        self.surface.blit(score_text, (5, 5))
        
        # High score (top center)
        hs_text = self.font_small.render(f"HIGH:{self.high_score}", True, WHITE)
        hs_rect = hs_text.get_rect(centerx=SCREEN_WIDTH//2, top=5)
        self.surface.blit(hs_text, hs_rect)
        
        # Lives (bottom left)
        lives_text = self.font_small.render(f"LIVES:{self.lives}", True, WHITE)
        self.surface.blit(lives_text, (5, SCREEN_HEIGHT - 12))
        
        # Round indicator (bottom center)
        round_text = self.font_small.render(f"ROUND:{self.round_num}", True, WHITE)
        round_rect = round_text.get_rect(centerx=SCREEN_WIDTH//2, top=SCREEN_HEIGHT - 12)
        self.surface.blit(round_text, round_rect)
        
        # Bonus life indicator
        if self.bonus_awarded:
            bonus = self.font_small.render("BONUS!", True, GOLD)
            bonus_rect = bonus.get_rect(centerx=SCREEN_WIDTH - 30, top=SCREEN_HEIGHT - 12)
            self.surface.blit(bonus, bonus_rect)
    
    def run(self):
        """Main game loop."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

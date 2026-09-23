"""Collision detection system."""
import pygame

def check_bullet_enemy_collisions(player_bullet, enemies, explosions):
    """Check if player bullet hits any enemy. Returns list of hit enemies."""
    if not player_bullet or player_bullet.hit:
        return []
    
    hit_enemies = []
    bullet_rect = player_bullet.get_rect()
    
    for enemy in enemies:
        if enemy.alive and bullet_rect.colliderect(enemy.rect):
            enemy.die()
            hit_enemies.append(enemy)
            player_bullet.hit = True
    
    return hit_enemies

def check_bullet_player_collisions(enemy_bullets, player):
    """Check if any enemy bullet hits player. Returns True if hit."""
    if not player.alive or player.invincible:
        return False
    
    player_rect = player.get_rect()
    for bullet in enemy_bullets:
        if bullet and not bullet.hit and bullet.get_rect().colliderect(player_rect):
            return True
    
    return False

def check_player_enemy_collisions(player, enemies):
    """Check if player collides with any enemy. Returns True if hit."""
    if not player.alive or player.invincible:
        return False
    
    player_rect = player.get_rect()
    for enemy in enemies:
        if enemy.alive and player_rect.colliderect(enemy.rect):
            return True
    
    return False

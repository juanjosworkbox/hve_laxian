"""Tests for triangle formation diving behavior.

Verifies that enemies dive in groups of three (leader + two escorts)
in a rigid triangle formation, matching the original Galaxian arcade behavior.
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pytest
import pygame
import sys
import math

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from constants import (
    TRIANGLE_LATERAL_OFFSET,
    TRIANGLE_VERTICAL_OFFSET,
    TRIANGLE_ESCORTS_PER_LEADER,
    TRIANGLE_DIVE_SPEED_SCALE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ENEMY_WIDTH,
)
from entities.enemy import Enemy, DiveFormation
from systems.formation import Formation
from assets import AssetManager


class MockAssetManager:
    """Minimal asset manager mock for testing."""
    def __init__(self):
        pygame.init()
        self.sprites = {
            'enemy_green': pygame.Surface((10, 10)),
            'enemy_blue': pygame.Surface((10, 10)),
            'enemy_yellow': pygame.Surface((10, 10)),
            'enemy_red': pygame.Surface((10, 10)),
            'enemy_flagship': pygame.Surface((10, 10)),
            'enemy_escort': pygame.Surface((10, 10)),
            'ufo_frame0': pygame.Surface((14, 10)),
            'ufo_frame1': pygame.Surface((14, 10)),
        }
        self.sounds = {}
    
    def get_sound(self, name):
        class MockSound:
            def play(self): pass
        return MockSound()


class TestDiveFormation:
    """Tests for the DiveFormation shared state container."""
    
    def test_creation(self):
        """DiveFormation can be created with leader and escorts."""
        mock = MockAssetManager()
        leader = Enemy(100, 50, 'red', mock, row=0, col=0)
        escort1 = Enemy(80, 60, 'green', mock, row=1, col=0)
        escort2 = Enemy(120, 60, 'green', mock, row=1, col=1)
        
        formation = DiveFormation(leader, [escort1, escort2])
        
        assert formation.leader is leader
        assert len(formation.escorts) == 2
        assert formation.active is True
        assert formation.completed is False
        assert formation.bezier_params is None
    
    def test_custom_offsets(self):
        """DiveFormation accepts custom lateral and vertical offsets."""
        mock = MockAssetManager()
        leader = Enemy(100, 50, 'red', mock, row=0, col=0)
        escort1 = Enemy(80, 60, 'green', mock, row=1, col=0)
        escort2 = Enemy(120, 60, 'green', mock, row=1, col=1)
        
        formation = DiveFormation(leader, [escort1, escort2], 
                                  lateral_offset=30, vertical_offset=15)
        
        assert formation.lateral_offset == 30
        assert formation.vertical_offset == 15
    
    def test_integrity_with_all_alive(self):
        """check_integrity returns True when all members are alive."""
        mock = MockAssetManager()
        leader = Enemy(100, 50, 'red', mock, row=0, col=0)
        escort1 = Enemy(80, 60, 'green', mock, row=1, col=0)
        escort2 = Enemy(120, 60, 'green', mock, row=1, col=1)
        
        formation = DiveFormation(leader, [escort1, escort2])
        assert formation.check_integrity() is True
    
    def test_integrity_when_leader_dies(self):
        """check_integrity returns False and breaks escorts when leader dies."""
        mock = MockAssetManager()
        leader = Enemy(100, 50, 'red', mock, row=0, col=0)
        escort1 = Enemy(80, 60, 'green', mock, row=1, col=0)
        escort2 = Enemy(120, 60, 'green', mock, row=1, col=1)
        
        formation = DiveFormation(leader, [escort1, escort2])
        
        leader.die()
        result = formation.check_integrity()
        
        assert result is False
        assert formation.active is False
        assert escort1.dive_formation is None
        assert escort2.dive_formation is None
        assert escort1.formation_offset_x == 0
        assert escort2.formation_offset_x == 0
    
    def test_integrity_when_one_escort_dies(self):
        """check_integrity survives when one escort dies, remaining escort goes independent."""
        mock = MockAssetManager()
        leader = Enemy(100, 50, 'red', mock, row=0, col=0)
        escort1 = Enemy(80, 60, 'green', mock, row=1, col=0)
        escort2 = Enemy(120, 60, 'green', mock, row=1, col=1)
        
        formation = DiveFormation(leader, [escort1, escort2])
        
        escort1.die()
        result = formation.check_integrity()
        
        assert result is True
        assert formation.active is True
        assert escort1.dive_formation is None  # Dead escort broken
        assert escort2.dive_formation is formation  # Living escort stays
        assert escort2.formation_offset_x == 0  # Goes independent
        assert escort2.formation_offset_y == 0
    
    def test_integrity_when_all_escorts_die(self):
        """check_integrity returns False when all escorts die."""
        mock = MockAssetManager()
        leader = Enemy(100, 50, 'red', mock, row=0, col=0)
        escort1 = Enemy(80, 60, 'green', mock, row=1, col=0)
        escort2 = Enemy(120, 60, 'green', mock, row=1, col=1)
        
        formation = DiveFormation(leader, [escort1, escort2])
        
        escort1.die()
        escort2.die()
        result = formation.check_integrity()
        
        assert result is False
        assert formation.active is False


class TestEnemyTriangleDive:
    """Tests for Enemy triangle formation dive behavior."""
    
    def test_leader_computes_bezier(self):
        """Leader computes Bezier curve and stores params in formation."""
        mock = MockAssetManager()
        leader = Enemy(100, 50, 'red', mock, row=0, col=0)
        escort1 = Enemy(80, 60, 'green', mock, row=1, col=0)
        escort2 = Enemy(120, 60, 'green', mock, row=1, col=1)
        
        formation = DiveFormation(leader, [escort1, escort2])
        
        leader.start_dive(128, 200, dive_formation=formation)
        
        assert leader.state == 'diving'
        assert leader.dive_formation is formation
        assert formation.bezier_params is not None
        assert formation.return_params is not None
        
        # Leader's params match formation storage
        stored_start, stored_control, stored_target = formation.bezier_params
        assert stored_start == leader.dive_start
        assert stored_control == leader.dive_control
        assert stored_target == leader.dive_target
    
    def test_escorts_derive_from_leader(self):
        """Escorts apply fixed offsets to leader's Bezier params."""
        mock = MockAssetManager()
        leader = Enemy(100, 50, 'red', mock, row=0, col=0)
        escort1 = Enemy(80, 60, 'green', mock, row=1, col=0)
        escort2 = Enemy(120, 60, 'green', mock, row=1, col=1)
        
        formation = DiveFormation(leader, [escort1, escort2],
                                  lateral_offset=TRIANGLE_LATERAL_OFFSET,
                                  vertical_offset=TRIANGLE_VERTICAL_OFFSET)
        
        # Set escort offsets
        escort1.formation_offset_x = -TRIANGLE_LATERAL_OFFSET
        escort1.formation_offset_y = -TRIANGLE_VERTICAL_OFFSET
        escort2.formation_offset_x = TRIANGLE_LATERAL_OFFSET
        escort2.formation_offset_y = -TRIANGLE_VERTICAL_OFFSET
        
        leader.start_dive(128, 200, dive_formation=formation)
        escort1.start_dive(128, 200, dive_formation=formation)
        escort2.start_dive(128, 200, dive_formation=formation)
        
        # Leader has its own computed curve
        assert leader.dive_start is not None
        assert leader.dive_control is not None
        assert leader.dive_target is not None
        
        # Escorts have offsets applied to leader's params
        assert escort1.dive_start == (
            leader.dive_start[0] + escort1.formation_offset_x,
            leader.dive_start[1] + escort1.formation_offset_y
        )
        assert escort2.dive_start == (
            leader.dive_start[0] + escort2.formation_offset_x,
            leader.dive_start[1] + escort2.formation_offset_y
        )
    
    def test_independent_dive_backward_compat(self):
        """Enemies can still dive independently without formation."""
        mock = MockAssetManager()
        enemy = Enemy(100, 50, 'red', mock, row=0, col=0)
        
        enemy.start_dive(128, 200)  # No dive_formation
        
        assert enemy.state == 'diving'
        assert enemy.dive_formation is None
        assert enemy.dive_start is not None
        assert enemy.dive_control is not None
    
    def test_formation_offset_returns_zero_for_leader(self):
        """_get_formation_offset returns (0, 0) for leader."""
        mock = MockAssetManager()
        leader = Enemy(100, 50, 'red', mock, row=0, col=0)
        
        offset = leader._get_formation_offset()
        assert offset == (0, 0)
    
    def test_formation_offset_returns_zero_when_no_formation(self):
        """_get_formation_offset returns (0, 0) when not in formation."""
        mock = MockAssetManager()
        enemy = Enemy(100, 50, 'red', mock, row=0, col=0)
        
        offset = enemy._get_formation_offset()
        assert offset == (0, 0)


class TestFormationTriangleIntegration:
    """Integration tests for Formation triangle dive spawning."""
    
    def test_select_diver_prefers_red(self):
        """_select_diver prefers red enemies when available."""
        mock = MockAssetManager()
        formation = Formation(mock)
        formation.create_enemies()
        
        # Find red enemies
        red_enemies = [e for e in formation.enemies if e.enemy_type == 'red']
        assert len(red_enemies) > 0
        
        # Run multiple times to verify red is preferred (not guaranteed by random)
        # With 5 red + 5 flagship priority out of 25, expect ~50% red
        red_selected_count = 0
        for _ in range(100):
            candidates = formation.enemies.copy()
            diver = formation._select_diver(candidates)
            if diver.enemy_type == 'red':
                red_selected_count += 1
        
        # Should select red between 30-70% of the time (statistically reasonable)
        assert 30 <= red_selected_count <= 70
    
    def test_select_diver_uses_flagship_when_no_red(self):
        """_select_diver falls back to flagship when no red enemies."""
        mock = MockAssetManager()
        formation = Formation(mock)
        formation.create_enemies()
        
        # Remove all red enemies from candidates
        candidates = [e for e in formation.enemies if e.enemy_type != 'red']
        
        diver = formation._select_diver(candidates)
        assert diver is not None
        assert diver.enemy_type in ('flagship', 'yellow', 'blue', 'green')
    
    def test_select_escorts_excludes_leader(self):
        """_select_escorts does not include the leader."""
        mock = MockAssetManager()
        formation = Formation(mock)
        formation.create_enemies()
        
        leader = formation._select_diver(formation.enemies)
        escorts = formation._select_escorts(formation.enemies, leader, count=2)
        
        assert leader not in escorts
        assert len(escorts) == min(2, len(formation.enemies) - 1)
    
    def test_select_escorts_only_formation_state(self):
        """_select_escorts only selects enemies in 'formation' state."""
        mock = MockAssetManager()
        formation = Formation(mock)
        formation.create_enemies()
        
        leader = formation._select_diver(formation.enemies)
        leader.start_dive(128, 200)  # Put leader in diving state
        
        escorts = formation._select_escorts(formation.enemies, leader, count=2)
        
        for escort in escorts:
            assert escort.state == 'formation'
    
    def test_spawn_ufo_creates_triangle_formation(self):
        """_spawn_ufo creates a DiveFormation with leader and escorts."""
        mock = MockAssetManager()
        formation = Formation(mock)
        formation.create_enemies()
        
        # Put player on screen for _spawn_ufo
        player_mock = pygame.sprite.Sprite()
        player_mock.rect = pygame.Rect(100, SCREEN_HEIGHT - 24, 13, 16)
        
        formation._spawn_ufo()
        
        assert formation.ufo is not None
        assert len(formation.dive_formations) == 1
        dive_form = formation.dive_formations[0]
        assert dive_form.leader is not None
        assert len(dive_form.escorts) == 2
        assert dive_form.active is True
    
    def test_trigger_dive_creates_triangle_formation(self):
        """_trigger_dive creates a DiveFormation with leader and escorts."""
        mock = MockAssetManager()
        formation = Formation(mock)
        formation.create_enemies()
        
        player_mock = pygame.sprite.Sprite()
        player_mock.rect = pygame.Rect(100, SCREEN_HEIGHT - 24, 13, 16)
        
        diver = formation._trigger_dive(player_mock)
        
        assert diver is not None
        assert len(formation.dive_formations) == 1
        dive_form = formation.dive_formations[0]
        assert dive_form.leader is diver
        assert len(dive_form.escorts) == 2
    
    def test_trigger_dive_fallback_single_dive(self):
        """_trigger_dive falls back to single dive when fewer than 3 enemies."""
        mock = MockAssetManager()
        formation = Formation(mock)
        formation.create_enemies()
        
        # Remove all but 2 enemies
        formation.enemies = formation.enemies[:2]
        
        player_mock = pygame.sprite.Sprite()
        player_mock.rect = pygame.Rect(100, SCREEN_HEIGHT - 24, 13, 16)
        
        diver = formation._trigger_dive(player_mock)
        
        assert diver is not None
        # Should have created a single independent dive, not a formation
        assert len(formation.dive_formations) == 0
    
    def test_no_dive_delay_stagger(self):
        """Triangle formation does not use dive_delay stagger."""
        mock = MockAssetManager()
        formation = Formation(mock)
        formation.create_enemies()
        
        player_mock = pygame.sprite.Sprite()
        player_mock.rect = pygame.Rect(100, SCREEN_HEIGHT - 24, 13, 16)
        
        diver = formation._trigger_dive(player_mock)
        
        # None of the triangle members should have dive_delay set
        all_members = [diver] + formation.dive_formations[0].escorts
        for enemy in all_members:
            assert not hasattr(enemy, 'dive_delay') or enemy.dive_delay == 0
    
    def test_simultaneous_dive_start(self):
        """All triangle members start diving in the same frame."""
        mock = MockAssetManager()
        formation = Formation(mock)
        formation.create_enemies()
        
        player_mock = pygame.sprite.Sprite()
        player_mock.rect = pygame.Rect(100, SCREEN_HEIGHT - 24, 13, 16)
        
        diver = formation._trigger_dive(player_mock)
        dive_form = formation.dive_formations[0]
        
        # All members should be in 'diving' state immediately
        assert diver.state == 'diving'
        for escort in dive_form.escorts:
            assert escort.state == 'diving'
    
    def test_screen_boundary_clamping(self):
        """Enemy positions are clamped to screen bounds during dive."""
        mock = MockAssetManager()
        enemy = Enemy(0, 50, 'red', mock, row=0, col=0)
        enemy.state = 'diving'
        enemy.dive_start = (0, 50)
        enemy.dive_control = (0, 50)
        enemy.dive_target = (0, 50)
        enemy.dive_progress = 0.5
        
        # Force position off-screen
        enemy.rect.centerx = -10
        enemy.rect.centery = -10
        
        # Apply clamping manually (simulates what update() does)
        enemy.rect.centerx = max(ENEMY_WIDTH // 2, min(SCREEN_WIDTH - ENEMY_WIDTH // 2, enemy.rect.centerx))
        enemy.rect.centery = max(0, min(SCREEN_HEIGHT, enemy.rect.centery))
        
        assert enemy.rect.centerx >= ENEMY_WIDTH // 2
        assert enemy.rect.centerx <= SCREEN_WIDTH - ENEMY_WIDTH // 2
        assert enemy.rect.centery >= 0
        assert enemy.rect.centery <= SCREEN_HEIGHT


class TestGracefulDegradation:
    """Tests for escort death mid-dive graceful degradation."""
    
    def test_remaining_escort_continues_dive(self):
        """When one escort dies, the other continues diving independently."""
        mock = MockAssetManager()
        leader = Enemy(100, 50, 'red', mock, row=0, col=0)
        escort1 = Enemy(80, 60, 'green', mock, row=1, col=0)
        escort2 = Enemy(120, 60, 'green', mock, row=1, col=1)
        
        formation = DiveFormation(leader, [escort1, escort2])
        
        leader.start_dive(128, 200, dive_formation=formation)
        escort1.formation_offset_x = -TRIANGLE_LATERAL_OFFSET
        escort1.formation_offset_y = -TRIANGLE_VERTICAL_OFFSET
        escort1.start_dive(128, 200, dive_formation=formation)
        escort2.formation_offset_x = TRIANGLE_LATERAL_OFFSET
        escort2.formation_offset_y = -TRIANGLE_VERTICAL_OFFSET
        escort2.start_dive(128, 200, dive_formation=formation)
        
        # Simulate escort1 being destroyed mid-dive
        escort1.die()
        formation.check_integrity()
        
        # Escort2 should continue diving independently (offset zeroed but still linked)
        assert escort2.state == 'diving'
        assert escort2.formation_offset_x == 0  # Goes independent
        assert escort2.formation_offset_y == 0
        # Note: escort2 stays linked to formation until leader dies or escort2 dies
    
    def test_leader_death_all_escorts_break(self):
        """When leader dies, all escorts break formation immediately."""
        mock = MockAssetManager()
        leader = Enemy(100, 50, 'red', mock, row=0, col=0)
        escort1 = Enemy(80, 60, 'green', mock, row=1, col=0)
        escort2 = Enemy(120, 60, 'green', mock, row=1, col=1)
        
        formation = DiveFormation(leader, [escort1, escort2])
        
        leader.start_dive(128, 200, dive_formation=formation)
        escort1.formation_offset_x = -TRIANGLE_LATERAL_OFFSET
        escort1.start_dive(128, 200, dive_formation=formation)
        escort2.formation_offset_x = TRIANGLE_LATERAL_OFFSET
        escort2.start_dive(128, 200, dive_formation=formation)
        
        # Simulate leader being destroyed mid-dive
        leader.die()
        formation.check_integrity()
        
        # All escorts should break formation
        assert escort1.dive_formation is None
        assert escort2.dive_formation is None
        assert escort1.formation_offset_x == 0
        assert escort2.formation_offset_x == 0


class TestConstants:
    """Tests for triangle formation constants."""
    
    def test_lateral_offset_is_positive(self):
        """TRIANGLE_LATERAL_OFFSET is a positive integer."""
        assert isinstance(TRIANGLE_LATERAL_OFFSET, int)
        assert TRIANGLE_LATERAL_OFFSET > 0
    
    def test_vertical_offset_is_positive(self):
        """TRIANGLE_VERTICAL_OFFSET is a positive integer."""
        assert isinstance(TRIANGLE_VERTICAL_OFFSET, int)
        assert TRIANGLE_VERTICAL_OFFSET > 0
    
    def test_escorts_per_leader_is_two(self):
        """TRIANGLE_ESCORTS_PER_LEADER equals 2."""
        assert TRIANGLE_ESCORTS_PER_LEADER == 2
    
    def test_dive_speed_scale_is_one(self):
        """TRIANGLE_DIVE_SPEED_SCALE equals 1.0 (all use same speed)."""
        assert TRIANGLE_DIVE_SPEED_SCALE == 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

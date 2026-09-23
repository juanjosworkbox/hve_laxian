"""Tests for the enemy formation system."""

import pytest
from constants import (
    FORMATION_ROWS, FORMATION_COLS, TOTAL_ENEMIES,
    FORMATION_TOP, FORMATION_SPACING_X, FORMATION_SPACING_Y,
    FORMATION_SPEED_BASE, DIVE_INTERVAL_BASE, MAX_DIVES_PER_ROUND,
    SCREEN_WIDTH,
)


class TestEnemyTypeAssignment:
    """Tests for enemy type assignment by row."""

    def test_enemy_type_assignment_row_0_flagships(self, formation):
        """Row 0 (top) should be 5 flagships."""
        for col in range(FORMATION_COLS):
            idx = 0 * FORMATION_COLS + col
            assert formation.enemy_types[idx] == 'flagship', \
                f"Row {col} should be flagship"

    def test_enemy_type_assignment_row_1_red(self, formation):
        """Row 1 should be 5 red enemies."""
        for col in range(FORMATION_COLS):
            idx = 1 * FORMATION_COLS + col
            assert formation.enemy_types[idx] == 'red', \
                f"Row {col} should be red"

    def test_enemy_type_assignment_row_2_yellow(self, formation):
        """Row 2 should be 5 yellow enemies."""
        for col in range(FORMATION_COLS):
            idx = 2 * FORMATION_COLS + col
            assert formation.enemy_types[idx] == 'yellow', \
                f"Row {col} should be yellow"

    def test_enemy_type_assignment_row_3_blue(self, formation):
        """Row 3 should be 5 blue enemies."""
        for col in range(FORMATION_COLS):
            idx = 3 * FORMATION_COLS + col
            assert formation.enemy_types[idx] == 'blue', \
                f"Row {col} should be blue"

    def test_enemy_type_assignment_row_4_green(self, formation):
        """Row 4 (bottom) should be 5 green enemies."""
        for col in range(FORMATION_COLS):
            idx = 4 * FORMATION_COLS + col
            assert formation.enemy_types[idx] == 'green', \
                f"Row {col} should be green"

    def test_enemy_type_assignment_total_25(self, formation):
        """Should have 25 enemy types total."""
        assert len(formation.enemy_types) == TOTAL_ENEMIES


class TestFormationCreation:
    """Tests for enemy formation creation."""

    def test_create_enemies_returns_list(self, formation):
        """create_enemies() should return a list."""
        assert isinstance(formation.enemies, list)

    def test_create_enemies_count(self, formation):
        """create_enemies() should create 25 enemies."""
        assert len(formation.enemies) == TOTAL_ENEMIES

    def test_create_enemies_positions(self, formation):
        """Enemies should be positioned in a grid."""
        # Check first enemy (row 0, col 0)
        first = formation.enemies[0]
        expected_x = (256 - (FORMATION_COLS - 1) * FORMATION_SPACING_X) / 2
        expected_y = FORMATION_TOP
        assert first.rect.x == expected_x
        assert first.rect.y == expected_y

    def test_create_enemies_reset_offset(self, formation):
        """create_enemies() should reset formation_offset to 0."""
        formation.formation_offset = 50
        formation.create_enemies()
        assert formation.formation_offset == 0

    def test_create_enemies_dives_reset(self, formation):
        """create_enemies() should reset dives counter."""
        formation.dives_this_round = 10
        formation.create_enemies()
        assert formation.dives_this_round == 0

    def test_create_enemies_v_shape(self, formation):
        """Enemies should be in V-shape (bottom rows offset inward)."""
        # Enemies in the same column should have different x based on row V-offset
        # col=0 enemies: x = start_x + row * 4 (col * SPACING_X = 0)
        row0_col0_x = formation.enemies[0].rect.x        # start_x
        row4_col0_x = formation.enemies[4 * FORMATION_COLS].rect.x  # start_x + 16
        expected_v_offset = 4 * 4  # row 4 * 4
        assert row4_col0_x == row0_col0_x + expected_v_offset, \
            "Row 4 should be offset inward by 16 pixels vs row 0"

        # Enemies in the same row should have consistent spacing
        row0_col1_x = formation.enemies[1].rect.x        # start_x + 20
        assert row0_col1_x == row0_col0_x + FORMATION_SPACING_X


class TestFormationMovement:
    """Tests for formation movement mechanics."""

    def test_formation_moves_right(self, formation):
        """Formation should move right each frame."""
        initial_offset = formation.formation_offset
        formation.update(round_num=1)
        assert formation.formation_offset > initial_offset

    def test_formation_bounces_left_edge(self, formation):
        """Formation should reverse direction at left edge (-20)."""
        # Start inside boundary, moving left. After enough updates, offset < -20 triggers direction flip.
        formation.formation_offset = -19
        formation.formation_direction = -1  # moving left
        # At round 1, speed = 0.6 per frame. -19 - 0.6 = -19.6, -19.6 - 0.6 = -20.2 (< -20, flips)
        for _ in range(10):
            formation.update(round_num=1)
        assert formation.formation_direction == 1, \
            f"Direction should flip to 1 (right) after crossing left edge, got {formation.formation_direction}"

    def test_formation_bounces_right_edge(self, formation):
        """Formation should reverse direction at right edge (20)."""
        # Manually set offset to 19 and move right
        formation.formation_offset = 19
        formation.formation_direction = 1
        # Multiple updates to push past 20
        for _ in range(10):
            formation.update(round_num=1)
        assert formation.formation_direction == -1

    def test_formation_hover_oscillates(self, formation):
        """Hover offset should oscillate between -3 and 3."""
        initial_hover = formation.hover_offset
        for _ in range(20):
            formation.update(round_num=1)
        # Hover should have changed
        assert formation.hover_offset != initial_hover
        # Hover should stay within bounds
        assert abs(formation.hover_offset) <= 3


class TestDifficultyScaling:
    """Tests for difficulty scaling with round number."""

    def test_formation_speed_scales_with_round(self, formation):
        """Formation speed should increase with round number."""
        formation.update(round_num=1)
        speed_1 = formation.formation_speed

        formation.update(round_num=5)
        speed_5 = formation.formation_speed

        assert speed_5 > speed_1, \
            f"Speed at round 5 ({speed_5}) should exceed round 1 ({speed_1})"

    def test_max_dives_scales_with_round(self, formation):
        """Max dives should increase with round number."""
        formation.update(round_num=1)
        max_1 = formation.max_dives

        formation.update(round_num=5)
        max_5 = formation.max_dives

        assert max_5 > max_1, \
            f"Max dives at round 5 ({max_5}) should exceed round 1 ({max_1})"

    def test_dive_timer_decreases_with_round(self, formation):
        """Dive timer interval should decrease with round number."""
        formation.update(round_num=1)
        timer_1 = formation.dive_timer

        formation.update(round_num=5)
        timer_5 = formation.dive_timer

        assert timer_5 < timer_1, \
            f"Dive timer at round 5 ({timer_5}) should be less than round 1 ({timer_1})"

    def test_formation_speed_minimum(self, formation):
        """Formation speed should never go below FORMATION_SPEED_BASE."""
        formation.update(round_num=1)
        assert formation.formation_speed >= FORMATION_SPEED_BASE

    def test_dive_timer_minimum_60(self, formation):
        """Dive timer should never go below 60."""
        formation.update(round_num=20)  # High round
        assert formation.dive_timer >= 60


class TestDiveLogic:
    """Tests for dive attack triggering."""

    def test_try_dive_max_reached_returns_none(self, formation, mock_player):
        """Should return None when max dives reached."""
        formation.max_dives = 2
        formation.dives_this_round = 2
        result = formation.try_dive(mock_player)
        assert result is None

    def test_try_dive_timer_not_ready(self, formation, mock_player):
        """Should return None when dive timer not expired."""
        formation.dive_timer = 100  # Far from ready
        result = formation.try_dive(mock_player)
        assert result is None

    def test_try_dive_no_formation_enemies(self, formation, mock_player):
        """Should return None when no alive formation enemies."""
        # Kill all enemies
        for enemy in formation.enemies:
            enemy.alive = False
            enemy.state = 'diving'
        formation.dive_timer = 0  # Ready to dive
        result = formation.try_dive(mock_player)
        assert result is None

    def test_try_dive_success(self, formation, mock_player):
        """Should trigger a dive when conditions are met."""
        formation.dive_timer = 0
        formation.dives_this_round = 0
        # All enemies alive and in formation
        for enemy in formation.enemies:
            enemy.alive = True
            enemy.state = 'formation'

        result = formation.try_dive(mock_player)
        assert result is not None, "Should return a diver"
        assert result.state == 'diving', "Diver should be in diving state"

    def test_try_dive_increments_counter(self, formation, mock_player):
        """Should increment dives_this_round counter."""
        initial_dives = formation.dives_this_round
        formation.dive_timer = 0
        formation.dives_this_round = 0
        for enemy in formation.enemies:
            enemy.alive = True
            enemy.state = 'formation'

        formation.try_dive(mock_player)
        assert formation.dives_this_round == initial_dives + 1

    def test_try_dive_prefers_red_flagship(self, formation, mock_player):
        """Should prefer red/flagship enemies to dive."""
        formation.dive_timer = 0
        formation.dives_this_round = 0
        for enemy in formation.enemies:
            enemy.alive = True
            enemy.state = 'formation'

        # Set all to green/blue (non-priority) except one red
        priority_found = False
        for _ in range(5):
            result = formation.try_dive(mock_player)
            if result and result.enemy_type in ('red', 'flagship'):
                priority_found = True
                break

        assert priority_found, "Should prefer red/flagship enemies"

    def test_try_dive_fallback_to_random(self, formation, mock_player):
        """Should fall back to random when no priority enemies."""
        formation.dive_timer = 0
        formation.dives_this_round = 0

        # Kill all flagships and reds
        for enemy in formation.enemies:
            if enemy.enemy_type in ('flagship', 'red'):
                enemy.alive = False
            else:
                enemy.alive = True
                enemy.state = 'formation'

        result = formation.try_dive(mock_player)
        assert result is not None, "Should still find a diver"
        assert result.enemy_type in ('yellow', 'blue', 'green')


class TestAliveCount:
    """Tests for alive enemy counting."""

    def test_alive_count_all_alive(self, formation):
        """alive_count() should return total when all alive."""
        count = formation.alive_count()
        assert count == TOTAL_ENEMIES

    def test_alive_count_some_dead(self, formation):
        """alive_count() should count only alive enemies."""
        for i in range(5):
            formation.enemies[i].alive = False
        count = formation.alive_count()
        assert count == TOTAL_ENEMIES - 5

    def test_alive_count_zero(self, formation):
        """alive_count() should return 0 when all dead."""
        for enemy in formation.enemies:
            enemy.alive = False
        count = formation.alive_count()
        assert count == 0

    def test_alive_count_dead_enemies_excluded(self, formation):
        """Dead enemies should not be counted."""
        formation.enemies[0].alive = False
        formation.enemies[1].alive = False
        formation.enemies[2].state = 'diving'
        count = formation.alive_count()
        assert count == TOTAL_ENEMIES - 2


class TestFormationReset:
    """Tests for formation reset."""

    def test_reset_clears_offset(self, formation):
        """reset() should clear formation_offset."""
        formation.formation_offset = 50
        formation.reset(round_num=1)
        assert formation.formation_offset == 0

    def test_reset_clears_hover(self, formation):
        """reset() should clear hover_offset."""
        formation.hover_offset = 5
        formation.reset(round_num=1)
        assert formation.hover_offset == 0

    def test_reset_clears_dives(self, formation):
        """reset() should clear dives counter."""
        formation.dives_this_round = 10
        formation.reset(round_num=1)
        assert formation.dives_this_round == 0

    def test_reset_clears_dive_timer(self, formation):
        """reset() should reset dive timer."""
        formation.dive_timer = 10
        formation.reset(round_num=1)
        assert formation.dive_timer == DIVE_INTERVAL_BASE

    def test_reset_sets_round_num(self, formation):
        """reset() should set round_num."""
        formation.reset(round_num=5)
        assert formation.round_num == 5

    def test_reset_clears_direction(self, formation):
        """reset() should reset direction flags."""
        formation.formation_direction = -1
        formation.hover_direction = -1
        formation.reset(round_num=1)
        assert formation.formation_direction == 1
        assert formation.hover_direction == 1

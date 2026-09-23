<!-- markdownlint-disable-file -->
# System Tests Implementation Plan

**Date**: 2026-09-22
**Status**: Ready for Implementation

---

## User Requests

1. **Add System Tests for Formation and Starfield** — Test enemy formation movement, dive triggers, difficulty scaling, and starfield update/draw behavior

---

## Overview and Objectives

Create dedicated test modules for the two game systems that currently have zero test coverage:
- `Formation` — enemy formation movement, hover oscillation, edge bouncing, difficulty scaling, dive triggers, enemy type assignment, alive counting, and reset
- `Starfield` — star generation, position updates, speed variation, brightness, wrap-around at screen edges, and drawing

---

## Context Summary

### Discovered Instructions Files

| File | Relevance |
|------|-----------|
| `.github/copilot-instructions.md` | Python environment (venv), requirements.txt, .copilot-tracking conventions |
| `hve-core/commit-message.instructions.md` | Commit message format (used at completion) |
| `hve-core/markdown.instructions.md` | Markdown formatting |
| `hve-core/writing-style.instructions.md` | Writing style conventions |
| `coding-standards/python-script.instructions.md` | Python coding conventions |
| `coding-standards/python-tests.instructions.md` | Python test conventions |

### Discovered Skills

| Skill | Relevant |
|-------|----------|
| `python-fact-grounded-coding` | Python code validation |
| `pylance-refactoring` | Python refactoring utilities |

### Codebase Architecture

**Formation system** (`systems/formation.py`):
- Manages enemy formation side-to-side movement with hover oscillation
- Difficulty scaling: formation_speed, max_dives, dive_timer all increase with round_num
- Edge bouncing: ±20 pixel bounds on formation_offset
- Dive priority: prefers red/flagship enemies
- Enemy type assignment: row-based (flagships top, red, yellow, blue, green bottom)

**Starfield system** (`systems/starfield.py`):
- Generates 80 stars with random positions, speeds (0.5/1/1.5/2), and brightness (100-255)
- Updates star positions each frame, wraps at SCREEN_HEIGHT
- Draws stars as 1x1 pixel rectangles at brightness level

### Prior Research

| Research Document | Key Findings |
|-------------------|--------------|
| `integration-testing-research.md` | pytest recommended, dummy driver for logic tests |
| `pygame-rendering-tests.md` (subagent) | software driver for rendering tests |
| `galaxian-research.md` | Full game architecture overview |

---

## Implementation Checklist

### Phase 1: Create Test Directory and Shared Fixtures
- [ ] Phase 1.1: Create `tests/test_systems/` directory
- [ ] Phase 1.2: Create `tests/test_systems/__init__.py`
- [ ] Phase 1.3: Create `tests/test_systems/conftest.py` with shared fixtures

**Dependencies**: None
**Parallelizable**: false

### Phase 2: Formation System Tests
- [ ] Phase 2.1: Create `tests/test_systems/test_formation.py`

**Dependencies**: Phase 1 (fixtures)
**Parallelizable**: false

### Phase 3: Starfield System Tests
- [ ] Phase 3.1: Create `tests/test_systems/test_starfield.py`

**Dependencies**: Phase 1 (fixtures)
**Parallelizable**: false

---

## Dependencies

### Existing Dependencies (No Changes Required)
- `pytest` — test framework
- `numpy` — pixel array operations (if needed)
- `pygame` — rendering engine

### No New Dependencies Required

---

## Success Criteria

1. **All test files created** in `tests/test_systems/` with proper structure
2. **Tests run successfully** with pytest in the project's venv
3. **Tests are importable** without display hardware (headless compatible)
4. **Tests verify Formation**:
   - Enemy type assignment (5 rows × 5 cols)
   - Formation movement (side-to-side, hover oscillation)
   - Edge bouncing (±20 bounds)
   - Difficulty scaling (speed, max_dives, dive_timer)
   - Dive trigger logic (priority selection, max dives check)
   - alive_count() accuracy
   - reset() clearing state
5. **Tests verify Starfield**:
   - 80 stars generated
   - Star properties (position, speed, brightness ranges)
   - Position update (y += speed)
   - Wrap-around at SCREEN_HEIGHT
   - Drawing (1x1 pixel rectangles)

---

## Implementation Details

### File: `tests/test_systems/__init__.py`
- Empty file to mark test_systems as a Python package

### File: `tests/test_systems/conftest.py`
- Set `SDL_VIDEODRIVER=dummy` at module level (BEFORE any pygame imports)
- Pytest fixtures:
  - `pygame_init` — session-scoped, initializes pygame and mixer
  - `asset_manager` — provides AssetManager instance
  - `formation` — provides fresh Formation instance
  - `starfield` — provides fresh Starfield instance
  - `mock_player` — provides a mock player rect for dive tests

### File: `tests/test_systems/test_formation.py`
- Test enemy type assignment:
  - `test_enemy_type_assignment_row_0_flagships` — 5 flagships in row 0
  - `test_enemy_type_assignment_row_4_green` — 5 green in row 4
  - `test_enemy_type_assignment_total_25` — 25 enemies total
- Test formation creation:
  - `test_create_enemies_returns_list` — returns list of Enemy objects
  - `test_create_enemies_count` — creates 25 enemies
  - `test_create_enemies_positions` — enemies in formation grid
  - `test_create_enemies_reset_offset` — formation_offset = 0
- Test formation movement:
  - `test_formation_moves_right` — formation_offset increases
  - `test_formation_bounces_left_edge` — direction reverses at -20
  - `test_formation_bounces_right_edge` — direction reverses at 20
  - `test_formation_hover_oscillates` — hover_offset oscillates ±3
- Test difficulty scaling:
  - `test_formation_speed_scales_with_round` — speed increases per round
  - `test_max_dives_scales_with_round` — max_dives increases per round
  - `test_dive_timer_decreases_with_round` — dive_interval decreases per round
- Test dive logic:
  - `test_try_dive_max_reached_returns_none` — returns None when max dives reached
  - `test_try_dive_timer_not_ready` — returns None when timer not expired
  - `test_try_dive_no_formation_enemies` — returns None when no alive formation enemies
  - `test_try_dive_prefers_red_flagship` — priority given to red/flagship
  - `test_try_dive_success` — triggers dive and increments counter
- Test alive count:
  - `test_alive_count` — counts only alive enemies
  - `test_alive_count_zero` — returns 0 when all dead
- Test reset:
  - `test_reset_clears_state` — resets offset, timer, dives counter

### File: `tests/test_systems/test_starfield.py`
- Test star generation:
  - `test_starfield_generates_80_stars` — exactly 80 stars
  - `test_star_positions_in_bounds` — all x in [0, 255], y in [0, 287]
  - `test_star_speeds_valid` — speeds in [0.5, 1, 1.5, 2]
  - `test_star_brightness_range` — brightness in [100, 255]
- Test star update:
  - `test_star_y_increases` — y += speed each update
  - `test_star_wraps_at_bottom` — y resets to 0 when > SCREEN_HEIGHT
  - `test_star_x_resets_on_wrap` — x randomized on wrap
  - `test_offset_y_increases` — offset_y increases by 0.5
- Test star drawing:
  - `test_starfield_draws_1x1_pixels` — draws 1x1 rectangles
  - `test_starfield_draws_correct_brightness` — pixel color matches brightness

---

## Planning Log

### Discrepancies
- None identified. Research provides sufficient detail for implementation.

### Implementation Paths Considered
1. **Single test file** vs **multiple test files** — Chose multiple files (formation, starfield) for organization
2. **Shared conftest.py** vs **separate conftest.py** — Chose shared conftest.py since both systems use pygame

### Suggested Follow-on Work
- Add entity behavior logic tests (Player, Enemy, Bullet, Explosion update methods)
- Add full game loop integration tests
- Add edge case and boundary tests
- Consider GameState enum refactoring

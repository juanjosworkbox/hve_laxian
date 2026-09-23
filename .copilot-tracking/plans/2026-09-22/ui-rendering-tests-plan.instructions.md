<!-- markdownlint-disable-file -->
# UI/Rendering Tests Implementation Plan

**Date**: 2026-09-22
**Status**: Ready for Implementation

---

## User Requests

1. **Add UI/Rendering Tests** — Test drawing functions, sprite blitting, and visual elements (requires non-headless pygame)
   - Source: `/rpi-plan` command
   - Requirement: Non-headless pygame (SDL_VIDEODRIVER=software instead of dummy)

---

## Overview and Objectives

Create a comprehensive test suite for the Galaxian game's rendering pipeline, covering:
- Game state draw methods (ATTRACT, PLAYING, ROUND_TRANSITION, GAME_OVER)
- Entity sprite blitting (Player, Enemy, Bullet, Explosion)
- Text rendering (HUD, title screens, overlays)
- Sprite generation verification (dimensions, animation frames, colors)
- Surface scaling and color preservation

**Critical constraint**: Rendering tests require `SDL_VIDEODRIVER=software` (not `dummy`), as the dummy driver disables all video operations.

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

| Skill | Relevance |
|-------|-----------|
| `python-fact-grounded-coding` | Python code validation |
| `pylance-refactoring` | Python refactoring utilities |
| `chronicle` | Session history analysis |

### Codebase Architecture

**Game rendering pipeline**:
- `Game.surface` (256x288) — offscreen native resolution surface
- `Game.screen` (512x564) — display surface (scaled from surface)
- `Game.draw()` — clears surface, calls state-specific `_draw_*()` methods, scales to screen, flips display
- `Entity.draw(screen)` — all entities blit their sprites to the provided screen

**Current test state**:
- `tests/test_integration.py` — uses `SDL_VIDEODRIVER=dummy`, 6+ integration tests
- No pytest fixtures for rendering tests
- No separate rendering test module

### Prior Research

| Research Document | Key Findings |
|-------------------|--------------|
| `integration-testing-research.md` | pytest recommended, dummy driver for logic tests |
| `pygame-rendering-tests.md` (subagent) | software driver for rendering tests, surfarray for pixel verification |

---

## Implementation Checklist

### Phase 1: Create Test Directory Structure
- [ ] Phase 1.1: Create `tests/test_rendering/` directory
- [ ] Phase 1.2: Create `tests/test_rendering/__init__.py`
- [ ] Phase 1.3: Create `tests/test_rendering/conftest.py` with software driver fixtures

**Dependencies**: None
**Parallelizable**: Partial (directories can be created in parallel, but conftest.py depends on understanding fixtures)

### Phase 2: Asset/Sprite Tests
- [ ] Phase 2.1: Create `tests/test_rendering/test_sprites.py` — verify sprite dimensions, animation frames, colors

**Dependencies**: Phase 1 (fixtures)
**Parallelizable**: false

### Phase 3: Entity Draw Tests
- [ ] Phase 3.1: Create `tests/test_rendering/test_blitting.py` — verify entity draw methods blit sprites correctly

**Dependencies**: Phase 1 (fixtures)
**Parallelizable**: false (depends on Phase 1 only)

### Phase 4: Game Draw Method Tests
- [ ] Phase 4.1: Create `tests/test_rendering/test_draw_methods.py` — verify Game.draw() state methods render correctly

**Dependencies**: Phase 1 (fixtures)
**Parallelizable**: false (depends on Phase 1 only)

### Phase 5: Text Rendering Tests
- [ ] Phase 5.1: Create `tests/test_rendering/test_text_rendering.py` — verify font rendering, HUD text, title text

**Dependencies**: Phase 1 (fixtures)
**Parallelizable**: false (depends on Phase 1 only)

### Phase 6: Surface Scaling Tests
- [ ] Phase 6.1: Create `tests/test_rendering/test_surfaces.py` — verify surface creation, scaling, color preservation

**Dependencies**: Phase 1 (fixtures)
**Parallelizable**: false (depends on Phase 1 only)

---

## Dependencies

### Existing Dependencies (No Changes Required)
- `pytest` — test framework
- `numpy` — pixel array operations (`pygame.surfarray` returns numpy arrays)
- `pygame` — rendering engine

### No New Dependencies Required

---

## Success Criteria

1. **All test files created** in `tests/test_rendering/` with proper structure
2. **Software driver fixture** properly configured (SDL_VIDEODRIVER=software)
3. **Pixel verification helpers** available via pytest fixtures (surfarray access, color checking)
4. **Tests verify rendering** for:
   - All 4 game states (ATTRACT, PLAYING, ROUND_TRANSITION, GAME_OVER)
   - All 4 entity types (Player, Enemy, Bullet, Explosion)
   - HUD elements (score, lives, round, high score)
   - Sprite generation (dimensions, animation frames, colors)
   - Surface scaling (dimensions, color preservation)
5. **Tests run successfully** with pytest in the project's venv
6. **Tests are importable** without display hardware (headless compatible)

---

## Implementation Details

### File: `tests/test_rendering/__init__.py`
- Empty file to mark test_rendering as a Python package

### File: `tests/test_rendering/conftest.py`
- Set `SDL_VIDEODRIVER=software` at module level (BEFORE imports that trigger pygame.init())
- Pytest fixtures:
  - `pygame_init` — session-scoped, initializes pygame and mixer
  - `asset_manager` — provides AssetManager instance
  - `game` — provides fresh Game instance with temp high-score directory
  - `black_surface` — provides 256x288 black surface for testing
  - `sample_sprite` — provides sample enemy sprite
  - `surface_array` — helper fixture for converting surface to numpy array
  - `pixel_checker` — helper class for pixel-level assertions

### File: `tests/test_rendering/test_sprites.py`
- Test sprite generation from AssetManager:
  - `test_player_sprite_dimensions` — 12x12
  - `test_enemy_sprite_animation_frames` — 2 frames, 10x10 each
  - `test_flagship_sprite_dimensions` — 14x14
  - `test_escort_sprite_dimensions` — verify dimensions
  - `test_bullet_sprite_dimensions` — player bullet 2x6, enemy bullet 2x4
  - `test_explosion_sprite_dimensions` — verify frames
  - `test_star_sprite_exists` — star UI sprite exists
  - `test_all_sprites_have_dimensions` — assert all sprites have width/height > 0

### File: `tests/test_rendering/test_blitting.py`
- Test entity draw methods:
  - `test_player_draw_blits_sprite` — player alive, not invincible, sprite appears on surface
  - `test_player_draw_skips_when_dead` — player dead, no pixels added to surface
  - `test_player_draw_blinks_when_invincible` — invincible player blinks (visible/hidden by timer)
  - `test_enemy_draw_blits_sprite` — enemy alive, sprite appears with correct color
  - `test_enemy_draw_skips_when_dead` — enemy dead, no pixels added
  - `test_bullet_draw_blits_sprite` — bullet active, sprite appears
  - `test_bullet_draw_skips_when_hit` — bullet hit, no pixels added
  - `test_explosion_draw_animation` — explosion frames advance, pixels present

### File: `tests/test_rendering/test_draw_methods.py`
- Test Game.draw() and _draw_*() methods:
  - `test_game_draw_attract_populates_surface` — ATTRACT state renders title text
  - `test_game_draw_playing_shows_entities` — PLAYING state renders player, enemies, bullets
  - `test_game_draw_round_transition_shows_overlay` — ROUND_TRANSITION renders semi-transparent overlay + text
  - `test_game_draw_game_over_shows_text` — GAME_OVER renders "GAME OVER" in red
  - `test_game_draw_scales_surface_to_screen` — screen is scaled version of surface
  - `test_game_draw_dimensions` — surface 256x288, screen 512x564

### File: `tests/test_rendering/test_text_rendering.py`
- Test font rendering:
  - `test_font_small_render_score` — score text renders with non-black pixels
  - `test_font_small_render_lives` — lives text renders with non-black pixels
  - `test_font_small_render_round` — round text renders with non-black pixels
  - `test_font_large_render_title` — large font renders "GALAXIAN"
  - `test_font_render_dimensions_match_font_size` — rendered width matches font.size()
  - `test_hud_text_positions` — HUD text appears at expected screen positions

### File: `tests/test_rendering/test_surfaces.py`
- Test surface operations:
  - `test_surface_creation_dimensions` — pygame.Surface creates with correct dimensions
  - `test_surface_fill_black` — surface.fill(BLACK) produces all-zero array
  - `test_surface_scaling_dimensions` — transform.scale produces correct output size
  - `test_surface_scaling_preserves_colors` — scaled surface preserves pixel colors
  - `test_surface_blit_overwrites_background` — blitting sprite replaces background pixels

---

## Planning Log

### Discrepancies
- None identified. Research provides sufficient detail for implementation.

### Implementation Paths Considered
1. **Single test file** vs **multiple test files** — Chose multiple files for organization (draw, blitting, text, surfaces, sprites)
2. **Separate conftest.py** vs **shared conftest.py** — Chose separate conftest.py in test_rendering/ to isolate SDL_VIDEODRIVER=software from dummy driver tests
3. **Pixel-exact tests** vs **presence-based tests** — Chose presence-based (non-black pixel counts, color masks) for robustness against anti-aliasing variations

### Suggested Follow-on Work
- Add visual regression tests (save rendered surfaces as images for manual comparison)
- Add CI/CD integration for rendering tests
- Add screenshot capture tests for documentation

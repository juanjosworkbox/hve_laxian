<!-- markdownlint-disable-file -->
# Galaxian Clone - Implementation Details

**Date:** 2026-09-22

## Context References
- Plan: `.copilot-tracking/plans/2026-09-22/galaxian-clone-plan.instructions.md`
- Research: `.copilot-tracking/research/2026-09-22/galaxian-clone-research.md`
- Research: `.copilot-tracking/research/2026-09-22/galaxian-research.md`

## Per-Phase Step Details

### Phase 1: Core Architecture

#### 1.1 - Project Structure and Module Layout
- Create directory structure: `main.py`, `assets/`, `game/`, `entities/`, `systems/`
- Create `__init__.py` files for each package
- Set up constants module for game configuration

#### 1.2 - Game Loop and State Management
- Implement Game class with main loop
- Game states: ATTRACT, PLAYING, ROUND_TRANSITION, GAME_OVER
- Pygame initialization at 256x288 base resolution, scaled 2x

#### 1.3 - Asset Loading System
- Create sprites.png with all game assets (procedural generation)
- Sprite sheet parser for extracting individual sprites
- Asset caching system

#### 1.4 - Pygame Initialization
- Screen resolution: 256x288 base, scaled 2x = 512x576
- 60 FPS target
- Clock management

### Phase 2: Sprite Assets

#### 2.1 - Generate sprites.png
- Player ship (Galaxip) - starfighter design
- Green/Blue regular enemies - dragonfly aliens
- Red regular enemies - dragonfly aliens (red variant)
- Galboss (Flagship) - larger distinct design
- Explosion frames (4-6 frames)
- Player bullet, enemy bullet
- Round flags, score/lives text

#### 2.2 - Sprite Sheet Parser
- Parse sprites.png into individual sprite images
- Palette support for color matching

#### 2.3 - Asset Extraction and Caching
- Cache loaded sprites for performance
- Asset management singleton

### Phase 3: Player System

#### 3.1 - Player Movement
- Left/right movement with arrow keys
- Bottom of screen restriction
- Speed: ~5 pixels/frame

#### 3.2 - Single-Shot Firing
- Only one bullet at a time
- Space bar to fire
- Must resolve bullet before next shot

#### 3.3-3.5 - Collision, Respawn, Rendering
- Collision with enemy bullets
- Invincibility frames on respawn
- Player sprite rendering

### Phase 4: Enemy Formation & Dive AI

#### 4.1-4.2 - Formation
- V-shaped formation: 5 rows, 5 columns = 25 regular enemies
- Side-to-side movement with hover
- ~2 pixels/frame horizontal movement

#### 4.3-4.8 - Dive AI
- Curved dive paths (quadratic bezier)
- Return to formation after dives
- Enemy shooting during dives
- Galboss escort system
- Enemy AI position tracking

### Phase 5: Game Systems

#### 5.1-5.9 - Complete Game Systems
- Scoring, lives, rounds, difficulty scaling
- Starfield background
- Sound effects (pygame.mixer synthesized)
- HUD rendering
- Game state management

### Phase 6: Polish

#### 6.1-6.4 - Authenticity
- Difficulty progression per round
- Somersault dive animation
- Explosion animations
- HUD and display polish

<!-- markdownlint-disable-file -->
# Galaxian Clone Implementation Plan

**Date:** 2026-09-22
**Objective:** Create a faithful clone as similar as possible to the original Namco Galaxian arcade game (1979)

---

## User Requests

- Make a Galaxian clone as similar as possible to the original arcade game

---

## Overview

Build a complete Galaxian arcade clone using Python and pygame that faithfully replicates the original 1979 Namco game mechanics, behavior, and visual style. The project is greenfield with no existing code or assets.

## Objectives

1. **Authentic Gameplay:** Replicate all original Galaxian mechanics — formation movement, curved dive attacks, single-shot restriction, scoring, progression
2. **Visual Fidelity:** Match original sprite design, color palette (true RGB), and screen layout
3. **Behavioral Accuracy:** Enemies track player position, dive with curved paths, return to formation
4. **Progressive Difficulty:** Smooth scaling of speed, dive frequency, and enemy shots across rounds

---

## Context Summary

### Game Specifications
- **Resolution:** 256×288 (original hardware)
- **Scale:** 2x (512×576 for modern displays)
- **Orientation:** Vertical
- **Player:** Galaxip — 2-way movement (left/right), single-shot firing
- **Enemies:** 28 per wave (25 regular + 2 escorts + 1 Galboss)
- **Formation:** V-shaped wedge, 5 rows
- **Lives:** 3 starting
- **Colors:** True RGB (first arcade game with full color)

### Key Behaviors to Implement
- V-shaped formation with side-to-side movement and hover
- Curved dive paths (quadratic bezier)
- Return-to-formation after dives
- Enemy AI that tracks player position
- Escort system for Galboss
- Single-shot restriction for player
- Animated starfield background

### Difficulty Scaling
- Faster formation movement per round
- More frequent dive attacks
- More enemy shots during dives
- Faster dive speeds

---

## Implementation Checklist

### Phase 1: Core Architecture
- [ ] **1.1** Create project structure and module layout
- [ ] **1.2** Implement game loop and state management
- [ ] **1.3** Build asset loading system (sprites.png parsing)
- [ ] **1.4** Set up pygame initialization with 256×288 resolution

### Phase 2: Sprite Assets
- [ ] **2.1** Design sprites.png with all game assets:
  - [ ] Player ship (Galaxip) — starfighter design
  - [ ] Green/Blue regular enemy — dragonfly alien
  - [ ] Red regular enemy — dragonfly alien (red variant)
  - [ ] Galboss (Flagship) — larger, distinct design
  - [ ] Explosion frames (4-6 frames)
  - [ ] Player bullet
  - [ ] Enemy bullet
  - [ ] Round flags (1-10)
  - [ ] Score/lives text sprites
- [ ] **2.2** Implement sprite sheet parser with palette support
- [ ] **2.3** Create asset extraction and caching system

### Phase 3: Player System
- [ ] **3.1** Player ship movement (left/right along bottom)
- [ ] **3.2** Single-shot firing mechanic (one bullet at a time)
- [ ] **3.3** Collision detection (player vs enemy bullets)
- [ ] **3.4** Respawning with brief invincibility frames
- [ ] **3.5** Player ship rendering and animation

### Phase 4: Enemy Formation & Dive AI
- [ ] **4.1** V-shaped formation layout (5 rows, 5 columns + escorts)
- [ ] **4.2** Formation side-to-side movement with hover
- [ ] **4.3** Dive attack system with quadratic bezier curves
- [ ] **4.4** Return-to-formation behavior after dives
- [ ] **4.5** Enemy shooting during dives
- [ ] **4.6** Enemy AI — position tracking and dive triggers
- [ ] **4.7** Galboss escort system (2 red escorts dive with flagship)
- [ ] **4.8** Enemy rendering and sprite animation

### Phase 5: Game Systems
- [ ] **5.1** Scoring system with point values per enemy type
- [ ] **5.2** Bonus Galaxip award at 4,000 points
- [ ] **5.3** Lives system (3 starting, lose on collision)
- [ ] **5.4** Round/wave progression (10+ rounds)
- [ ] **5.5** Difficulty scaling (speed, dive frequency, shots)
- [ ] **5.6** Game states (attract, playing, game over, round transition)
- [ ] **5.7** HUD rendering (score, lives, round indicator)
- [ ] **5.8** Animated starfield background
- [ ] **5.9** Sound effects (pygame.mixer synthesized tones)

---

## Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Resolution | 256×288 | Authentic to original hardware |
| Scale | 2x (512×576) | Better visibility on modern displays |
| Sprite format | sprites.png with palette | Matches original tile-based approach |
| Enemy paths | Quadratic bezier curves | Authentic curved dive paths |
| Difficulty | Per-round multipliers | Smooth scaling without sudden jumps |
| Sound | pygame.mixer with synthesized tones | Mono channel matching original |
| Enemy AI | Position tracking + random dive triggers | Authentic "personality" behavior |

---

## Dependencies

### Python Packages (requirements.txt)
- pygame>=2.1.0
- Pillow>=10.0.0
- numpy>=1.24.0

### Assets Required
- sprites.png — All game sprites in a single sheet with indexed palette

---

## Success Criteria

1. **Formation Behavior:** Enemies appear in V-shaped formation, move side-to-side with hover
2. **Dive Attacks:** Enemies break formation, dive on curved paths toward player, shoot, return to formation
3. **Single-Shot:** Player can only fire one bullet at a time
4. **Enemy Count:** 28 enemies per wave (25 regular + 2 escorts + 1 Galboss)
5. **Scoring:** Correct point values (Green=100, Red=150, Galboss=200, Bonus=4000)
6. **Progression:** Difficulty scales smoothly across rounds
7. **Visual Authenticity:** Matches original color palette and sprite design
8. **Game Flow:** Attract → Playing → Round transition → Game over → Continue/Restart

---

## Assumptions

- Player ship speed: ~5 pixels per frame at 60 FPS
- Formation movement: ~2 pixels per frame horizontally
- Dive speed: ~3-4 pixels per frame (increases with rounds)
- Enemy shot rate: Increases from ~1 per 10 seconds (round 1) to ~1 per 3 seconds (round 10+)
- Player invincibility: 2 seconds (120 frames) after respawn
- Round transition: 3-second pause with score display

---

## File Structure

```
galaxian/
├── main.py                    # Entry point, game loop
├── requirements.txt           # Python dependencies
├── sprites/
│   └── sprites.png           # All game sprites (indexed palette)
├── assets/
│   ├── __init__.py
│   ├── sprite_loader.py      # Sprite sheet parsing
│   └── sound.py              # Sound effect management
├── game/
│   ├── __init__.py
│   ├── game.py               # Main Game class
│   ├── states.py             # Game state machine
│   └── hud.py                # HUD rendering (score, lives, round)
├── entities/
│   ├── __init__.py
│   ├── player.py             # Player ship
│   ├── enemy.py              # Enemy class
│   ├── bullet.py             # Bullets (player + enemy)
│   └── explosion.py          # Explosion animation
├── systems/
│   ├── __init__.py
│   ├── formation.py          # Formation layout and movement
│   ├── dive_ai.py            # Dive attack system
│   ├── collision.py          # Collision detection
│   └── starfield.py          # Animated background
└── .copilot-tracking/        # Research, plans, changes logs
```

---

## Notes

- This is a faithful recreation — prioritize authenticity over convenience
- All enemy behaviors must match original Galaxian documentation
- Curved dive paths are critical for authentic feel
- Formation return behavior is essential
- Difficulty scaling must be gradual, not sudden

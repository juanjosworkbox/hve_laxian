<!-- markdownlint-disable-file -->
# Galaxian Clone Research

**Date:** 2026-09-22
**Source:** Original Namco Galaxian (1979)
**Objective:** Create a faithful clone as similar as possible to the original arcade game

---

## 1. Gameplay Mechanics

### Player Ship (Galaxip)
- **Movement:** 2-way joystick (left/right only)
- **Shooting:** Single-shot firing — player can fire only ONE bullet at a time, must resolve before next shot (hardware limitation)
- **Lives:** 3 starting lives
- **Invincibility:** Brief invincibility on respawn (standard arcade convention)
- **Speed:** Constant horizontal movement along bottom of screen

### Scoring
| Enemy Type | Points | Behavior |
|------------|--------|----------|
| Regular Galaxian (Green/Blue) | 100 | Stays in formation, occasional dive |
| Regular Galaxian (Red) | 150 | More frequent dive attacks |
| Galaxian Flagship (Galboss) | 200 | Frequent dive attacks with escorts |
| Bonus Galaxip | 4,000 | Awarded periodically |
| Dive bonus | Variable | Shooting enemies during somersault/dive |

### Controls
- Joystick: 2-way (left, right)
- Button: 1 (fire)
- 1 simultaneous player, 2 maximum (alternating)

---

## 2. Enemy Formation

### Layout
- **V-shaped / wedge formation** (5 rows, 5 columns = 25 regular enemies)
- **2 escort ships** accompany the Galaxian Flagship
- **1 Galboss** (Flagship) per wave
- **Total:** 28 enemies per wave (25 + 2 + 1)
- Formation moves **side to side** at top of screen
- Characteristic **hovering motion** — enemies subtly move up and down while traversing

### Key Design Philosophy (from Kazunori Sawano)
- Number of enemies **never changes** between stages
- Difficulty increase is **almost imperceptible** from stage to stage
- **Gradual build-up** — no sudden spikes or new enemy types
- Comparing stage 1 to stage 10 shows clear difficulty increase

---

## 3. Enemy Behaviors

### Two Enemy Types (4 including color variants)

| Type | Color | Points | Behavior |
|------|-------|--------|----------|
| Regular Galaxian | Green/Blue | 100 | Stays in formation, occasional dive |
| Galaxian Flagship (Galboss) | Red | 200 | More frequent dive attacks |

### Dive Bomb / Swoop Mechanics
- Individual enemies **break formation** and **dive-bomb toward the player**
- Dives follow **curved/smooth paths** (not straight lines) — signature Galaxian feature
- Enemies **shoot projectiles** during dive attacks
- Enemies **monitor player movements** and make attacks based on position
- After diving, enemies **return to formation** at top of screen
- **Red escort ships** accompany Galboss during dive — shooting all three together awards bonus points

### Dive Triggers
- Random but becomes more frequent as game progresses
- Enemies "judge" player position and react
- Game described as having enemies with "a will and personality of their own"

---

## 4. Screen Layout & Technical Specs

| Specification | Value |
|---------------|-------|
| **Resolution** | 256×288 (Namco Galaxian hardware standard) |
| **Orientation** | Vertical |
| **Monitor** | Standard raster color CRT |
| **Playfield** | Enemies occupy top ~2/3 of screen; player at bottom |
| **Boundaries** | Player restricted to bottom area; enemies confined to upper area (except during dives) |
| **Starfield** | Scrolling animated starfield background (only scrolling element) |
| **Rounds indicator** | Small flags at bottom of screen |

### Hardware (Original)
- **CPU:** Z80 microprocessor
- **First game with 100% true RGB color graphics**
- **First to use tile-based hardware system** (8×8 pixel tiles) — reduced memory by 64× vs Space Invaders
- **Multi-color sprites** capable of animation
- **Sprite rendering system** (influenced Nintendo Famicom/NES design)
- Namco's first game composed with a **synthesizer** for sound

---

## 5. Sound/Music

- **Amplified mono** (one channel)
- **First Namco game to use actual synthesizer** for sound effects
- Sound effects heavily laborated over — Sawano went through many iterations
- Inspired by **Star Wars space battle sounds**
- Characteristic back-and-forth sound effects for enemy movement
- Special sound for bonus stages/medals
- Attract mode text: **"WE ARE THE GALAXIANS. MISSION: DESTROY ALIENS"**

---

## 6. Progression / Difficulty

### Difficulty Scaling
- Number of enemies **never changes** between stages
- Difficulty increase is **almost imperceptible** from stage to stage
- **Gradual build-up** — no sudden spikes or new enemy types
- Comparing stage 1 to stage 10 shows clear difficulty increase

### Increases Through
- **Faster enemy movement** (formation side-to-side speed)
- **More enemy shots** fired during dives
- **More frequent dive attacks**
- **Faster dive speeds**

### Waves/Rounds
- Indicated by small flags at bottom of screen
- Game loops endlessly with increasing difficulty
- Designed to "keep evolving infinitely"

---

## 7. Visual Style

### Color Palette
- **True RGB color** — first video game with 100% color graphics
- Multi-color sprites (unlike Space Invaders monochrome)
- Enemy colors: **Green, Red** (primary), with color variations

### Sprite Design
- **8×8 pixel tile-based** sprites
- Enemy sprites resemble **dragonfly-like aliens**
- Originally intended to look like **Star Wars TIE Fighters**
- Player ship: Starfighter design
- Animated sprites (enemies bob/fly in curved paths)
- Artist: **Hiroshi Ono** ("Mr. Dotman")
- Cabinet art: White cabinet with painted player ship shooting green dragonfly alien

### Visual Effects
- Scrolling animated starfield background
- Enemies move on **curved/smooth paths** during dives (not straight lines)
- Sprite animation for diving enemies

---

## 8. Key Implementation Notes

1. **Enemy AI:** Enemies track player position and make decisions based on it
2. **Formation:** Enemies return to formation after diving — crucial for authentic behavior
3. **Single-shot restriction:** Hardware limitation must be replicated
4. **Curved dive paths:** Not straight-line attacks — enemies swoop in arcs
5. **Gradual difficulty:** No sudden changes; smooth scaling of speed/frequency
6. **Tile-based rendering:** 8×8 pixel tile system for sprite rendering
7. **Two enemy types** with color-based differentiation (4 total including color variants)
8. **Flagship + escort combo:** Special behavior where Galboss appears with 2 red escorts

---

## 9. Project Status: GREENFIELD

No source code, assets, or game structure exists. Required creation:
- Game engine architecture
- Sprite assets (sprites.png)
- Player ship, enemy types, explosions
- Formation system
- Dive attack system
- Scoring/lives UI
- Sound system

---

## Sources

- Wikipedia: Galaxian (2026)
- Shmuplations: Galaxian 1985 Developer Interview with Kazunori Sawano
- Shmuplations: Galaga 30th Anniversary Developer Interview with Shigeru Yokoyama
- KLOV/Arcade-Museum: Galaxian technical specifications
- MAME driver documentation (Z80 hardware)

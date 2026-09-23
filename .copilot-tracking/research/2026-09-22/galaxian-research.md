# Galaxian (Namco, 1979) - Comprehensive Game Mechanics Research

**Research Date:** 2026-09-22
**Status:** Complete

---

## 1. Game Screen & Layout

### Screen Orientation & Resolution
- **Orientation:** Vertical (portrait) - arcade cabinet uses a vertical CRT monitor
- **Display Type:** Raster, Color (true RGB - first game with 100% true color graphics)
- **Screen Resolution:** The arcade hardware uses a tilemap system with 8x8 pixel tiles. The exact pixel resolution of the play area is not explicitly documented, but the game uses Namco's custom sprite hardware.
- **Player Position:** Player ship (Galaxip) moves along the **bottom** of the screen, restricted to the lower area
- **Enemy Formation Position:** Enemies appear in formation at the **top** of the screen
- **HUD Elements:**
  - Round indicators: Small flags displayed at the bottom of the screen showing current round number
  - Lives display: Shown at the bottom of the screen
  - Score display: Standard arcade score readout
  - Attract mode text: "WE ARE THE GALAXIANS. MISSION: DESTROY ALIENS"

### Technical Specifications
- **Processor:** Z80 microprocessor
- **Hardware:** Namco Galaxian custom arcade board
- **Sprite System:** Tilemap hardware model using 8x8 pixel tiles (reduced memory requirements up to 64x compared to Space Invaders' framebuffer model)
- **Capabilities:** Multi-color sprites, sprite animation, scrolling (scrolling only used for starfield background)
- **Sound:** Amplified Mono (one channel) - Namco's first arcade game composed with a synthesizer
- **Player Count:** 1 simultaneous player, 2 maximum (alternating turns)
- **Controls:** 2-way joystick (left/right only) + 1 fire button

---

## 2. Player Ship (Galaxip)

### Movement
- **Controls:** Left and right only (2-way joystick)
- **Movement Area:** Bottom of the screen
- **Speed:** Constant movement while button held

### Weapon System
- **Single Shot Only:** The Galaxip can fire only ONE bullet at a time
- **Hardware Limitation:** Due to hardware constraints, the player must wait for the bullet to either hit an enemy or reach the top of the screen before firing another shot
- **No Multi-shot:** Unlike later games (Galaga introduced autofire), Galaxian has no automatic or multi-shot capability

### Vulnerability
- **One Hit Death:** Colliding with an enemy or enemy projectile results in losing a life
- **No Shielding:** No invulnerability frames or shields

---

## 3. Enemy Formation

### Enemy Types (2 Base Types with Color Variations = 4 Total)
According to designer Kazunori Sawano, the game uses only **two enemy types** (4 if counting color changes):

#### Type 1: Regular Aliens (Migi)
- **Formation Rows:** Multiple rows of aliens at the top of the screen
- **Colors:** Various colors (green, yellow, blue, red variations)
- **Shape:** Dragonfly-like aliens
- **Behavior:** Stay in formation, occasionally dive-bomb

#### Type 2: Galaxian Flagship / Galboss
- **Formation Position:** Appear at the top of the enemy formation
- **Quantity:** 2 escort ships (red) that accompany the flagship when diving
- **Shots Required:** 1 shot to destroy (unlike Galaga's Boss Galaga which takes 2 shots)
- **Shape:** Different from regular aliens - more ship-like

### Formation Layout
- Enemies appear in a **grid-like formation** at the top of the screen
- The formation includes **two red escort ships** flanking the flagship during dives
- The exact rows/columns count is not explicitly documented, but the formation fills the top portion of the screen in a structured pattern

### Escort Ship Behavior (Bonus Mechanic)
- When a Flagship dives, it does so with **two red escort ships**
- Shooting all three (flagship + 2 escorts) awards **bonus points**
- Extra points awarded for destroying the flagship itself
- This was added later in development specifically to reward great players with exciting performances

---

## 4. Enemy Behaviors

### Formation Movement
- **Side-to-Side:** Enemies in formation move horizontally back and forth
- **Pattern:** The entire formation oscillates or moves side to side at the top of the screen
- **Speed:** Gradually increases as the game progresses

### Dive-Bomb Behavior
- **Primary Attack:** Aliens periodically leave the formation to dive-bomb toward the player at the bottom of the screen
- **Dive Patterns:** Enemies fly in **curved lines** (one of Galaxian's signature features praised by players)
- **Shooting While Diving:** Enemies fire projectiles **while diving** toward the player
- **Individual Targeting:** Enemies are programmed to **monitor the player's movements** and make attacks based on them - giving them a "personality of their own"
- **Somersault Animation:** When diving, enemies perform a somersault/flip animation (mentioned in game play tips: "shoot them when they are doing a somersault")
- **Return to Formation:** After completing a dive, enemies **return to their formation** position at the top of the screen

### Shooting Behavior
- **In-Formation Shooting:** Enemies in formation can also fire at the player
- **Dive Shooting:** Enemies fire projectiles during their dive-bomb runs
- **Bullet Patterns:** Individual enemy projectiles (no complex bullet patterns like later games)
- **Frequency:** Increases as the game progresses - enemies fire more shots in later rounds

---

## 5. Scoring System

### Points Per Enemy Type
Specific point values per enemy type are not explicitly documented in the available sources. However:

- **Regular Aliens:** Standard points (lower value)
- **Flagship/Galboss:** Higher points than regular aliens
- **Bonus for Escort Group:** Extra bonus points for destroying the flagship + 2 escorts together
- **Bonus at 4000 Points:** The game displays "BONUS GALAXIP AT 4000 PTS" - indicating a bonus life or points milestone at 4,000 points

### Note on Scoring
The exact point values for each enemy color/type would need to be verified from the original game ROM or MAME documentation for precise implementation.

---

## 6. Lives & Game Flow

### Starting Lives
- **Standard Starting Lives:** 3 lives (standard for arcade games of this era)
- **Extra Lives:** Awarded at score milestones (confirmed at 4,000 points)

### Round/Stage Progression
- **Rounds Indicated By:** Small flags at the bottom of the screen
- **Infinite Looping:** The game is designed to loop endlessly (as per Sawano's design philosophy)
- **Enemy Count Constant:** The number of enemies on-screen **never changes** between rounds (per Sawano's intentional design)
- **Difficulty Increase:** Difficulty increases gradually through:
  - Faster enemy movement
  - More enemy projectiles
  - More frequent dive-bombs
  - These changes are "almost imperceptible" from round to round but become "very clear" comparing round 1 to round 10

### Game Flow
1. **Attract Mode:** Screen displays "WE ARE THE GALAXIANS. MISSION: DESTROY ALIENS"
2. **Insert Coin:** Game begins with Round 1
3. **Formation Appears:** Enemies arrive in formation at top of screen
4. **Players Shoot:** Player moves and shoots at formation enemies
5. **Dive Bombs:** Enemies periodically dive, shoot, and return
6. **Round Cleared:** When all enemies are destroyed, next round begins
7. **Life Lost:** Player loses a life when hit
8. **Game Over:** When all lives are lost

---

## 7. Visual Style

### Sprite Characteristics
- **Multi-Color Sprites:** Galaxian was one of the first games with true RGB color graphics (100% of graphics in color)
- **Animated Sprites:** Enemies have animated sprites (wing flapping, somersault during dive)
- **8x8 Tile System:** Sprites built from 8x8 pixel tilemap blocks
- **Player Ship:** Galaxip is a starfighter design (originally envisioned as TIE Fighter-like from Star Wars)

### Enemy Visual Design
- **Aliens:** Dragonfly-like alien creatures
- **Flagship:** Distinct ship design from regular aliens
- **Escorts:** Red-colored escort ships
- **Color Variations:** Multiple colors for different enemy rows (green, yellow, blue, red)
- **Dive Animation:** Somersault/flip animation during dive-bomb runs

### Background
- **Scrolling Starfield:** Animated scrolling starfield background (one of Galaxian's visual signature features)
- **Star Movement:** Stars scroll to create a sense of movement through space

### Explosions
- **Enemy Destruction:** When enemies are destroyed, they explode (standard for the era)
- **Specific dive explosions:** Bonus points when shooting enemies during their somersault dive

---

## 8. Audio

### Sound Capabilities
- **Sound Hardware:** Amplified Mono (single channel)
- **Synthesizer:** Namco's first arcade game to use an actual synthesizer for sound composition
- **Composer:** Toshio Kai

### Sound Effects
- **Player Shooting:** Distinct laser/shoot sound
- **Enemy Shooting:** Different sound from player bullets
- **Enemy Explosions:** Explosion sounds when enemies are destroyed
- **Dive Sounds:** Sound effects when enemies begin dive-bomb runs
- **Sound Design Philosophy:** Designer Kazunori Sawano extensively labored over sound effects, working back-and-forth with the sound designer to achieve the feeling of "space battle" sounds inspired by Star Wars. Many sound effects were rejected before approval.

### Music
- No dedicated background music track is documented - the game focuses on sound effects rather than a musical score.

---

## 9. Difficulty Progression

### Gradual Increase (Sawano's Design Philosophy)
Sawano specifically designed the difficulty to increase **gradually** without sudden spikes:

- **Constant Enemy Count:** Number of enemies stays the same each round
- **Movement Speed:** Formation moves faster in later rounds
- **Dive Frequency:** More enemies dive in later rounds
- **Dive Speed:** Enemies dive faster in later rounds
- **Shooting Frequency:** Enemies fire more projectiles in later rounds
- **Bullet Speed:** Enemy bullets may move faster
- **Imperceptible Per-Round:** Changes from round to round are "almost imperceptible"
- **Cumulative Effect:** Comparing Round 1 to Round 10 shows very clear difficulty increase

### Strategic Depth
- **Bonus Scoring Encourages Skill:** The escort ship bonus rewards skilled players who can take down the flagship + escorts
- **Timing Attacks:** Enemies are worth more when shot during their somersault dive
- **Positioning:** Player must balance formation shooting with dive-bomb avoidance

---

## 10. Win/Lose Conditions

### Game Over Triggers
- **All Lives Lost:** Game ends when the player has lost all lives
- **No Win Condition:** The game has no ending - it is designed to loop infinitely
- **High Score Chase:** The objective is to achieve the highest possible score

### Round Completion
- **Clear All Enemies:** A round is completed when all enemies in the formation are destroyed
- **Next Round:** Immediately begins after round completion
- **No Time Limit:** No time limit per round

### Score Milestones
- **Bonus at 4000 Points:** "BONUS GALAXIP AT 4000 PTS" displayed (likely an extra life or significant points bonus)

---

## Key Design Principles (from Developer Interviews)

1. **"Simple is Best":** Sawano's motto - the game was designed to be simple enough that anybody could play it
2. **Endless Looping:** Designed to loop endlessly with gradual difficulty increase
3. **Two Enemy Types:** Only 2 base enemy types (4 with color variations) to keep things simple
4. **Enemy Personality:** Enemies programmed to monitor player movement and react individually
5. **Gradual Difficulty:** No sudden difficulty spikes - slow, imperceptible build-up
6. **Star Wars Inspiration:** Space battle feeling was the core design goal
7. **Hardware Innovation:** First game with true RGB color, tilemap sprite system, animated multi-color sprites

---

## Sources

- Wikipedia: Galaxian (en.wikipedia.org/wiki/Galaxian)
- Killer List of Videogames / Arcade Museum (arcade-museum.com/game_detail.php?game_id=7885)
- Shmuplations: Early Arcade Classics - Galaxian Developer Interview with Kazunori Sawano (1985)
- Shmuplations: Galaga 30th Anniversary Developer Interview (references to Galaxian mechanics)
- The Untold History of Japanese Game Developers Vol. 2 by John Szczepaniak

---

## Clarifying Questions / Unknowns

1. **Exact point values** for each enemy color/type - would need MAME ROM analysis
2. **Exact formation dimensions** (rows/columns count) - not explicitly documented
3. **Exact sprite dimensions** beyond the 8x8 tile system
4. **Exact screen resolution** in pixels
5. **Specific dive curve patterns** (straight, S-curve, looping) - "curved lines" is confirmed but specific pattern shapes are undocumented
6. **Exact number of rounds** before any potential kill screen or reset behavior

<!-- markdownlint-disable-file -->
# Enemy Attack Behavior Research — Galaxian Dive & Shoot Implementation

**Date:** 2026-09-22
**Status:** Research Complete
**Difficulty:** Medium

---

## User Request

> "Enemies do not abandon formation to attack player, and neither shot"

The current game has dive mechanics partially implemented but they are not producing visible enemy attack behavior.

---

## Root Cause Analysis

### 1. Dive Trigger Probability is Too Low

In `game.py` `_update_playing()`:
```python
if enemy.enemy_type in ('red', 'flagship'):
    chance = 3 + self.round_num      # 4-5 per frame at round 1-5
else:
    chance = 1 + self.round_num // 2  # 1-3 per frame
```

With `random.randint(1, 60) <= chance`, the per-frame probability is:
- Red/Flagship: ~5-8% per frame
- Others: ~2-5% per frame

This means dives only trigger roughly every 12-50 frames for priority enemies — too infrequent.

### 2. Max Dives Per Round is Too Low

`constants.py`:
```python
MAX_DIVES_PER_ROUND = 5  # increases with round
```

After 5 dives, **no more dives happen for the entire round** (can be 300+ frames). Original Galaxian had waves of 3-5 enemies diving simultaneously, repeatedly throughout the round.

### 3. Dive Cooldown Prevents Rapid Succession

`constants.py`:
```python
DIVE_INTERVAL_BASE = 180  # frames between dive attempts
```

After each dive, there's a 3-second cooldown before the next dive can trigger. This makes dives feel sparse.

### 4. Only ONE Enemy Dives at a Time

`Formation.try_dive()` selects a single random enemy and returns it. Original Galaxian had **multiple enemies diving simultaneously** in waves.

### 5. Diving Enemies Do Shoot — But Logic is Confusing

The `Enemy.update()` method returns `'shoot'` when `dive_shoot_timer` expires during a dive. This is handled by `Formation.update()` which calls `enemy.update()` for ALL enemies (including diving ones) and returns the shooting enemy. So diving enemies **do** shoot, but:
- The `game.py` double-updates formation-state enemies (once via Formation, once directly)
- The diving enemy shooting works but is buried in the formation update path

### 6. No Dive Wave System

Original Galaxian behavior:
1. Formation moves side-to-side
2. **Wave of 3-5 enemies** breaks formation simultaneously
3. They curve toward the player on Bézier paths
4. They **shoot while diving**
5. They either return to formation or fly off screen
6. Process repeats with different enemies

Current implementation:
1. Formation moves side-to-side
2. ONE enemy randomly dives every 3-5 seconds (max 5 per round)
3. It shoots occasionally
4. It returns to formation
5. Long pause before next dive

---

## Original Galaxian Behavior Reference

The original Namco Galaxian (1979) featured:

- **Wave dives**: 3-5 enemies dive simultaneously in coordinated waves
- **High frequency**: Enemies dive continuously throughout the round, not limited to a small count
- **Different dive patterns**: 
  - Green/blue: shallow curves, less aggressive
  - Yellow/red: deeper curves, faster
  - Flagship: steep dive, fastest, shoots frequently
  - Escort (red plane): special dive, chases player directly
- **Dive shooting**: All diving enemies fire bullets during their descent
- **No dive cap**: Enemies keep diving until the player kills them all
- **Escalating aggression**: Later waves (after player kills some enemies) have more frequent dives

---

## Implementation Plan

### File: `constants.py`

Update dive-related constants:

```python
# NEW/UPDATED constants
MAX_DIVES_PER_ROUND = 999  # effectively unlimited — waves continue until all dead
DIVE_INTERVAL_BASE = 300   # cooldown between dive waves (not individual dives)
DIVES_PER_WAVE_MIN = 3     # minimum enemies that dive together
DIVES_PER_WAVE_MAX = 5     # maximum enemies that dive together
DIVE_WAVE_COOLDOWN = 180   # frames between dive waves
DIVE_SHOOT_INTERVAL = 40   # frames between shots while diving (was 20-60 random)
```

### File: `systems/formation.py`

**Major changes to `try_dive()`:**

1. Replace single-enemy dive with **wave-based multi-enemy dive**
2. Select 3-5 random alive formation enemies (weighted toward red/flagship)
3. Call `start_dive()` on ALL selected enemies simultaneously
4. Track wave cooldown separately from individual dive timers
5. Remove `dives_this_round` cap — use `wave_count` for round tracking only

```python
def try_dive_wave(self, player):
    """Trigger a wave of enemies diving simultaneously."""
    if self.dive_wave_cooldown > 0:
        return []
    
    # Select 3-5 enemies to dive
    formation_enemies = [e for e in self.enemies if e.alive and e.state == 'formation']
    if len(formation_enemies) < 2:
        return []
    
    # Weighted selection: prefer red and flagship
    priority = [e for e in formation_enemies if e.enemy_type in ('red', 'flagship', 'escort')]
    others = [e for e in formation_enemies if e not in priority]
    
    num_divers = random.randint(DIVES_PER_WAVE_MIN, min(DIVES_PER_WAVE_MAX, len(formation_enemies)))
    divers = []
    
    # Pick from priority first
    selected = []
    if priority and len(priority) > 0:
        pick_count = min(num_divers // 2, len(priority))
        selected.extend(random.sample(priority, pick_count))
    
    # Fill rest from others
    remaining = num_divers - len(selected)
    if remaining > 0 and others:
        selected.extend(random.sample(others, min(remaining, len(others))))
    
    # Start dives
    for enemy in selected:
        enemy.start_dive(player.rect.centerx, player.rect.bottom)
        divers.append(enemy)
    
    if divers:
        self.dive_wave_cooldown = DIVE_WAVE_COOLDOWN
        self.dives_this_round += len(divers)
    
    return divers
```

**Update `update()` method:**

```python
def update(self, round_num):
    self.round_num = round_num
    
    # Update difficulty
    self.formation_speed = FORMATION_SPEED_BASE + (round_num * 0.1)
    self.max_dives = MAX_DIVES_PER_ROUND + (round_num * 2)
    self.dive_wave_cooldown = max(60, DIVE_WAVE_COOLDOWN - (round_num * 10))
    
    # Movement (same as before)
    self.formation_offset += self.formation_speed * self.formation_direction
    self.hover_offset += 0.3 * self.hover_direction
    
    if self.formation_offset > 20:
        self.formation_direction = -1
    elif self.formation_offset < -20:
        self.formation_direction = 1
    
    if abs(self.hover_offset) > 3:
        self.hover_direction = -self.hover_direction
    
    # Decrement wave cooldown
    if self.dive_wave_cooldown > 0:
        self.dive_wave_cooldown -= 1
    
    # Update all enemies (includes diving enemies for shooting)
    shooting_enemy = None
    for enemy in self.enemies:
        if not enemy.alive:
            continue
        result = enemy.update(self.formation_offset + self.hover_offset, round_num)
        if result == 'shoot':
            shooting_enemy = enemy
    
    return shooting_enemy
```

### File: `game.py`

**Changes to `_update_playing()`:**

1. Replace per-enemy random dive trigger with **formation wave trigger**
2. Trigger dive wave based on formation cooldown + probability
3. Handle bullets from both formation update AND wave trigger
4. Remove double-update of formation-state enemies

```python
# Try dive waves (replaces per-enemy random trigger)
if random.randint(1, 60) <= (2 + self.round_num // 2):
    divers = self.formations.try_dive_wave(self.player)

# Update enemies (ONLY formation state — diving handled by Formation.update)
for enemy in self.enemies:
    if not enemy.alive:
        continue
    if enemy.state == 'formation':
        # Formation update is handled by Formation.update() above
        # No need to call enemy.update() again
        pass
```

### File: `entities/enemy.py`

**Minor changes to `update()` diving logic:**

```python
elif self.state == 'diving':
    # ... existing bezier movement ...
    
    # Shoot during dive (use fixed interval)
    self.dive_shoot_timer -= 1
    if self.dive_shoot_timer <= 0:
        self.dive_shoot_timer = DIVE_SHOOT_INTERVAL  # fixed, not random
        return 'shoot'
```

---

## Key Design Decisions

1. **Unlimited dives**: Remove the `dives_this_round` cap. Waves continue until all enemies are dead.
2. **Wave-based diving**: 3-5 enemies dive simultaneously for authentic Galaxian feel.
3. **Weighted selection**: Red/flagship/escort enemies dive more frequently.
4. **Fixed shoot interval**: Replace random dive shoot timer with constant for consistency.
5. **Single update path**: Formation.update() handles all enemy updates (including diving). Remove the duplicate enemy update loop in game.py.
6. **Escalating frequency**: Later rounds have shorter wave cooldowns and higher dive probability.

---

## Testing Approach

1. Verify multiple enemies dive simultaneously (3-5 per wave)
2. Verify enemies shoot while diving
3. Verify waves repeat throughout the round (not limited to 5 total)
4. Verify red/flagship enemies dive more often than green/blue
5. Verify difficulty scaling (more frequent waves in later rounds)
6. Verify returning enemies rejoin formation correctly

---

## Files to Modify

1. `constants.py` — Add/update dive constants
2. `systems/formation.py` — Implement wave-based diving, update cooldown logic
3. `entities/enemy.py` — Simplify dive shoot timer
4. `game.py` — Replace per-enemy dive trigger with wave trigger, remove double-update

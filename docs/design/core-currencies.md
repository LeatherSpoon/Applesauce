# MyRPG Core Currencies & Systems Design

## Overview

MyRPG is a loop-driven RPG built around themed environments, master-student training, combat for loot, and a pedometer-based progression system. This document defines the core currencies, their interactions, and the fundamental gameplay loops.

---

## Core Currencies

### 1. Power Level

**Purpose:** The main "big number" representing overall progression and combat strength.

| Property | Value |
|----------|-------|
| Type | Persistent, always-increasing |
| Starting Value | 1 |
| Cap | None (infinite scaling) |
| Affects | Combat damage, combat defense, opponent difficulty scaling |
| Does NOT affect | Movement speed |

**Sources of Power Level Increase:**
- Completing training sessions with Masters
- Defeating opponents in combat
- Finishing environment bosses
- Tournament performance milestones
- Combat theme mastery bonuses
- Controlling variable upgrades (Strength, Dexterity, etc.)

**Design Note:** Power Level is the player's primary sense of progression. It should always feel like it's growing, even during "reset" events.

---

### 2. Pedometer Count (Total Steps Taken)

**Purpose:** A lifetime movement counter used for speed upgrades and Power Level achievement unlocks.

| Property | Value |
|----------|-------|
| Type | Accumulating, spend-all-or-nothing |
| Starting Value | 0 |
| Cap | None (but speed upgrades cap at threshold) |
| Affects | Speed upgrade purchases, achievement unlocks |

**Accumulation:**
- +1 per step/movement tick
- Rate can be multiplied by speed (faster movement = faster accumulation)
- Special tiles may grant bonus steps

**Spending Mechanic (Full Reset Style):**
When the player chooses to spend Pedometer Count:
1. The ENTIRE current count is consumed
2. A reward is granted based on the amount spent
3. Counter resets to 0
4. Player begins accumulating again

This creates a **tension loop**: spend now for a smaller reward, or wait for a larger reward but delay gratification.

**Pedometer Milestones:**
| Steps | Reward Type |
|-------|-------------|
| 1,000 | Minor speed upgrade |
| 10,000 | Medium speed upgrade |
| 100,000 | Major speed upgrade |
| 1,000,000 | Speed tile unlock |
| 10,000,000+ | Achievement-based Power Level bonuses |

**Speed Upgrade Cap:** Speed upgrades purchased via pedometer are capped at a high threshold (e.g., +500% base speed). Beyond this, pedometer spending only grants Power Level achievement bonuses.

---

### 3. Gold

**Purpose:** Active economy currency for equipment, consumables, and permanent upgrades.

| Property | Value |
|----------|-------|
| Type | Spendable, non-accumulating |
| Starting Value | 0 |
| Cap | None |
| Passive Generation | None (active only) |

**Sources:**
- Selling dropped loot from opponents
- Selling crafted items
- Tournament participation rewards
- Environment completion bonuses

**Sinks:**
- Equipment purchases
- Consumable items
- Manager hiring
- Training acceleration
- Tile purchases for route building
- Combat theme upgrades

**Design Philosophy:** Gold requires active engagement. There is NO idle gold generation. This keeps players engaged in combat and loot loops.

---

## Secondary Currencies / Resources

### 4. Controlling Variables

These are the stats that determine combat theme effectiveness. Each can be trained actively or automated via managers.

| Variable | Primary Benefit | Secondary Benefit | Training Activity |
|----------|-----------------|-------------------|-------------------|
| **Strength** | Armed damage, Unarmed damage | Carry capacity | Mining |
| **Dexterity** | Ranged accuracy, Attack speed | Movement efficiency | Obstacle courses |
| **Focus** | Energy damage, Energy capacity | Training efficiency | Meditation |
| **Endurance** | Health pool, Defense | Stamina regeneration | Distance running |

**Interaction with Combat Themes:**
- Each combat theme scales with 1-2 controlling variables
- All themes benefit from all variables to some degree
- Specialization is rewarded but not required

---

## Combat Themes

### Theme Progression Sequence

```
Unarmed → Armed → Ranged → Energy → [Cycle repeats at higher tier]
```

### Theme Definitions

#### Unarmed
| Property | Value |
|----------|-------|
| Primary Scaling | Strength, Endurance |
| Unlock Requirement | Default (starting theme) |
| Playstyle | Close-range, high attack speed, lower damage per hit |
| Special Mechanic | Combo chains increase damage |

#### Armed
| Property | Value |
|----------|-------|
| Primary Scaling | Strength, Dexterity |
| Unlock Requirement | Reach Unarmed Mastery Level 10 |
| Playstyle | Close-range, balanced speed/damage |
| Special Mechanic | Weapon types with unique movesets |

#### Ranged
| Property | Value |
|----------|-------|
| Primary Scaling | Dexterity, Focus |
| Unlock Requirement | Reach Armed Mastery Level 10 |
| Playstyle | Long-range, positioning-dependent |
| Special Mechanic | Ammunition management, critical distance bonuses |

#### Energy
| Property | Value |
|----------|-------|
| Primary Scaling | Focus, Endurance |
| Unlock Requirement | Reach Ranged Mastery Level 10 |
| Playstyle | Variable range, resource-intensive |
| Special Mechanic | Energy pool management, charge attacks |

### Theme Exclusivity Rule

**Players may only use ONE combat theme at a time.**

However, all themes benefit from controlling variable improvements:
- Training Strength helps Armed AND Unarmed
- Automating Focus training helps Ranged AND Energy
- This creates incentive to diversify training even when specializing in one theme

### Theme Cycling Logic

**Trigger:** Completing an environment's infinite tournament (losing after significant progress)

**Mechanic:**
1. Upon tournament defeat, the next Master uses a different combat theme
2. Theme sequence follows: Unarmed → Armed → Ranged → Energy → Unarmed...
3. Player must train in the new theme to progress
4. Previous themes remain available for farming earlier environments

**Why This Works:**
- Forces engagement with all combat systems
- Creates natural reasons to return to earlier content
- Rewards players who invest in all controlling variables
- Prevents pure specialization from trivializing content

---

## Manager & Automation System

### Overview

Managers automate active tasks that increase controlling variables. This creates an idle/incremental layer on top of the active gameplay.

### Manager Hierarchy

```
Tier 1: Task Managers (automate single activities)
    ↓
Tier 2: Department Managers (manage multiple Task Managers)
    ↓
Tier 3: Executive Managers (manage Department Managers)
    ↓
Tier 4: CEO (manages all Executives, unlocks prestige features)
```

### Tier 1: Task Managers

| Manager | Automates | Cost (Gold) | Efficiency |
|---------|-----------|-------------|------------|
| Mining Foreman | Mining (Strength) | 1,000 | 50% of active |
| Course Instructor | Obstacle courses (Dexterity) | 1,000 | 50% of active |
| Meditation Guide | Meditation (Focus) | 1,000 | 50% of active |
| Running Coach | Distance running (Endurance) | 1,000 | 50% of active |

**Notes:**
- Multiple Task Managers of the same type can be hired
- Each additional manager adds efficiency (diminishing returns)
- Managers work while player is active OR idle

### Tier 2: Department Managers

| Manager | Manages | Cost (Gold) | Bonus |
|---------|---------|-------------|-------|
| Physical Director | Mining Foreman, Running Coach | 10,000 | +25% efficiency to managed |
| Mental Director | Course Instructor, Meditation Guide | 10,000 | +25% efficiency to managed |

**Unlock Requirement:** Own at least 2 Task Managers in the relevant category

### Tier 3: Executive Managers

| Manager | Manages | Cost (Gold) | Bonus |
|---------|---------|-------------|-------|
| VP of Training | All Department Managers | 100,000 | +50% efficiency, auto-hire Task Managers |

**Unlock Requirement:** Own both Department Managers

### Tier 4: CEO

| Manager | Manages | Cost (Gold) | Bonus |
|---------|---------|-------------|-------|
| CEO | All Executives | 1,000,000 | Prestige multiplier, unlock new manager tiers |

**Unlock Requirement:** Own VP of Training, complete at least one full theme cycle

### Manager Efficiency Formula

```
Total Efficiency = Base × (1 + Tier1Bonus) × (1 + Tier2Bonus) × (1 + Tier3Bonus) × PrestigeMultiplier

Where:
- Base = 50% per Task Manager (diminishing: 50%, 75%, 87.5%, ...)
- Tier2Bonus = 25% if Department Manager owned
- Tier3Bonus = 50% if Executive Manager owned
- PrestigeMultiplier = 1.0 + (0.1 × PrestigeLevel)
```

---

## Speed & Movement System

### Base Movement

| Property | Value |
|----------|-------|
| Starting Speed | 100 units/second |
| Speed Cap (from pedometer) | 600 units/second (+500%) |
| Speed Cap (from tiles) | None |

### Speed Sources

1. **Pedometer Upgrades** (permanent, capped)
2. **Speed Tiles** (placed on map, unlimited stacking potential)
3. **Equipment** (temporary bonuses)
4. **Consumables** (temporary buffs)

### Speed Tiles

Players can purchase and place special tiles that grant speed bonuses when traveled upon.

| Tile Type | Speed Bonus | Cost (Gold) | Size |
|-----------|-------------|-------------|------|
| Dirt Path | +10% | 100 | 1x1 |
| Cobblestone | +25% | 500 | 1x1 |
| Paved Road | +50% | 2,500 | 1x1 |
| Speed Rail | +100% | 10,000 | 1x3 (linear) |
| Teleport Pad | Instant (linked pair) | 50,000 | 1x1 |

**Route Building:** Players optimize routes through environments by placing tiles strategically. This creates a meta-game of efficient path planning.

### Environment Speed Requirements

| Environment Tier | Minimum Speed Required |
|------------------|----------------------|
| Tier 1 (Starting) | 100 (no requirement) |
| Tier 2 | 150 |
| Tier 3 | 225 |
| Tier 4 | 350 |
| Tier 5 | 500 |
| Tier 6+ | 500 + tiles recommended |

**Soft vs Hard Requirements:**
- Below minimum: Movement is possible but severely penalized (enemies outrun you)
- At minimum: Normal gameplay
- Above minimum: Advantageous positioning, faster farming

---

## Environment & Progression Structure

### Environment Composition

Each environment contains:

| Component | Description |
|-----------|-------------|
| **Themed Master** | NPC who trains the player in a specific combat theme |
| **Themed Mobs** | Regular opponents matching the environment's aesthetic |
| **Themed Boss** | Powerful opponent guarding progression |
| **Infinite Tournament** | Unlocked after boss defeat |

### Progression Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    ENVIRONMENT CYCLE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│  │  Train  │ →  │  Farm   │ →  │  Boss   │ →  │ Tourney │  │
│  │  with   │    │  Mobs   │    │  Fight  │    │ (Inf.)  │  │
│  │ Master  │    │         │    │         │    │         │  │
│  └─────────┘    └─────────┘    └─────────┘    └────┬────┘  │
│       ↑                                            │       │
│       │         ┌──────────────────────────────────┘       │
│       │         ↓                                          │
│       │    ┌─────────┐                                     │
│       │    │ DEFEAT  │ ← (Expected outcome)                │
│       │    │ EVENT   │                                     │
│       │    └────┬────┘                                     │
│       │         │                                          │
│       │         ↓                                          │
│       │    ┌─────────┐    ┌─────────┐                      │
│       │    │   New   │ →  │   New   │                      │
│       └────│ Master  │    │  Zone   │                      │
│            │ Unlock  │    │ Access  │                      │
│            └─────────┘    └─────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Infinite Tournament Details

| Property | Value |
|----------|-------|
| Opponent Scaling | +5% Power Level per victory |
| Expected Defeats | After 15-25 victories (varies by preparation) |
| Rewards | Gold per victory, Power Level milestone bonuses |
| Defeat Trigger | Loss triggers new environment unlock |

### Environment Persistence

**All environments remain accessible after progression:**
- Return for farming gold/loot
- Complete mastery achievements
- Optimize speed tile routes
- Train alternative combat themes

---

## Core Gameplay Loops

### Loop 1: Combat Loop (Short-term)
```
Combat → Loot Drop → Sell for Gold → Buy Upgrades → Stronger Combat
```
**Frequency:** Continuous during play sessions

### Loop 2: Pedometer Loop (Medium-term)
```
Movement → Steps Accumulate → Spend All → Speed Upgrade → Faster Movement → Access New Zones
```
**Frequency:** Major decision every 30-60 minutes of active play

### Loop 3: Environment Loop (Long-term)
```
Train → Boss → Tournament → Defeat → New Master/Theme → New Environment
```
**Frequency:** Major milestone every 2-4 hours of play

### Loop 4: Automation Loop (Background)
```
Earn Gold → Hire Managers → Automate Training → Controlling Variables Increase → All Themes Improve
```
**Frequency:** Incremental, always running

### Loop Interconnections

```
                    ┌─────────────────┐
                    │   POWER LEVEL   │
                    │  (Big Number)   │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           ↓                 ↓                 ↓
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │   COMBAT     │  │  PEDOMETER   │  │  AUTOMATION  │
    │    LOOP      │  │    LOOP      │  │    LOOP      │
    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
           │                 │                 │
           ↓                 ↓                 ↓
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │    GOLD      │  │    SPEED     │  │  CONTROLLING │
    │              │  │              │  │  VARIABLES   │
    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             ↓
                    ┌─────────────────┐
                    │  ENVIRONMENT    │
                    │  PROGRESSION    │
                    └─────────────────┘
```

---

## Balance Considerations

### Preventing Stagnation
- Speed requirements force pedometer engagement
- Combat theme cycling forces variable diversity
- Tournament defeats are expected, not failures

### Preventing Runaway Acceleration
- Pedometer spending is all-or-nothing (can't hoard AND spend)
- Speed upgrades are capped (tiles require gold investment)
- Manager efficiency has diminishing returns

### Encouraging Return to Old Content
- Different combat themes excel in different environments
- Speed tile optimization rewards route planning
- Mastery achievements provide Power Level bonuses

---

## Appendix: Formulas

### Combat Damage
```
Damage = BaseDamage × (1 + PowerLevel/100) × ThemeMultiplier × VariableScaling

Where:
- ThemeMultiplier = based on current combat theme
- VariableScaling = (PrimaryVar × 0.02) + (SecondaryVar × 0.01)
```

### Pedometer Reward Scaling
```
SpeedBonus = log10(StepsSpent) × 10

Example:
- 1,000 steps → +30% speed
- 10,000 steps → +40% speed
- 100,000 steps → +50% speed
```

### Tournament Difficulty
```
OpponentPower = BasePower × (1.05 ^ VictoryCount) × EnvironmentTier

Expected Loss Point = when OpponentPower > PlayerPower × 1.2
```

---

*Document Version: 1.0*
*Last Updated: 2026-02-04*

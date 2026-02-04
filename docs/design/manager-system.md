# Manager & Automation System

## Design Philosophy

The manager system transforms active grinding into passive progression. It creates an incremental/idle layer that respects player time while maintaining the value of active play. Managers are expensive enough to feel earned, effective enough to feel worthwhile, and hierarchical enough to create long-term goals.

---

## Core Principles

1. **Automation is a Reward, Not a Replacement**
   - Managers produce at reduced efficiency vs. active play
   - Active players always progress faster
   - Automation extends session value into offline time

2. **Hierarchical Depth Creates Goals**
   - Tier 1 managers are accessible early
   - Higher tiers require significant investment
   - Each tier multiplies effectiveness of lower tiers

3. **Managers Cost Gold, Not Premium Currency**
   - All managers purchasable with in-game gold
   - Creates gold sink for economy balance
   - Rewards active combat loop participation

---

## Manager Tiers

### Tier 1: Task Managers

Task Managers automate a single training activity at reduced efficiency.

#### Mining Foreman
| Property | Value |
|----------|-------|
| Automates | Mining (Strength training) |
| Base Cost | 1,000 Gold |
| Efficiency | 50% of active casual mining |
| Stack Cost | Previous × 2 |
| Stack Efficiency | Diminishing (+50%, +25%, +12.5%, ...) |

#### Course Instructor
| Property | Value |
|----------|-------|
| Automates | Obstacle Courses (Dexterity training) |
| Base Cost | 1,000 Gold |
| Efficiency | 50% of active basic course |
| Stack Cost | Previous × 2 |
| Stack Efficiency | Diminishing |

#### Meditation Guide
| Property | Value |
|----------|-------|
| Automates | Meditation (Focus training) |
| Base Cost | 1,000 Gold |
| Efficiency | 50% of active light meditation |
| Stack Cost | Previous × 2 |
| Stack Efficiency | Diminishing |

#### Running Coach
| Property | Value |
|----------|-------|
| Automates | Distance Running (Endurance training) |
| Base Cost | 1,000 Gold |
| Efficiency | 50% of active jogging |
| Stack Cost | Previous × 2 |
| Stack Efficiency | Diminishing |

### Stacking Formula

```
Total Efficiency = Sum of individual efficiencies

Manager 1: 50%
Manager 2: 50% + 25% = 75%
Manager 3: 75% + 12.5% = 87.5%
Manager 4: 87.5% + 6.25% = 93.75%
Manager 5: 93.75% + 3.125% = 96.875%
...
Asymptotic limit: 100% (never reached)
```

### Cost Scaling

| Manager # | Cost | Total Investment |
|-----------|------|------------------|
| 1 | 1,000 | 1,000 |
| 2 | 2,000 | 3,000 |
| 3 | 4,000 | 7,000 |
| 4 | 8,000 | 15,000 |
| 5 | 16,000 | 31,000 |
| 10 | 512,000 | 1,023,000 |

**Design Intent:** Early managers are cheap and impactful. Later managers provide diminishing returns at exponential costs, creating natural stopping points.

---

### Tier 2: Department Managers

Department Managers oversee multiple Task Managers, providing efficiency bonuses to all managed units.

#### Physical Director
| Property | Value |
|----------|-------|
| Manages | Mining Foremen, Running Coaches |
| Cost | 10,000 Gold |
| Unlock Requirement | Own 2+ Task Managers in Physical category |
| Bonus | +25% efficiency to all managed Task Managers |
| Stack Limit | 1 (unique) |

#### Mental Director
| Property | Value |
|----------|-------|
| Manages | Course Instructors, Meditation Guides |
| Cost | 10,000 Gold |
| Unlock Requirement | Own 2+ Task Managers in Mental category |
| Bonus | +25% efficiency to all managed Task Managers |
| Stack Limit | 1 (unique) |

### Department Manager Effect

```
With Physical Director:
- Mining Foreman efficiency: 50% × 1.25 = 62.5%
- Running Coach efficiency: 50% × 1.25 = 62.5%
- Combined with stacking:
  - 3 Mining Foremen: 87.5% × 1.25 = 109.375% (caps at 100%)
```

**Cap Rule:** Total automation efficiency cannot exceed 100% of the base active rate. Managers approach but never surpass active play effectiveness.

---

### Tier 3: Executive Managers

Executive Managers manage Department Managers and provide powerful bonuses.

#### VP of Training
| Property | Value |
|----------|-------|
| Manages | Physical Director, Mental Director |
| Cost | 100,000 Gold |
| Unlock Requirement | Own both Department Managers |
| Bonuses | +50% efficiency to all managed, Auto-hire feature |
| Stack Limit | 1 (unique) |

**Auto-Hire Feature:**
- Every 10,000 gold earned, automatically purchases the cheapest available Task Manager
- Can be toggled on/off
- Does not spend gold reserved by player

### Executive Manager Effect

```
With VP of Training (and both Directors):
- Base Task Manager: 50%
- With Department Director: 50% × 1.25 = 62.5%
- With VP of Training: 62.5% × 1.5 = 93.75%

Maximum achievable passive efficiency: 93.75% of active rate
```

---

### Tier 4: CEO

The CEO is the ultimate manager, overseeing all operations and unlocking prestige features.

#### Chief Executive Officer
| Property | Value |
|----------|-------|
| Manages | All Executive Managers |
| Cost | 1,000,000 Gold |
| Unlock Requirement | Own VP of Training, Complete 1 full theme cycle |
| Bonuses | Prestige multiplier, New manager tier unlock |
| Stack Limit | 1 (unique) |

**Prestige System:**

Upon hiring the CEO:
1. Player can trigger "Corporate Restructuring" (prestige)
2. All managers are reset (fired)
3. Player receives Prestige Points based on manager count
4. Prestige multiplier increases permanently

```
Prestige Multiplier = 1.0 + (0.1 × Prestige Level)

Level 1: 1.1× all manager efficiency
Level 2: 1.2× all manager efficiency
Level 5: 1.5× all manager efficiency
Level 10: 2.0× all manager efficiency
```

**New Manager Tier (Post-Prestige):**

After first prestige, unlock Tier 5: Regional Managers

---

### Tier 5: Regional Managers (Post-Prestige)

Regional Managers extend automation to environment-specific activities.

#### Regional Resource Manager
| Property | Value |
|----------|-------|
| Scope | Single environment |
| Cost | 50,000 Gold |
| Effect | Auto-collect environment resources |
| Limit | 1 per environment |

#### Regional Combat Manager
| Property | Value |
|----------|-------|
| Scope | Single environment |
| Cost | 100,000 Gold |
| Effect | Auto-farm weak mobs (25% loot efficiency) |
| Limit | 1 per environment |

#### Regional Tile Manager
| Property | Value |
|----------|-------|
| Scope | Single environment |
| Cost | 25,000 Gold |
| Effect | Auto-optimize tile placement |
| Limit | 1 per environment |

---

## Manager Efficiency Formula

### Complete Calculation

```
Final Efficiency = BaseEfficiency
                 × StackMultiplier
                 × DepartmentBonus
                 × ExecutiveBonus
                 × PrestigeMultiplier

Where:
- BaseEfficiency = 0.5 (50%)
- StackMultiplier = Sum of (0.5^n) for n managers
- DepartmentBonus = 1.25 if Department Manager owned, else 1.0
- ExecutiveBonus = 1.5 if VP of Training owned, else 1.0
- PrestigeMultiplier = 1.0 + (0.1 × PrestigeLevel)

Cap: Final Efficiency ≤ 1.0 (100%)
```

### Example Calculations

**Early Game (1 Mining Foreman):**
```
0.5 × 1.0 × 1.0 × 1.0 × 1.0 = 50%
```

**Mid Game (3 Mining Foremen + Physical Director):**
```
Stack: 0.5 + 0.25 + 0.125 = 0.875
0.875 × 1.25 × 1.0 × 1.0 = 109% → capped to 100%
```

**Late Game (5 Mining Foremen + Physical Director + VP + Prestige 2):**
```
Stack: 0.5 + 0.25 + 0.125 + 0.0625 + 0.03125 = 0.96875
0.96875 × 1.25 × 1.5 × 1.2 = 218% → capped to 100%
```

**Note:** The cap ensures automation never surpasses active play value.

---

## Manager Acquisition Flow

### Unlock Tree

```
                    ┌─────────────────┐
                    │      CEO        │
                    │  (1,000,000g)   │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │  VP of Training │
                    │   (100,000g)    │
                    └────────┬────────┘
                             │
           ┌─────────────────┴─────────────────┐
           │                                   │
    ┌──────┴──────┐                     ┌──────┴──────┐
    │  Physical   │                     │   Mental    │
    │  Director   │                     │  Director   │
    │  (10,000g)  │                     │  (10,000g)  │
    └──────┬──────┘                     └──────┬──────┘
           │                                   │
     ┌─────┴─────┐                       ┌─────┴─────┐
     │           │                       │           │
┌────┴────┐ ┌────┴────┐           ┌────┴────┐ ┌────┴────┐
│ Mining  │ │ Running │           │ Course  │ │  Med.   │
│ Foreman │ │  Coach  │           │Instruct.│ │  Guide  │
│(1,000g) │ │(1,000g) │           │(1,000g) │ │(1,000g) │
└─────────┘ └─────────┘           └─────────┘ └─────────┘
```

### Recommended Acquisition Order

**Phase 1: Foundation (0-5,000 Gold)**
1. First Mining Foreman (Strength is universal)
2. First Running Coach (Endurance helps all themes)

**Phase 2: Coverage (5,000-15,000 Gold)**
3. First Course Instructor (Dexterity for Armed/Ranged)
4. First Meditation Guide (Focus for Energy)
5. Physical Director unlock

**Phase 3: Scaling (15,000-50,000 Gold)**
6. Mental Director unlock
7. Second manager in each category
8. Third manager in priority categories

**Phase 4: Optimization (50,000-200,000 Gold)**
9. VP of Training
10. Fill out manager roster
11. Approach efficiency caps

**Phase 5: Prestige (200,000+ Gold)**
12. CEO acquisition
13. First prestige
14. Regional manager expansion

---

## Manager UI Design

### Manager Panel Layout

```
┌─────────────────────────────────────────────────────────┐
│                    MANAGER OVERVIEW                      │
├─────────────────────────────────────────────────────────┤
│  Prestige Level: 2          Multiplier: 1.2×            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─── PHYSICAL ───┐        ┌─── MENTAL ────┐           │
│  │                │        │               │           │
│  │ Mining: 3/∞    │        │ Course: 2/∞   │           │
│  │ [====----] 87% │        │ [===-----] 75%│           │
│  │                │        │               │           │
│  │ Running: 2/∞   │        │ Meditate: 2/∞ │           │
│  │ [===-----] 75% │        │ [===-----] 75%│           │
│  │                │        │               │           │
│  │ Director: ✓    │        │ Director: ✓   │           │
│  │ Bonus: +25%    │        │ Bonus: +25%   │           │
│  └────────────────┘        └───────────────┘           │
│                                                         │
│  Executive: VP of Training ✓    Bonus: +50%            │
│  CEO: ✗ (Need 1M Gold)                                 │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  [Hire Mining Foreman - 8,000g]  [Hire Instructor...]   │
└─────────────────────────────────────────────────────────┘
```

### Efficiency Breakdown Tooltip

```
┌─────────────────────────────────────┐
│     MINING EFFICIENCY BREAKDOWN     │
├─────────────────────────────────────┤
│ Base (3 Foremen):           87.5%   │
│ Physical Director:          ×1.25   │
│ VP of Training:             ×1.50   │
│ Prestige Level 2:           ×1.20   │
├─────────────────────────────────────┤
│ Calculated:                 196.9%  │
│ Capped at:                  100.0%  │
├─────────────────────────────────────┤
│ Strength/Hour:              10.0    │
│ (Active would be:           10.0)   │
└─────────────────────────────────────┘
```

---

## Economic Balance

### Gold Generation vs. Manager Costs

| Activity | Gold/Hour (Active) |
|----------|-------------------|
| Early Combat | 200-500 |
| Mid Combat | 1,000-3,000 |
| Late Combat | 5,000-15,000 |
| Optimized Farming | 20,000+ |

### Time to Acquire (Active Play)

| Manager | Early Game | Mid Game | Late Game |
|---------|------------|----------|-----------|
| First Task Manager | 2-5 hours | 20-60 min | 5-15 min |
| Department Manager | 20-50 hours | 3-10 hours | 40-120 min |
| VP of Training | 200+ hours | 30-100 hours | 5-20 hours |
| CEO | 2000+ hours | 300+ hours | 50-200 hours |

**Design Intent:** Early managers are achievable in first sessions. CEO is a long-term goal requiring significant investment.

### Gold Sink Analysis

Manager system as gold sink:
- Prevents gold inflation
- Creates meaningful spending decisions
- Rewards efficient farming
- Provides clear goals for gold accumulation

---

## Integration with Other Systems

### Manager Impact on Combat Themes

Managers don't directly affect combat, but:
- Automated Strength training benefits Unarmed/Armed
- Automated Dexterity training benefits Armed/Ranged
- Automated Focus training benefits Ranged/Energy
- Automated Endurance training benefits all themes

**Result:** Manager investment makes theme switching smoother.

### Manager Impact on Speed Loop

Managers don't generate steps, but:
- Endurance managers increase stamina (longer active runs)
- Regional Tile Managers optimize routes
- Freed active time can focus on movement

### Manager Impact on Environment Progression

Managers support progression by:
- Maintaining stat growth during breaks
- Preparing controlling variables for next theme
- Generating passive readiness for new challenges

---

## Anti-Exploitation Measures

### Preventing AFK Abuse

1. **Efficiency Cap:** Managers never exceed active play value
2. **No Gold Generation:** Managers don't produce gold
3. **Combat Exclusion:** Managers don't fight or farm loot
4. **Diminishing Returns:** Stacking has hard limits

### Preventing Pay-to-Win

1. **Gold Only:** No premium currency purchases for managers
2. **Time Gates:** Unlock requirements prevent rushing
3. **Prestige Resets:** Progress requires engagement, not just spending

---

*Document Version: 1.0*
*Last Updated: 2026-02-04*

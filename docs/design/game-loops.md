# Game Loops & System Interconnections

## Overview

MyRPG is built on interlocking gameplay loops operating at different timescales. Each loop reinforces others, creating a cohesive progression experience where no system exists in isolation.

---

## Loop Hierarchy

```
┌────────────────────────────────────────────────────────────────┐
│                     LONG-TERM LOOPS (Hours)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 ENVIRONMENT CYCLE                         │  │
│  │     Master → Boss → Tournament → Defeat → New Master     │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  PRESTIGE CYCLE                           │  │
│  │       Build → Optimize → Reset → Multiply → Rebuild      │  │
│  └──────────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────────┤
│                    MEDIUM-TERM LOOPS (Minutes)                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  PEDOMETER CYCLE                          │  │
│  │         Move → Accumulate → Decide → Spend → Faster      │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   UPGRADE CYCLE                           │  │
│  │       Farm → Collect Gold → Purchase → Return Stronger   │  │
│  └──────────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────────┤
│                     SHORT-TERM LOOPS (Seconds)                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    COMBAT LOOP                            │  │
│  │         Engage → Attack → Loot → Heal → Engage           │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   TRAINING LOOP                           │  │
│  │       Activity → Minigame → Variable Gain → Repeat       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## Short-Term Loops (Seconds)

### Combat Loop

**Duration:** 5-30 seconds per encounter

```
     ┌────────┐
     │ ENGAGE │
     └────┬───┘
          │
          ▼
     ┌────────┐      ┌────────┐
     │ ATTACK │ ───► │  LOOT  │
     └────┬───┘      └────┬───┘
          │               │
          │    ┌──────────┘
          │    │
          ▼    ▼
     ┌────────────┐
     │    HEAL    │
     │ (if needed)│
     └─────┬──────┘
           │
           ▼
     ┌────────────┐
     │ NEXT TARGET│
     └────────────┘
```

**Inputs:**
- Player Power Level (determines viable opponents)
- Current combat theme (determines tactics)
- Equipment and consumables

**Outputs:**
- Loot drops (sellable for gold)
- Combat XP (increases theme mastery)
- Power Level increments
- Resource consumption (consumables, energy)

**Player Decisions:**
- Target selection (risk vs. reward)
- Ability timing (theme-specific mechanics)
- Resource management (when to heal, retreat)

---

### Training Loop

**Duration:** 10-60 seconds per activity cycle

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   SELECT    │ ──► │   PERFORM   │ ──► │    GAIN     │
│  ACTIVITY   │     │  MINIGAME   │     │  VARIABLE   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┘
                    │
                    ▼
              ┌───────────┐
              │  REPEAT   │
              │     or    │
              │  SWITCH   │
              └───────────┘
```

**Activities:**
| Activity | Variable | Minigame | Active Rate |
|----------|----------|----------|-------------|
| Mining | Strength | Timing clicks | 10-50/hour |
| Obstacle Course | Dexterity | Navigation | 10-50/hour |
| Meditation | Focus | Breathing rhythm | 10-50/hour |
| Distance Running | Endurance | Pace maintenance | 10-50/hour |

**Player Decisions:**
- Which variable to prioritize
- Active engagement level (casual vs. focused)
- When to switch to combat or movement

---

## Medium-Term Loops (Minutes)

### Pedometer Cycle

**Duration:** 30-60 minutes between spending decisions

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│   MOVE   │ ──► │ACCUMULATE│ ──► │  DECIDE  │
│          │     │  STEPS   │     │          │
└──────────┘     └──────────┘     └────┬─────┘
                                       │
                 ┌─────────────────────┴─────────────────────┐
                 │                                           │
                 ▼                                           ▼
          ┌────────────┐                            ┌────────────┐
          │   SPEND    │                            │    WAIT    │
          │    ALL     │                            │   (more)   │
          └─────┬──────┘                            └─────┬──────┘
                │                                         │
                ▼                                         │
          ┌────────────┐                                  │
          │   SPEED    │                                  │
          │  UPGRADE   │                                  │
          └─────┬──────┘                                  │
                │                                         │
                └─────────────────┬───────────────────────┘
                                  │
                                  ▼
                           ┌────────────┐
                           │   FASTER   │
                           │  MOVEMENT  │
                           └────────────┘
```

**The Tension:**
- Spending early: Smaller speed bonus, but sooner
- Waiting longer: Larger speed bonus, but delayed

**Spending Milestones:**
| Steps | Speed Bonus | Typical Wait |
|-------|-------------|--------------|
| 1,000 | +10% | 10-15 min |
| 5,000 | +20% | 30-45 min |
| 10,000 | +25% | 60-90 min |
| 50,000 | +35% | 4-6 hours |
| 100,000 | +40% | 8-12 hours |

**Cap Behavior:**
Once speed cap is reached (from pedometer), spending grants:
- Power Level achievement bonuses instead
- Cosmetic rewards
- Achievement completions

---

### Upgrade Cycle

**Duration:** 15-45 minutes between significant purchases

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│   FARM   │ ──► │ COLLECT  │ ──► │ PURCHASE │
│  COMBAT  │     │   GOLD   │     │ UPGRADE  │
└──────────┘     └──────────┘     └────┬─────┘
                                       │
                                       ▼
                                ┌────────────┐
                                │  STRONGER  │
                                │   COMBAT   │
                                └─────┬──────┘
                                      │
                                      ▼
                                ┌────────────┐
                                │  HARDER    │
                                │  CONTENT   │
                                └────────────┘
```

**Gold Sinks (by priority):**
1. Equipment upgrades (direct power)
2. Manager hiring (passive progress)
3. Speed tiles (movement optimization)
4. Consumables (temporary boosts)

**Player Decisions:**
- Current power vs. passive income (equipment vs. managers)
- Combat efficiency vs. exploration (gear vs. tiles)
- Immediate power vs. long-term scaling

---

## Long-Term Loops (Hours)

### Environment Cycle

**Duration:** 2-4 hours per environment

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────────────┐ │
│  │  TRAIN  │──►│  FARM   │──►│  BOSS   │──►│   TOURNAMENT    │ │
│  │   with  │   │  MOBS   │   │  FIGHT  │   │   (Infinite)    │ │
│  │ MASTER  │   │         │   │         │   │                 │ │
│  └─────────┘   └─────────┘   └─────────┘   └────────┬────────┘ │
│                                                     │          │
│                              ┌──────────────────────┘          │
│                              ▼                                 │
│                        ┌───────────┐                           │
│                        │  DEFEAT   │ ◄── (Expected)            │
│                        │  (Loss)   │                           │
│                        └─────┬─────┘                           │
│                              │                                 │
│           ┌──────────────────┴──────────────────┐              │
│           ▼                                     ▼              │
│     ┌───────────┐                        ┌───────────┐         │
│     │    NEW    │                        │    NEW    │         │
│     │  MASTER   │                        │   ZONE    │         │
│     │  (Theme)  │                        │  UNLOCK   │         │
│     └───────────┘                        └───────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Phase Breakdown:**

| Phase | Duration | Primary Activity |
|-------|----------|------------------|
| Training | 15-30 min | Learn new theme, build variables |
| Farming | 45-90 min | Combat mobs, collect gold/loot |
| Boss | 5-15 min | Challenge run, gear check |
| Tournament | 30-60 min | Push limits, collect rewards |

**Defeat as Progression:**
- Tournament is designed to be unwinnable
- Difficulty scales infinitely (+5% per victory)
- Loss triggers positive outcome (new content)
- Removes frustration from "failure"

---

### Prestige Cycle

**Duration:** 50-200 hours between prestiges

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌─────────────┐                                                │
│  │    BUILD    │ ─── Hire managers, accumulate bonuses          │
│  └──────┬──────┘                                                │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐                                                │
│  │  OPTIMIZE   │ ─── Fill out manager tree, approach caps       │
│  └──────┬──────┘                                                │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐                                                │
│  │   ACQUIRE   │ ─── Purchase CEO (1M gold)                     │
│  │     CEO     │                                                │
│  └──────┬──────┘                                                │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐                                                │
│  │   PRESTIGE  │ ─── Reset managers, gain multiplier            │
│  └──────┬──────┘                                                │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────┐                                                │
│  │   REBUILD   │ ─── Re-hire with permanent boost               │
│  └─────────────┘                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Prestige Rewards:**
| Level | Multiplier | Unlock |
|-------|------------|--------|
| 1 | 1.1× | Regional Managers |
| 2 | 1.2× | Auto-sell common loot |
| 3 | 1.3× | Bulk manager hiring |
| 5 | 1.5× | Manager specializations |
| 10 | 2.0× | Ultimate manager tier |

---

## System Interconnections

### The Grand Loop Diagram

```
                              ┌──────────────┐
                              │ POWER LEVEL  │
                              │  (Primary)   │
                              └──────┬───────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│    COMBAT     │◄────────►│   MOVEMENT    │◄────────►│   TRAINING    │
│    SYSTEM     │          │    SYSTEM     │          │    SYSTEM     │
└───────┬───────┘          └───────┬───────┘          └───────┬───────┘
        │                          │                          │
        │  ┌───────────────────────┼───────────────────────┐  │
        │  │                       │                       │  │
        ▼  ▼                       ▼                       ▼  ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│     GOLD      │          │   PEDOMETER   │          │  CONTROLLING  │
│   (Currency)  │          │    (Steps)    │          │   VARIABLES   │
└───────┬───────┘          └───────┬───────┘          └───────┬───────┘
        │                          │                          │
        │         ┌────────────────┴────────────────┐         │
        │         │                                 │         │
        ▼         ▼                                 ▼         ▼
┌─────────────────────┐                    ┌─────────────────────┐
│      MANAGERS       │                    │    SPEED/ACCESS     │
│   (Automation)      │                    │  (New Environments) │
└─────────────────────┘                    └─────────────────────┘
        │                                           │
        │                                           │
        └───────────────────┬───────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  ENVIRONMENT  │
                    │  PROGRESSION  │
                    └───────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ COMBAT THEME  │
                    │    CYCLING    │
                    └───────────────┘
```

### Connection Matrix

| System A | System B | Connection Type | Description |
|----------|----------|-----------------|-------------|
| Combat | Gold | Direct Output | Combat drops loot → sell for gold |
| Combat | Power Level | Direct Output | Combat victories increase Power Level |
| Combat | Theme Mastery | Direct Output | Using a theme increases its mastery |
| Movement | Pedometer | Direct Output | Movement increases step count |
| Pedometer | Speed | Spend Conversion | Spending steps grants speed upgrades |
| Speed | Environment | Gate Requirement | Higher environments require more speed |
| Training | Variables | Direct Output | Activities increase controlling variables |
| Variables | Combat | Scaling Factor | Variables affect combat effectiveness |
| Gold | Managers | Purchase | Gold buys manager automation |
| Managers | Variables | Automation | Managers passively increase variables |
| Managers | Gold | Sink | Managers consume gold (economy balance) |
| Environment | Theme | Forced Transition | New environment = new combat theme |
| Theme | Training | Priority Shift | Current theme affects which variables matter most |

---

## Feedback Loops

### Positive Feedback (Acceleration)

**Combat → Gold → Equipment → Better Combat**
- Winning fights earns gold
- Gold buys better gear
- Better gear wins harder fights
- Harder fights drop more gold

**Movement → Steps → Speed → Faster Movement → More Steps**
- Moving accumulates steps
- Steps buy speed upgrades
- Faster speed means more distance
- More distance means more steps per time

**Training → Variables → Theme Power → Easier Training**
- Training builds variables
- Variables make combat easier
- Easier combat means less interruption
- More uninterrupted training time

### Negative Feedback (Balance)

**Power Level → Opponent Scaling**
- Higher Power Level = stronger enemies
- Prevents trivializing content
- Maintains challenge curve

**Speed Upgrades → Diminishing Returns**
- Each upgrade gives less than the last
- Prevents runaway acceleration
- Maintains pedometer decision tension

**Manager Efficiency → Cap**
- Stacking managers has diminishing returns
- Can never exceed 100% active efficiency
- Preserves value of active play

---

## Player Experience Curves

### Early Game (Hours 1-10)

```
Engagement:  ████████████████████████████████ High
                Combat and exploration

Progression: ████████████████████████████████ High
                Rapid Power Level gains

Decision:    ██████████░░░░░░░░░░░░░░░░░░░░░░ Low
                Limited options, learn systems

Systems:     Combat, Training, Basic Gold loop
```

### Mid Game (Hours 10-50)

```
Engagement:  ████████████████████████░░░░░░░░ Medium-High
                Combat + Manager optimization

Progression: ████████████████░░░░░░░░░░░░░░░░ Medium
                Slower but steady gains

Decision:    ████████████████████████████████ High
                Many competing priorities

Systems:     All systems active, theme cycling begins
```

### Late Game (Hours 50+)

```
Engagement:  ████████████████████████████████ Variable
                Active bursts + passive accumulation

Progression: ████████████░░░░░░░░░░░░░░░░░░░░ Slow
                Incremental optimization

Decision:    ████████████████████░░░░░░░░░░░░ Medium
                Prestige timing, mastery completion

Systems:     Prestige loop, environment mastery, completionism
```

---

## Loop Failure Prevention

### What Keeps Players Engaged

| Loop | Failure Risk | Prevention Mechanism |
|------|--------------|---------------------|
| Combat | Gets boring | Theme cycling forces variety |
| Training | Feels like grind | Manager automation takes over |
| Pedometer | Decision paralysis | Clear milestone rewards |
| Environment | Stuck at difficulty | Defeat unlocks new content |
| Economy | Gold overflow | Manager costs as sink |

### Restart Points

If a player returns after break:
1. Managers continued working (passive progress)
2. Power Level didn't decay (no punishment)
3. Current environment still available (no lost progress)
4. Clear next objective (always a "what to do")

---

## Appendix: Loop Timing Summary

| Loop | Duration | Engagement Type |
|------|----------|-----------------|
| Combat Encounter | 5-30s | Active |
| Training Cycle | 10-60s | Active/Semi-Active |
| Pedometer Decision | 30-60 min | Active |
| Upgrade Purchase | 15-45 min | Active |
| Environment Completion | 2-4 hours | Active |
| Theme Cycle | 8-16 hours | Background |
| Prestige | 50-200 hours | Milestone |

---

*Document Version: 1.0*
*Last Updated: 2026-02-04*

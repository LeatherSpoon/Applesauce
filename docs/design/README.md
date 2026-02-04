# MyRPG Game Design Documentation

## Overview

MyRPG is a loop-driven RPG featuring:
- **Themed environments** with Masters, mobs, and bosses
- **Combat theme cycling** (Unarmed → Armed → Ranged → Energy)
- **Pedometer-based progression** for speed upgrades
- **Manager automation** for idle/incremental progression

---

## Design Documents

| Document | Description |
|----------|-------------|
| [Core Currencies](./core-currencies.md) | Power Level, Pedometer, Gold, and secondary resources |
| [Combat Themes](./combat-themes.md) | The four combat styles and controlling variables |
| [Manager System](./manager-system.md) | Automation hierarchy and prestige mechanics |
| [Game Loops](./game-loops.md) | System interconnections and player experience flow |

---

## Quick Reference

### Core Currencies

| Currency | Type | Primary Use |
|----------|------|-------------|
| **Power Level** | Always-increasing | Combat strength |
| **Pedometer Count** | Accumulate & spend-all | Speed upgrades |
| **Gold** | Spendable | Equipment, managers, tiles |

### Combat Themes

| Theme | Primary Stats | Unlocked By |
|-------|---------------|-------------|
| Unarmed | Strength, Endurance | Default |
| Armed | Strength, Dexterity | Unarmed Mastery 10 |
| Ranged | Dexterity, Focus | Armed Mastery 10 |
| Energy | Focus, Endurance | Ranged Mastery 10 |

### Controlling Variables

| Variable | Training Activity | Benefits |
|----------|-------------------|----------|
| Strength | Mining | Unarmed, Armed damage |
| Dexterity | Obstacle Courses | Ranged accuracy, Armed speed |
| Focus | Meditation | Energy capacity, Ranged range |
| Endurance | Distance Running | HP, all theme defense |

### Manager Tiers

```
Tier 1: Task Managers (1,000g) → Automate training
Tier 2: Department Managers (10,000g) → +25% efficiency
Tier 3: VP of Training (100,000g) → +50% efficiency
Tier 4: CEO (1,000,000g) → Prestige system
```

---

## Design Principles

1. **Loops Reinforce Loops** - Every system feeds into others
2. **Defeat is Progression** - Tournament loss unlocks new content
3. **Active > Passive** - Automation helps but never surpasses active play
4. **Theme Variety** - Forced cycling prevents over-specialization
5. **Clear Goals** - Always a next objective visible

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-04 | Initial design documentation |

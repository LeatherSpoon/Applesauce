# Combat Themes & Controlling Variables

## Design Philosophy

Combat themes provide strategic variety while controlling variables create a unified progression system. The player cannot multi-class during combat, but investments in controlling variables benefit all themes—creating incentive for broad development even when specializing.

---

## The Four Combat Themes

### Unarmed Combat

**Identity:** The foundational combat style. Raw, fast, personal.

| Attribute | Value |
|-----------|-------|
| Range | Melee (1 tile) |
| Attack Speed | Fast (0.5s base) |
| Damage per Hit | Low |
| DPS Potential | Medium-High (via combos) |

**Primary Scaling:**
- Strength (70%): Raw damage
- Endurance (30%): Combo sustain

**Unique Mechanic: Combo Chains**
```
Hit 1 → Hit 2 → Hit 3 → Hit 4 → Hit 5 (Finisher)
  ×1.0   ×1.1   ×1.2   ×1.4   ×2.0

- Taking damage breaks the combo
- Combo resets after 2 seconds of no attacks
- Endurance increases combo window duration
```

**Mastery Bonuses (per 10 levels):**
| Level | Bonus |
|-------|-------|
| 10 | Combo window +0.5s |
| 20 | Finisher damage ×2.5 |
| 30 | 6th hit added to combo |
| 40 | Strength gains +10% effectiveness |
| 50 | Unlock "Flurry" - 10 rapid hits, 30s cooldown |

---

### Armed Combat

**Identity:** The balanced warrior. Versatile, equipment-focused.

| Attribute | Value |
|-----------|-------|
| Range | Melee to Short (1-2 tiles, weapon dependent) |
| Attack Speed | Medium (0.8s base) |
| Damage per Hit | Medium-High |
| DPS Potential | Medium (consistent) |

**Primary Scaling:**
- Strength (50%): Base damage
- Dexterity (50%): Attack speed, critical chance

**Unique Mechanic: Weapon Classes**

| Weapon Class | Speed | Damage | Range | Special |
|--------------|-------|--------|-------|---------|
| Daggers | Fast | Low | 1 | +25% crit chance |
| Swords | Medium | Medium | 1 | Balanced, +10% all stats |
| Axes | Slow | High | 1 | Armor penetration |
| Spears | Medium | Medium | 2 | First-strike advantage |
| Hammers | Very Slow | Very High | 1 | Stun chance |

**Weapon Switching:**
- Can carry 2 weapons
- Swap costs 1 attack cycle
- Creates tactical depth without breaking single-theme rule

**Mastery Bonuses (per 10 levels):**
| Level | Bonus |
|-------|-------|
| 10 | Weapon swap is instant |
| 20 | +15% damage with all weapon types |
| 30 | Carry 3 weapons |
| 40 | Dexterity gains +10% effectiveness |
| 50 | Unlock "Arsenal" - use all carried weapons in one attack |

---

### Ranged Combat

**Identity:** The precision striker. Positioning is everything.

| Attribute | Value |
|-----------|-------|
| Range | Medium to Long (3-8 tiles) |
| Attack Speed | Slow (1.2s base) |
| Damage per Hit | High |
| DPS Potential | High (at optimal range) |

**Primary Scaling:**
- Dexterity (60%): Accuracy, critical damage
- Focus (40%): Optimal range extension

**Unique Mechanic: Critical Distance**

```
Distance from Target → Damage Multiplier

Too Close (1-2 tiles): ×0.5 (panic penalty)
Close (3-4 tiles): ×0.8
Optimal (5-6 tiles): ×1.5 (sweet spot)
Far (7-8 tiles): ×1.0
Too Far (9+ tiles): Miss

Focus increases optimal range bracket width
```

**Ammunition System:**
| Ammo Type | Base Damage | Special | Capacity |
|-----------|-------------|---------|----------|
| Standard | ×1.0 | None | Unlimited |
| Piercing | ×0.8 | Ignores 50% armor | 50 |
| Explosive | ×1.5 | AoE splash | 20 |
| Tracking | ×0.9 | Cannot miss | 30 |

**Mastery Bonuses (per 10 levels):**
| Level | Bonus |
|-------|-------|
| 10 | Optimal range +1 tile each direction |
| 20 | Special ammo capacity +50% |
| 30 | "Quick Draw" - first attack instant after entering combat |
| 40 | Focus gains +10% effectiveness |
| 50 | Unlock "Sniper Mode" - ×3 damage, 3s charge time |

---

### Energy Combat

**Identity:** The mystical force. Resource management defines mastery.

| Attribute | Value |
|-----------|-------|
| Range | Variable (1-6 tiles, ability dependent) |
| Attack Speed | Variable |
| Damage per Hit | Variable (scaling with charge) |
| DPS Potential | Highest (with perfect management) |

**Primary Scaling:**
- Focus (60%): Energy pool size, regen rate
- Endurance (40%): Cooldown reduction, overheat resistance

**Unique Mechanic: Energy Pool**

```
Energy Pool = 100 + (Focus × 5)
Regen Rate = 5 + (Focus × 0.5) per second
Overheat Threshold = 80% of max

Above Overheat:
- Abilities cost +50% energy
- Regen stops for 3 seconds after each ability
```

**Energy Abilities:**
| Ability | Cost | Damage | Range | Special |
|---------|------|--------|-------|---------|
| Bolt | 10 | Low | 4 | Fast, spammable |
| Blast | 30 | Medium | 3 | Small AoE |
| Beam | 50 | High | 6 | Channeled, 2s duration |
| Nova | 80 | Very High | 2 (AoE) | Self-centered explosion |
| Surge | 100 | Extreme | 1 | Touch range, empties pool |

**Charge Attacks:**
- Hold attack button to charge
- Damage scales with charge time (up to ×3 at full charge)
- Full charge takes 3 seconds
- Overcharging (past full) causes self-damage

**Mastery Bonuses (per 10 levels):**
| Level | Bonus |
|-------|-------|
| 10 | Overheat threshold raised to 90% |
| 20 | New ability: "Siphon" - drain enemy energy |
| 30 | Charge attacks reach full 1s faster |
| 40 | Endurance gains +10% effectiveness |
| 50 | Unlock "Unlimited" - no energy costs for 10s, 60s cooldown |

---

## Controlling Variables Deep Dive

### Strength

**Training Activity:** Mining

| Activity Level | Gains/Hour | Active Requirement |
|----------------|------------|-------------------|
| Casual Mining | 10 | Click rocks |
| Focused Mining | 25 | Combo timing minigame |
| Deep Mining | 50 | Rare ore locations |

**Effects:**
| Beneficiary | Effect per Point |
|-------------|------------------|
| Unarmed | +2% damage |
| Armed | +2% damage |
| Ranged | +0.5% damage |
| Energy | +0.5% damage |
| General | +1 carry capacity |

**Manager Automation:**
- Mining Foreman: 50% of casual mining rate
- Can stack foremen (diminishing: 50%, 25%, 12.5%, ...)

---

### Dexterity

**Training Activity:** Obstacle Courses

| Activity Level | Gains/Hour | Active Requirement |
|----------------|------------|-------------------|
| Basic Course | 10 | Navigate obstacles |
| Advanced Course | 25 | Timed runs |
| Master Course | 50 | Perfect runs required |

**Effects:**
| Beneficiary | Effect per Point |
|-------------|------------------|
| Ranged | +1% accuracy, +1% crit damage |
| Armed | +0.5% attack speed, +0.5% crit chance |
| Unarmed | +0.5% attack speed |
| Energy | +0.5% cast speed |
| General | +0.5% movement efficiency |

**Manager Automation:**
- Course Instructor: 50% of basic course rate

---

### Focus

**Training Activity:** Meditation

| Activity Level | Gains/Hour | Active Requirement |
|----------------|------------|-------------------|
| Light Meditation | 10 | Idle in meditation zone |
| Deep Meditation | 25 | Breathing minigame |
| Transcendent | 50 | Perfect concentration |

**Effects:**
| Beneficiary | Effect per Point |
|-------------|------------------|
| Energy | +5 max energy, +0.5 regen/s |
| Ranged | +0.5 optimal range |
| Armed | +0.5% equipment effectiveness |
| Unarmed | +0.5% combo window |
| General | +1% training efficiency (all activities) |

**Manager Automation:**
- Meditation Guide: 50% of light meditation rate

---

### Endurance

**Training Activity:** Distance Running

| Activity Level | Gains/Hour | Active Requirement |
|----------------|------------|-------------------|
| Jogging | 10 | Move continuously |
| Running | 25 | Maintain pace threshold |
| Sprinting | 50 | Maximum speed runs |

**Effects:**
| Beneficiary | Effect per Point |
|-------------|------------------|
| Energy | +1% cooldown reduction |
| Unarmed | +0.5s combo window |
| Armed | +1% damage reduction |
| Ranged | +1% reload speed |
| General | +1 max HP, +1% stamina regen |

**Manager Automation:**
- Running Coach: 50% of jogging rate

---

## Theme Cycling System

### Why Themes Cycle

The game forces theme transitions to:
1. Ensure players experience all combat systems
2. Create value for broad controlling variable investment
3. Provide natural content pacing
4. Prevent early over-specialization

### Cycle Trigger: Tournament Defeat

When defeated in an infinite tournament:
```
Current Theme Index = (Current Theme Index + 1) mod 4

Theme Order:
0: Unarmed
1: Armed
2: Ranged
3: Energy
```

### New Master Assignment

Each new environment's Master teaches the next theme in sequence:

| Environment | Master | Theme | Combat Style |
|-------------|--------|-------|--------------|
| Forest Dojo | Master Chen | Unarmed | Flowing martial arts |
| Iron Fortress | Sir Aldric | Armed | Knightly combat |
| Wind Valley | Hawk Eye | Ranged | Precision archery |
| Crystal Spire | Archmage Vera | Energy | Arcane manipulation |
| Desert Temple | Grandmaster Kai | Unarmed | Desert monk style |
| ... | ... | ... | (cycle continues) |

### Returning to Previous Themes

**Players CAN return to earlier environments and use their established themes.**

This creates strategic choices:
- Farm easy content with mastered theme
- Challenge yourself with new theme in new content
- Optimize gold/hour vs progression

### Theme Viability Convergence

Over time, all themes become viable due to shared controlling variables:

```
Early Game:
- Unarmed: Strong (only option)
- Others: Locked

Mid Game:
- Current Theme: Strong (focused training)
- Previous Themes: Medium (passive variable gains)
- Locked Themes: Weak

Late Game (all themes unlocked):
- All Themes: Strong (variables benefit all)
- Specialization: Slight edge in mastery bonuses
```

**This is intentional.** Players should feel free to use any theme by late game, with marginal advantages for themes they've mastered.

---

## Theme-Environment Synergies

Certain environments favor certain themes:

| Environment Type | Favored Theme | Reason |
|------------------|---------------|--------|
| Tight corridors | Unarmed/Armed | No room for ranged |
| Open fields | Ranged | Positioning freedom |
| Enemy swarms | Energy | AoE effectiveness |
| Single bosses | Armed | Consistent DPS |
| Moving targets | Ranged (tracking) | Pursuit difficulty |
| Armored foes | Energy/Piercing | Bypass defenses |

This creates additional reasons to return to old content with new themes.

---

## Mastery System

### Mastery Points

Each theme has its own mastery level:
- Gained through combat using that theme
- Each level requires more XP than the last
- Max mastery level: 100

### Mastery XP Formula

```
XP Required = 100 × (Level ^ 1.5)

Level 1: 100 XP
Level 10: 3,162 XP
Level 50: 35,355 XP
Level 100: 100,000 XP
```

### Cross-Theme Mastery Bonus

High mastery in multiple themes grants a "Martial Versatility" bonus:

| Themes at 50+ | Bonus |
|---------------|-------|
| 2 | +5% damage all themes |
| 3 | +10% damage all themes |
| 4 | +20% damage all themes, unlock "Theme Shift" ability |

**Theme Shift (Ultimate Ability):**
- Instantly swap combat theme mid-fight
- 60 second cooldown
- Does not break the single-theme rule (one at a time)
- Rewards players who invest in multiple themes

---

*Document Version: 1.0*
*Last Updated: 2026-02-04*

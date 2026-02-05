#!/usr/bin/env python3
"""Interactive demo of MyRPG core systems."""

import time
from myrpg import GameState, GameEvent
from myrpg.combat import ThemeType, CombatEngine, Opponent
from myrpg.items import create_weapon, WeaponClass, ItemRarity, DropManager
from myrpg.movement import TileManager, TileType
from myrpg.persistence import SaveManager


def print_header(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def print_status(gs: GameState) -> None:
    print(f"\n  Power Level: {gs.power_level.value:,.1f}")
    print(f"  Gold: {gs.gold.amount:,}g")
    print(f"  Steps: {gs.pedometer.steps:,} (+{gs.pedometer.speed_bonus_percent:.1f}% speed)")
    print(f"  Current Theme: {gs.current_theme.name}")
    print(f"  Environment: {gs.current_environment.name} (Tier {gs.current_environment.tier})")


def demo_combat_loop(gs: GameState) -> None:
    """Demonstrate the combat loop."""
    print_header("COMBAT LOOP")
    print("  Farming mobs for gold and XP...\n")

    initial_gold = gs.gold.amount
    initial_mastery = gs.mastery.get_xp(gs.current_theme)

    for i in range(5):
        success, gold, xp = gs.farm_mob()
        if success:
            print(f"  [{i+1}] Victory! +{gold}g, +{xp:.1f} XP")
        else:
            print(f"  [{i+1}] Defeated!")
        time.sleep(0.2)

    print(f"\n  Total gold earned: {gs.gold.amount - initial_gold}g")
    print(f"  Mastery XP gained: {gs.mastery.get_xp(gs.current_theme) - initial_mastery:.1f}")


def demo_pedometer_loop(gs: GameState) -> None:
    """Demonstrate the pedometer/speed loop."""
    print_header("PEDOMETER LOOP")
    print("  Moving around to accumulate steps...\n")

    # Simulate movement
    for i in range(5):
        steps = 500
        gs.move(steps)
        print(f"  Moved {steps} steps. Total: {gs.pedometer.steps:,}")
        time.sleep(0.2)

    print(f"\n  Current speed: {gs.get_current_speed():.0f} units/sec")

    # Show what spending would give
    reward = gs.pedometer.calculate_spend_reward()
    print(f"  Spending all steps would grant: +{reward.speed_bonus_percent:.1f}% speed")


def demo_training_loop(gs: GameState) -> None:
    """Demonstrate the training/automation loop."""
    print_header("TRAINING & AUTOMATION")

    print("\n  Current stats:")
    print(f"    Strength: {gs.variables.strength.value:.1f}")
    print(f"    Dexterity: {gs.variables.dexterity.value:.1f}")
    print(f"    Focus: {gs.variables.focus.value:.1f}")
    print(f"    Endurance: {gs.variables.endurance.value:.1f}")

    # Give player some gold to hire managers
    gs.gold.add(5000, source="Demo bonus")
    print(f"\n  [Demo] Added 5,000g for demonstration")

    # Hire a manager
    if gs.hire_manager("strength"):
        print("  Hired Mining Foreman (automates Strength training)")

    # Simulate time passing
    print("\n  Simulating 1 hour of automation...")
    gains = gs.update(3600)  # 1 hour

    print(f"  Automated gains:")
    for stat, gain in gains.items():
        if gain > 0:
            print(f"    {stat.title()}: +{gain:.2f}")


def demo_loot_system() -> None:
    """Demonstrate the loot/equipment system."""
    print_header("LOOT & EQUIPMENT")

    dm = DropManager(base_drop_chance=1.0)  # Guaranteed drops for demo

    print("\n  Generating loot drops...\n")

    for i in range(5):
        drop = dm.roll_mob_drop(tier=2, theme=ThemeType.ARMED, source="Demo Mob")
        if drop:
            item = drop.item
            print(f"  [{i+1}] {item} - Sell value: {item.sell_value}g")
        time.sleep(0.2)

    # Show weapon creation
    print("\n  Creating specific weapons:")
    sword = create_weapon(WeaponClass.SWORD, tier=2, rarity=ItemRarity.RARE)
    print(f"    {sword}")
    print(f"      Damage: {sword.effective_damage:.1f}")
    print(f"      Speed modifier: {sword.speed_modifier}x")
    print(f"      Requires: {sword.required_theme.name} theme")


def demo_tiles_system() -> None:
    """Demonstrate the speed tiles system."""
    print_header("SPEED TILES")

    tm = TileManager()

    print("\n  Placing tiles in environment 1...")

    tiles = [
        (TileType.DIRT_PATH, (0, 0)),
        (TileType.COBBLESTONE, (1, 0)),
        (TileType.PAVED_ROAD, (2, 0)),
    ]

    for tile_type, pos in tiles:
        tile = tm.place_tile(tile_type, env_id=1, position=pos)
        print(f"    Placed {tile.tile_def.name} at {pos} (+{tile.speed_bonus*100:.0f}% speed)")

    print(f"\n  Route bonus: {tm.calculate_route_bonus(1):.2f}x speed")

    print("\n  Speed at different positions:")
    for x in range(4):
        speed = tm.get_speed_at_position(1, x, 0)
        print(f"    Position ({x}, 0): {speed:.2f}x speed")


def demo_combat_themes(gs: GameState) -> None:
    """Demonstrate combat theme mechanics."""
    print_header("COMBAT THEMES")

    print("\n  Theme progression: UNARMED -> ARMED -> RANGED -> ENERGY")
    print(f"\n  Current theme: {gs.current_theme.name}")
    print(f"  Mastery level: {gs.mastery.get_level(gs.current_theme)}")

    # Show unlocked themes
    unlocked = gs.get_unlocked_themes()
    print(f"\n  Unlocked themes: {', '.join(t.name for t in unlocked)}")

    # Show theme-specific mechanics
    engine = CombatEngine()

    print("\n  Theme-specific mechanics:")
    print("    UNARMED: Combo system (1.0x -> 1.1x -> 1.2x -> 1.4x -> 2.0x finisher)")
    print("    ARMED: Weapon switching, varied weapon types")
    print("    RANGED: Critical distance bonus, ammunition")
    print("    ENERGY: Energy pool management, charge attacks")


def demo_save_load(gs: GameState) -> None:
    """Demonstrate save/load functionality."""
    print_header("SAVE/LOAD SYSTEM")

    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        sm = SaveManager(Path(tmpdir))

        print(f"\n  Current power level: {gs.power_level.value:.1f}")
        print(f"  Current gold: {gs.gold.amount}")

        if sm.save_game(gs, slot=0):
            print("\n  Game saved to slot 0!")

        saves = sm.list_saves()
        print(f"  Available saves: {len(saves)}")

        for save in saves:
            print(f"    Slot {save['slot']}: Power {save['power_level']:.1f}")


def run_demo() -> None:
    """Run the full demo."""
    print("\n" + "="*60)
    print("         MyRPG - Interactive Demo")
    print("="*60)
    print("\n  A loop-driven RPG with:")
    print("    - Combat themes (Unarmed, Armed, Ranged, Energy)")
    print("    - Pedometer progression for speed upgrades")
    print("    - Manager automation system")
    print("    - Equipment and loot drops")
    print("    - Speed tile route optimization")

    # Create game state
    gs = GameState()

    # Boost power for demo
    gs.power_level.add(500)

    print_status(gs)

    # Run demos
    demo_combat_loop(gs)
    input("\n  Press Enter to continue...")

    demo_pedometer_loop(gs)
    input("\n  Press Enter to continue...")

    demo_training_loop(gs)
    input("\n  Press Enter to continue...")

    demo_loot_system()
    input("\n  Press Enter to continue...")

    demo_tiles_system()
    input("\n  Press Enter to continue...")

    demo_combat_themes(gs)
    input("\n  Press Enter to continue...")

    demo_save_load(gs)

    print_header("DEMO COMPLETE")
    print_status(gs)
    print("\n  Thanks for trying MyRPG!")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_demo()

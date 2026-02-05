"""Loot generation system for MyRPG."""

import random
from dataclasses import dataclass, field
from typing import Callable

from .base import Item, ItemRarity, Material, ItemType
from .weapons import Weapon, WeaponClass, create_weapon
from .armor import Armor, ArmorWeight, create_armor, EquipmentSlot
from ..combat.themes import ThemeType


# Rarity drop chances (cumulative)
RARITY_CHANCES = {
    1: [(0.70, ItemRarity.COMMON), (0.92, ItemRarity.UNCOMMON), (0.99, ItemRarity.RARE), (1.0, ItemRarity.EPIC)],
    2: [(0.60, ItemRarity.COMMON), (0.88, ItemRarity.UNCOMMON), (0.97, ItemRarity.RARE), (0.995, ItemRarity.EPIC), (1.0, ItemRarity.LEGENDARY)],
    3: [(0.50, ItemRarity.COMMON), (0.82, ItemRarity.UNCOMMON), (0.95, ItemRarity.RARE), (0.99, ItemRarity.EPIC), (1.0, ItemRarity.LEGENDARY)],
    4: [(0.40, ItemRarity.COMMON), (0.75, ItemRarity.UNCOMMON), (0.92, ItemRarity.RARE), (0.985, ItemRarity.EPIC), (1.0, ItemRarity.LEGENDARY)],
    5: [(0.30, ItemRarity.COMMON), (0.65, ItemRarity.UNCOMMON), (0.88, ItemRarity.RARE), (0.97, ItemRarity.EPIC), (1.0, ItemRarity.LEGENDARY)],
}


def get_rarity_for_tier(tier: int) -> ItemRarity:
    """Roll a random rarity based on tier."""
    tier = min(tier, 5)
    chances = RARITY_CHANCES.get(tier, RARITY_CHANCES[1])
    roll = random.random()

    for threshold, rarity in chances:
        if roll <= threshold:
            return rarity

    return ItemRarity.COMMON


@dataclass
class LootDrop:
    """Represents a single loot drop."""
    item: Item
    source: str


@dataclass
class LootTable:
    """Configurable loot table for generating drops."""
    tier: int = 1
    theme_bias: ThemeType | None = None
    weapon_chance: float = 0.30
    armor_chance: float = 0.25
    material_chance: float = 0.45
    _rng: random.Random = field(default_factory=random.Random, repr=False)

    def seed(self, seed: int) -> None:
        """Set random seed for reproducible drops."""
        self._rng.seed(seed)

    def generate_drop(self, source: str = "unknown") -> LootDrop | None:
        """
        Generate a random loot drop.

        Args:
            source: Description of drop source (e.g., "Forest Mob")

        Returns:
            LootDrop or None if nothing dropped
        """
        roll = self._rng.random()

        if roll < self.weapon_chance:
            item = self._generate_weapon()
        elif roll < self.weapon_chance + self.armor_chance:
            item = self._generate_armor()
        elif roll < self.weapon_chance + self.armor_chance + self.material_chance:
            item = self._generate_material()
        else:
            return None

        return LootDrop(item=item, source=source)

    def _generate_weapon(self) -> Weapon:
        """Generate a random weapon."""
        # Bias toward theme-appropriate weapons
        theme_weapons = {
            ThemeType.UNARMED: [WeaponClass.FIST],
            ThemeType.ARMED: [WeaponClass.DAGGER, WeaponClass.SWORD, WeaponClass.AXE, WeaponClass.SPEAR, WeaponClass.HAMMER],
            ThemeType.RANGED: [WeaponClass.BOW, WeaponClass.CROSSBOW],
            ThemeType.ENERGY: [WeaponClass.STAFF, WeaponClass.WAND],
        }

        if self.theme_bias and self._rng.random() < 0.6:
            weapon_classes = theme_weapons[self.theme_bias]
        else:
            weapon_classes = list(WeaponClass)

        weapon_class = self._rng.choice(weapon_classes)
        rarity = get_rarity_for_tier(self.tier)

        return create_weapon(weapon_class, self.tier, rarity)

    def _generate_armor(self) -> Armor:
        """Generate a random armor piece."""
        slot = self._rng.choice([
            EquipmentSlot.HEAD,
            EquipmentSlot.BODY,
            EquipmentSlot.HANDS,
            EquipmentSlot.FEET,
        ])

        # Bias weight based on theme
        if self.theme_bias == ThemeType.ENERGY:
            weights = [ArmorWeight.CLOTH, ArmorWeight.CLOTH, ArmorWeight.LIGHT]
        elif self.theme_bias == ThemeType.RANGED:
            weights = [ArmorWeight.LIGHT, ArmorWeight.LIGHT, ArmorWeight.MEDIUM]
        elif self.theme_bias == ThemeType.ARMED:
            weights = [ArmorWeight.MEDIUM, ArmorWeight.HEAVY, ArmorWeight.HEAVY]
        else:
            weights = list(ArmorWeight)

        weight = self._rng.choice(weights)
        rarity = get_rarity_for_tier(self.tier)

        return create_armor(slot, weight, self.tier, rarity)

    def _generate_material(self) -> Material:
        """Generate a random material."""
        materials = [
            ("Iron Ore", "Common crafting material"),
            ("Leather Scraps", "Used for light armor"),
            ("Arcane Dust", "Magical residue"),
            ("Monster Bone", "Strong crafting material"),
            ("Crystal Shard", "Resonates with energy"),
            ("Ancient Coin", "Valuable collectible"),
        ]

        name, desc = self._rng.choice(materials)
        rarity = get_rarity_for_tier(self.tier)
        tier_prefix = ["", "Quality ", "Fine ", "Superior ", "Perfect "][min(self.tier - 1, 4)]

        return Material(
            name=f"{tier_prefix}{name}",
            description=desc,
            rarity=rarity,
            base_sell_value=5 * self.tier,
            tier=self.tier,
        )


@dataclass
class DropManager:
    """Manages loot drops with configurable rates."""
    base_drop_chance: float = 0.5
    boss_drop_multiplier: float = 3.0
    _drop_count: int = field(default=0)
    _listeners: list[Callable[[LootDrop], None]] = field(
        default_factory=list, repr=False
    )

    def roll_mob_drop(
        self,
        tier: int,
        theme: ThemeType | None = None,
        source: str = "Mob",
    ) -> LootDrop | None:
        """
        Roll for a drop from a regular mob.

        Args:
            tier: Environment tier affecting quality
            theme: Current combat theme for biasing
            source: Source description

        Returns:
            LootDrop if successful, None otherwise
        """
        if random.random() > self.base_drop_chance:
            return None

        table = LootTable(tier=tier, theme_bias=theme)
        drop = table.generate_drop(source)

        if drop:
            self._drop_count += 1
            self._notify_listeners(drop)

        return drop

    def roll_boss_drop(
        self,
        tier: int,
        theme: ThemeType | None = None,
        source: str = "Boss",
    ) -> list[LootDrop]:
        """
        Roll for drops from a boss (guaranteed drops).

        Returns:
            List of loot drops (usually 2-4 items)
        """
        drops = []
        # Bosses drop 2-4 items
        num_drops = random.randint(2, 4)

        # Higher tier table for boss loot
        table = LootTable(tier=min(tier + 1, 5), theme_bias=theme)

        for _ in range(num_drops):
            drop = table.generate_drop(source)
            if drop:
                drops.append(drop)
                self._drop_count += 1
                self._notify_listeners(drop)

        return drops

    def roll_tournament_drop(
        self,
        tier: int,
        victories: int,
        theme: ThemeType | None = None,
    ) -> LootDrop | None:
        """
        Roll for drop from tournament opponent.

        Higher victories = better drop chance and quality.
        """
        # Increasing drop chance with victories
        adjusted_chance = min(self.base_drop_chance + victories * 0.02, 0.9)

        if random.random() > adjusted_chance:
            return None

        # Quality boost from victories
        quality_boost = victories // 5
        table = LootTable(tier=min(tier + quality_boost, 5), theme_bias=theme)

        drop = table.generate_drop(f"Tournament Opponent #{victories + 1}")
        if drop:
            self._drop_count += 1
            self._notify_listeners(drop)

        return drop

    @property
    def total_drops(self) -> int:
        return self._drop_count

    def on_drop(self, callback: Callable[[LootDrop], None]) -> None:
        """Register listener for loot drops."""
        self._listeners.append(callback)

    def _notify_listeners(self, drop: LootDrop) -> None:
        for listener in self._listeners:
            listener(drop)

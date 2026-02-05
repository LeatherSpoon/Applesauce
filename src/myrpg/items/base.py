"""Base item classes for MyRPG."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..combat.themes import ThemeType


class ItemRarity(Enum):
    """Item rarity tiers affecting stats and sell value."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


RARITY_MULTIPLIERS = {
    ItemRarity.COMMON: 1.0,
    ItemRarity.UNCOMMON: 1.5,
    ItemRarity.RARE: 2.5,
    ItemRarity.EPIC: 4.0,
    ItemRarity.LEGENDARY: 7.0,
}

RARITY_SELL_MULTIPLIERS = {
    ItemRarity.COMMON: 1,
    ItemRarity.UNCOMMON: 3,
    ItemRarity.RARE: 10,
    ItemRarity.EPIC: 35,
    ItemRarity.LEGENDARY: 100,
}


class ItemType(Enum):
    """Types of items in the game."""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    MATERIAL = "material"


class EquipmentSlot(Enum):
    """Equipment slots on a character."""
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    HEAD = "head"
    BODY = "body"
    HANDS = "hands"
    FEET = "feet"
    ACCESSORY_1 = "accessory_1"
    ACCESSORY_2 = "accessory_2"


@dataclass
class ItemStats:
    """Stats provided by an item."""
    power_bonus: float = 0.0
    strength_bonus: float = 0.0
    dexterity_bonus: float = 0.0
    focus_bonus: float = 0.0
    endurance_bonus: float = 0.0
    speed_bonus: float = 0.0
    health_bonus: float = 0.0
    damage_multiplier: float = 1.0
    defense_multiplier: float = 1.0

    def __add__(self, other: "ItemStats") -> "ItemStats":
        """Combine stats from multiple items."""
        return ItemStats(
            power_bonus=self.power_bonus + other.power_bonus,
            strength_bonus=self.strength_bonus + other.strength_bonus,
            dexterity_bonus=self.dexterity_bonus + other.dexterity_bonus,
            focus_bonus=self.focus_bonus + other.focus_bonus,
            endurance_bonus=self.endurance_bonus + other.endurance_bonus,
            speed_bonus=self.speed_bonus + other.speed_bonus,
            health_bonus=self.health_bonus + other.health_bonus,
            damage_multiplier=self.damage_multiplier * other.damage_multiplier,
            defense_multiplier=self.defense_multiplier * other.defense_multiplier,
        )

    @classmethod
    def empty(cls) -> "ItemStats":
        """Create empty stats."""
        return cls()


@dataclass
class Item(ABC):
    """Base class for all items."""
    name: str
    description: str
    item_type: ItemType
    rarity: ItemRarity
    base_sell_value: int
    tier: int = 1

    @property
    def sell_value(self) -> int:
        """Calculate sell value based on rarity and tier."""
        multiplier = RARITY_SELL_MULTIPLIERS[self.rarity]
        return int(self.base_sell_value * multiplier * self.tier)

    @property
    @abstractmethod
    def stats(self) -> ItemStats:
        """Get the stats this item provides."""
        pass

    def __str__(self) -> str:
        rarity_prefix = "" if self.rarity == ItemRarity.COMMON else f"[{self.rarity.value.upper()}] "
        return f"{rarity_prefix}{self.name}"


@dataclass
class Equipment(Item):
    """Base class for equippable items."""
    slot: EquipmentSlot = field(default=EquipmentSlot.MAIN_HAND)
    required_theme: "ThemeType | None" = field(default=None)
    _base_stats: ItemStats = field(default_factory=ItemStats.empty)

    @property
    def stats(self) -> ItemStats:
        """Get stats scaled by rarity."""
        multiplier = RARITY_MULTIPLIERS[self.rarity]
        base = self._base_stats
        return ItemStats(
            power_bonus=base.power_bonus * multiplier,
            strength_bonus=base.strength_bonus * multiplier,
            dexterity_bonus=base.dexterity_bonus * multiplier,
            focus_bonus=base.focus_bonus * multiplier,
            endurance_bonus=base.endurance_bonus * multiplier,
            speed_bonus=base.speed_bonus * multiplier,
            health_bonus=base.health_bonus * multiplier,
            damage_multiplier=1.0 + (base.damage_multiplier - 1.0) * multiplier,
            defense_multiplier=1.0 + (base.defense_multiplier - 1.0) * multiplier,
        )

    def can_equip(self, current_theme: "ThemeType") -> bool:
        """Check if this equipment can be used with current theme."""
        if self.required_theme is None:
            return True
        return self.required_theme == current_theme


@dataclass
class Consumable(Item):
    """Items that can be used and consumed."""
    item_type: ItemType = field(default=ItemType.CONSUMABLE, init=False)
    duration_seconds: float = 0.0  # 0 = instant
    heal_amount: float = 0.0
    temp_power_bonus: float = 0.0
    temp_speed_bonus: float = 0.0
    temp_damage_multiplier: float = 1.0

    @property
    def stats(self) -> ItemStats:
        """Consumables don't provide passive stats."""
        return ItemStats.empty()

    @property
    def is_instant(self) -> bool:
        return self.duration_seconds == 0.0


@dataclass
class Material(Item):
    """Crafting or sell-only materials."""
    item_type: ItemType = field(default=ItemType.MATERIAL, init=False)

    @property
    def stats(self) -> ItemStats:
        """Materials don't provide stats."""
        return ItemStats.empty()

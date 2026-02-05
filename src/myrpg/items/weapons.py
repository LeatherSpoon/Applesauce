"""Weapon system for Armed combat theme."""

from dataclasses import dataclass, field
from enum import Enum

from .base import Equipment, EquipmentSlot, ItemType, ItemRarity, ItemStats
from ..combat.themes import ThemeType


class WeaponClass(Enum):
    """Weapon classes with distinct characteristics."""
    DAGGER = "dagger"
    SWORD = "sword"
    AXE = "axe"
    SPEAR = "spear"
    HAMMER = "hammer"
    BOW = "bow"
    CROSSBOW = "crossbow"
    STAFF = "staff"
    WAND = "wand"
    FIST = "fist"  # Unarmed enhancement


# Weapon class characteristics
WEAPON_CHARACTERISTICS = {
    WeaponClass.DAGGER: {
        "speed_modifier": 1.5,
        "damage_modifier": 0.7,
        "range": 1,
        "crit_bonus": 0.25,
        "theme": ThemeType.ARMED,
    },
    WeaponClass.SWORD: {
        "speed_modifier": 1.0,
        "damage_modifier": 1.0,
        "range": 1,
        "crit_bonus": 0.10,
        "theme": ThemeType.ARMED,
    },
    WeaponClass.AXE: {
        "speed_modifier": 0.7,
        "damage_modifier": 1.4,
        "range": 1,
        "crit_bonus": 0.0,
        "armor_pen": 0.3,
        "theme": ThemeType.ARMED,
    },
    WeaponClass.SPEAR: {
        "speed_modifier": 0.9,
        "damage_modifier": 1.1,
        "range": 2,
        "crit_bonus": 0.05,
        "theme": ThemeType.ARMED,
    },
    WeaponClass.HAMMER: {
        "speed_modifier": 0.5,
        "damage_modifier": 1.8,
        "range": 1,
        "crit_bonus": 0.0,
        "stun_chance": 0.15,
        "theme": ThemeType.ARMED,
    },
    WeaponClass.BOW: {
        "speed_modifier": 0.8,
        "damage_modifier": 1.2,
        "range": 6,
        "crit_bonus": 0.15,
        "theme": ThemeType.RANGED,
    },
    WeaponClass.CROSSBOW: {
        "speed_modifier": 0.5,
        "damage_modifier": 1.6,
        "range": 8,
        "crit_bonus": 0.20,
        "theme": ThemeType.RANGED,
    },
    WeaponClass.STAFF: {
        "speed_modifier": 0.9,
        "damage_modifier": 1.0,
        "range": 4,
        "crit_bonus": 0.0,
        "energy_bonus": 20,
        "theme": ThemeType.ENERGY,
    },
    WeaponClass.WAND: {
        "speed_modifier": 1.2,
        "damage_modifier": 0.8,
        "range": 5,
        "crit_bonus": 0.05,
        "energy_regen": 2,
        "theme": ThemeType.ENERGY,
    },
    WeaponClass.FIST: {
        "speed_modifier": 1.3,
        "damage_modifier": 0.9,
        "range": 1,
        "crit_bonus": 0.0,
        "combo_bonus": 0.1,
        "theme": ThemeType.UNARMED,
    },
}


@dataclass
class Weapon(Equipment):
    """A weapon that can be equipped for combat."""
    item_type: ItemType = field(default=ItemType.WEAPON, init=False)
    slot: EquipmentSlot = field(default=EquipmentSlot.MAIN_HAND)
    weapon_class: WeaponClass = field(default=WeaponClass.SWORD)
    base_damage: float = 10.0

    def __post_init__(self) -> None:
        chars = WEAPON_CHARACTERISTICS[self.weapon_class]
        self.required_theme = chars["theme"]

    @property
    def characteristics(self) -> dict:
        """Get weapon class characteristics."""
        return WEAPON_CHARACTERISTICS[self.weapon_class]

    @property
    def speed_modifier(self) -> float:
        return self.characteristics["speed_modifier"]

    @property
    def damage_modifier(self) -> float:
        return self.characteristics["damage_modifier"]

    @property
    def range(self) -> int:
        return self.characteristics["range"]

    @property
    def crit_bonus(self) -> float:
        return self.characteristics.get("crit_bonus", 0.0)

    @property
    def effective_damage(self) -> float:
        """Calculate effective damage including rarity."""
        from .base import RARITY_MULTIPLIERS
        return self.base_damage * self.damage_modifier * RARITY_MULTIPLIERS[self.rarity]

    @property
    def stats(self) -> ItemStats:
        """Get weapon stats."""
        from .base import RARITY_MULTIPLIERS
        multiplier = RARITY_MULTIPLIERS[self.rarity]

        base_stats = self._base_stats
        return ItemStats(
            power_bonus=(base_stats.power_bonus + self.base_damage * 0.5) * multiplier,
            strength_bonus=base_stats.strength_bonus * multiplier,
            dexterity_bonus=base_stats.dexterity_bonus * multiplier,
            focus_bonus=base_stats.focus_bonus * multiplier,
            endurance_bonus=base_stats.endurance_bonus * multiplier,
            speed_bonus=base_stats.speed_bonus * multiplier,
            health_bonus=base_stats.health_bonus * multiplier,
            damage_multiplier=1.0 + (self.damage_modifier - 1.0) * 0.5 * multiplier,
            defense_multiplier=base_stats.defense_multiplier,
        )


# Predefined weapon templates
def create_weapon(
    weapon_class: WeaponClass,
    tier: int = 1,
    rarity: ItemRarity = ItemRarity.COMMON,
) -> Weapon:
    """Factory function to create weapons."""
    templates = {
        WeaponClass.DAGGER: ("Iron Dagger", "A quick stabbing weapon"),
        WeaponClass.SWORD: ("Steel Sword", "A balanced blade"),
        WeaponClass.AXE: ("Battle Axe", "A heavy chopping weapon"),
        WeaponClass.SPEAR: ("Iron Spear", "A weapon with superior reach"),
        WeaponClass.HAMMER: ("War Hammer", "A devastating crushing weapon"),
        WeaponClass.BOW: ("Longbow", "A ranged weapon for precision"),
        WeaponClass.CROSSBOW: ("Heavy Crossbow", "A powerful ranged weapon"),
        WeaponClass.STAFF: ("Arcane Staff", "Channels magical energy"),
        WeaponClass.WAND: ("Crystal Wand", "Quick magical implement"),
        WeaponClass.FIST: ("Fighting Gauntlets", "Enhances unarmed strikes"),
    }

    name, desc = templates[weapon_class]
    tier_prefix = ["", "Fine ", "Superior ", "Masterwork ", "Legendary "][min(tier - 1, 4)]

    return Weapon(
        name=f"{tier_prefix}{name}",
        description=desc,
        rarity=rarity,
        base_sell_value=50 * tier,
        tier=tier,
        weapon_class=weapon_class,
        base_damage=10.0 * tier,
    )

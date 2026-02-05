"""Armor system for MyRPG."""

from dataclasses import dataclass, field
from enum import Enum

from .base import Equipment, EquipmentSlot, ItemType, ItemRarity, ItemStats, RARITY_MULTIPLIERS


class ArmorWeight(Enum):
    """Armor weight classes affecting stats and mobility."""
    CLOTH = "cloth"
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"


ARMOR_CHARACTERISTICS = {
    ArmorWeight.CLOTH: {
        "defense_modifier": 0.5,
        "speed_penalty": 0.0,
        "focus_bonus": 5.0,
        "energy_bonus": 10.0,
    },
    ArmorWeight.LIGHT: {
        "defense_modifier": 0.75,
        "speed_penalty": 0.0,
        "dexterity_bonus": 3.0,
    },
    ArmorWeight.MEDIUM: {
        "defense_modifier": 1.0,
        "speed_penalty": 0.05,
        "strength_bonus": 2.0,
        "endurance_bonus": 2.0,
    },
    ArmorWeight.HEAVY: {
        "defense_modifier": 1.5,
        "speed_penalty": 0.15,
        "strength_bonus": 5.0,
        "endurance_bonus": 5.0,
    },
}


@dataclass
class Armor(Equipment):
    """Armor that can be equipped for defense."""
    item_type: ItemType = field(default=ItemType.ARMOR, init=False)
    armor_weight: ArmorWeight = field(default=ArmorWeight.MEDIUM)
    base_defense: float = 10.0

    @property
    def characteristics(self) -> dict:
        return ARMOR_CHARACTERISTICS[self.armor_weight]

    @property
    def defense_modifier(self) -> float:
        return self.characteristics["defense_modifier"]

    @property
    def speed_penalty(self) -> float:
        return self.characteristics.get("speed_penalty", 0.0)

    @property
    def effective_defense(self) -> float:
        """Calculate effective defense including rarity."""
        return self.base_defense * self.defense_modifier * RARITY_MULTIPLIERS[self.rarity]

    @property
    def stats(self) -> ItemStats:
        """Get armor stats."""
        multiplier = RARITY_MULTIPLIERS[self.rarity]
        chars = self.characteristics
        base = self._base_stats

        return ItemStats(
            power_bonus=base.power_bonus * multiplier,
            strength_bonus=(base.strength_bonus + chars.get("strength_bonus", 0)) * multiplier,
            dexterity_bonus=(base.dexterity_bonus + chars.get("dexterity_bonus", 0)) * multiplier,
            focus_bonus=(base.focus_bonus + chars.get("focus_bonus", 0)) * multiplier,
            endurance_bonus=(base.endurance_bonus + chars.get("endurance_bonus", 0)) * multiplier,
            speed_bonus=(base.speed_bonus - self.speed_penalty * 100) * multiplier,
            health_bonus=(base.health_bonus + self.base_defense) * multiplier,
            damage_multiplier=base.damage_multiplier,
            defense_multiplier=1.0 + (self.defense_modifier - 1.0) * 0.3 * multiplier,
        )


def create_armor(
    slot: EquipmentSlot,
    weight: ArmorWeight,
    tier: int = 1,
    rarity: ItemRarity = ItemRarity.COMMON,
) -> Armor:
    """Factory function to create armor pieces."""
    slot_names = {
        EquipmentSlot.HEAD: ("Helmet", "Protects the head"),
        EquipmentSlot.BODY: ("Chestplate", "Protects the torso"),
        EquipmentSlot.HANDS: ("Gauntlets", "Protects the hands"),
        EquipmentSlot.FEET: ("Boots", "Protects the feet"),
    }

    weight_prefixes = {
        ArmorWeight.CLOTH: "Cloth",
        ArmorWeight.LIGHT: "Leather",
        ArmorWeight.MEDIUM: "Chain",
        ArmorWeight.HEAVY: "Plate",
    }

    base_name, desc = slot_names.get(slot, ("Armor", "Protective gear"))
    weight_prefix = weight_prefixes[weight]
    tier_prefix = ["", "Fine ", "Superior ", "Masterwork ", "Legendary "][min(tier - 1, 4)]

    return Armor(
        name=f"{tier_prefix}{weight_prefix} {base_name}",
        description=desc,
        rarity=rarity,
        base_sell_value=40 * tier,
        tier=tier,
        slot=slot,
        armor_weight=weight,
        base_defense=8.0 * tier,
    )

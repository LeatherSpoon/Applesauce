"""Item and equipment system for MyRPG."""

from .base import (
    Item,
    ItemType,
    ItemRarity,
    ItemStats,
    Equipment,
    EquipmentSlot,
    Consumable,
    Material,
)
from .weapons import Weapon, WeaponClass, create_weapon
from .armor import Armor, ArmorWeight, create_armor
from .inventory import Inventory, EquipmentLoadout, ActiveEffects
from .loot import LootTable, LootDrop, DropManager

__all__ = [
    # Base
    "Item",
    "ItemType",
    "ItemRarity",
    "ItemStats",
    "Equipment",
    "EquipmentSlot",
    "Consumable",
    "Material",
    # Weapons
    "Weapon",
    "WeaponClass",
    "create_weapon",
    # Armor
    "Armor",
    "ArmorWeight",
    "create_armor",
    # Inventory
    "Inventory",
    "EquipmentLoadout",
    "ActiveEffects",
    # Loot
    "LootTable",
    "LootDrop",
    "DropManager",
]

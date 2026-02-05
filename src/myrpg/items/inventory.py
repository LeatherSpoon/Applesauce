"""Inventory and equipment management for MyRPG."""

from dataclasses import dataclass, field
from typing import Callable

from .base import Item, Equipment, EquipmentSlot, ItemStats, Consumable
from ..combat.themes import ThemeType


@dataclass
class EquipmentLoadout:
    """Manages equipped items in each slot."""
    _slots: dict[EquipmentSlot, Equipment | None] = field(default_factory=lambda: {
        slot: None for slot in EquipmentSlot
    })
    _listeners: list[Callable[[EquipmentSlot, Equipment | None], None]] = field(
        default_factory=list, repr=False
    )

    def get(self, slot: EquipmentSlot) -> Equipment | None:
        """Get the item equipped in a slot."""
        return self._slots.get(slot)

    def equip(self, item: Equipment, current_theme: ThemeType) -> Equipment | None:
        """
        Equip an item, returning any previously equipped item.

        Args:
            item: The equipment to equip
            current_theme: Player's current combat theme

        Returns:
            Previously equipped item if any, None otherwise

        Raises:
            ValueError: If item cannot be equipped with current theme
        """
        if not item.can_equip(current_theme):
            raise ValueError(
                f"Cannot equip {item.name} with {current_theme.name} theme"
            )

        slot = item.slot
        previous = self._slots[slot]
        self._slots[slot] = item
        self._notify_listeners(slot, item)
        return previous

    def unequip(self, slot: EquipmentSlot) -> Equipment | None:
        """
        Remove and return the item from a slot.

        Returns:
            The unequipped item, or None if slot was empty
        """
        item = self._slots[slot]
        self._slots[slot] = None
        if item:
            self._notify_listeners(slot, None)
        return item

    def get_total_stats(self) -> ItemStats:
        """Calculate combined stats from all equipped items."""
        total = ItemStats.empty()
        for item in self._slots.values():
            if item:
                total = total + item.stats
        return total

    def get_equipped_items(self) -> list[Equipment]:
        """Get list of all equipped items."""
        return [item for item in self._slots.values() if item is not None]

    def on_change(self, callback: Callable[[EquipmentSlot, Equipment | None], None]) -> None:
        """Register listener for equipment changes."""
        self._listeners.append(callback)

    def _notify_listeners(self, slot: EquipmentSlot, item: Equipment | None) -> None:
        for listener in self._listeners:
            listener(slot, item)

    def __str__(self) -> str:
        lines = ["Equipment:"]
        for slot in EquipmentSlot:
            item = self._slots[slot]
            item_str = item.name if item else "(empty)"
            lines.append(f"  {slot.value}: {item_str}")
        return "\n".join(lines)


@dataclass
class Inventory:
    """Player inventory for storing items."""
    _items: list[Item] = field(default_factory=list)
    _capacity: int = field(default=50)
    _listeners: list[Callable[[Item, bool], None]] = field(
        default_factory=list, repr=False
    )

    @property
    def items(self) -> list[Item]:
        """Get all items in inventory."""
        return list(self._items)

    @property
    def capacity(self) -> int:
        """Get inventory capacity."""
        return self._capacity

    @property
    def count(self) -> int:
        """Get number of items in inventory."""
        return len(self._items)

    @property
    def is_full(self) -> bool:
        """Check if inventory is full."""
        return self.count >= self._capacity

    def add(self, item: Item) -> bool:
        """
        Add an item to inventory.

        Returns:
            True if added successfully, False if inventory full
        """
        if self.is_full:
            return False
        self._items.append(item)
        self._notify_listeners(item, True)
        return True

    def remove(self, item: Item) -> bool:
        """
        Remove an item from inventory.

        Returns:
            True if removed, False if item not found
        """
        if item in self._items:
            self._items.remove(item)
            self._notify_listeners(item, False)
            return True
        return False

    def get_by_type(self, item_type) -> list[Item]:
        """Get all items of a specific type."""
        return [item for item in self._items if item.item_type == item_type]

    def get_equipment(self) -> list[Equipment]:
        """Get all equippable items."""
        return [item for item in self._items if isinstance(item, Equipment)]

    def get_consumables(self) -> list[Consumable]:
        """Get all consumable items."""
        return [item for item in self._items if isinstance(item, Consumable)]

    def get_total_sell_value(self) -> int:
        """Calculate total sell value of all items."""
        return sum(item.sell_value for item in self._items)

    def sell_all(self) -> tuple[int, int]:
        """
        Sell all items in inventory.

        Returns:
            Tuple of (gold_earned, items_sold)
        """
        total_value = self.get_total_sell_value()
        count = len(self._items)
        self._items.clear()
        return total_value, count

    def sell_item(self, item: Item) -> int:
        """
        Sell a specific item.

        Returns:
            Gold earned, or 0 if item not found
        """
        if self.remove(item):
            return item.sell_value
        return 0

    def expand_capacity(self, amount: int) -> None:
        """Increase inventory capacity."""
        self._capacity += amount

    def on_change(self, callback: Callable[[Item, bool], None]) -> None:
        """Register listener for inventory changes (item, added)."""
        self._listeners.append(callback)

    def _notify_listeners(self, item: Item, added: bool) -> None:
        for listener in self._listeners:
            listener(item, added)

    def __str__(self) -> str:
        return f"Inventory: {self.count}/{self._capacity} items"

    def __len__(self) -> int:
        return self.count


@dataclass
class ActiveEffects:
    """Tracks active consumable effects."""
    _effects: list[tuple[Consumable, float]] = field(default_factory=list)

    def add_effect(self, consumable: Consumable) -> None:
        """Add an active effect from a consumable."""
        if not consumable.is_instant:
            self._effects.append((consumable, consumable.duration_seconds))

    def update(self, delta_seconds: float) -> list[Consumable]:
        """
        Update effect durations.

        Returns:
            List of expired effects
        """
        expired = []
        remaining = []

        for consumable, time_left in self._effects:
            new_time = time_left - delta_seconds
            if new_time <= 0:
                expired.append(consumable)
            else:
                remaining.append((consumable, new_time))

        self._effects = remaining
        return expired

    def get_total_stats(self) -> ItemStats:
        """Get combined stats from active effects."""
        total = ItemStats.empty()
        for consumable, _ in self._effects:
            effect_stats = ItemStats(
                power_bonus=consumable.temp_power_bonus,
                speed_bonus=consumable.temp_speed_bonus,
                damage_multiplier=consumable.temp_damage_multiplier,
            )
            total = total + effect_stats
        return total

    def clear(self) -> None:
        """Clear all active effects."""
        self._effects.clear()

    def __len__(self) -> int:
        return len(self._effects)

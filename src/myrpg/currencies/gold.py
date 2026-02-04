"""Gold - active economy currency for purchases."""

from dataclasses import dataclass, field
from typing import Callable
from enum import Enum


class TransactionResult(Enum):
    """Result of a gold transaction."""
    SUCCESS = "success"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    INVALID_AMOUNT = "invalid_amount"


@dataclass
class Gold:
    """
    Active economy currency for equipment, consumables, and managers.

    - Earned actively by selling loot (no passive generation)
    - Spent on equipment, managers, tiles, consumables
    - No cap
    """

    _amount: int = field(default=0)
    _total_earned: int = field(default=0)
    _total_spent: int = field(default=0)
    _listeners: list[Callable[[int, int], None]] = field(default_factory=list, repr=False)

    @property
    def amount(self) -> int:
        """Current gold balance."""
        return self._amount

    @property
    def total_earned(self) -> int:
        """Lifetime gold earned."""
        return self._total_earned

    @property
    def total_spent(self) -> int:
        """Lifetime gold spent."""
        return self._total_spent

    def add(self, amount: int, source: str = "unknown") -> None:
        """
        Add gold from selling loot or other sources.

        Args:
            amount: Amount of gold to add (must be positive)
            source: Description of where the gold came from
        """
        if amount < 0:
            raise ValueError("Use spend() to remove gold")
        if amount == 0:
            return

        old_amount = self._amount
        self._amount += amount
        self._total_earned += amount
        self._notify_listeners(old_amount, self._amount)

    def spend(self, amount: int, purpose: str = "unknown") -> TransactionResult:
        """
        Spend gold on a purchase.

        Args:
            amount: Amount to spend (must be positive)
            purpose: Description of what the gold is being spent on

        Returns:
            TransactionResult indicating success or failure
        """
        if amount < 0:
            return TransactionResult.INVALID_AMOUNT
        if amount == 0:
            return TransactionResult.SUCCESS
        if amount > self._amount:
            return TransactionResult.INSUFFICIENT_FUNDS

        old_amount = self._amount
        self._amount -= amount
        self._total_spent += amount
        self._notify_listeners(old_amount, self._amount)
        return TransactionResult.SUCCESS

    def can_afford(self, amount: int) -> bool:
        """Check if the player can afford a purchase."""
        return self._amount >= amount

    def on_change(self, callback: Callable[[int, int], None]) -> None:
        """Register a listener for gold changes (old_amount, new_amount)."""
        self._listeners.append(callback)

    def _notify_listeners(self, old_amount: int, new_amount: int) -> None:
        for listener in self._listeners:
            listener(old_amount, new_amount)

    def __int__(self) -> int:
        return self._amount

    def __str__(self) -> str:
        return f"Gold: {self._amount:,}g"

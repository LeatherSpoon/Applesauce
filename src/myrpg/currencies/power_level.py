"""Power Level - the main progression metric representing combat strength."""

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class PowerLevel:
    """
    The main "big number" representing overall progression and combat strength.

    Power Level:
    - Always increases (never decreases)
    - Affects combat damage and defense
    - Does NOT affect movement speed
    - Has no cap (infinite scaling)
    """

    _value: float = field(default=1.0)
    _listeners: list[Callable[[float, float], None]] = field(default_factory=list, repr=False)

    @property
    def value(self) -> float:
        return self._value

    def add(self, amount: float) -> None:
        """Add to power level. Amount must be positive."""
        if amount < 0:
            raise ValueError("Cannot reduce Power Level")
        if amount == 0:
            return
        old_value = self._value
        self._value += amount
        self._notify_listeners(old_value, self._value)

    def add_percentage(self, percentage: float) -> None:
        """Add a percentage of current power level."""
        amount = self._value * (percentage / 100)
        self.add(amount)

    def calculate_damage_multiplier(self) -> float:
        """Calculate combat damage multiplier based on power level."""
        return 1 + (self._value / 100)

    def calculate_defense_multiplier(self) -> float:
        """Calculate defense multiplier based on power level."""
        return 1 + (self._value / 200)

    def on_change(self, callback: Callable[[float, float], None]) -> None:
        """Register a listener for power level changes."""
        self._listeners.append(callback)

    def _notify_listeners(self, old_value: float, new_value: float) -> None:
        for listener in self._listeners:
            listener(old_value, new_value)

    def __float__(self) -> float:
        return self._value

    def __int__(self) -> int:
        return int(self._value)

    def __str__(self) -> str:
        return f"Power Level: {self._value:,.1f}"

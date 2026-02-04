"""Controlling Variables - stats that determine combat theme effectiveness."""

from dataclasses import dataclass, field
from typing import Callable
from enum import Enum


class VariableType(Enum):
    """The four controlling variables."""
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    FOCUS = "focus"
    ENDURANCE = "endurance"


@dataclass
class Variable:
    """A single controlling variable with its current value."""

    type: VariableType
    _value: float = field(default=1.0)
    _bonus_multiplier: float = field(default=1.0)

    @property
    def value(self) -> float:
        """Current value of the variable."""
        return self._value

    @property
    def effective_value(self) -> float:
        """Value after applying bonus multipliers."""
        return self._value * self._bonus_multiplier

    def add(self, amount: float) -> None:
        """Add to the variable value."""
        if amount < 0:
            raise ValueError("Cannot reduce controlling variables")
        self._value += amount

    def set_bonus_multiplier(self, multiplier: float) -> None:
        """Set the bonus multiplier (from mastery, equipment, etc.)."""
        self._bonus_multiplier = max(1.0, multiplier)

    def __str__(self) -> str:
        return f"{self.type.value.title()}: {self._value:.1f}"


@dataclass
class ControllingVariables:
    """
    Container for all controlling variables.

    Variables affect combat theme effectiveness:
    - Strength: Unarmed/Armed damage, carry capacity
    - Dexterity: Ranged accuracy, Armed speed, movement efficiency
    - Focus: Energy capacity/regen, training efficiency
    - Endurance: HP, defense, stamina regen
    """

    strength: Variable = field(default_factory=lambda: Variable(VariableType.STRENGTH))
    dexterity: Variable = field(default_factory=lambda: Variable(VariableType.DEXTERITY))
    focus: Variable = field(default_factory=lambda: Variable(VariableType.FOCUS))
    endurance: Variable = field(default_factory=lambda: Variable(VariableType.ENDURANCE))
    _listeners: list[Callable[[VariableType, float], None]] = field(
        default_factory=list, repr=False
    )

    def get(self, var_type: VariableType) -> Variable:
        """Get a variable by type."""
        mapping = {
            VariableType.STRENGTH: self.strength,
            VariableType.DEXTERITY: self.dexterity,
            VariableType.FOCUS: self.focus,
            VariableType.ENDURANCE: self.endurance,
        }
        return mapping[var_type]

    def add(self, var_type: VariableType, amount: float) -> None:
        """Add to a specific variable."""
        variable = self.get(var_type)
        old_value = variable.value
        variable.add(amount)
        self._notify_listeners(var_type, variable.value)

    def calculate_unarmed_bonus(self) -> float:
        """Calculate damage bonus for Unarmed combat."""
        # Strength 70%, Endurance 30%
        return (
            self.strength.effective_value * 0.02 * 0.7 +
            self.endurance.effective_value * 0.02 * 0.3
        )

    def calculate_armed_bonus(self) -> float:
        """Calculate damage bonus for Armed combat."""
        # Strength 50%, Dexterity 50%
        return (
            self.strength.effective_value * 0.02 * 0.5 +
            self.dexterity.effective_value * 0.02 * 0.5
        )

    def calculate_ranged_bonus(self) -> float:
        """Calculate damage bonus for Ranged combat."""
        # Dexterity 60%, Focus 40%
        return (
            self.dexterity.effective_value * 0.02 * 0.6 +
            self.focus.effective_value * 0.02 * 0.4
        )

    def calculate_energy_bonus(self) -> float:
        """Calculate damage bonus for Energy combat."""
        # Focus 60%, Endurance 40%
        return (
            self.focus.effective_value * 0.02 * 0.6 +
            self.endurance.effective_value * 0.02 * 0.4
        )

    def calculate_max_hp(self, base_hp: float = 100) -> float:
        """Calculate max HP based on Endurance."""
        return base_hp + self.endurance.effective_value

    def calculate_training_efficiency(self) -> float:
        """Calculate training efficiency multiplier from Focus."""
        return 1.0 + (self.focus.effective_value * 0.01)

    def on_change(self, callback: Callable[[VariableType, float], None]) -> None:
        """Register a listener for variable changes."""
        self._listeners.append(callback)

    def _notify_listeners(self, var_type: VariableType, new_value: float) -> None:
        for listener in self._listeners:
            listener(var_type, new_value)

    def __str__(self) -> str:
        return (
            f"STR: {self.strength.value:.0f} | "
            f"DEX: {self.dexterity.value:.0f} | "
            f"FOC: {self.focus.value:.0f} | "
            f"END: {self.endurance.value:.0f}"
        )

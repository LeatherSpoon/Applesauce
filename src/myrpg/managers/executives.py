"""Tier 3-4 Executive Managers - top-level management."""

from dataclasses import dataclass, field

from .base import ExecutiveManager, ManagerTier, ManagerCategory


@dataclass
class VPOfTraining(ExecutiveManager):
    """
    VP of Training - manages all Department Managers.

    Grants +50% efficiency to all managed managers.
    Enables auto-hire feature.
    """

    _auto_hire_enabled: bool = field(default=False)
    _bonus: float = field(default=0.5)

    @property
    def name(self) -> str:
        return "VP of Training"

    @property
    def base_cost(self) -> int:
        return 100000

    @property
    def bonus(self) -> float:
        """Efficiency bonus granted to all department managers."""
        return self._bonus

    @property
    def auto_hire_enabled(self) -> bool:
        return self._auto_hire_enabled

    def set_auto_hire(self, enabled: bool) -> None:
        """Enable or disable auto-hire feature."""
        self._auto_hire_enabled = enabled

    def get_description(self) -> str:
        return (
            "Grants +50% efficiency to all managers. "
            "Enables auto-hire of task managers."
        )


@dataclass
class CEO(ExecutiveManager):
    """
    CEO - top of the hierarchy, unlocks prestige system.

    Manages all executives.
    Unlocks corporate restructuring (prestige).
    """

    @property
    def tier(self) -> ManagerTier:
        return ManagerTier.CEO

    @property
    def name(self) -> str:
        return "CEO"

    @property
    def base_cost(self) -> int:
        return 1000000

    def get_description(self) -> str:
        return (
            "Top of the corporate ladder. "
            "Unlocks prestige system and regional managers."
        )

"""Base manager class and manager tier definitions."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..training.variables import VariableType


class ManagerTier(Enum):
    """Manager hierarchy tiers."""
    TASK = 1        # Automate single activities
    DEPARTMENT = 2  # Manage multiple Task Managers
    EXECUTIVE = 3   # Manage Department Managers
    CEO = 4         # Manage all, unlock prestige


class ManagerCategory(Enum):
    """Categories for grouping managers."""
    PHYSICAL = "physical"  # Strength, Endurance
    MENTAL = "mental"      # Dexterity, Focus
    ALL = "all"            # Executive level


@dataclass
class Manager(ABC):
    """Base class for all managers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Display name of the manager."""
        pass

    @property
    @abstractmethod
    def tier(self) -> ManagerTier:
        """The tier of this manager."""
        pass

    @property
    @abstractmethod
    def base_cost(self) -> int:
        """Base gold cost to hire."""
        pass

    @property
    @abstractmethod
    def category(self) -> ManagerCategory:
        """Which category this manager belongs to."""
        pass

    @property
    def is_unique(self) -> bool:
        """Whether only one of this manager can be owned."""
        return self.tier != ManagerTier.TASK

    @abstractmethod
    def get_description(self) -> str:
        """Get a description of what this manager does."""
        pass


@dataclass
class TaskManager(Manager):
    """Base class for Tier 1 task managers that automate training."""

    _efficiency: float = field(default=0.5)  # 50% base efficiency

    @property
    def tier(self) -> ManagerTier:
        return ManagerTier.TASK

    @property
    def is_unique(self) -> bool:
        return False  # Can own multiple task managers

    @property
    @abstractmethod
    def target_variable(self) -> "VariableType":
        """Which variable this manager trains."""
        pass

    @property
    @abstractmethod
    def activity_name(self) -> str:
        """Name of the activity being automated."""
        pass

    @property
    def efficiency(self) -> float:
        """Current efficiency (0.0 to 1.0)."""
        return self._efficiency

    def get_description(self) -> str:
        return f"Automates {self.activity_name} at {self._efficiency * 100:.0f}% efficiency"


@dataclass
class DepartmentManager(Manager):
    """Base class for Tier 2 department managers."""

    _bonus: float = field(default=0.25)  # 25% bonus to managed

    @property
    def tier(self) -> ManagerTier:
        return ManagerTier.DEPARTMENT

    @property
    def bonus(self) -> float:
        """Efficiency bonus granted to managed task managers."""
        return self._bonus

    @abstractmethod
    def get_managed_variables(self) -> list["VariableType"]:
        """Get the variables whose task managers this department manages."""
        pass


@dataclass
class ExecutiveManager(Manager):
    """Base class for Tier 3+ executive managers."""

    @property
    def tier(self) -> ManagerTier:
        return ManagerTier.EXECUTIVE

    @property
    def category(self) -> ManagerCategory:
        return ManagerCategory.ALL

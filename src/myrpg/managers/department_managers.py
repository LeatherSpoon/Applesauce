"""Tier 2 Department Managers - manage groups of task managers."""

from dataclasses import dataclass

from .base import DepartmentManager, ManagerCategory
from ..training.variables import VariableType


@dataclass
class PhysicalDirector(DepartmentManager):
    """
    Manages Mining Foremen and Running Coaches.

    Grants +25% efficiency to all physical task managers.
    """

    @property
    def name(self) -> str:
        return "Physical Director"

    @property
    def base_cost(self) -> int:
        return 10000

    @property
    def category(self) -> ManagerCategory:
        return ManagerCategory.PHYSICAL

    def get_managed_variables(self) -> list[VariableType]:
        return [VariableType.STRENGTH, VariableType.ENDURANCE]

    def get_description(self) -> str:
        return "Grants +25% efficiency to Mining Foremen and Running Coaches"


@dataclass
class MentalDirector(DepartmentManager):
    """
    Manages Course Instructors and Meditation Guides.

    Grants +25% efficiency to all mental task managers.
    """

    @property
    def name(self) -> str:
        return "Mental Director"

    @property
    def base_cost(self) -> int:
        return 10000

    @property
    def category(self) -> ManagerCategory:
        return ManagerCategory.MENTAL

    def get_managed_variables(self) -> list[VariableType]:
        return [VariableType.DEXTERITY, VariableType.FOCUS]

    def get_description(self) -> str:
        return "Grants +25% efficiency to Course Instructors and Meditation Guides"

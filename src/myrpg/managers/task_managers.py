"""Tier 1 Task Managers - automate single training activities."""

from dataclasses import dataclass

from .base import TaskManager, ManagerCategory
from ..training.variables import VariableType


@dataclass
class MiningForeman(TaskManager):
    """Automates Mining (Strength training)."""

    @property
    def name(self) -> str:
        return "Mining Foreman"

    @property
    def base_cost(self) -> int:
        return 1000

    @property
    def category(self) -> ManagerCategory:
        return ManagerCategory.PHYSICAL

    @property
    def target_variable(self) -> VariableType:
        return VariableType.STRENGTH

    @property
    def activity_name(self) -> str:
        return "Mining"


@dataclass
class RunningCoach(TaskManager):
    """Automates Distance Running (Endurance training)."""

    @property
    def name(self) -> str:
        return "Running Coach"

    @property
    def base_cost(self) -> int:
        return 1000

    @property
    def category(self) -> ManagerCategory:
        return ManagerCategory.PHYSICAL

    @property
    def target_variable(self) -> VariableType:
        return VariableType.ENDURANCE

    @property
    def activity_name(self) -> str:
        return "Distance Running"


@dataclass
class CourseInstructor(TaskManager):
    """Automates Obstacle Courses (Dexterity training)."""

    @property
    def name(self) -> str:
        return "Course Instructor"

    @property
    def base_cost(self) -> int:
        return 1000

    @property
    def category(self) -> ManagerCategory:
        return ManagerCategory.MENTAL

    @property
    def target_variable(self) -> VariableType:
        return VariableType.DEXTERITY

    @property
    def activity_name(self) -> str:
        return "Obstacle Course"


@dataclass
class MeditationGuide(TaskManager):
    """Automates Meditation (Focus training)."""

    @property
    def name(self) -> str:
        return "Meditation Guide"

    @property
    def base_cost(self) -> int:
        return 1000

    @property
    def category(self) -> ManagerCategory:
        return ManagerCategory.MENTAL

    @property
    def target_variable(self) -> VariableType:
        return VariableType.FOCUS

    @property
    def activity_name(self) -> str:
        return "Meditation"

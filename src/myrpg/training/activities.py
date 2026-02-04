"""Training activities that increase controlling variables."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .variables import ControllingVariables, VariableType


class ActivityLevel(Enum):
    """Intensity level of training activity."""
    CASUAL = "casual"
    FOCUSED = "focused"
    INTENSE = "intense"


@dataclass
class TrainingResult:
    """Result of performing a training activity."""
    variable_type: "VariableType"
    amount_gained: float
    activity_name: str
    level: ActivityLevel


class TrainingActivity(ABC):
    """Base class for training activities."""

    # Gains per hour at each level
    CASUAL_GAINS_PER_HOUR: float = 10.0
    FOCUSED_GAINS_PER_HOUR: float = 25.0
    INTENSE_GAINS_PER_HOUR: float = 50.0

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the activity."""
        pass

    @property
    @abstractmethod
    def target_variable(self) -> "VariableType":
        """Which variable this activity trains."""
        pass

    def get_gains_per_hour(self, level: ActivityLevel) -> float:
        """Get the gains per hour for a given intensity level."""
        rates = {
            ActivityLevel.CASUAL: self.CASUAL_GAINS_PER_HOUR,
            ActivityLevel.FOCUSED: self.FOCUSED_GAINS_PER_HOUR,
            ActivityLevel.INTENSE: self.INTENSE_GAINS_PER_HOUR,
        }
        return rates[level]

    def perform(
        self,
        variables: "ControllingVariables",
        duration_seconds: float,
        level: ActivityLevel = ActivityLevel.CASUAL,
    ) -> TrainingResult:
        """
        Perform the training activity.

        Args:
            variables: The player's controlling variables to modify
            duration_seconds: How long the activity was performed
            level: Intensity level of the activity

        Returns:
            TrainingResult with details of the gains
        """
        from .variables import VariableType

        # Calculate gains (convert from per-hour to per-second)
        gains_per_second = self.get_gains_per_hour(level) / 3600
        efficiency = variables.calculate_training_efficiency()
        total_gains = gains_per_second * duration_seconds * efficiency

        # Apply gains
        variables.add(self.target_variable, total_gains)

        return TrainingResult(
            variable_type=self.target_variable,
            amount_gained=total_gains,
            activity_name=self.name,
            level=level,
        )

    def calculate_automation_rate(
        self,
        efficiency_percent: float,
        level: ActivityLevel = ActivityLevel.CASUAL,
    ) -> float:
        """
        Calculate the automation rate for managers.

        Args:
            efficiency_percent: Manager efficiency (0-100)
            level: Base activity level being automated

        Returns:
            Gains per hour when automated
        """
        base_rate = self.get_gains_per_hour(level)
        return base_rate * (efficiency_percent / 100)


class Mining(TrainingActivity):
    """Mining activity - trains Strength."""

    @property
    def name(self) -> str:
        return "Mining"

    @property
    def target_variable(self) -> "VariableType":
        from .variables import VariableType
        return VariableType.STRENGTH


class ObstacleCourse(TrainingActivity):
    """Obstacle course activity - trains Dexterity."""

    @property
    def name(self) -> str:
        return "Obstacle Course"

    @property
    def target_variable(self) -> "VariableType":
        from .variables import VariableType
        return VariableType.DEXTERITY


class Meditation(TrainingActivity):
    """Meditation activity - trains Focus."""

    @property
    def name(self) -> str:
        return "Meditation"

    @property
    def target_variable(self) -> "VariableType":
        from .variables import VariableType
        return VariableType.FOCUS


class DistanceRunning(TrainingActivity):
    """Distance running activity - trains Endurance."""

    @property
    def name(self) -> str:
        return "Distance Running"

    @property
    def target_variable(self) -> "VariableType":
        from .variables import VariableType
        return VariableType.ENDURANCE

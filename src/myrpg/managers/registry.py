"""Manager Registry - tracks owned managers and calculates efficiency."""

from dataclasses import dataclass, field
from typing import Callable

from .base import Manager, TaskManager, DepartmentManager, ManagerTier, ManagerCategory
from .task_managers import MiningForeman, RunningCoach, CourseInstructor, MeditationGuide
from .department_managers import PhysicalDirector, MentalDirector
from .executives import VPOfTraining, CEO
from ..training.variables import VariableType


@dataclass
class ManagerRegistry:
    """
    Tracks all owned managers and calculates combined efficiency.

    Handles:
    - Purchasing managers (with cost scaling for task managers)
    - Calculating total efficiency per variable
    - Prestige reset functionality
    """

    # Task managers (can own multiple)
    _task_managers: dict[VariableType, list[TaskManager]] = field(
        default_factory=lambda: {
            VariableType.STRENGTH: [],
            VariableType.DEXTERITY: [],
            VariableType.FOCUS: [],
            VariableType.ENDURANCE: [],
        }
    )

    # Unique managers
    _physical_director: PhysicalDirector | None = field(default=None)
    _mental_director: MentalDirector | None = field(default=None)
    _vp_of_training: VPOfTraining | None = field(default=None)
    _ceo: CEO | None = field(default=None)

    # Prestige
    _prestige_level: int = field(default=0)

    # Listeners
    _listeners: list[Callable[[str], None]] = field(default_factory=list, repr=False)

    @property
    def prestige_level(self) -> int:
        return self._prestige_level

    @property
    def prestige_multiplier(self) -> float:
        """Get the prestige efficiency multiplier."""
        return 1.0 + (self._prestige_level * 0.1)

    @property
    def has_physical_director(self) -> bool:
        return self._physical_director is not None

    @property
    def has_mental_director(self) -> bool:
        return self._mental_director is not None

    @property
    def has_vp(self) -> bool:
        return self._vp_of_training is not None

    @property
    def has_ceo(self) -> bool:
        return self._ceo is not None

    def get_task_manager_count(self, variable: VariableType) -> int:
        """Get number of task managers for a variable."""
        return len(self._task_managers[variable])

    def get_total_task_managers(self) -> int:
        """Get total number of all task managers."""
        return sum(len(managers) for managers in self._task_managers.values())

    def get_next_task_manager_cost(self, variable: VariableType) -> int:
        """Calculate cost for the next task manager (doubles each time)."""
        count = self.get_task_manager_count(variable)
        base_cost = 1000
        return base_cost * (2 ** count)

    def calculate_stack_efficiency(self, count: int) -> float:
        """
        Calculate stacked efficiency for multiple task managers.

        Each additional manager adds half of the previous bonus.
        1: 50%, 2: 75%, 3: 87.5%, etc.
        """
        if count == 0:
            return 0.0

        total = 0.0
        for i in range(count):
            total += 0.5 ** (i + 1)
        return total

    def calculate_efficiency(self, variable: VariableType) -> float:
        """
        Calculate total automation efficiency for a variable.

        Formula:
        Base × StackMultiplier × DepartmentBonus × ExecutiveBonus × PrestigeMultiplier
        Capped at 1.0 (100%)
        """
        count = self.get_task_manager_count(variable)
        if count == 0:
            return 0.0

        # Base stacked efficiency
        efficiency = self.calculate_stack_efficiency(count)

        # Department bonus (+25%)
        if variable in (VariableType.STRENGTH, VariableType.ENDURANCE):
            if self.has_physical_director:
                efficiency *= 1.25
        elif variable in (VariableType.DEXTERITY, VariableType.FOCUS):
            if self.has_mental_director:
                efficiency *= 1.25

        # Executive bonus (+50%)
        if self.has_vp:
            efficiency *= 1.5

        # Prestige multiplier
        efficiency *= self.prestige_multiplier

        # Cap at 100%
        return min(efficiency, 1.0)

    def hire_task_manager(self, variable: VariableType) -> TaskManager:
        """Create and register a new task manager."""
        manager_classes = {
            VariableType.STRENGTH: MiningForeman,
            VariableType.DEXTERITY: CourseInstructor,
            VariableType.FOCUS: MeditationGuide,
            VariableType.ENDURANCE: RunningCoach,
        }
        manager = manager_classes[variable]()
        self._task_managers[variable].append(manager)
        self._notify_listeners(f"Hired {manager.name}")
        return manager

    def hire_physical_director(self) -> PhysicalDirector:
        """Hire the Physical Director."""
        if self._physical_director is not None:
            raise ValueError("Physical Director already hired")
        self._physical_director = PhysicalDirector()
        self._notify_listeners("Hired Physical Director")
        return self._physical_director

    def hire_mental_director(self) -> MentalDirector:
        """Hire the Mental Director."""
        if self._mental_director is not None:
            raise ValueError("Mental Director already hired")
        self._mental_director = MentalDirector()
        self._notify_listeners("Hired Mental Director")
        return self._mental_director

    def hire_vp(self) -> VPOfTraining:
        """Hire the VP of Training."""
        if self._vp_of_training is not None:
            raise ValueError("VP of Training already hired")
        self._vp_of_training = VPOfTraining()
        self._notify_listeners("Hired VP of Training")
        return self._vp_of_training

    def hire_ceo(self) -> CEO:
        """Hire the CEO."""
        if self._ceo is not None:
            raise ValueError("CEO already hired")
        self._ceo = CEO()
        self._notify_listeners("Hired CEO")
        return self._ceo

    def can_hire_physical_director(self) -> bool:
        """Check if Physical Director can be hired."""
        if self._physical_director is not None:
            return False
        # Need at least 2 physical task managers
        physical_count = (
            self.get_task_manager_count(VariableType.STRENGTH) +
            self.get_task_manager_count(VariableType.ENDURANCE)
        )
        return physical_count >= 2

    def can_hire_mental_director(self) -> bool:
        """Check if Mental Director can be hired."""
        if self._mental_director is not None:
            return False
        # Need at least 2 mental task managers
        mental_count = (
            self.get_task_manager_count(VariableType.DEXTERITY) +
            self.get_task_manager_count(VariableType.FOCUS)
        )
        return mental_count >= 2

    def can_hire_vp(self) -> bool:
        """Check if VP of Training can be hired."""
        if self._vp_of_training is not None:
            return False
        return self.has_physical_director and self.has_mental_director

    def can_hire_ceo(self) -> bool:
        """Check if CEO can be hired."""
        if self._ceo is not None:
            return False
        return self.has_vp

    def prestige(self) -> int:
        """
        Perform prestige reset.

        Returns the new prestige level.
        """
        if not self.has_ceo:
            raise ValueError("Must have CEO to prestige")

        # Calculate prestige points based on total managers
        total_managers = self.get_total_task_managers()

        # Reset all managers
        self._task_managers = {v: [] for v in VariableType}
        self._physical_director = None
        self._mental_director = None
        self._vp_of_training = None
        self._ceo = None

        # Increase prestige level
        self._prestige_level += 1
        self._notify_listeners(f"Prestige! Now level {self._prestige_level}")

        return self._prestige_level

    def calculate_gains_per_hour(self, variable: VariableType, base_rate: float = 10.0) -> float:
        """Calculate automated gains per hour for a variable."""
        efficiency = self.calculate_efficiency(variable)
        return base_rate * efficiency

    def on_change(self, callback: Callable[[str], None]) -> None:
        """Register a listener for manager changes."""
        self._listeners.append(callback)

    def _notify_listeners(self, message: str) -> None:
        for listener in self._listeners:
            listener(message)

    def get_summary(self) -> str:
        """Get a summary of all owned managers."""
        lines = [f"Prestige Level: {self._prestige_level} ({self.prestige_multiplier:.1f}x)"]

        for var in VariableType:
            count = self.get_task_manager_count(var)
            eff = self.calculate_efficiency(var)
            lines.append(f"  {var.value.title()}: {count} managers ({eff * 100:.1f}% eff)")

        lines.append(f"  Physical Director: {'Yes' if self.has_physical_director else 'No'}")
        lines.append(f"  Mental Director: {'Yes' if self.has_mental_director else 'No'}")
        lines.append(f"  VP of Training: {'Yes' if self.has_vp else 'No'}")
        lines.append(f"  CEO: {'Yes' if self.has_ceo else 'No'}")

        return "\n".join(lines)

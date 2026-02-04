"""Manager automation system for MyRPG."""

from .base import Manager
from .task_managers import MiningForeman, CourseInstructor, MeditationGuide, RunningCoach
from .department_managers import PhysicalDirector, MentalDirector
from .executives import VPOfTraining, CEO
from .registry import ManagerRegistry

__all__ = [
    "Manager",
    "MiningForeman",
    "CourseInstructor",
    "MeditationGuide",
    "RunningCoach",
    "PhysicalDirector",
    "MentalDirector",
    "VPOfTraining",
    "CEO",
    "ManagerRegistry",
]

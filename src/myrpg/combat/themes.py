"""Combat themes - the four distinct combat styles."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..training.variables import ControllingVariables


class ThemeType(Enum):
    """The four combat themes in sequence order."""
    UNARMED = 0
    ARMED = 1
    RANGED = 2
    ENERGY = 3

    def next(self) -> "ThemeType":
        """Get the next theme in the cycle."""
        return ThemeType((self.value + 1) % 4)


@dataclass
class CombatStats:
    """Calculated combat statistics for a theme."""
    damage_multiplier: float
    attack_speed: float  # attacks per second
    range: int  # tiles
    special_value: float  # theme-specific (combo, crit, energy, etc.)


class CombatTheme(ABC):
    """Base class for combat themes."""

    @property
    @abstractmethod
    def theme_type(self) -> ThemeType:
        """The type of this combat theme."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Display name of the theme."""
        pass

    @property
    @abstractmethod
    def base_attack_speed(self) -> float:
        """Base attacks per second."""
        pass

    @property
    @abstractmethod
    def base_range(self) -> int:
        """Base attack range in tiles."""
        pass

    @property
    @abstractmethod
    def unlock_requirement(self) -> int:
        """Mastery level required in previous theme to unlock."""
        pass

    @abstractmethod
    def calculate_damage_bonus(self, variables: "ControllingVariables") -> float:
        """Calculate damage bonus from controlling variables."""
        pass

    @abstractmethod
    def calculate_special(self, variables: "ControllingVariables") -> float:
        """Calculate theme-specific special value."""
        pass

    def get_combat_stats(
        self,
        variables: "ControllingVariables",
        mastery_level: int = 0,
    ) -> CombatStats:
        """Calculate full combat statistics."""
        damage_bonus = self.calculate_damage_bonus(variables)
        mastery_bonus = 1 + (mastery_level * 0.01)  # 1% per mastery level

        return CombatStats(
            damage_multiplier=damage_bonus * mastery_bonus,
            attack_speed=self.base_attack_speed,
            range=self.base_range,
            special_value=self.calculate_special(variables),
        )


class Unarmed(CombatTheme):
    """
    Unarmed combat - close range, fast attacks, combo-based.

    Primary scaling: Strength (70%), Endurance (30%)
    Special mechanic: Combo chains increase damage
    """

    @property
    def theme_type(self) -> ThemeType:
        return ThemeType.UNARMED

    @property
    def name(self) -> str:
        return "Unarmed"

    @property
    def base_attack_speed(self) -> float:
        return 2.0  # 2 attacks per second (0.5s per attack)

    @property
    def base_range(self) -> int:
        return 1  # Melee range

    @property
    def unlock_requirement(self) -> int:
        return 0  # Default starting theme

    def calculate_damage_bonus(self, variables: "ControllingVariables") -> float:
        return 1.0 + variables.calculate_unarmed_bonus()

    def calculate_special(self, variables: "ControllingVariables") -> float:
        """Calculate combo window duration in seconds."""
        base_window = 2.0
        endurance_bonus = variables.endurance.effective_value * 0.005
        return base_window + endurance_bonus


class Armed(CombatTheme):
    """
    Armed combat - melee to short range, balanced, equipment-focused.

    Primary scaling: Strength (50%), Dexterity (50%)
    Special mechanic: Weapon variety with unique movesets
    """

    @property
    def theme_type(self) -> ThemeType:
        return ThemeType.ARMED

    @property
    def name(self) -> str:
        return "Armed"

    @property
    def base_attack_speed(self) -> float:
        return 1.25  # 1.25 attacks per second (0.8s per attack)

    @property
    def base_range(self) -> int:
        return 1  # Base melee, weapons can extend

    @property
    def unlock_requirement(self) -> int:
        return 10  # Requires Unarmed Mastery 10

    def calculate_damage_bonus(self, variables: "ControllingVariables") -> float:
        return 1.0 + variables.calculate_armed_bonus()

    def calculate_special(self, variables: "ControllingVariables") -> float:
        """Calculate critical hit chance percentage."""
        base_crit = 5.0
        dex_bonus = variables.dexterity.effective_value * 0.1
        return min(base_crit + dex_bonus, 50.0)  # Cap at 50%


class Ranged(CombatTheme):
    """
    Ranged combat - long range, positioning-dependent, precision-based.

    Primary scaling: Dexterity (60%), Focus (40%)
    Special mechanic: Critical distance bonuses
    """

    @property
    def theme_type(self) -> ThemeType:
        return ThemeType.RANGED

    @property
    def name(self) -> str:
        return "Ranged"

    @property
    def base_attack_speed(self) -> float:
        return 0.83  # ~1.2s per attack

    @property
    def base_range(self) -> int:
        return 6  # Long range base

    @property
    def unlock_requirement(self) -> int:
        return 10  # Requires Armed Mastery 10

    def calculate_damage_bonus(self, variables: "ControllingVariables") -> float:
        return 1.0 + variables.calculate_ranged_bonus()

    def calculate_special(self, variables: "ControllingVariables") -> float:
        """Calculate optimal range bracket width."""
        base_bracket = 2  # 5-6 tiles optimal
        focus_bonus = variables.focus.effective_value * 0.01
        return base_bracket + focus_bonus


class Energy(CombatTheme):
    """
    Energy combat - variable range, resource-intensive, highest damage potential.

    Primary scaling: Focus (60%), Endurance (40%)
    Special mechanic: Energy pool management
    """

    @property
    def theme_type(self) -> ThemeType:
        return ThemeType.ENERGY

    @property
    def name(self) -> str:
        return "Energy"

    @property
    def base_attack_speed(self) -> float:
        return 1.0  # Variable, but base 1 per second

    @property
    def base_range(self) -> int:
        return 4  # Medium range, abilities vary

    @property
    def unlock_requirement(self) -> int:
        return 10  # Requires Ranged Mastery 10

    def calculate_damage_bonus(self, variables: "ControllingVariables") -> float:
        return 1.0 + variables.calculate_energy_bonus()

    def calculate_special(self, variables: "ControllingVariables") -> float:
        """Calculate max energy pool."""
        base_energy = 100
        focus_bonus = variables.focus.effective_value * 5
        return base_energy + focus_bonus


# Theme registry for easy access
THEMES: dict[ThemeType, type[CombatTheme]] = {
    ThemeType.UNARMED: Unarmed,
    ThemeType.ARMED: Armed,
    ThemeType.RANGED: Ranged,
    ThemeType.ENERGY: Energy,
}


def get_theme(theme_type: ThemeType) -> CombatTheme:
    """Get an instance of a combat theme by type."""
    return THEMES[theme_type]()


def get_next_theme(current: ThemeType) -> ThemeType:
    """Get the next theme in the cycle."""
    return current.next()

"""Theme Mastery - progression within each combat theme."""

from dataclasses import dataclass, field
from typing import Callable
import math

from .themes import ThemeType


@dataclass
class MasteryMilestone:
    """A milestone reached in theme mastery."""
    level: int
    theme: ThemeType
    bonus_description: str


@dataclass
class ThemeMastery:
    """
    Tracks mastery progression for all combat themes.

    Each theme has its own mastery level that increases through combat.
    Higher mastery grants theme-specific bonuses.
    """

    _levels: dict[ThemeType, int] = field(default_factory=lambda: {
        ThemeType.UNARMED: 0,
        ThemeType.ARMED: 0,
        ThemeType.RANGED: 0,
        ThemeType.ENERGY: 0,
    })
    _xp: dict[ThemeType, float] = field(default_factory=lambda: {
        ThemeType.UNARMED: 0.0,
        ThemeType.ARMED: 0.0,
        ThemeType.RANGED: 0.0,
        ThemeType.ENERGY: 0.0,
    })
    _listeners: list[Callable[[ThemeType, int], None]] = field(
        default_factory=list, repr=False
    )

    MAX_LEVEL: int = 100

    def get_level(self, theme: ThemeType) -> int:
        """Get current mastery level for a theme."""
        return self._levels[theme]

    def get_xp(self, theme: ThemeType) -> float:
        """Get current XP for a theme."""
        return self._xp[theme]

    def get_xp_required(self, level: int) -> float:
        """
        Calculate XP required for a level.

        Formula: 100 × (level ^ 1.5)
        """
        if level <= 0:
            return 0
        return 100 * (level ** 1.5)

    def get_xp_for_next_level(self, theme: ThemeType) -> float:
        """Get XP needed for next level."""
        current_level = self._levels[theme]
        if current_level >= self.MAX_LEVEL:
            return float('inf')
        return self.get_xp_required(current_level + 1)

    def get_xp_progress(self, theme: ThemeType) -> float:
        """Get progress to next level as percentage (0-100)."""
        current_level = self._levels[theme]
        if current_level >= self.MAX_LEVEL:
            return 100.0

        current_threshold = self.get_xp_required(current_level)
        next_threshold = self.get_xp_required(current_level + 1)
        current_xp = self._xp[theme]

        xp_into_level = current_xp - current_threshold
        xp_needed = next_threshold - current_threshold

        return (xp_into_level / xp_needed) * 100

    def add_xp(self, theme: ThemeType, amount: float) -> list[MasteryMilestone]:
        """
        Add mastery XP for a theme.

        Returns list of milestones reached.
        """
        if amount <= 0:
            return []

        milestones = []
        self._xp[theme] += amount

        # Check for level ups
        while self._levels[theme] < self.MAX_LEVEL:
            next_level = self._levels[theme] + 1
            required = self.get_xp_required(next_level)

            if self._xp[theme] >= required:
                self._levels[theme] = next_level
                milestone = self._create_milestone(theme, next_level)
                if milestone:
                    milestones.append(milestone)
                self._notify_listeners(theme, next_level)
            else:
                break

        return milestones

    def _create_milestone(self, theme: ThemeType, level: int) -> MasteryMilestone | None:
        """Create a milestone for significant levels."""
        # Only create milestones for levels divisible by 10
        if level % 10 != 0:
            return None

        bonuses = {
            ThemeType.UNARMED: {
                10: "Combo window +0.5s",
                20: "Finisher damage ×2.5",
                30: "6th hit added to combo",
                40: "Strength gains +10% effectiveness",
                50: "Unlock 'Flurry' ability",
                60: "Combo damage +25%",
                70: "7th hit added to combo",
                80: "Unarmed range +1",
                90: "Finisher damage ×3.0",
                100: "Unlock 'One Punch' ultimate",
            },
            ThemeType.ARMED: {
                10: "Weapon swap is instant",
                20: "+15% damage with all weapons",
                30: "Carry 3 weapons",
                40: "Dexterity gains +10% effectiveness",
                50: "Unlock 'Arsenal' ability",
                60: "Critical damage +50%",
                70: "Carry 4 weapons",
                80: "+25% attack speed",
                90: "All weapon bonuses doubled",
                100: "Unlock 'Blade Storm' ultimate",
            },
            ThemeType.RANGED: {
                10: "Optimal range +1 tile",
                20: "Special ammo capacity +50%",
                30: "Unlock 'Quick Draw' ability",
                40: "Focus gains +10% effectiveness",
                50: "Unlock 'Sniper Mode' ability",
                60: "Critical distance bonus +25%",
                70: "Optimal range +2 tiles",
                80: "Reload speed +50%",
                90: "Piercing shots standard",
                100: "Unlock 'Rain of Arrows' ultimate",
            },
            ThemeType.ENERGY: {
                10: "Overheat threshold raised to 90%",
                20: "Unlock 'Siphon' ability",
                30: "Charge attacks 1s faster",
                40: "Endurance gains +10% effectiveness",
                50: "Unlock 'Unlimited' ability",
                60: "Energy regen +50%",
                70: "No overheat penalty",
                80: "Ability costs -25%",
                90: "Charge damage ×4",
                100: "Unlock 'Supernova' ultimate",
            },
        }

        theme_bonuses = bonuses.get(theme, {})
        description = theme_bonuses.get(level, f"Mastery Level {level}")

        return MasteryMilestone(
            level=level,
            theme=theme,
            bonus_description=description,
        )

    def is_theme_unlocked(self, theme: ThemeType) -> bool:
        """Check if a theme is unlocked based on previous theme mastery."""
        if theme == ThemeType.UNARMED:
            return True  # Always unlocked

        # Get the previous theme in sequence
        prev_theme = ThemeType((theme.value - 1) % 4)
        required_mastery = 10

        return self._levels[prev_theme] >= required_mastery

    def get_unlocked_themes(self) -> list[ThemeType]:
        """Get list of all unlocked themes."""
        return [t for t in ThemeType if self.is_theme_unlocked(t)]

    def count_themes_at_level(self, level: int) -> int:
        """Count how many themes have reached a certain mastery level."""
        return sum(1 for lvl in self._levels.values() if lvl >= level)

    def calculate_versatility_bonus(self) -> float:
        """
        Calculate the Martial Versatility bonus.

        2 themes at 50+: +5% damage
        3 themes at 50+: +10% damage
        4 themes at 50+: +20% damage
        """
        count = self.count_themes_at_level(50)
        if count >= 4:
            return 0.20
        elif count >= 3:
            return 0.10
        elif count >= 2:
            return 0.05
        return 0.0

    def can_theme_shift(self) -> bool:
        """Check if Theme Shift ability is unlocked (all themes at 50+)."""
        return self.count_themes_at_level(50) >= 4

    def on_level_up(self, callback: Callable[[ThemeType, int], None]) -> None:
        """Register a listener for mastery level ups."""
        self._listeners.append(callback)

    def _notify_listeners(self, theme: ThemeType, level: int) -> None:
        for listener in self._listeners:
            listener(theme, level)

    def __str__(self) -> str:
        parts = [f"{t.name}: {self._levels[t]}" for t in ThemeType]
        return "Mastery - " + " | ".join(parts)

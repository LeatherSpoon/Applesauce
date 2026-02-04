"""Pedometer - step counter for speed upgrades with spend-all mechanic."""

from dataclasses import dataclass, field
from typing import Callable
from enum import Enum
import math


class SpeedUpgradeResult(Enum):
    """Result of attempting a pedometer spend."""
    SUCCESS = "success"
    INSUFFICIENT_STEPS = "insufficient_steps"
    SPEED_CAPPED = "speed_capped"


@dataclass
class SpeedUpgrade:
    """Represents a speed upgrade from spending pedometer steps."""
    steps_spent: int
    speed_bonus_percent: float
    achievement_bonus: float = 0.0


@dataclass
class Pedometer:
    """
    Lifetime step counter with spend-all-or-nothing mechanic.

    - Accumulates from movement
    - Spending depletes the entire counter (full reset)
    - Grants speed upgrades up to a cap
    - Beyond cap, grants Power Level achievement bonuses
    """

    _steps: int = field(default=0)
    _total_steps_ever: int = field(default=0)
    _speed_bonus_percent: float = field(default=0.0)
    _times_spent: int = field(default=0)
    _listeners: list[Callable[[int], None]] = field(default_factory=list, repr=False)

    # Speed cap from pedometer upgrades (500% = 6x base speed)
    SPEED_CAP_PERCENT: float = 500.0

    @property
    def steps(self) -> int:
        """Current accumulated steps (spendable)."""
        return self._steps

    @property
    def total_steps_ever(self) -> int:
        """Lifetime total steps taken."""
        return self._total_steps_ever

    @property
    def speed_bonus_percent(self) -> float:
        """Current permanent speed bonus from pedometer spending."""
        return self._speed_bonus_percent

    @property
    def is_speed_capped(self) -> bool:
        """Whether speed bonus has reached the cap."""
        return self._speed_bonus_percent >= self.SPEED_CAP_PERCENT

    @property
    def times_spent(self) -> int:
        """Number of times the pedometer has been spent."""
        return self._times_spent

    def add_steps(self, amount: int) -> None:
        """Add steps from movement."""
        if amount < 0:
            raise ValueError("Cannot remove steps")
        if amount == 0:
            return
        self._steps += amount
        self._total_steps_ever += amount
        self._notify_listeners(self._steps)

    def calculate_spend_reward(self) -> SpeedUpgrade:
        """
        Calculate what reward would be given for spending current steps.
        Uses logarithmic scaling: speed_bonus = log10(steps) * 10
        """
        if self._steps < 100:
            return SpeedUpgrade(
                steps_spent=self._steps,
                speed_bonus_percent=0.0,
                achievement_bonus=0.0
            )

        # Logarithmic speed bonus
        raw_bonus = math.log10(self._steps) * 10

        # Check if we're at or beyond the cap
        if self.is_speed_capped:
            # All bonus goes to achievement (Power Level bonus)
            return SpeedUpgrade(
                steps_spent=self._steps,
                speed_bonus_percent=0.0,
                achievement_bonus=raw_bonus / 10  # Reduced rate for achievements
            )

        # Calculate how much speed bonus we can actually grant
        remaining_cap = self.SPEED_CAP_PERCENT - self._speed_bonus_percent
        actual_speed_bonus = min(raw_bonus, remaining_cap)
        overflow_bonus = raw_bonus - actual_speed_bonus

        return SpeedUpgrade(
            steps_spent=self._steps,
            speed_bonus_percent=actual_speed_bonus,
            achievement_bonus=overflow_bonus / 10 if overflow_bonus > 0 else 0.0
        )

    def spend(self) -> SpeedUpgradeResult:
        """
        Spend ALL current steps to receive speed upgrade.

        Returns the result of the spend attempt.
        """
        if self._steps < 100:
            return SpeedUpgradeResult.INSUFFICIENT_STEPS

        reward = self.calculate_spend_reward()

        # Apply the reward
        self._speed_bonus_percent = min(
            self._speed_bonus_percent + reward.speed_bonus_percent,
            self.SPEED_CAP_PERCENT
        )

        # Reset step counter
        self._steps = 0
        self._times_spent += 1
        self._notify_listeners(0)

        if reward.speed_bonus_percent == 0 and self.is_speed_capped:
            return SpeedUpgradeResult.SPEED_CAPPED

        return SpeedUpgradeResult.SUCCESS

    def get_speed_multiplier(self) -> float:
        """Get the total speed multiplier (1.0 = base speed)."""
        return 1.0 + (self._speed_bonus_percent / 100)

    def on_change(self, callback: Callable[[int], None]) -> None:
        """Register a listener for step count changes."""
        self._listeners.append(callback)

    def _notify_listeners(self, steps: int) -> None:
        for listener in self._listeners:
            listener(steps)

    def __str__(self) -> str:
        return (
            f"Pedometer: {self._steps:,} steps "
            f"(+{self._speed_bonus_percent:.1f}% speed)"
        )

"""Infinite Tournament - the endgame loop for each environment."""

from dataclasses import dataclass, field
from typing import Callable
from enum import Enum


class TournamentResult(Enum):
    """Result of a tournament battle."""
    VICTORY = "victory"
    DEFEAT = "defeat"


@dataclass
class TournamentOpponent:
    """An opponent in the infinite tournament."""
    wave_number: int
    power_level: float
    gold_reward: int


@dataclass
class InfiniteTournament:
    """
    The infinite tournament mode unlocked after defeating an environment's boss.

    - Opponents scale infinitely (+5% power per wave)
    - Player eventually loses (expected outcome)
    - Defeat triggers progression to new environment
    """

    environment_tier: int
    base_opponent_power: float = field(default=100.0)
    _current_wave: int = field(default=0)
    _victories: int = field(default=0)
    _total_gold_earned: int = field(default=0)
    _listeners: list[Callable[[TournamentResult, int], None]] = field(
        default_factory=list, repr=False
    )

    # Scaling constants
    POWER_SCALE_PER_WAVE: float = 1.05  # +5% per wave
    GOLD_BASE_REWARD: int = 50
    GOLD_SCALE_PER_WAVE: float = 1.1  # +10% gold per wave

    @property
    def current_wave(self) -> int:
        return self._current_wave

    @property
    def victories(self) -> int:
        return self._victories

    @property
    def total_gold_earned(self) -> int:
        return self._total_gold_earned

    def get_current_opponent(self) -> TournamentOpponent:
        """Get the current opponent to face."""
        wave = self._current_wave + 1

        # Calculate opponent power: base × tier × (1.05 ^ wave)
        power = (
            self.base_opponent_power *
            self.environment_tier *
            (self.POWER_SCALE_PER_WAVE ** wave)
        )

        # Calculate gold reward
        gold = int(
            self.GOLD_BASE_REWARD *
            self.environment_tier *
            (self.GOLD_SCALE_PER_WAVE ** wave)
        )

        return TournamentOpponent(
            wave_number=wave,
            power_level=power,
            gold_reward=gold,
        )

    def fight(self, player_power: float) -> tuple[TournamentResult, TournamentOpponent]:
        """
        Fight the current opponent.

        Args:
            player_power: The player's effective power level

        Returns:
            Tuple of (result, opponent fought)
        """
        opponent = self.get_current_opponent()

        # Simple combat resolution: player wins if power > opponent * 0.8
        # This gives some variance and makes it possible to win against
        # slightly stronger opponents
        win_threshold = opponent.power_level * 0.8

        if player_power >= win_threshold:
            result = TournamentResult.VICTORY
            self._victories += 1
            self._total_gold_earned += opponent.gold_reward
            self._current_wave += 1
        else:
            result = TournamentResult.DEFEAT

        self._notify_listeners(result, self._current_wave)
        return result, opponent

    def calculate_expected_defeat_wave(self, player_power: float) -> int:
        """
        Estimate which wave the player will likely be defeated.

        This helps with UI/planning.
        """
        wave = 1
        while True:
            opponent_power = (
                self.base_opponent_power *
                self.environment_tier *
                (self.POWER_SCALE_PER_WAVE ** wave)
            )
            if player_power < opponent_power * 0.8:
                return wave
            wave += 1
            if wave > 1000:  # Safety cap
                return wave

    def reset(self) -> None:
        """Reset the tournament (for a new attempt)."""
        self._current_wave = 0
        self._victories = 0
        self._total_gold_earned = 0

    def on_battle(self, callback: Callable[[TournamentResult, int], None]) -> None:
        """Register a listener for battle results."""
        self._listeners.append(callback)

    def _notify_listeners(self, result: TournamentResult, wave: int) -> None:
        for listener in self._listeners:
            listener(result, wave)

    def __str__(self) -> str:
        return f"Tournament Wave {self._current_wave + 1} ({self._victories} victories)"

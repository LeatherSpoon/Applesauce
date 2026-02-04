"""Environment - themed game areas with Masters, mobs, and bosses."""

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from .master import Master, get_master_for_tier
from .tournament import InfiniteTournament

if TYPE_CHECKING:
    from ..combat.themes import ThemeType


class EnvironmentState(Enum):
    """Current state of an environment."""
    LOCKED = "locked"
    TRAINING = "training"
    FARMING = "farming"
    BOSS_AVAILABLE = "boss_available"
    BOSS_DEFEATED = "boss_defeated"
    TOURNAMENT_ACTIVE = "tournament_active"


@dataclass
class EnvironmentConfig:
    """Configuration for an environment."""
    name: str
    tier: int
    description: str
    min_speed_required: int
    boss_power_level: float
    mob_base_power: float
    gold_per_mob: int


# Predefined environments
ENVIRONMENT_CONFIGS = [
    EnvironmentConfig(
        name="Forest Dojo",
        tier=1,
        description="A peaceful forest with a hidden martial arts school",
        min_speed_required=100,
        boss_power_level=500,
        mob_base_power=50,
        gold_per_mob=10,
    ),
    EnvironmentConfig(
        name="Iron Fortress",
        tier=2,
        description="An ancient fortress where knights train for battle",
        min_speed_required=150,
        boss_power_level=1500,
        mob_base_power=150,
        gold_per_mob=25,
    ),
    EnvironmentConfig(
        name="Wind Valley",
        tier=3,
        description="A vast valley with perfect conditions for archery",
        min_speed_required=225,
        boss_power_level=4000,
        mob_base_power=400,
        gold_per_mob=50,
    ),
    EnvironmentConfig(
        name="Crystal Spire",
        tier=4,
        description="A tower of pure crystal resonating with magical energy",
        min_speed_required=350,
        boss_power_level=10000,
        mob_base_power=1000,
        gold_per_mob=100,
    ),
    EnvironmentConfig(
        name="Sand Temple",
        tier=5,
        description="An ancient temple buried in the endless desert",
        min_speed_required=500,
        boss_power_level=25000,
        mob_base_power=2500,
        gold_per_mob=200,
    ),
    EnvironmentConfig(
        name="Frozen Peaks",
        tier=6,
        description="Mountain peaks where only the strongest survive",
        min_speed_required=600,
        boss_power_level=60000,
        mob_base_power=6000,
        gold_per_mob=400,
    ),
]


@dataclass
class Environment:
    """
    A themed game environment containing a Master, mobs, and boss.

    Progression flow:
    1. Train with Master
    2. Farm mobs for gold/XP
    3. Challenge boss
    4. Enter infinite tournament
    5. Defeat → unlock next environment
    """

    config: EnvironmentConfig
    master: Master = field(init=False)
    tournament: InfiniteTournament = field(init=False)
    _state: EnvironmentState = field(default=EnvironmentState.LOCKED)
    _mobs_defeated: int = field(default=0)
    _boss_defeated: bool = field(default=False)
    _training_completed: bool = field(default=False)

    def __post_init__(self) -> None:
        self.master = get_master_for_tier(self.config.tier)
        self.tournament = InfiniteTournament(
            environment_tier=self.config.tier,
            base_opponent_power=self.config.boss_power_level,
        )

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def tier(self) -> int:
        return self.config.tier

    @property
    def state(self) -> EnvironmentState:
        return self._state

    @property
    def theme(self) -> "ThemeType":
        return self.master.theme

    @property
    def is_unlocked(self) -> bool:
        return self._state != EnvironmentState.LOCKED

    @property
    def is_boss_defeated(self) -> bool:
        return self._boss_defeated

    @property
    def mobs_defeated(self) -> int:
        return self._mobs_defeated

    def unlock(self) -> None:
        """Unlock this environment for play."""
        if self._state == EnvironmentState.LOCKED:
            self._state = EnvironmentState.TRAINING

    def can_enter(self, player_speed: float) -> bool:
        """Check if player meets speed requirements."""
        return player_speed >= self.config.min_speed_required

    def get_speed_penalty(self, player_speed: float) -> float:
        """
        Calculate speed penalty if below requirements.

        Returns multiplier (1.0 = no penalty, 0.5 = half speed, etc.)
        """
        if player_speed >= self.config.min_speed_required:
            return 1.0
        return player_speed / self.config.min_speed_required

    def complete_training(self) -> None:
        """Mark training as completed, enabling farming."""
        if self._state == EnvironmentState.TRAINING:
            self._training_completed = True
            self._state = EnvironmentState.FARMING

    def defeat_mob(self, player_power: float) -> tuple[bool, int]:
        """
        Attempt to defeat a mob.

        Args:
            player_power: Player's effective power level

        Returns:
            Tuple of (success, gold_earned)
        """
        if player_power >= self.config.mob_base_power * 0.5:
            self._mobs_defeated += 1
            gold = self.config.gold_per_mob

            # Check if boss should become available (every 50 mobs)
            if not self._boss_defeated and self._mobs_defeated >= 50:
                self._state = EnvironmentState.BOSS_AVAILABLE

            return True, gold
        return False, 0

    def challenge_boss(self, player_power: float) -> bool:
        """
        Challenge the environment boss.

        Args:
            player_power: Player's effective power level

        Returns:
            True if boss defeated, False otherwise
        """
        if self._state != EnvironmentState.BOSS_AVAILABLE:
            return False

        if player_power >= self.config.boss_power_level * 0.7:
            self._boss_defeated = True
            self._state = EnvironmentState.BOSS_DEFEATED
            return True
        return False

    def enter_tournament(self) -> InfiniteTournament | None:
        """
        Enter the infinite tournament (after boss defeated).

        Returns the tournament if successful, None otherwise.
        """
        if self._state == EnvironmentState.BOSS_DEFEATED:
            self._state = EnvironmentState.TOURNAMENT_ACTIVE
            self.tournament.reset()
            return self.tournament
        return None

    def __str__(self) -> str:
        return f"{self.name} (Tier {self.tier}) - {self._state.value}"


def create_environment(tier: int) -> Environment:
    """Create an environment for a specific tier."""
    # Cycle through configs if tier exceeds defined environments
    config_index = (tier - 1) % len(ENVIRONMENT_CONFIGS)
    base_config = ENVIRONMENT_CONFIGS[config_index]

    # Scale for higher tiers
    tier_multiplier = 2 ** ((tier - 1) // len(ENVIRONMENT_CONFIGS))

    config = EnvironmentConfig(
        name=f"{base_config.name} {'II' * ((tier - 1) // len(ENVIRONMENT_CONFIGS))}".strip(),
        tier=tier,
        description=base_config.description,
        min_speed_required=int(base_config.min_speed_required * (1 + (tier - 1) * 0.2)),
        boss_power_level=base_config.boss_power_level * tier_multiplier,
        mob_base_power=base_config.mob_base_power * tier_multiplier,
        gold_per_mob=base_config.gold_per_mob * tier_multiplier,
    )

    return Environment(config=config)

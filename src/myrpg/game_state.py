"""Game State - the central state manager for MyRPG."""

from dataclasses import dataclass, field
from typing import Callable
from enum import Enum

from .currencies import PowerLevel, Pedometer, Gold
from .training import ControllingVariables
from .combat import ThemeType, ThemeMastery, get_theme
from .managers import ManagerRegistry
from .environments import Environment, create_environment, InfiniteTournament
from .environments.tournament import TournamentResult


class GameEvent(Enum):
    """Events that can occur during gameplay."""
    ENVIRONMENT_UNLOCKED = "environment_unlocked"
    BOSS_DEFEATED = "boss_defeated"
    TOURNAMENT_DEFEAT = "tournament_defeat"
    THEME_UNLOCKED = "theme_unlocked"
    MASTERY_MILESTONE = "mastery_milestone"
    PRESTIGE = "prestige"


@dataclass
class GameState:
    """
    Central game state managing all systems.

    This is the main entry point for game logic, coordinating:
    - Currencies (Power Level, Pedometer, Gold)
    - Controlling Variables
    - Combat Themes and Mastery
    - Managers
    - Environments and Progression
    """

    # Core currencies
    power_level: PowerLevel = field(default_factory=PowerLevel)
    pedometer: Pedometer = field(default_factory=Pedometer)
    gold: Gold = field(default_factory=Gold)

    # Stats and combat
    variables: ControllingVariables = field(default_factory=ControllingVariables)
    mastery: ThemeMastery = field(default_factory=ThemeMastery)
    _current_theme: ThemeType = field(default=ThemeType.UNARMED)

    # Managers
    managers: ManagerRegistry = field(default_factory=ManagerRegistry)

    # Environments
    _environments: list[Environment] = field(default_factory=list)
    _current_environment_index: int = field(default=0)
    _active_tournament: InfiniteTournament | None = field(default=None)

    # Time tracking for automation
    _last_update_time: float = field(default=0.0)

    # Event listeners
    _event_listeners: list[Callable[[GameEvent, dict], None]] = field(
        default_factory=list, repr=False
    )

    def __post_init__(self) -> None:
        """Initialize the game with starting environment."""
        if not self._environments:
            first_env = create_environment(1)
            first_env.unlock()
            self._environments.append(first_env)

    # ==================== Properties ====================

    @property
    def current_theme(self) -> ThemeType:
        return self._current_theme

    @property
    def current_environment(self) -> Environment:
        return self._environments[self._current_environment_index]

    @property
    def unlocked_environments(self) -> list[Environment]:
        return [e for e in self._environments if e.is_unlocked]

    @property
    def active_tournament(self) -> InfiniteTournament | None:
        return self._active_tournament

    # ==================== Combat ====================

    def get_effective_power(self) -> float:
        """Calculate effective combat power including all bonuses."""
        theme = get_theme(self._current_theme)
        stats = theme.get_combat_stats(
            self.variables,
            self.mastery.get_level(self._current_theme)
        )

        base_power = self.power_level.value
        theme_multiplier = stats.damage_multiplier
        versatility_bonus = 1 + self.mastery.calculate_versatility_bonus()

        return base_power * theme_multiplier * versatility_bonus

    def switch_theme(self, theme: ThemeType) -> bool:
        """
        Switch to a different combat theme.

        Returns True if successful, False if theme is locked.
        """
        if not self.mastery.is_theme_unlocked(theme):
            return False
        self._current_theme = theme
        return True

    def get_unlocked_themes(self) -> list[ThemeType]:
        """Get all unlocked combat themes."""
        return self.mastery.get_unlocked_themes()

    # ==================== Movement & Speed ====================

    def get_current_speed(self) -> float:
        """Get current movement speed including all bonuses."""
        base_speed = 100.0
        pedometer_multiplier = self.pedometer.get_speed_multiplier()
        # Could add equipment/tile bonuses here
        return base_speed * pedometer_multiplier

    def move(self, steps: int = 1) -> None:
        """Process movement, adding to pedometer."""
        self.pedometer.add_steps(steps)

    def spend_pedometer(self) -> bool:
        """Spend all pedometer steps for speed upgrade."""
        from .currencies.pedometer import SpeedUpgradeResult

        result = self.pedometer.spend()
        if result == SpeedUpgradeResult.SUCCESS:
            # Could grant achievement power level bonus here
            return True
        return False

    # ==================== Combat & Farming ====================

    def farm_mob(self) -> tuple[bool, int, float]:
        """
        Farm a mob in the current environment.

        Returns: (success, gold_earned, xp_earned)
        """
        env = self.current_environment
        power = self.get_effective_power()

        success, gold = env.defeat_mob(power)
        if success:
            self.gold.add(gold, source=f"Mob in {env.name}")

            # Add mastery XP
            xp_gained = 10.0 * env.tier
            milestones = self.mastery.add_xp(self._current_theme, xp_gained)

            # Check for theme unlocks
            for milestone in milestones:
                if milestone.level == 10:
                    next_theme = self._current_theme.next()
                    if self.mastery.is_theme_unlocked(next_theme):
                        self._emit_event(GameEvent.THEME_UNLOCKED, {"theme": next_theme})
                self._emit_event(GameEvent.MASTERY_MILESTONE, {"milestone": milestone})

            # Small power level increase
            self.power_level.add(0.1 * env.tier)

            return True, gold, xp_gained
        return False, 0, 0.0

    def challenge_boss(self) -> bool:
        """Challenge the current environment's boss."""
        env = self.current_environment
        power = self.get_effective_power()

        if env.challenge_boss(power):
            # Bonus rewards for boss defeat
            boss_gold = env.config.gold_per_mob * 50
            self.gold.add(boss_gold, source=f"Boss in {env.name}")
            self.power_level.add(env.tier * 10)
            self._emit_event(GameEvent.BOSS_DEFEATED, {"environment": env})
            return True
        return False

    # ==================== Tournament ====================

    def enter_tournament(self) -> bool:
        """Enter the infinite tournament for current environment."""
        tournament = self.current_environment.enter_tournament()
        if tournament:
            self._active_tournament = tournament
            return True
        return False

    def fight_tournament(self) -> tuple[TournamentResult, int]:
        """
        Fight the next tournament opponent.

        Returns: (result, gold_earned)
        """
        if not self._active_tournament:
            raise ValueError("Not in a tournament")

        power = self.get_effective_power()
        result, opponent = self._active_tournament.fight(power)

        gold_earned = 0
        if result == TournamentResult.VICTORY:
            gold_earned = opponent.gold_reward
            self.gold.add(gold_earned, source="Tournament victory")
            self.power_level.add(1.0 * self.current_environment.tier)
        else:
            # Defeat triggers progression
            self._handle_tournament_defeat()

        return result, gold_earned

    def _handle_tournament_defeat(self) -> None:
        """Handle tournament defeat - unlock next environment."""
        current_tier = self.current_environment.tier

        # Create and unlock next environment
        next_env = create_environment(current_tier + 1)
        next_env.unlock()
        self._environments.append(next_env)

        # Move to new environment
        self._current_environment_index = len(self._environments) - 1

        # Switch to new theme (cycling)
        new_theme = self._current_theme.next()
        if self.mastery.is_theme_unlocked(new_theme):
            self._current_theme = new_theme

        # Clear tournament
        self._active_tournament = None

        self._emit_event(GameEvent.TOURNAMENT_DEFEAT, {
            "old_environment": self._environments[-2],
            "new_environment": next_env,
            "new_theme": new_theme,
        })

    def leave_tournament(self) -> None:
        """Leave the current tournament without defeat penalty."""
        self._active_tournament = None

    # ==================== Environment Navigation ====================

    def travel_to_environment(self, index: int) -> bool:
        """Travel to a different unlocked environment."""
        if 0 <= index < len(self._environments):
            env = self._environments[index]
            if env.is_unlocked:
                self._current_environment_index = index
                self._active_tournament = None
                return True
        return False

    def can_enter_current_environment(self) -> bool:
        """Check if player meets speed requirements for current environment."""
        return self.current_environment.can_enter(self.get_current_speed())

    # ==================== Automation ====================

    def update(self, delta_seconds: float) -> dict:
        """
        Update game state for elapsed time (handles automation).

        Args:
            delta_seconds: Time elapsed since last update

        Returns:
            Dict of gains from automation
        """
        from .training.variables import VariableType

        gains = {
            "strength": 0.0,
            "dexterity": 0.0,
            "focus": 0.0,
            "endurance": 0.0,
        }

        # Calculate automated gains for each variable
        for var_type in VariableType:
            efficiency = self.managers.calculate_efficiency(var_type)
            if efficiency > 0:
                # Base rate is 10 per hour
                gains_per_second = (10.0 * efficiency) / 3600
                total_gain = gains_per_second * delta_seconds
                self.variables.add(var_type, total_gain)
                gains[var_type.value] = total_gain

        return gains

    # ==================== Managers ====================

    def hire_manager(self, manager_type: str) -> bool:
        """
        Hire a manager by type string.

        Types: 'strength', 'dexterity', 'focus', 'endurance',
               'physical_director', 'mental_director', 'vp', 'ceo'
        """
        from .currencies.gold import TransactionResult
        from .training.variables import VariableType

        cost_map = {
            "strength": self.managers.get_next_task_manager_cost(VariableType.STRENGTH),
            "dexterity": self.managers.get_next_task_manager_cost(VariableType.DEXTERITY),
            "focus": self.managers.get_next_task_manager_cost(VariableType.FOCUS),
            "endurance": self.managers.get_next_task_manager_cost(VariableType.ENDURANCE),
            "physical_director": 10000,
            "mental_director": 10000,
            "vp": 100000,
            "ceo": 1000000,
        }

        if manager_type not in cost_map:
            return False

        cost = cost_map[manager_type]
        if self.gold.spend(cost, purpose=f"Hire {manager_type}") != TransactionResult.SUCCESS:
            return False

        # Hire the appropriate manager
        if manager_type in ("strength", "dexterity", "focus", "endurance"):
            var_type = VariableType(manager_type)
            self.managers.hire_task_manager(var_type)
        elif manager_type == "physical_director":
            if not self.managers.can_hire_physical_director():
                self.gold.add(cost)  # Refund
                return False
            self.managers.hire_physical_director()
        elif manager_type == "mental_director":
            if not self.managers.can_hire_mental_director():
                self.gold.add(cost)
                return False
            self.managers.hire_mental_director()
        elif manager_type == "vp":
            if not self.managers.can_hire_vp():
                self.gold.add(cost)
                return False
            self.managers.hire_vp()
        elif manager_type == "ceo":
            if not self.managers.can_hire_ceo():
                self.gold.add(cost)
                return False
            self.managers.hire_ceo()

        return True

    def prestige(self) -> bool:
        """Perform prestige reset."""
        if not self.managers.has_ceo:
            return False

        new_level = self.managers.prestige()
        self._emit_event(GameEvent.PRESTIGE, {"level": new_level})
        return True

    # ==================== Events ====================

    def on_event(self, callback: Callable[[GameEvent, dict], None]) -> None:
        """Register a listener for game events."""
        self._event_listeners.append(callback)

    def _emit_event(self, event: GameEvent, data: dict) -> None:
        for listener in self._event_listeners:
            listener(event, data)

    # ==================== Serialization ====================

    def get_summary(self) -> str:
        """Get a text summary of current game state."""
        lines = [
            "=== MyRPG Status ===",
            str(self.power_level),
            str(self.pedometer),
            str(self.gold),
            f"Speed: {self.get_current_speed():.0f}",
            "",
            f"Current Theme: {self._current_theme.name}",
            str(self.mastery),
            "",
            str(self.variables),
            "",
            f"Environment: {self.current_environment}",
            f"Effective Power: {self.get_effective_power():.0f}",
            "",
            "Managers:",
            self.managers.get_summary(),
        ]
        return "\n".join(lines)

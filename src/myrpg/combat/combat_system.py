"""Enhanced combat system with tactical mechanics."""

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING
import random
import math

if TYPE_CHECKING:
    from ..training.variables import ControllingVariables
    from ..items import ItemStats, Weapon

from .themes import ThemeType, get_theme


class CombatResult(Enum):
    """Result of a combat encounter."""
    VICTORY = "victory"
    DEFEAT = "defeat"
    FLED = "fled"


class DamageType(Enum):
    """Types of damage in combat."""
    PHYSICAL = "physical"
    RANGED = "ranged"
    ENERGY = "energy"


@dataclass
class CombatStats:
    """Combat statistics for an entity."""
    max_health: float
    current_health: float
    attack_power: float
    defense: float
    speed: float
    crit_chance: float = 0.05
    crit_multiplier: float = 1.5
    armor_penetration: float = 0.0

    @property
    def is_alive(self) -> bool:
        return self.current_health > 0

    @property
    def health_percent(self) -> float:
        return (self.current_health / self.max_health) * 100

    def take_damage(self, amount: float, armor_pen: float = 0.0) -> float:
        """
        Apply damage after defense calculation.

        Returns actual damage taken.
        """
        # Calculate effective defense (reduced by armor penetration)
        effective_defense = self.defense * (1 - armor_pen)
        # Damage reduction formula
        reduction = effective_defense / (effective_defense + 100)
        actual_damage = amount * (1 - reduction)

        self.current_health = max(0, self.current_health - actual_damage)
        return actual_damage

    def heal(self, amount: float) -> float:
        """
        Heal health.

        Returns actual amount healed.
        """
        old_health = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        return self.current_health - old_health


@dataclass
class CombatAction:
    """A single combat action."""
    attacker_name: str
    target_name: str
    damage_dealt: float
    is_critical: bool
    damage_type: DamageType
    special_effect: str | None = None


@dataclass
class CombatLog:
    """Log of combat actions."""
    actions: list[CombatAction] = field(default_factory=list)
    total_damage_dealt: float = 0
    total_damage_taken: float = 0
    turns_taken: int = 0

    def add_action(self, action: CombatAction, is_player: bool) -> None:
        self.actions.append(action)
        if is_player:
            self.total_damage_dealt += action.damage_dealt
        else:
            self.total_damage_taken += action.damage_dealt
        self.turns_taken += 1


@dataclass
class ComboState:
    """Tracks combo state for unarmed combat."""
    current_hits: int = 0
    max_combo: int = 5
    combo_window: float = 2.0
    time_since_last_hit: float = 0.0

    def add_hit(self) -> float:
        """
        Add a combo hit.

        Returns damage multiplier for this hit.
        """
        self.time_since_last_hit = 0.0
        self.current_hits = min(self.current_hits + 1, self.max_combo)

        # Combo multipliers: 1.0, 1.1, 1.2, 1.4, 2.0 (finisher)
        multipliers = [1.0, 1.1, 1.2, 1.4, 2.0]
        return multipliers[min(self.current_hits - 1, len(multipliers) - 1)]

    def update(self, delta: float) -> None:
        """Update combo timer."""
        self.time_since_last_hit += delta
        if self.time_since_last_hit > self.combo_window:
            self.reset()

    def reset(self) -> None:
        """Reset combo."""
        self.current_hits = 0
        self.time_since_last_hit = 0.0


@dataclass
class EnergyPool:
    """Energy resource for Energy theme combat."""
    max_energy: float = 100.0
    current_energy: float = 100.0
    regen_rate: float = 5.0
    overheat_threshold: float = 0.8

    @property
    def is_overheated(self) -> bool:
        return self.current_energy < self.max_energy * (1 - self.overheat_threshold)

    @property
    def energy_percent(self) -> float:
        return (self.current_energy / self.max_energy) * 100

    def spend(self, amount: float) -> bool:
        """
        Attempt to spend energy.

        Returns True if successful.
        """
        cost = amount * (1.5 if self.is_overheated else 1.0)
        if self.current_energy >= cost:
            self.current_energy -= cost
            return True
        return False

    def regenerate(self, delta: float) -> None:
        """Regenerate energy over time."""
        if not self.is_overheated:
            self.current_energy = min(
                self.max_energy,
                self.current_energy + self.regen_rate * delta
            )


@dataclass
class Opponent:
    """An enemy in combat."""
    name: str
    stats: CombatStats
    tier: int
    gold_reward: int
    xp_reward: float
    damage_type: DamageType = DamageType.PHYSICAL

    @classmethod
    def create_mob(cls, name: str, tier: int, power_multiplier: float = 1.0) -> "Opponent":
        """Create a standard mob opponent."""
        base_health = 50 * tier * power_multiplier
        base_attack = 10 * tier * power_multiplier
        base_defense = 5 * tier * power_multiplier

        return cls(
            name=name,
            stats=CombatStats(
                max_health=base_health,
                current_health=base_health,
                attack_power=base_attack,
                defense=base_defense,
                speed=80 + tier * 5,
            ),
            tier=tier,
            gold_reward=int(10 * tier * power_multiplier),
            xp_reward=10.0 * tier,
        )

    @classmethod
    def create_boss(cls, name: str, tier: int) -> "Opponent":
        """Create a boss opponent."""
        return cls.create_mob(name, tier, power_multiplier=5.0)

    @classmethod
    def create_tournament(cls, tier: int, wave: int) -> "Opponent":
        """Create a tournament opponent with scaling difficulty."""
        power = 1.0 + (wave * 0.05)  # +5% per wave
        opponent = cls.create_mob(f"Champion #{wave + 1}", tier, power)
        opponent.gold_reward = int(opponent.gold_reward * (1 + wave * 0.1))
        return opponent


class CombatEngine:
    """Handles combat resolution and mechanics."""

    def __init__(self):
        self._rng = random.Random()
        self.combo_state = ComboState()
        self.energy_pool = EnergyPool()

    def seed(self, seed: int) -> None:
        """Set random seed for reproducible combat."""
        self._rng.seed(seed)

    def calculate_player_stats(
        self,
        base_power: float,
        variables: "ControllingVariables",
        theme: ThemeType,
        mastery_level: int,
        equipment_stats: "ItemStats | None" = None,
        weapon: "Weapon | None" = None,
    ) -> CombatStats:
        """Calculate player combat stats from all sources."""
        theme_obj = get_theme(theme)
        theme_stats = theme_obj.get_combat_stats(variables, mastery_level)

        # Base stats
        health = 100 + variables.endurance.value * 2
        attack = base_power * theme_stats.damage_multiplier
        defense = 10 + variables.endurance.value * 0.5
        speed = 100 + variables.dexterity.value * 0.5

        # Apply equipment bonuses
        if equipment_stats:
            health += equipment_stats.health_bonus
            attack *= equipment_stats.damage_multiplier
            defense *= equipment_stats.defense_multiplier
            speed += equipment_stats.speed_bonus

        # Apply weapon bonuses
        crit_chance = 0.05
        if weapon:
            attack += weapon.effective_damage
            speed *= weapon.speed_modifier
            crit_chance += weapon.crit_bonus

        return CombatStats(
            max_health=health,
            current_health=health,
            attack_power=attack,
            defense=defense,
            speed=speed,
            crit_chance=crit_chance,
        )

    def simulate_combat(
        self,
        player_stats: CombatStats,
        opponent: Opponent,
        theme: ThemeType,
        max_turns: int = 100,
    ) -> tuple[CombatResult, CombatLog]:
        """
        Simulate a full combat encounter.

        Returns result and combat log.
        """
        log = CombatLog()
        self.combo_state.reset()
        self.energy_pool.current_energy = self.energy_pool.max_energy

        while player_stats.is_alive and opponent.stats.is_alive and log.turns_taken < max_turns:
            # Determine turn order by speed
            player_first = player_stats.speed >= opponent.stats.speed

            if player_first:
                self._player_attack(player_stats, opponent, theme, log)
                if opponent.stats.is_alive:
                    self._opponent_attack(player_stats, opponent, log)
            else:
                self._opponent_attack(player_stats, opponent, log)
                if player_stats.is_alive:
                    self._player_attack(player_stats, opponent, theme, log)

        if not player_stats.is_alive:
            return CombatResult.DEFEAT, log
        return CombatResult.VICTORY, log

    def _player_attack(
        self,
        player: CombatStats,
        opponent: Opponent,
        theme: ThemeType,
        log: CombatLog,
    ) -> None:
        """Execute player attack based on theme."""
        damage_type = self._get_damage_type(theme)
        base_damage = player.attack_power

        # Apply theme-specific mechanics
        if theme == ThemeType.UNARMED:
            combo_mult = self.combo_state.add_hit()
            base_damage *= combo_mult
            special = f"Combo x{self.combo_state.current_hits}" if combo_mult > 1 else None
        elif theme == ThemeType.ENERGY:
            # Energy attacks cost energy
            if not self.energy_pool.spend(20):
                base_damage *= 0.3  # Weak attack if no energy
                special = "Low energy"
            else:
                special = None
        else:
            special = None

        # Critical hit check
        is_crit = self._rng.random() < player.crit_chance
        if is_crit:
            base_damage *= player.crit_multiplier

        # Apply damage
        actual_damage = opponent.stats.take_damage(base_damage, player.armor_penetration)

        log.add_action(CombatAction(
            attacker_name="Player",
            target_name=opponent.name,
            damage_dealt=actual_damage,
            is_critical=is_crit,
            damage_type=damage_type,
            special_effect=special,
        ), is_player=True)

    def _opponent_attack(
        self,
        player: CombatStats,
        opponent: Opponent,
        log: CombatLog,
    ) -> None:
        """Execute opponent attack."""
        # Taking damage breaks combo
        self.combo_state.reset()

        base_damage = opponent.stats.attack_power
        is_crit = self._rng.random() < opponent.stats.crit_chance

        if is_crit:
            base_damage *= opponent.stats.crit_multiplier

        actual_damage = player.take_damage(base_damage)

        log.add_action(CombatAction(
            attacker_name=opponent.name,
            target_name="Player",
            damage_dealt=actual_damage,
            is_critical=is_crit,
            damage_type=opponent.damage_type,
        ), is_player=False)

    def _get_damage_type(self, theme: ThemeType) -> DamageType:
        """Get damage type for a combat theme."""
        if theme in (ThemeType.UNARMED, ThemeType.ARMED):
            return DamageType.PHYSICAL
        elif theme == ThemeType.RANGED:
            return DamageType.RANGED
        return DamageType.ENERGY

    def quick_resolve(
        self,
        player_power: float,
        opponent_power: float,
        variance: float = 0.2,
    ) -> bool:
        """
        Quick combat resolution for farming.

        Returns True if player wins.
        """
        # Add some variance
        player_roll = player_power * (1 + self._rng.uniform(-variance, variance))
        opponent_roll = opponent_power * (1 + self._rng.uniform(-variance, variance))

        return player_roll >= opponent_roll * 0.7  # 70% threshold for victory

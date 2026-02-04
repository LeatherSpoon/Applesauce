"""Tests for the main game state."""

import pytest
from myrpg.game_state import GameState, GameEvent
from myrpg.combat.themes import ThemeType
from myrpg.environments.tournament import TournamentResult


class TestGameState:
    def test_initial_state(self):
        gs = GameState()
        assert gs.power_level.value == 1.0
        assert gs.gold.amount == 0
        assert gs.current_theme == ThemeType.UNARMED
        assert len(gs.unlocked_environments) == 1

    def test_movement_adds_steps(self):
        gs = GameState()
        gs.move(100)
        assert gs.pedometer.steps == 100

    def test_farm_mob_gives_gold(self):
        gs = GameState()
        # Boost power to ensure victory
        gs.power_level.add(1000)

        success, gold, xp = gs.farm_mob()
        assert success
        assert gold > 0
        assert gs.gold.amount > 0

    def test_farm_mob_increases_mastery(self):
        gs = GameState()
        gs.power_level.add(1000)

        initial_xp = gs.mastery.get_xp(ThemeType.UNARMED)
        gs.farm_mob()
        assert gs.mastery.get_xp(ThemeType.UNARMED) > initial_xp

    def test_theme_switching(self):
        gs = GameState()
        # Armed is initially locked
        assert not gs.switch_theme(ThemeType.ARMED)

        # Unlock Armed by leveling Unarmed
        gs.mastery.add_xp(ThemeType.UNARMED, 5000)
        assert gs.switch_theme(ThemeType.ARMED)
        assert gs.current_theme == ThemeType.ARMED

    def test_effective_power_includes_bonuses(self):
        gs = GameState()
        base_power = gs.get_effective_power()

        # Increase variables
        gs.variables.strength.add(100)
        new_power = gs.get_effective_power()

        assert new_power > base_power

    def test_environment_progression(self):
        gs = GameState()
        assert gs.current_environment.tier == 1

        # Can't enter tournament without defeating boss
        assert not gs.enter_tournament()

    def test_automation_update(self):
        gs = GameState()
        # Hire a manager
        gs.gold.add(1000)
        gs.hire_manager("strength")

        initial_str = gs.variables.strength.value

        # Simulate 1 hour
        gains = gs.update(3600)

        assert gs.variables.strength.value > initial_str
        assert gains["strength"] > 0

    def test_hire_manager(self):
        gs = GameState()
        gs.gold.add(10000)

        # Hire first manager
        assert gs.hire_manager("strength")
        assert gs.managers.get_task_manager_count(
            gs.variables.strength.type
        ) == 1

    def test_hire_manager_insufficient_gold(self):
        gs = GameState()
        assert not gs.hire_manager("strength")

    def test_game_event_listener(self):
        gs = GameState()
        events = []
        gs.on_event(lambda e, d: events.append(e))

        # Boost power and farm many mobs to reach a milestone
        gs.power_level.add(1000)

        # Farm many mobs to accumulate enough XP for level 10 milestone
        # Level 10 requires ~3162 XP, each mob gives 10 XP
        for _ in range(400):
            gs.farm_mob()

        # Should have mastery milestone events (level 10 milestone)
        assert any(e == GameEvent.MASTERY_MILESTONE for e in events)

    def test_speed_affects_environment_access(self):
        gs = GameState()
        # First environment has no speed requirement
        assert gs.can_enter_current_environment()

        # Manually check higher tier requirement
        from myrpg.environments import create_environment
        high_tier = create_environment(5)
        assert not high_tier.can_enter(gs.get_current_speed())

    def test_get_summary(self):
        gs = GameState()
        summary = gs.get_summary()
        assert "Power Level" in summary
        assert "Gold" in summary
        assert "Unarmed" in summary.upper() or "UNARMED" in summary


class TestTournamentProgression:
    def test_tournament_flow(self):
        gs = GameState()

        # Power up significantly
        gs.power_level.add(10000)

        # Farm until boss available
        for _ in range(60):
            gs.farm_mob()

        # Challenge boss
        assert gs.challenge_boss()

        # Enter tournament
        assert gs.enter_tournament()
        assert gs.active_tournament is not None

        # Fight until defeat
        victories = 0
        while True:
            result, gold = gs.fight_tournament()
            if result == TournamentResult.DEFEAT:
                break
            victories += 1
            if victories > 100:  # Safety cap
                break

        # Should have unlocked new environment
        assert len(gs.unlocked_environments) == 2
        assert gs.current_environment.tier == 2

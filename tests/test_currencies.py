"""Tests for core currency systems."""

import pytest
from myrpg.currencies import PowerLevel, Pedometer, Gold
from myrpg.currencies.pedometer import SpeedUpgradeResult
from myrpg.currencies.gold import TransactionResult


class TestPowerLevel:
    def test_initial_value(self):
        pl = PowerLevel()
        assert pl.value == 1.0

    def test_add_increases_value(self):
        pl = PowerLevel()
        pl.add(10)
        assert pl.value == 11.0

    def test_cannot_add_negative(self):
        pl = PowerLevel()
        with pytest.raises(ValueError):
            pl.add(-5)

    def test_damage_multiplier(self):
        pl = PowerLevel()
        pl.add(99)  # Total 100
        assert pl.calculate_damage_multiplier() == 2.0  # 1 + 100/100

    def test_listener_called(self):
        pl = PowerLevel()
        changes = []
        pl.on_change(lambda old, new: changes.append((old, new)))
        pl.add(5)
        assert changes == [(1.0, 6.0)]


class TestPedometer:
    def test_initial_state(self):
        p = Pedometer()
        assert p.steps == 0
        assert p.speed_bonus_percent == 0.0

    def test_add_steps(self):
        p = Pedometer()
        p.add_steps(100)
        assert p.steps == 100
        assert p.total_steps_ever == 100

    def test_spend_resets_counter(self):
        p = Pedometer()
        p.add_steps(1000)
        result = p.spend()
        assert result == SpeedUpgradeResult.SUCCESS
        assert p.steps == 0
        assert p.speed_bonus_percent > 0

    def test_spend_insufficient_steps(self):
        p = Pedometer()
        p.add_steps(50)
        result = p.spend()
        assert result == SpeedUpgradeResult.INSUFFICIENT_STEPS
        assert p.steps == 50  # Not reset

    def test_speed_multiplier(self):
        p = Pedometer()
        assert p.get_speed_multiplier() == 1.0
        p.add_steps(10000)
        p.spend()
        assert p.get_speed_multiplier() > 1.0


class TestGold:
    def test_initial_amount(self):
        g = Gold()
        assert g.amount == 0

    def test_add_gold(self):
        g = Gold()
        g.add(100)
        assert g.amount == 100
        assert g.total_earned == 100

    def test_spend_success(self):
        g = Gold()
        g.add(100)
        result = g.spend(50)
        assert result == TransactionResult.SUCCESS
        assert g.amount == 50
        assert g.total_spent == 50

    def test_spend_insufficient_funds(self):
        g = Gold()
        g.add(50)
        result = g.spend(100)
        assert result == TransactionResult.INSUFFICIENT_FUNDS
        assert g.amount == 50  # Unchanged

    def test_can_afford(self):
        g = Gold()
        g.add(100)
        assert g.can_afford(100)
        assert g.can_afford(50)
        assert not g.can_afford(101)

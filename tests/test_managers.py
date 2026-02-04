"""Tests for manager automation system."""

import pytest
from myrpg.managers import ManagerRegistry
from myrpg.training.variables import VariableType


class TestManagerRegistry:
    def test_initial_state(self):
        r = ManagerRegistry()
        assert r.get_total_task_managers() == 0
        assert r.prestige_level == 0
        assert r.prestige_multiplier == 1.0

    def test_hire_task_manager(self):
        r = ManagerRegistry()
        manager = r.hire_task_manager(VariableType.STRENGTH)
        assert manager.name == "Mining Foreman"
        assert r.get_task_manager_count(VariableType.STRENGTH) == 1

    def test_cost_scaling(self):
        r = ManagerRegistry()
        assert r.get_next_task_manager_cost(VariableType.STRENGTH) == 1000
        r.hire_task_manager(VariableType.STRENGTH)
        assert r.get_next_task_manager_cost(VariableType.STRENGTH) == 2000
        r.hire_task_manager(VariableType.STRENGTH)
        assert r.get_next_task_manager_cost(VariableType.STRENGTH) == 4000

    def test_stack_efficiency(self):
        r = ManagerRegistry()
        assert r.calculate_stack_efficiency(0) == 0.0
        assert r.calculate_stack_efficiency(1) == 0.5
        assert r.calculate_stack_efficiency(2) == 0.75
        assert r.calculate_stack_efficiency(3) == 0.875

    def test_efficiency_calculation(self):
        r = ManagerRegistry()
        # No managers = 0 efficiency
        assert r.calculate_efficiency(VariableType.STRENGTH) == 0.0

        # One manager = 50%
        r.hire_task_manager(VariableType.STRENGTH)
        assert r.calculate_efficiency(VariableType.STRENGTH) == 0.5

    def test_department_manager_unlock(self):
        r = ManagerRegistry()
        assert not r.can_hire_physical_director()

        # Need 2 physical managers
        r.hire_task_manager(VariableType.STRENGTH)
        assert not r.can_hire_physical_director()

        r.hire_task_manager(VariableType.ENDURANCE)
        assert r.can_hire_physical_director()

    def test_department_bonus(self):
        r = ManagerRegistry()
        r.hire_task_manager(VariableType.STRENGTH)
        base_eff = r.calculate_efficiency(VariableType.STRENGTH)

        r.hire_task_manager(VariableType.ENDURANCE)
        r.hire_physical_director()

        # Should have 25% bonus now
        new_eff = r.calculate_efficiency(VariableType.STRENGTH)
        assert new_eff == min(base_eff * 1.25, 1.0)

    def test_vp_unlock_requires_both_directors(self):
        r = ManagerRegistry()
        assert not r.can_hire_vp()

        # Hire physical requirements
        r.hire_task_manager(VariableType.STRENGTH)
        r.hire_task_manager(VariableType.ENDURANCE)
        r.hire_physical_director()
        assert not r.can_hire_vp()

        # Hire mental requirements
        r.hire_task_manager(VariableType.DEXTERITY)
        r.hire_task_manager(VariableType.FOCUS)
        r.hire_mental_director()
        assert r.can_hire_vp()

    def test_prestige_resets_managers(self):
        r = ManagerRegistry()
        r.hire_task_manager(VariableType.STRENGTH)
        r.hire_task_manager(VariableType.ENDURANCE)
        r.hire_physical_director()
        r.hire_task_manager(VariableType.DEXTERITY)
        r.hire_task_manager(VariableType.FOCUS)
        r.hire_mental_director()
        r.hire_vp()
        r.hire_ceo()

        # Prestige
        new_level = r.prestige()
        assert new_level == 1
        assert r.get_total_task_managers() == 0
        assert not r.has_physical_director
        assert not r.has_ceo
        assert r.prestige_multiplier == 1.1

    def test_efficiency_cap(self):
        r = ManagerRegistry()
        # Hire many managers to try to exceed cap
        for _ in range(10):
            r.hire_task_manager(VariableType.STRENGTH)

        efficiency = r.calculate_efficiency(VariableType.STRENGTH)
        assert efficiency <= 1.0

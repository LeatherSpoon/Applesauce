"""Tests for combat theme and mastery systems."""

import pytest
from myrpg.combat import ThemeType, ThemeMastery, Unarmed, Armed, Ranged, Energy, get_theme
from myrpg.training import ControllingVariables


class TestThemeType:
    def test_sequence(self):
        assert ThemeType.UNARMED.next() == ThemeType.ARMED
        assert ThemeType.ARMED.next() == ThemeType.RANGED
        assert ThemeType.RANGED.next() == ThemeType.ENERGY
        assert ThemeType.ENERGY.next() == ThemeType.UNARMED  # Cycles back


class TestCombatThemes:
    def test_unarmed_defaults(self):
        theme = Unarmed()
        assert theme.theme_type == ThemeType.UNARMED
        assert theme.unlock_requirement == 0
        assert theme.base_attack_speed == 2.0
        assert theme.base_range == 1

    def test_armed_unlock_requirement(self):
        theme = Armed()
        assert theme.unlock_requirement == 10

    def test_ranged_has_long_range(self):
        theme = Ranged()
        assert theme.base_range == 6

    def test_energy_special_is_energy_pool(self):
        theme = Energy()
        vars = ControllingVariables()
        # Base energy should be 100 + focus*5
        special = theme.calculate_special(vars)
        assert special == 100 + vars.focus.value * 5

    def test_get_theme_factory(self):
        theme = get_theme(ThemeType.ARMED)
        assert isinstance(theme, Armed)


class TestThemeMastery:
    def test_initial_levels(self):
        m = ThemeMastery()
        for theme in ThemeType:
            assert m.get_level(theme) == 0

    def test_unarmed_always_unlocked(self):
        m = ThemeMastery()
        assert m.is_theme_unlocked(ThemeType.UNARMED)

    def test_armed_initially_locked(self):
        m = ThemeMastery()
        assert not m.is_theme_unlocked(ThemeType.ARMED)

    def test_armed_unlocked_at_unarmed_10(self):
        m = ThemeMastery()
        # Need enough XP for level 10
        # Level 10 requires 100 * 10^1.5 = 3162 XP
        m.add_xp(ThemeType.UNARMED, 3200)
        assert m.get_level(ThemeType.UNARMED) >= 10
        assert m.is_theme_unlocked(ThemeType.ARMED)

    def test_add_xp_returns_milestones(self):
        m = ThemeMastery()
        milestones = m.add_xp(ThemeType.UNARMED, 5000)
        assert len(milestones) > 0
        assert milestones[0].theme == ThemeType.UNARMED

    def test_versatility_bonus(self):
        m = ThemeMastery()
        assert m.calculate_versatility_bonus() == 0.0

        # Get two themes to level 50
        # Level 50 requires ~35000 XP
        m.add_xp(ThemeType.UNARMED, 40000)
        m.add_xp(ThemeType.ARMED, 40000)

        assert m.count_themes_at_level(50) >= 2
        assert m.calculate_versatility_bonus() >= 0.05

    def test_xp_progress(self):
        m = ThemeMastery()
        m.add_xp(ThemeType.UNARMED, 50)  # Not enough for level 1
        progress = m.get_xp_progress(ThemeType.UNARMED)
        assert 0 < progress < 100

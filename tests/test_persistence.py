"""Tests for save/load functionality."""

import pytest
import tempfile
from pathlib import Path

from myrpg.persistence import GameSerializer, SaveManager
from myrpg.currencies import PowerLevel, Pedometer, Gold
from myrpg.training import ControllingVariables
from myrpg.combat import ThemeType, ThemeMastery
from myrpg.managers import ManagerRegistry
from myrpg.items import Inventory, EquipmentLoadout, create_weapon, WeaponClass, ItemRarity
from myrpg.movement import TileManager, TileType


class TestGameSerializer:
    def test_serialize_power_level(self):
        pl = PowerLevel()
        pl.add(100)
        data = GameSerializer.serialize_power_level(pl)
        assert data["value"] == 101.0

        restored = GameSerializer.deserialize_power_level(data)
        assert restored.value == pl.value

    def test_serialize_pedometer(self):
        p = Pedometer()
        p.add_steps(5000)
        data = GameSerializer.serialize_pedometer(p)
        assert data["steps"] == 5000
        assert data["total_steps_ever"] == 5000

        restored = GameSerializer.deserialize_pedometer(data)
        assert restored.steps == p.steps
        assert restored.total_steps_ever == p.total_steps_ever

    def test_serialize_gold(self):
        g = Gold()
        g.add(1000)
        g.spend(300)
        data = GameSerializer.serialize_gold(g)
        assert data["amount"] == 700

        restored = GameSerializer.deserialize_gold(data)
        assert restored.amount == g.amount
        assert restored.total_earned == g.total_earned

    def test_serialize_variables(self):
        v = ControllingVariables()
        v.strength.add(50)
        v.dexterity.add(30)
        data = GameSerializer.serialize_variables(v)

        restored = GameSerializer.deserialize_variables(data)
        assert restored.strength.value == v.strength.value
        assert restored.dexterity.value == v.dexterity.value

    def test_serialize_mastery(self):
        m = ThemeMastery()
        m.add_xp(ThemeType.UNARMED, 5000)
        m.add_xp(ThemeType.ARMED, 1000)
        data = GameSerializer.serialize_mastery(m)

        restored = GameSerializer.deserialize_mastery(data)
        assert restored.get_level(ThemeType.UNARMED) == m.get_level(ThemeType.UNARMED)
        assert restored.get_xp(ThemeType.ARMED) == m.get_xp(ThemeType.ARMED)

    def test_serialize_managers(self):
        mr = ManagerRegistry()
        from myrpg.training import VariableType
        mr.hire_task_manager(VariableType.STRENGTH)
        mr.hire_task_manager(VariableType.STRENGTH)
        mr.hire_task_manager(VariableType.ENDURANCE)

        data = GameSerializer.serialize_managers(mr)
        assert data["task_counts"]["strength"] == 2

        restored = GameSerializer.deserialize_managers(data)
        assert restored.get_task_manager_count(VariableType.STRENGTH) == 2
        assert restored.get_task_manager_count(VariableType.ENDURANCE) == 1

    def test_serialize_inventory(self):
        inv = Inventory()
        sword = create_weapon(WeaponClass.SWORD, tier=2, rarity=ItemRarity.RARE)
        inv.add(sword)

        data = GameSerializer.serialize_inventory(inv)
        assert len(data["items"]) == 1

        restored = GameSerializer.deserialize_inventory(data)
        assert restored.count == 1
        assert restored.items[0].rarity == ItemRarity.RARE

    def test_serialize_tiles(self):
        tm = TileManager()
        tm.place_tile(TileType.DIRT_PATH, 1, (0, 0))
        tm.place_tile(TileType.COBBLESTONE, 1, (1, 0))

        data = GameSerializer.serialize_tiles(tm)
        assert "1" in data
        assert len(data["1"]) == 2

        restored = GameSerializer.deserialize_tiles(data)
        assert restored.get_tile_count(TileType.DIRT_PATH) == 1
        assert restored.get_tile_count(TileType.COBBLESTONE) == 1


class TestSaveManager:
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sm = SaveManager(Path(tmpdir))

            # Create a mock game state with required attributes
            class MockGameState:
                def __init__(self):
                    self.power_level = PowerLevel()
                    self.power_level.add(500)
                    self.pedometer = Pedometer()
                    self.pedometer.add_steps(10000)
                    self.gold = Gold()
                    self.gold.add(5000)
                    self.variables = ControllingVariables()
                    self.mastery = ThemeMastery()
                    self.current_theme = ThemeType.ARMED
                    self.managers = ManagerRegistry()
                    self._current_environment_index = 1
                    self.unlocked_environments = [None, None]  # 2 environments

            gs = MockGameState()
            assert sm.save_game(gs, slot=0)
            assert sm.save_exists(0)

            data = sm.load_game(0)
            assert data is not None
            assert data["power_level"].value == gs.power_level.value
            assert data["current_theme"] == ThemeType.ARMED

    def test_list_saves(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sm = SaveManager(Path(tmpdir))

            class MockGameState:
                def __init__(self):
                    self.power_level = PowerLevel()
                    self.pedometer = Pedometer()
                    self.gold = Gold()
                    self.variables = ControllingVariables()
                    self.mastery = ThemeMastery()
                    self.current_theme = ThemeType.UNARMED
                    self.managers = ManagerRegistry()
                    self._current_environment_index = 0
                    self.unlocked_environments = [None]

            gs = MockGameState()
            sm.save_game(gs, slot=0)
            sm.save_game(gs, slot=1)

            saves = sm.list_saves()
            assert len(saves) == 2

    def test_delete_save(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sm = SaveManager(Path(tmpdir))

            class MockGameState:
                def __init__(self):
                    self.power_level = PowerLevel()
                    self.pedometer = Pedometer()
                    self.gold = Gold()
                    self.variables = ControllingVariables()
                    self.mastery = ThemeMastery()
                    self.current_theme = ThemeType.UNARMED
                    self.managers = ManagerRegistry()
                    self._current_environment_index = 0
                    self.unlocked_environments = [None]

            gs = MockGameState()
            sm.save_game(gs, slot=0)
            assert sm.save_exists(0)

            sm.delete_save(0)
            assert not sm.save_exists(0)

    def test_load_nonexistent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sm = SaveManager(Path(tmpdir))
            assert sm.load_game(99) is None

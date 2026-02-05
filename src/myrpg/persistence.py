"""Save/load functionality for MyRPG."""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any
from datetime import datetime

from .currencies import PowerLevel, Pedometer, Gold
from .training import ControllingVariables, VariableType
from .combat import ThemeType, ThemeMastery
from .managers import ManagerRegistry
from .items import (
    Inventory, EquipmentLoadout, ItemRarity, EquipmentSlot,
    Weapon, WeaponClass, Armor, ArmorWeight, Material,
    create_weapon, create_armor,
)
from .movement import TileType, TileManager


class GameSerializer:
    """Handles serialization and deserialization of game state."""

    VERSION = "1.0.0"

    @classmethod
    def serialize_power_level(cls, pl: PowerLevel) -> dict:
        return {
            "value": pl.value,
        }

    @classmethod
    def deserialize_power_level(cls, data: dict) -> PowerLevel:
        pl = PowerLevel()
        pl._value = data["value"]
        return pl

    @classmethod
    def serialize_pedometer(cls, p: Pedometer) -> dict:
        return {
            "steps": p.steps,
            "total_steps_ever": p._total_steps_ever,
            "times_spent": p._times_spent,
            "speed_bonus_percent": p._speed_bonus_percent,
        }

    @classmethod
    def deserialize_pedometer(cls, data: dict) -> Pedometer:
        p = Pedometer()
        p._steps = data["steps"]
        p._total_steps_ever = data.get("total_steps_ever", data["steps"])
        p._times_spent = data.get("times_spent", 0)
        p._speed_bonus_percent = data.get("speed_bonus_percent", 0.0)
        return p

    @classmethod
    def serialize_gold(cls, g: Gold) -> dict:
        return {
            "amount": g.amount,
            "total_earned": g.total_earned,
            "total_spent": g.total_spent,
        }

    @classmethod
    def deserialize_gold(cls, data: dict) -> Gold:
        g = Gold()
        g._amount = data["amount"]
        g._total_earned = data["total_earned"]
        g._total_spent = data["total_spent"]
        return g

    @classmethod
    def serialize_variables(cls, v: ControllingVariables) -> dict:
        return {
            "strength": v.strength.value,
            "dexterity": v.dexterity.value,
            "focus": v.focus.value,
            "endurance": v.endurance.value,
        }

    @classmethod
    def deserialize_variables(cls, data: dict) -> ControllingVariables:
        v = ControllingVariables()
        v.strength._value = data["strength"]
        v.dexterity._value = data["dexterity"]
        v.focus._value = data["focus"]
        v.endurance._value = data["endurance"]
        return v

    @classmethod
    def serialize_mastery(cls, m: ThemeMastery) -> dict:
        return {
            "levels": {t.value: m.get_level(t) for t in ThemeType},
            "xp": {t.value: m.get_xp(t) for t in ThemeType},
        }

    @classmethod
    def deserialize_mastery(cls, data: dict) -> ThemeMastery:
        m = ThemeMastery()
        for theme in ThemeType:
            m._levels[theme] = data["levels"].get(theme.value, 0)
            m._xp[theme] = data["xp"].get(theme.value, 0.0)
        return m

    @classmethod
    def serialize_managers(cls, mr: ManagerRegistry) -> dict:
        return {
            "task_counts": {v.value: mr.get_task_manager_count(v) for v in VariableType},
            "has_physical_director": mr.has_physical_director,
            "has_mental_director": mr.has_mental_director,
            "has_vp": mr.has_vp,
            "has_ceo": mr.has_ceo,
            "prestige_level": mr.prestige_level,
        }

    @classmethod
    def deserialize_managers(cls, data: dict) -> ManagerRegistry:
        mr = ManagerRegistry()
        mr._prestige_level = data.get("prestige_level", 0)

        # Rebuild task managers
        for var_type in VariableType:
            count = data["task_counts"].get(var_type.value, 0)
            for _ in range(count):
                mr.hire_task_manager(var_type)

        # Rebuild higher tier managers
        if data.get("has_physical_director"):
            mr._physical_director = mr.hire_physical_director() if mr.can_hire_physical_director() else None
        if data.get("has_mental_director"):
            mr._mental_director = mr.hire_mental_director() if mr.can_hire_mental_director() else None
        if data.get("has_vp"):
            mr._vp_of_training = mr.hire_vp() if mr.can_hire_vp() else None
        if data.get("has_ceo"):
            mr._ceo = mr.hire_ceo() if mr.can_hire_ceo() else None

        return mr

    @classmethod
    def serialize_inventory(cls, inv: Inventory) -> dict:
        items = []
        for item in inv.items:
            item_data = {
                "type": type(item).__name__,
                "name": item.name,
                "description": item.description,
                "rarity": item.rarity.value,
                "base_sell_value": item.base_sell_value,
                "tier": item.tier,
            }
            if isinstance(item, Weapon):
                item_data["weapon_class"] = item.weapon_class.value
                item_data["base_damage"] = item.base_damage
            elif isinstance(item, Armor):
                item_data["slot"] = item.slot.value
                item_data["armor_weight"] = item.armor_weight.value
                item_data["base_defense"] = item.base_defense
            items.append(item_data)

        return {
            "items": items,
            "capacity": inv.capacity,
        }

    @classmethod
    def deserialize_inventory(cls, data: dict) -> Inventory:
        inv = Inventory()
        inv._capacity = data.get("capacity", 50)

        for item_data in data.get("items", []):
            item = cls._recreate_item(item_data)
            if item:
                inv.add(item)

        return inv

    @classmethod
    def _recreate_item(cls, data: dict):
        """Recreate an item from serialized data."""
        item_type = data.get("type")
        rarity = ItemRarity(data["rarity"])
        tier = data.get("tier", 1)

        if item_type == "Weapon":
            weapon_class = WeaponClass(data["weapon_class"])
            return create_weapon(weapon_class, tier, rarity)
        elif item_type == "Armor":
            slot = EquipmentSlot(data["slot"])
            weight = ArmorWeight(data["armor_weight"])
            return create_armor(slot, weight, tier, rarity)
        elif item_type == "Material":
            return Material(
                name=data["name"],
                description=data["description"],
                rarity=rarity,
                base_sell_value=data["base_sell_value"],
                tier=tier,
            )
        return None

    @classmethod
    def serialize_equipment(cls, eq: EquipmentLoadout) -> dict:
        slots = {}
        for slot in EquipmentSlot:
            item = eq.get(slot)
            if item:
                slots[slot.value] = {
                    "type": type(item).__name__,
                    "name": item.name,
                    "description": item.description,
                    "rarity": item.rarity.value,
                    "tier": item.tier,
                    "base_sell_value": item.base_sell_value,
                }
                if isinstance(item, Weapon):
                    slots[slot.value]["weapon_class"] = item.weapon_class.value
                    slots[slot.value]["base_damage"] = item.base_damage
                elif isinstance(item, Armor):
                    slots[slot.value]["slot"] = item.slot.value
                    slots[slot.value]["armor_weight"] = item.armor_weight.value
                    slots[slot.value]["base_defense"] = item.base_defense
        return slots

    @classmethod
    def deserialize_equipment(cls, data: dict) -> EquipmentLoadout:
        eq = EquipmentLoadout()
        for slot_name, item_data in data.items():
            slot = EquipmentSlot(slot_name)
            item = cls._recreate_item(item_data)
            if item:
                eq._slots[slot] = item
        return eq

    @classmethod
    def serialize_tiles(cls, tm: TileManager) -> dict:
        tiles_data = {}
        for env_id, tiles in tm._tiles.items():
            tiles_data[str(env_id)] = [
                {
                    "type": tile.tile_type.value,
                    "position": list(tile.position),
                }
                for tile in tiles
            ]
        return tiles_data

    @classmethod
    def deserialize_tiles(cls, data: dict) -> TileManager:
        tm = TileManager()
        for env_id_str, tiles in data.items():
            env_id = int(env_id_str)
            for tile_data in tiles:
                tile_type = TileType(tile_data["type"])
                position = tuple(tile_data["position"])
                tm.place_tile(tile_type, env_id, position)
        return tm


class SaveManager:
    """Manages game save files."""

    DEFAULT_SAVE_DIR = Path.home() / ".myrpg" / "saves"

    def __init__(self, save_dir: Path | None = None):
        self.save_dir = save_dir or self.DEFAULT_SAVE_DIR
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def get_save_path(self, slot: int = 0) -> Path:
        """Get path for a save slot."""
        return self.save_dir / f"save_{slot}.json"

    def save_exists(self, slot: int = 0) -> bool:
        """Check if a save exists in a slot."""
        return self.get_save_path(slot).exists()

    def list_saves(self) -> list[dict]:
        """List all available saves with metadata."""
        saves = []
        for save_file in self.save_dir.glob("save_*.json"):
            try:
                with open(save_file) as f:
                    data = json.load(f)
                    saves.append({
                        "slot": int(save_file.stem.split("_")[1]),
                        "timestamp": data.get("timestamp"),
                        "play_time": data.get("play_time", 0),
                        "power_level": data.get("power_level", {}).get("value", 1),
                    })
            except (json.JSONDecodeError, KeyError, IndexError):
                continue
        return sorted(saves, key=lambda x: x["slot"])

    def save_game(self, game_state, slot: int = 0) -> bool:
        """
        Save game state to a slot.

        Args:
            game_state: The GameState object to save
            slot: Save slot number

        Returns:
            True if saved successfully
        """
        try:
            data = {
                "version": GameSerializer.VERSION,
                "timestamp": datetime.now().isoformat(),
                "power_level": GameSerializer.serialize_power_level(game_state.power_level),
                "pedometer": GameSerializer.serialize_pedometer(game_state.pedometer),
                "gold": GameSerializer.serialize_gold(game_state.gold),
                "variables": GameSerializer.serialize_variables(game_state.variables),
                "mastery": GameSerializer.serialize_mastery(game_state.mastery),
                "current_theme": game_state.current_theme.value,
                "managers": GameSerializer.serialize_managers(game_state.managers),
                "current_environment_index": game_state._current_environment_index,
                "environments_unlocked": len(game_state.unlocked_environments),
            }

            # Add inventory if present
            if hasattr(game_state, 'inventory'):
                data["inventory"] = GameSerializer.serialize_inventory(game_state.inventory)
            if hasattr(game_state, 'equipment'):
                data["equipment"] = GameSerializer.serialize_equipment(game_state.equipment)
            if hasattr(game_state, 'tiles'):
                data["tiles"] = GameSerializer.serialize_tiles(game_state.tiles)

            save_path = self.get_save_path(slot)
            with open(save_path, 'w') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f"Save failed: {e}")
            return False

    def load_game(self, slot: int = 0) -> dict | None:
        """
        Load game data from a slot.

        Returns:
            Dictionary with deserialized game components, or None if failed
        """
        save_path = self.get_save_path(slot)
        if not save_path.exists():
            return None

        try:
            with open(save_path) as f:
                data = json.load(f)

            # Verify version compatibility
            version = data.get("version", "0.0.0")
            if version.split(".")[0] != GameSerializer.VERSION.split(".")[0]:
                print(f"Warning: Save version {version} may not be compatible")

            return {
                "power_level": GameSerializer.deserialize_power_level(data["power_level"]),
                "pedometer": GameSerializer.deserialize_pedometer(data["pedometer"]),
                "gold": GameSerializer.deserialize_gold(data["gold"]),
                "variables": GameSerializer.deserialize_variables(data["variables"]),
                "mastery": GameSerializer.deserialize_mastery(data["mastery"]),
                "current_theme": ThemeType(data["current_theme"]),
                "managers": GameSerializer.deserialize_managers(data["managers"]),
                "current_environment_index": data.get("current_environment_index", 0),
                "environments_unlocked": data.get("environments_unlocked", 1),
                "inventory": GameSerializer.deserialize_inventory(data.get("inventory", {})),
                "equipment": GameSerializer.deserialize_equipment(data.get("equipment", {})),
                "tiles": GameSerializer.deserialize_tiles(data.get("tiles", {})),
                "timestamp": data.get("timestamp"),
            }
        except Exception as e:
            print(f"Load failed: {e}")
            return None

    def delete_save(self, slot: int = 0) -> bool:
        """Delete a save file."""
        save_path = self.get_save_path(slot)
        if save_path.exists():
            save_path.unlink()
            return True
        return False

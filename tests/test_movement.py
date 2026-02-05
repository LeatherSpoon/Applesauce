"""Tests for the movement and speed tiles system."""

import pytest
from myrpg.movement import TileType, TileManager, TILE_DEFINITIONS


class TestTileDefinitions:
    def test_all_tiles_defined(self):
        for tile_type in TileType:
            assert tile_type in TILE_DEFINITIONS

    def test_tile_costs_increase(self):
        costs = [TILE_DEFINITIONS[t].cost for t in [
            TileType.DIRT_PATH,
            TileType.COBBLESTONE,
            TileType.PAVED_ROAD,
            TileType.SPEED_RAIL,
        ]]
        assert costs == sorted(costs)

    def test_tile_bonuses_increase(self):
        bonuses = [TILE_DEFINITIONS[t].speed_bonus for t in [
            TileType.DIRT_PATH,
            TileType.COBBLESTONE,
            TileType.PAVED_ROAD,
            TileType.SPEED_RAIL,
        ]]
        assert bonuses == sorted(bonuses)


class TestTileManager:
    def test_place_tile(self):
        tm = TileManager()
        tile = tm.place_tile(TileType.DIRT_PATH, env_id=1, position=(0, 0))
        assert tile.tile_type == TileType.DIRT_PATH
        assert tm.get_tile_count(TileType.DIRT_PATH) == 1

    def test_get_tiles_for_environment(self):
        tm = TileManager()
        tm.place_tile(TileType.DIRT_PATH, env_id=1, position=(0, 0))
        tm.place_tile(TileType.COBBLESTONE, env_id=1, position=(1, 0))
        tm.place_tile(TileType.DIRT_PATH, env_id=2, position=(0, 0))

        env1_tiles = tm.get_tiles_for_environment(1)
        assert len(env1_tiles) == 2

        env2_tiles = tm.get_tiles_for_environment(2)
        assert len(env2_tiles) == 1

    def test_remove_tile(self):
        tm = TileManager()
        tile = tm.place_tile(TileType.DIRT_PATH, env_id=1, position=(0, 0))
        assert tm.remove_tile(tile)
        assert tm.get_tile_count(TileType.DIRT_PATH) == 0

    def test_speed_at_position(self):
        tm = TileManager()
        tm.place_tile(TileType.PAVED_ROAD, env_id=1, position=(0, 0))

        # On tile
        assert tm.get_speed_at_position(1, 0, 0) == 1.5  # +50%

        # Off tile
        assert tm.get_speed_at_position(1, 5, 5) == 1.0

    def test_speed_rail_covers_multiple_positions(self):
        tm = TileManager()
        tm.place_tile(TileType.SPEED_RAIL, env_id=1, position=(0, 0))

        # Speed rail is 3x1
        assert tm.get_speed_at_position(1, 0, 0) == 2.0
        assert tm.get_speed_at_position(1, 1, 0) == 2.0
        assert tm.get_speed_at_position(1, 2, 0) == 2.0
        assert tm.get_speed_at_position(1, 3, 0) == 1.0

    def test_link_teleport_pads(self):
        tm = TileManager()
        pad1 = tm.place_tile(TileType.TELEPORT_PAD, env_id=1, position=(0, 0))
        pad2 = tm.place_tile(TileType.TELEPORT_PAD, env_id=1, position=(10, 10))

        assert tm.link_teleport_pads(pad1, pad2)
        assert pad1.linked_to == pad2
        assert pad2.linked_to == pad1

    def test_route_bonus_calculation(self):
        tm = TileManager()
        # No tiles = no bonus
        assert tm.calculate_route_bonus(1) == 1.0

        # Add some tiles
        tm.place_tile(TileType.PAVED_ROAD, env_id=1, position=(0, 0))
        bonus = tm.calculate_route_bonus(1, path_length=10)
        assert bonus > 1.0

    def test_total_tiles(self):
        tm = TileManager()
        tm.place_tile(TileType.DIRT_PATH, env_id=1, position=(0, 0))
        tm.place_tile(TileType.COBBLESTONE, env_id=1, position=(1, 0))
        tm.place_tile(TileType.DIRT_PATH, env_id=2, position=(0, 0))

        assert tm.get_total_tiles() == 3

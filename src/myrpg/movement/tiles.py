"""Speed tiles system for movement optimization."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class TileType(Enum):
    """Types of speed tiles with different bonuses."""
    DIRT_PATH = "dirt_path"
    COBBLESTONE = "cobblestone"
    PAVED_ROAD = "paved_road"
    SPEED_RAIL = "speed_rail"
    TELEPORT_PAD = "teleport_pad"


@dataclass
class TileDefinition:
    """Definition of a tile type's properties."""
    tile_type: TileType
    name: str
    description: str
    speed_bonus: float  # Percentage bonus (0.1 = +10%)
    cost: int  # Gold cost
    size: tuple[int, int]  # Width, Height
    is_teleporter: bool = False

    @property
    def speed_multiplier(self) -> float:
        """Get speed multiplier (1.0 = normal, 1.5 = +50%)."""
        return 1.0 + self.speed_bonus


TILE_DEFINITIONS = {
    TileType.DIRT_PATH: TileDefinition(
        tile_type=TileType.DIRT_PATH,
        name="Dirt Path",
        description="A simple dirt path that slightly improves movement",
        speed_bonus=0.10,
        cost=100,
        size=(1, 1),
    ),
    TileType.COBBLESTONE: TileDefinition(
        tile_type=TileType.COBBLESTONE,
        name="Cobblestone Road",
        description="A sturdy cobblestone road for better travel",
        speed_bonus=0.25,
        cost=500,
        size=(1, 1),
    ),
    TileType.PAVED_ROAD: TileDefinition(
        tile_type=TileType.PAVED_ROAD,
        name="Paved Road",
        description="A smooth paved road for fast travel",
        speed_bonus=0.50,
        cost=2500,
        size=(1, 1),
    ),
    TileType.SPEED_RAIL: TileDefinition(
        tile_type=TileType.SPEED_RAIL,
        name="Speed Rail",
        description="A magical rail that propels travelers at high speed",
        speed_bonus=1.00,
        cost=10000,
        size=(3, 1),
    ),
    TileType.TELEPORT_PAD: TileDefinition(
        tile_type=TileType.TELEPORT_PAD,
        name="Teleport Pad",
        description="Instantly teleport to a linked pad",
        speed_bonus=0.0,
        cost=50000,
        size=(1, 1),
        is_teleporter=True,
    ),
}


@dataclass
class PlacedTile:
    """A tile placed in an environment."""
    tile_def: TileDefinition
    environment_id: int
    position: tuple[int, int]
    linked_to: "PlacedTile | None" = None  # For teleport pads

    @property
    def tile_type(self) -> TileType:
        return self.tile_def.tile_type

    @property
    def speed_bonus(self) -> float:
        return self.tile_def.speed_bonus

    def covers_position(self, x: int, y: int) -> bool:
        """Check if this tile covers a given position."""
        tx, ty = self.position
        width, height = self.tile_def.size
        return tx <= x < tx + width and ty <= y < ty + height


@dataclass
class TileManager:
    """Manages placed tiles across all environments."""
    _tiles: dict[int, list[PlacedTile]] = field(default_factory=dict)
    _tile_counts: dict[TileType, int] = field(default_factory=lambda: {t: 0 for t in TileType})
    _listeners: list[Callable[[PlacedTile, bool], None]] = field(
        default_factory=list, repr=False
    )

    def get_tiles_for_environment(self, env_id: int) -> list[PlacedTile]:
        """Get all tiles placed in an environment."""
        return self._tiles.get(env_id, [])

    def get_tile_count(self, tile_type: TileType) -> int:
        """Get total count of a tile type across all environments."""
        return self._tile_counts[tile_type]

    def get_total_tiles(self) -> int:
        """Get total number of placed tiles."""
        return sum(self._tile_counts.values())

    def place_tile(
        self,
        tile_type: TileType,
        env_id: int,
        position: tuple[int, int],
    ) -> PlacedTile:
        """
        Place a tile in an environment.

        Args:
            tile_type: Type of tile to place
            env_id: Environment ID to place in
            position: (x, y) position

        Returns:
            The placed tile
        """
        tile_def = TILE_DEFINITIONS[tile_type]
        tile = PlacedTile(
            tile_def=tile_def,
            environment_id=env_id,
            position=position,
        )

        if env_id not in self._tiles:
            self._tiles[env_id] = []

        self._tiles[env_id].append(tile)
        self._tile_counts[tile_type] += 1
        self._notify_listeners(tile, True)

        return tile

    def remove_tile(self, tile: PlacedTile) -> bool:
        """
        Remove a placed tile.

        Returns:
            True if removed, False if not found
        """
        env_tiles = self._tiles.get(tile.environment_id, [])
        if tile in env_tiles:
            env_tiles.remove(tile)
            self._tile_counts[tile.tile_type] -= 1
            self._notify_listeners(tile, False)
            return True
        return False

    def link_teleport_pads(self, pad1: PlacedTile, pad2: PlacedTile) -> bool:
        """
        Link two teleport pads for bidirectional teleportation.

        Returns:
            True if linked successfully
        """
        if (pad1.tile_type != TileType.TELEPORT_PAD or
            pad2.tile_type != TileType.TELEPORT_PAD):
            return False

        pad1.linked_to = pad2
        pad2.linked_to = pad1
        return True

    def calculate_route_bonus(self, env_id: int, path_length: int = 10) -> float:
        """
        Calculate average speed bonus for traveling through an environment.

        This is a simplified calculation assuming uniform tile distribution.
        A more complex implementation would trace actual paths.

        Args:
            env_id: Environment to calculate for
            path_length: Assumed path length in tiles

        Returns:
            Average speed multiplier for the route
        """
        tiles = self.get_tiles_for_environment(env_id)
        if not tiles:
            return 1.0

        # Calculate coverage-weighted bonus
        total_coverage = 0
        weighted_bonus = 0.0

        for tile in tiles:
            width, height = tile.tile_def.size
            coverage = width * height
            total_coverage += coverage
            weighted_bonus += tile.speed_bonus * coverage

        # Assume tiles cover portion of standard path
        coverage_ratio = min(total_coverage / path_length, 1.0)
        if total_coverage > 0:
            avg_bonus = weighted_bonus / total_coverage
        else:
            avg_bonus = 0.0

        # Weighted average: covered portion gets bonus, rest is normal
        return 1.0 + (avg_bonus * coverage_ratio)

    def get_speed_at_position(self, env_id: int, x: int, y: int) -> float:
        """
        Get speed multiplier at a specific position.

        Returns the highest bonus if multiple tiles overlap.
        """
        tiles = self.get_tiles_for_environment(env_id)
        best_multiplier = 1.0

        for tile in tiles:
            if tile.covers_position(x, y):
                multiplier = tile.tile_def.speed_multiplier
                if multiplier > best_multiplier:
                    best_multiplier = multiplier

        return best_multiplier

    def get_cost(self, tile_type: TileType) -> int:
        """Get the gold cost to place a tile."""
        return TILE_DEFINITIONS[tile_type].cost

    def get_available_tiles(self) -> list[TileDefinition]:
        """Get list of all available tile types."""
        return list(TILE_DEFINITIONS.values())

    def on_change(self, callback: Callable[[PlacedTile, bool], None]) -> None:
        """Register listener for tile changes (tile, placed)."""
        self._listeners.append(callback)

    def _notify_listeners(self, tile: PlacedTile, placed: bool) -> None:
        for listener in self._listeners:
            listener(tile, placed)

    def get_summary(self) -> str:
        """Get summary of all placed tiles."""
        lines = ["Speed Tiles:"]
        for tile_type in TileType:
            count = self._tile_counts[tile_type]
            if count > 0:
                tile_def = TILE_DEFINITIONS[tile_type]
                lines.append(f"  {tile_def.name}: {count} (+{tile_def.speed_bonus * 100:.0f}% each)")

        total = self.get_total_tiles()
        lines.append(f"  Total: {total} tiles")
        return "\n".join(lines)

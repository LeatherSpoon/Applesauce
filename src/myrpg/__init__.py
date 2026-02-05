"""MyRPG - A loop-driven RPG with combat themes and pedometer progression."""

__version__ = "0.1.0"

from .game_state import GameState, GameEvent
from .persistence import SaveManager, GameSerializer

__all__ = [
    "GameState",
    "GameEvent",
    "SaveManager",
    "GameSerializer",
    "__version__",
]

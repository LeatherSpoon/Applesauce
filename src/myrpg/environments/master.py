"""Master - NPC trainers that teach combat themes."""

from dataclasses import dataclass
from ..combat.themes import ThemeType


@dataclass
class Master:
    """
    A Master NPC that trains the player in a specific combat theme.

    Each environment has one Master who teaches a specific theme.
    """

    name: str
    theme: ThemeType
    description: str
    environment_tier: int

    def get_training_bonus(self) -> float:
        """Get the training speed bonus from this Master."""
        # Higher tier masters give better training bonuses
        return 1.0 + (self.environment_tier * 0.1)

    def __str__(self) -> str:
        return f"Master {self.name} ({self.theme.name})"


# Predefined masters for the game
MASTERS = [
    Master(
        name="Chen",
        theme=ThemeType.UNARMED,
        description="A flowing martial artist from the Forest Dojo",
        environment_tier=1,
    ),
    Master(
        name="Sir Aldric",
        theme=ThemeType.ARMED,
        description="A noble knight from the Iron Fortress",
        environment_tier=2,
    ),
    Master(
        name="Hawk Eye",
        theme=ThemeType.RANGED,
        description="A precision archer from Wind Valley",
        environment_tier=3,
    ),
    Master(
        name="Archmage Vera",
        theme=ThemeType.ENERGY,
        description="A mystical sorcerer from the Crystal Spire",
        environment_tier=4,
    ),
    Master(
        name="Grandmaster Kai",
        theme=ThemeType.UNARMED,
        description="A desert monk from the Sand Temple",
        environment_tier=5,
    ),
    Master(
        name="Blade Dancer Yuki",
        theme=ThemeType.ARMED,
        description="A sword master from the Frozen Peaks",
        environment_tier=6,
    ),
    Master(
        name="Shadow Hunter Rex",
        theme=ThemeType.RANGED,
        description="A legendary marksman from the Dark Forest",
        environment_tier=7,
    ),
    Master(
        name="Void Walker Zara",
        theme=ThemeType.ENERGY,
        description="An otherworldly mage from the Astral Plane",
        environment_tier=8,
    ),
]


def get_master_for_tier(tier: int) -> Master:
    """Get the master for a specific environment tier."""
    index = (tier - 1) % len(MASTERS)
    master = MASTERS[index]
    # Create a copy with the correct tier
    return Master(
        name=master.name,
        theme=master.theme,
        description=master.description,
        environment_tier=tier,
    )

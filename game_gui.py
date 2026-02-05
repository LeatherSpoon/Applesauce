#!/usr/bin/env python3
"""
MyRPG - Visual Demo with Pygame
A 2D grid-based RPG demo

Controls:
  Arrow Keys / WASD - Move
  Space - Attack (farm mob)
  E - Interact
  P - Spend pedometer steps
  ESC - Quit
"""

import sys

try:
    import pygame
except ImportError:
    print("Pygame not installed. Install it with:")
    print("  pip install pygame")
    print("\nOr on your system:")
    print('  C:/Users/pd101sp/AppData/Local/Programs/Python/Python313/python.exe -m pip install pygame')
    sys.exit(1)

import random
from dataclasses import dataclass
from enum import Enum

# Add src to path
sys.path.insert(0, 'src')

from myrpg import GameState
from myrpg.combat import ThemeType
from myrpg.items import DropManager, ItemRarity

# =============================================================================
# CONSTANTS
# =============================================================================
TILE_SIZE = 48
GRID_WIDTH = 20
GRID_HEIGHT = 12
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT + 120  # Extra space for UI

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (40, 40, 50)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
BLUE = (65, 105, 225)
RED = (220, 20, 60)
GOLD = (255, 215, 0)
PURPLE = (138, 43, 226)
CYAN = (0, 255, 255)

# Tile types
class TileType(Enum):
    GRASS = 0
    DIRT = 1
    WATER = 2
    TREE = 3
    ROCK = 4
    MASTER = 5  # NPC
    MOB = 6     # Enemy


@dataclass
class Entity:
    x: int
    y: int
    tile_type: TileType
    color: tuple
    name: str = ""


class GameGUI:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("MyRPG - Python Demo")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 36)

        # Game state
        self.game = GameState()
        self.game.power_level.add(100)  # Starting boost

        # Player position
        self.player_x = GRID_WIDTH // 2
        self.player_y = GRID_HEIGHT // 2

        # World generation
        self.world = self._generate_world()
        self.mobs = self._spawn_mobs(8)
        self.master = Entity(3, 3, TileType.MASTER, PURPLE, "Master Chen")

        # Loot system
        self.drop_manager = DropManager(base_drop_chance=0.6)

        # Notifications
        self.notifications = []
        self.notification_timer = 0

        # Move cooldown
        self.move_cooldown = 0

        self.running = True

    def _generate_world(self) -> list:
        """Generate a simple tile map."""
        world = [[TileType.GRASS for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

        # Add some variety
        for _ in range(15):
            x, y = random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1)
            world[y][x] = TileType.TREE

        for _ in range(10):
            x, y = random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1)
            world[y][x] = TileType.ROCK

        for _ in range(8):
            x, y = random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1)
            world[y][x] = TileType.DIRT

        # Add a small pond
        pond_x, pond_y = random.randint(5, GRID_WIDTH-5), random.randint(3, GRID_HEIGHT-3)
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if 0 <= pond_y+dy < GRID_HEIGHT and 0 <= pond_x+dx < GRID_WIDTH:
                    world[pond_y+dy][pond_x+dx] = TileType.WATER

        return world

    def _spawn_mobs(self, count: int) -> list:
        """Spawn enemy mobs."""
        mobs = []
        for i in range(count):
            while True:
                x = random.randint(0, GRID_WIDTH-1)
                y = random.randint(0, GRID_HEIGHT-1)
                # Don't spawn on player or obstacles
                if (x, y) != (self.player_x, self.player_y) and self.world[y][x] == TileType.GRASS:
                    mobs.append(Entity(x, y, TileType.MOB, RED, f"Mob {i+1}"))
                    break
        return mobs

    def add_notification(self, text: str, color: tuple = WHITE):
        """Add a notification message."""
        self.notifications.append({"text": text, "color": color, "time": 120})

    def handle_events(self):
        """Handle input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                if event.key == pygame.K_p:
                    self._spend_pedometer()

                if event.key == pygame.K_SPACE:
                    self._attack()

                if event.key == pygame.K_e:
                    self._interact()

        # Continuous movement with cooldown
        if self.move_cooldown <= 0:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0

            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1

            if dx != 0 or dy != 0:
                self._move_player(dx, dy)
                self.move_cooldown = 8  # frames
        else:
            self.move_cooldown -= 1

    def _move_player(self, dx: int, dy: int):
        """Move the player on the grid."""
        new_x = self.player_x + dx
        new_y = self.player_y + dy

        # Bounds check
        if not (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT):
            return

        # Collision check
        tile = self.world[new_y][new_x]
        if tile in (TileType.WATER, TileType.TREE, TileType.ROCK):
            return

        # Check mob collision
        for mob in self.mobs:
            if mob.x == new_x and mob.y == new_y:
                return  # Can't walk through mobs

        # Move
        self.player_x = new_x
        self.player_y = new_y

        # Update pedometer
        self.game.move(1)

    def _attack(self):
        """Attack nearby mob."""
        # Check adjacent tiles for mobs
        for mob in self.mobs[:]:  # Copy list to allow removal
            if abs(mob.x - self.player_x) <= 1 and abs(mob.y - self.player_y) <= 1:
                # Combat!
                success, gold, xp = self.game.farm_mob()

                if success:
                    self.mobs.remove(mob)
                    self.add_notification(f"Defeated {mob.name}! +{gold}g +{xp:.0f}XP", GOLD)

                    # Check for loot drop
                    drop = self.drop_manager.roll_mob_drop(
                        tier=self.game.current_environment.tier,
                        theme=self.game.current_theme
                    )
                    if drop:
                        self.add_notification(f"Dropped: {drop.item}", CYAN)

                    # Respawn mob elsewhere
                    self.mobs.extend(self._spawn_mobs(1))
                else:
                    self.add_notification("Attack missed!", RED)
                return

        self.add_notification("No enemy nearby!", GRAY)

    def _interact(self):
        """Interact with nearby NPCs."""
        # Check if near master
        if abs(self.master.x - self.player_x) <= 1 and abs(self.master.y - self.player_y) <= 1:
            self.add_notification(f"{self.master.name}: Train hard, student!", PURPLE)
            # Give small training bonus
            self.game.variables.strength.add(1)
            self.add_notification("+1 Strength from training", GREEN)
            return

        self.add_notification("Nothing to interact with", GRAY)

    def _spend_pedometer(self):
        """Spend accumulated steps for speed upgrade."""
        if self.game.pedometer.steps < 100:
            self.add_notification("Need at least 100 steps to spend!", RED)
            return

        reward = self.game.pedometer.calculate_spend_reward()
        if self.game.spend_pedometer():
            self.add_notification(f"Speed +{reward.speed_bonus_percent:.1f}%!", CYAN)

    def update(self):
        """Update game state."""
        # Update notifications
        self.notifications = [n for n in self.notifications if n["time"] > 0]
        for n in self.notifications:
            n["time"] -= 1

        # Manager automation (simulate time passing)
        self.game.update(1/60)  # 60 FPS

    def draw(self):
        """Draw everything."""
        self.screen.fill(DARK_GRAY)

        # Draw world tiles
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                tile = self.world[y][x]
                color = self._get_tile_color(tile)
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE - 1, TILE_SIZE - 1)
                pygame.draw.rect(self.screen, color, rect)

        # Draw master NPC
        self._draw_entity(self.master, "M")

        # Draw mobs
        for mob in self.mobs:
            self._draw_entity(mob, "E")

        # Draw player
        player_rect = pygame.Rect(
            self.player_x * TILE_SIZE + 4,
            self.player_y * TILE_SIZE + 4,
            TILE_SIZE - 8,
            TILE_SIZE - 8
        )
        pygame.draw.rect(self.screen, BLUE, player_rect)
        pygame.draw.rect(self.screen, WHITE, player_rect, 2)

        # Draw UI panel
        ui_y = GRID_HEIGHT * TILE_SIZE
        pygame.draw.rect(self.screen, BLACK, (0, ui_y, SCREEN_WIDTH, 120))
        pygame.draw.line(self.screen, WHITE, (0, ui_y), (SCREEN_WIDTH, ui_y), 2)

        # Stats
        stats = [
            f"Power: {self.game.power_level.value:.0f}",
            f"Gold: {self.game.gold.amount}",
            f"Steps: {self.game.pedometer.steps} (+{self.game.pedometer.speed_bonus_percent:.0f}% speed)",
            f"Theme: {self.game.current_theme.name} Lv.{self.game.mastery.get_level(self.game.current_theme)}",
        ]

        for i, stat in enumerate(stats):
            text = self.font.render(stat, True, WHITE)
            self.screen.blit(text, (10 + (i % 2) * 300, ui_y + 10 + (i // 2) * 25))

        # Environment info
        env_text = f"Environment: {self.game.current_environment.name} (Tier {self.game.current_environment.tier})"
        text = self.font.render(env_text, True, GREEN)
        self.screen.blit(text, (10, ui_y + 65))

        # Controls hint
        controls = "WASD:Move | SPACE:Attack | E:Interact | P:Spend Steps | ESC:Quit"
        text = self.font.render(controls, True, GRAY)
        self.screen.blit(text, (10, ui_y + 95))

        # Notifications
        for i, notif in enumerate(self.notifications[-3:]):  # Show last 3
            alpha = min(255, notif["time"] * 4)
            text = self.font.render(notif["text"], True, notif["color"])
            text.set_alpha(alpha)
            self.screen.blit(text, (SCREEN_WIDTH - text.get_width() - 10, 10 + i * 25))

        pygame.display.flip()

    def _get_tile_color(self, tile: TileType) -> tuple:
        """Get color for a tile type."""
        colors = {
            TileType.GRASS: GREEN,
            TileType.DIRT: (139, 90, 43),
            TileType.WATER: (30, 144, 255),
            TileType.TREE: DARK_GREEN,
            TileType.ROCK: GRAY,
        }
        return colors.get(tile, GREEN)

    def _draw_entity(self, entity: Entity, label: str):
        """Draw an entity on the grid."""
        rect = pygame.Rect(
            entity.x * TILE_SIZE + 6,
            entity.y * TILE_SIZE + 6,
            TILE_SIZE - 12,
            TILE_SIZE - 12
        )
        pygame.draw.rect(self.screen, entity.color, rect)
        pygame.draw.rect(self.screen, WHITE, rect, 1)

        # Label
        text = self.font.render(label, True, WHITE)
        text_rect = text.get_rect(center=rect.center)
        self.screen.blit(text, text_rect)

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()


def main():
    print("Starting MyRPG Visual Demo...")
    print("Controls:")
    print("  Arrow Keys / WASD - Move")
    print("  Space - Attack nearby enemy")
    print("  E - Interact with NPCs")
    print("  P - Spend pedometer steps")
    print("  ESC - Quit")
    print()

    game = GameGUI()
    game.run()


if __name__ == "__main__":
    main()

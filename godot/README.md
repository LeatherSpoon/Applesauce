# MyRPG - Godot Project

A 2D grid-based RPG built with Godot 4.2 for cross-platform deployment.

## Requirements

- **Godot 4.2+** (download from https://godotengine.org/download)

## Quick Start

1. Download and install Godot 4.2 or later
2. Open Godot and click "Import"
3. Navigate to this `godot` folder and select `project.godot`
4. Click "Import & Edit"
5. Press F5 (or click Play) to run the game

## Controls

| Input | Action |
|-------|--------|
| WASD / Arrow Keys | Move |
| Space | Attack (farm mobs) |
| E | Interact |
| Touch/Swipe | Move (mobile) |

## Project Structure

```
godot/
├── project.godot          # Main project file
├── scenes/
│   └── main.tscn          # Main game scene
├── scripts/
│   ├── core/
│   │   ├── game_manager.gd    # Global state (autoload)
│   │   ├── event_bus.gd       # Signal bus (autoload)
│   │   └── currencies.gd      # Currency classes
│   ├── combat/
│   │   └── themes.gd          # Combat theme system
│   ├── ui/
│   │   └── hud.gd             # HUD controller
│   └── player.gd              # Player controller
└── assets/
    ├── sprites/           # Game sprites
    ├── ui/                # UI assets
    └── audio/             # Sound effects & music
```

## Exporting for Distribution

### PC (Steam)

1. In Godot: Project → Export
2. Add preset: "Windows Desktop" / "macOS" / "Linux"
3. Configure settings and export

### iOS (App Store)

1. Requires macOS with Xcode installed
2. In Godot: Project → Export
3. Add preset: "iOS"
4. Set Bundle Identifier (e.g., com.yourcompany.myrpg)
5. Export .ipa file
6. Submit via App Store Connect

### Android (Google Play)

1. Install Android SDK and set path in Editor Settings
2. In Godot: Project → Export
3. Add preset: "Android"
4. Configure keystore for signing
5. Export .apk or .aab file
6. Upload to Google Play Console

## Core Systems

### Currencies
- **Power Level**: Main progression metric
- **Gold**: Active economy (no passive generation)
- **Pedometer**: Steps → speed upgrades

### Combat Themes
- **Unarmed**: Fast combos (1.0x → 2.0x finisher)
- **Armed**: Weapon variety
- **Ranged**: Distance bonuses
- **Energy**: Resource management

### Progression
1. Train with Master
2. Farm mobs for gold/XP
3. Defeat boss
4. Enter tournament
5. Lose → unlock next environment

## Next Steps

- [ ] Add tilemap with actual terrain
- [ ] Create enemy sprites and AI
- [ ] Build inventory UI
- [ ] Add NPC masters for training
- [ ] Implement equipment system
- [ ] Add sound effects and music
- [ ] Create more environments

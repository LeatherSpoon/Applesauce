extends Node
## Global event bus for decoupled communication between systems

# Currency signals
signal power_level_changed(old_value: float, new_value: float)
signal gold_changed(old_amount: int, new_amount: int)
signal pedometer_changed(steps: int)
signal pedometer_spent(speed_bonus: float)

# Combat signals
signal combat_started(opponent_name: String)
signal combat_ended(result: String, rewards: Dictionary)
signal damage_dealt(amount: float, is_critical: bool)
signal damage_taken(amount: float)
signal combo_hit(combo_count: int, multiplier: float)

# Theme signals
signal theme_changed(old_theme: String, new_theme: String)
signal mastery_xp_gained(theme: String, amount: float)
signal mastery_level_up(theme: String, new_level: int)
signal theme_unlocked(theme: String)

# Environment signals
signal environment_entered(env_name: String, tier: int)
signal boss_available(env_name: String)
signal boss_defeated(env_name: String)
signal tournament_started(env_name: String)
signal tournament_victory(wave: int, rewards: Dictionary)
signal tournament_defeat(wave: int)

# Training signals
signal training_started(activity: String)
signal training_completed(variable: String, amount: float)
signal variable_increased(variable: String, new_value: float)

# Manager signals
signal manager_hired(manager_type: String)
signal manager_automation_tick(gains: Dictionary)
signal prestige_triggered(new_level: int)

# Loot signals
signal loot_dropped(item_name: String, rarity: String)
signal item_equipped(slot: String, item_name: String)
signal item_sold(item_name: String, gold: int)

# Movement signals
signal player_moved(new_position: Vector2i)
signal tile_placed(tile_type: String, position: Vector2i)
signal speed_changed(new_speed: float)

# UI signals
signal show_notification(message: String, type: String)
signal open_menu(menu_name: String)
signal close_menu(menu_name: String)

extends Node
## Global game state manager - autoloaded singleton

# Core currencies
var power_level: Currencies.PowerLevel
var gold: Currencies.Gold
var pedometer: Currencies.Pedometer
var variables: Currencies.ControllingVariables

# Combat
var current_theme: CombatThemes.ThemeType = CombatThemes.ThemeType.UNARMED
var mastery: CombatThemes.ThemeMastery

# Environment
var current_environment_tier: int = 1
var current_environment_name: String = "Forest Dojo"
var mobs_defeated: int = 0
var boss_defeated: bool = false

# Manager automation
var managers: Dictionary = {
	"strength": 0,
	"dexterity": 0,
	"focus": 0,
	"endurance": 0
}
var has_physical_director: bool = false
var has_mental_director: bool = false
var has_vp: bool = false
var has_ceo: bool = false
var prestige_level: int = 0

# Player position
var player_grid_position: Vector2i = Vector2i.ZERO

func _ready() -> void:
	# Initialize systems
	power_level = Currencies.PowerLevel.new()
	gold = Currencies.Gold.new()
	pedometer = Currencies.Pedometer.new()
	variables = Currencies.ControllingVariables.new()
	mastery = CombatThemes.ThemeMastery.new()

	print("GameManager initialized")

func _process(delta: float) -> void:
	# Process manager automation
	_process_automation(delta)

# =============================================================================
# MOVEMENT
# =============================================================================
func move_player(direction: Vector2i) -> void:
	player_grid_position += direction
	pedometer.add_steps(1)
	EventBus.player_moved.emit(player_grid_position)

func get_current_speed() -> float:
	var base_speed = 100.0
	return base_speed * pedometer.get_speed_multiplier()

# =============================================================================
# COMBAT
# =============================================================================
func get_effective_power() -> float:
	var theme_damage = CombatThemes.calculate_damage(current_theme, variables, mastery.levels[current_theme])
	var versatility = 1.0 + mastery.get_versatility_bonus()
	return power_level.value * theme_damage * versatility

func farm_mob() -> Dictionary:
	var effective_power = get_effective_power()
	var mob_power = 50.0 * current_environment_tier

	# Simple combat resolution
	if effective_power >= mob_power * 0.5:
		var gold_reward = 10 * current_environment_tier
		var xp_reward = 10.0 * current_environment_tier

		gold.add(gold_reward)
		mastery.add_xp(current_theme, xp_reward)
		power_level.add(0.1 * current_environment_tier)
		mobs_defeated += 1

		# Check boss availability
		if not boss_defeated and mobs_defeated >= 50:
			EventBus.boss_available.emit(current_environment_name)

		EventBus.combat_ended.emit("victory", {"gold": gold_reward, "xp": xp_reward})
		return {"success": true, "gold": gold_reward, "xp": xp_reward}

	EventBus.combat_ended.emit("defeat", {})
	return {"success": false, "gold": 0, "xp": 0.0}

func challenge_boss() -> bool:
	if boss_defeated:
		return false

	var effective_power = get_effective_power()
	var boss_power = 500.0 * current_environment_tier

	if effective_power >= boss_power * 0.7:
		boss_defeated = true
		var gold_reward = 500 * current_environment_tier
		gold.add(gold_reward)
		power_level.add(10.0 * current_environment_tier)
		EventBus.boss_defeated.emit(current_environment_name)
		return true

	return false

func switch_theme(new_theme: CombatThemes.ThemeType) -> bool:
	if not mastery.is_theme_unlocked(new_theme):
		return false

	var old_theme = current_theme
	current_theme = new_theme
	EventBus.theme_changed.emit(
		CombatThemes.THEME_DATA[old_theme].name,
		CombatThemes.THEME_DATA[new_theme].name
	)
	return true

# =============================================================================
# ENVIRONMENT PROGRESSION
# =============================================================================
func advance_to_next_environment() -> void:
	current_environment_tier += 1
	mobs_defeated = 0
	boss_defeated = false

	var env_names = ["Forest Dojo", "Iron Fortress", "Wind Valley", "Crystal Spire", "Sand Temple", "Frozen Peaks"]
	current_environment_name = env_names[(current_environment_tier - 1) % env_names.size()]

	# Theme cycling
	var next_theme = CombatThemes.get_next_theme(current_theme)
	if mastery.is_theme_unlocked(next_theme):
		switch_theme(next_theme)

	EventBus.environment_entered.emit(current_environment_name, current_environment_tier)

# =============================================================================
# MANAGER AUTOMATION
# =============================================================================
func hire_manager(variable: String) -> bool:
	var cost = get_manager_cost(variable)
	if not gold.can_afford(cost):
		return false

	gold.spend(cost)
	managers[variable] += 1
	EventBus.manager_hired.emit(variable)
	return true

func get_manager_cost(variable: String) -> int:
	var count = managers.get(variable, 0)
	return 1000 * int(pow(2, count))

func calculate_efficiency(variable: String) -> float:
	var count = managers.get(variable, 0)
	if count == 0:
		return 0.0

	# Stack efficiency (diminishing returns)
	var efficiency = 0.0
	for i in range(count):
		efficiency += pow(0.5, i + 1)

	# Department bonus
	if variable in ["strength", "endurance"] and has_physical_director:
		efficiency *= 1.25
	elif variable in ["dexterity", "focus"] and has_mental_director:
		efficiency *= 1.25

	# Executive bonus
	if has_vp:
		efficiency *= 1.5

	# Prestige multiplier
	efficiency *= 1.0 + (prestige_level * 0.1)

	return min(efficiency, 1.0)

func _process_automation(delta: float) -> void:
	var gains = {}

	for variable in ["strength", "dexterity", "focus", "endurance"]:
		var efficiency = calculate_efficiency(variable)
		if efficiency > 0:
			var gain = (10.0 * efficiency / 3600.0) * delta
			gains[variable] = gain

			match variable:
				"strength": variables.add_strength(gain)
				"dexterity": variables.add_dexterity(gain)
				"focus": variables.add_focus(gain)
				"endurance": variables.add_endurance(gain)

	if gains.size() > 0:
		EventBus.manager_automation_tick.emit(gains)

# =============================================================================
# SAVE/LOAD
# =============================================================================
func save_game(slot: int = 0) -> bool:
	var save_data = {
		"version": "1.0.0",
		"power_level": power_level.value,
		"gold": gold.amount,
		"pedometer_steps": pedometer.steps,
		"pedometer_speed_bonus": pedometer.speed_bonus_percent,
		"variables": {
			"strength": variables.strength,
			"dexterity": variables.dexterity,
			"focus": variables.focus,
			"endurance": variables.endurance
		},
		"current_theme": current_theme,
		"mastery_levels": mastery.levels.duplicate(),
		"mastery_xp": mastery.xp.duplicate(),
		"environment_tier": current_environment_tier,
		"managers": managers.duplicate(),
		"prestige_level": prestige_level
	}

	var save_path = "user://save_%d.json" % slot
	var file = FileAccess.open(save_path, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(save_data, "\t"))
		file.close()
		return true
	return false

func load_game(slot: int = 0) -> bool:
	var save_path = "user://save_%d.json" % slot
	if not FileAccess.file_exists(save_path):
		return false

	var file = FileAccess.open(save_path, FileAccess.READ)
	if not file:
		return false

	var json = JSON.new()
	var parse_result = json.parse(file.get_as_text())
	file.close()

	if parse_result != OK:
		return false

	var data = json.get_data()

	power_level.value = data.get("power_level", 1.0)
	gold.amount = data.get("gold", 0)
	pedometer.steps = data.get("pedometer_steps", 0)
	pedometer.speed_bonus_percent = data.get("pedometer_speed_bonus", 0.0)

	var vars = data.get("variables", {})
	variables.strength = vars.get("strength", 0.0)
	variables.dexterity = vars.get("dexterity", 0.0)
	variables.focus = vars.get("focus", 0.0)
	variables.endurance = vars.get("endurance", 0.0)

	current_theme = data.get("current_theme", CombatThemes.ThemeType.UNARMED)
	mastery.levels = data.get("mastery_levels", mastery.levels)
	mastery.xp = data.get("mastery_xp", mastery.xp)
	current_environment_tier = data.get("environment_tier", 1)
	managers = data.get("managers", managers)
	prestige_level = data.get("prestige_level", 0)

	return true

# =============================================================================
# DEBUG / STATUS
# =============================================================================
func get_status_text() -> String:
	return """Power Level: %.1f
Gold: %d
Steps: %d (+%.1f%% speed)
Theme: %s (Level %d)
Environment: %s (Tier %d)
Effective Power: %.1f""" % [
		power_level.value,
		gold.amount,
		pedometer.steps,
		pedometer.speed_bonus_percent,
		CombatThemes.THEME_DATA[current_theme].name,
		mastery.levels[current_theme],
		current_environment_name,
		current_environment_tier,
		get_effective_power()
	]

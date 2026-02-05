extends RefCounted
class_name CombatThemes
## Combat theme definitions and mechanics

enum ThemeType { UNARMED, ARMED, RANGED, ENERGY }

# Theme data with scaling and mechanics
const THEME_DATA = {
	ThemeType.UNARMED: {
		"name": "Unarmed",
		"description": "Fast combo-based melee combat",
		"primary_stat": "strength",
		"secondary_stat": "endurance",
		"base_damage": 1.0,
		"attack_speed": 0.5,
		"range": 1,
		"special": "combo"
	},
	ThemeType.ARMED: {
		"name": "Armed",
		"description": "Balanced weapon-based combat",
		"primary_stat": "strength",
		"secondary_stat": "dexterity",
		"base_damage": 1.2,
		"attack_speed": 0.8,
		"range": 1,
		"special": "weapon_swap"
	},
	ThemeType.RANGED: {
		"name": "Ranged",
		"description": "Precision long-range attacks",
		"primary_stat": "dexterity",
		"secondary_stat": "focus",
		"base_damage": 1.4,
		"attack_speed": 1.2,
		"range": 6,
		"special": "critical_distance"
	},
	ThemeType.ENERGY: {
		"name": "Energy",
		"description": "Powerful magic with resource management",
		"primary_stat": "focus",
		"secondary_stat": "endurance",
		"base_damage": 1.6,
		"attack_speed": 1.0,
		"range": 4,
		"special": "energy_pool"
	}
}

static func get_theme_name(theme: ThemeType) -> String:
	return THEME_DATA[theme].name

static func get_next_theme(theme: ThemeType) -> ThemeType:
	return (theme + 1) % 4 as ThemeType

static func calculate_damage(theme: ThemeType, variables: Currencies.ControllingVariables, mastery_level: int) -> float:
	var data = THEME_DATA[theme]
	var base = data.base_damage

	# Get primary and secondary stat values
	var primary_value = 0.0
	var secondary_value = 0.0

	match data.primary_stat:
		"strength": primary_value = variables.strength
		"dexterity": primary_value = variables.dexterity
		"focus": primary_value = variables.focus
		"endurance": primary_value = variables.endurance

	match data.secondary_stat:
		"strength": secondary_value = variables.strength
		"dexterity": secondary_value = variables.dexterity
		"focus": secondary_value = variables.focus
		"endurance": secondary_value = variables.endurance

	# Calculate multiplier
	var stat_mult = 1.0 + (primary_value * 0.02) + (secondary_value * 0.01)
	var mastery_mult = 1.0 + (mastery_level * 0.02)

	return base * stat_mult * mastery_mult


# =============================================================================
# THEME MASTERY
# =============================================================================
class ThemeMastery:
	const MAX_LEVEL = 100

	var levels: Dictionary = {
		ThemeType.UNARMED: 0,
		ThemeType.ARMED: 0,
		ThemeType.RANGED: 0,
		ThemeType.ENERGY: 0
	}
	var xp: Dictionary = {
		ThemeType.UNARMED: 0.0,
		ThemeType.ARMED: 0.0,
		ThemeType.RANGED: 0.0,
		ThemeType.ENERGY: 0.0
	}

	func get_xp_required(level: int) -> float:
		if level <= 0:
			return 0.0
		return 100.0 * pow(level, 1.5)

	func add_xp(theme: ThemeType, amount: float) -> Array:
		var milestones = []
		xp[theme] += amount
		EventBus.mastery_xp_gained.emit(THEME_DATA[theme].name, amount)

		# Check for level ups
		while levels[theme] < MAX_LEVEL:
			var required = get_xp_required(levels[theme] + 1)
			if xp[theme] >= required:
				levels[theme] += 1
				EventBus.mastery_level_up.emit(THEME_DATA[theme].name, levels[theme])

				# Check for theme unlock at level 10
				if levels[theme] == 10:
					var next_theme = CombatThemes.get_next_theme(theme)
					EventBus.theme_unlocked.emit(THEME_DATA[next_theme].name)
					milestones.append({"type": "unlock", "theme": next_theme})

				if levels[theme] % 10 == 0:
					milestones.append({"type": "milestone", "level": levels[theme]})
			else:
				break

		return milestones

	func is_theme_unlocked(theme: ThemeType) -> bool:
		if theme == ThemeType.UNARMED:
			return true
		var prev_theme = (theme - 1) as ThemeType
		if prev_theme < 0:
			prev_theme = ThemeType.ENERGY
		return levels[prev_theme] >= 10

	func get_unlocked_themes() -> Array:
		var unlocked = []
		for theme in ThemeType.values():
			if is_theme_unlocked(theme):
				unlocked.append(theme)
		return unlocked

	func count_themes_at_level(level: int) -> int:
		var count = 0
		for l in levels.values():
			if l >= level:
				count += 1
		return count

	func get_versatility_bonus() -> float:
		var count = count_themes_at_level(50)
		if count >= 4:
			return 0.20
		elif count >= 3:
			return 0.10
		elif count >= 2:
			return 0.05
		return 0.0

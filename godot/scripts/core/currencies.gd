extends RefCounted
class_name Currencies
## Core currency classes for MyRPG

# =============================================================================
# POWER LEVEL
# =============================================================================
class PowerLevel:
	var value: float = 1.0:
		set(v):
			var old = value
			value = v
			EventBus.power_level_changed.emit(old, value)

	func add(amount: float) -> void:
		if amount > 0:
			value += amount

	func get_damage_multiplier() -> float:
		return 1.0 + (value / 100.0)

	func get_defense_multiplier() -> float:
		return 1.0 + (value / 200.0)


# =============================================================================
# GOLD
# =============================================================================
class Gold:
	var amount: int = 0:
		set(v):
			var old = amount
			amount = v
			EventBus.gold_changed.emit(old, amount)
	var total_earned: int = 0
	var total_spent: int = 0

	func add(value: int) -> void:
		if value > 0:
			amount += value
			total_earned += value

	func spend(value: int) -> bool:
		if value <= 0:
			return true
		if amount >= value:
			amount -= value
			total_spent += value
			return true
		return false

	func can_afford(value: int) -> bool:
		return amount >= value


# =============================================================================
# PEDOMETER
# =============================================================================
class Pedometer:
	const SPEED_CAP_PERCENT: float = 500.0

	var steps: int = 0:
		set(v):
			steps = v
			EventBus.pedometer_changed.emit(steps)
	var total_steps_ever: int = 0
	var speed_bonus_percent: float = 0.0
	var times_spent: int = 0

	func add_steps(amount: int) -> void:
		if amount > 0:
			steps += amount
			total_steps_ever += amount

	func calculate_spend_reward() -> Dictionary:
		if steps < 100:
			return {"speed_bonus": 0.0, "achievement_bonus": 0.0}

		var raw_bonus = log(steps) / log(10) * 10.0

		if speed_bonus_percent >= SPEED_CAP_PERCENT:
			return {"speed_bonus": 0.0, "achievement_bonus": raw_bonus / 10.0}

		var remaining_cap = SPEED_CAP_PERCENT - speed_bonus_percent
		var actual_speed = min(raw_bonus, remaining_cap)
		var overflow = raw_bonus - actual_speed

		return {
			"speed_bonus": actual_speed,
			"achievement_bonus": overflow / 10.0 if overflow > 0 else 0.0
		}

	func spend() -> bool:
		if steps < 100:
			return false

		var reward = calculate_spend_reward()
		speed_bonus_percent = min(speed_bonus_percent + reward.speed_bonus, SPEED_CAP_PERCENT)

		EventBus.pedometer_spent.emit(reward.speed_bonus)
		steps = 0
		times_spent += 1
		return true

	func get_speed_multiplier() -> float:
		return 1.0 + (speed_bonus_percent / 100.0)


# =============================================================================
# CONTROLLING VARIABLES
# =============================================================================
class ControllingVariables:
	var strength: float = 0.0
	var dexterity: float = 0.0
	var focus: float = 0.0
	var endurance: float = 0.0

	func add_strength(amount: float) -> void:
		strength += amount
		EventBus.variable_increased.emit("strength", strength)

	func add_dexterity(amount: float) -> void:
		dexterity += amount
		EventBus.variable_increased.emit("dexterity", dexterity)

	func add_focus(amount: float) -> void:
		focus += amount
		EventBus.variable_increased.emit("focus", focus)

	func add_endurance(amount: float) -> void:
		endurance += amount
		EventBus.variable_increased.emit("endurance", endurance)

	func get_training_efficiency() -> float:
		return 1.0 + (focus * 0.01)

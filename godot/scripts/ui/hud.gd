extends CanvasLayer
class_name HUD
## Main game HUD displaying stats and notifications

@onready var power_label: Label = $TopBar/PowerLevel
@onready var gold_label: Label = $TopBar/Gold
@onready var steps_label: Label = $TopBar/Steps
@onready var theme_label: Label = $TopBar/Theme
@onready var env_label: Label = $BottomBar/Environment

@onready var notification_label: Label = $NotificationContainer/Notification
@onready var notification_timer: Timer = $NotificationContainer/Timer

var notification_queue: Array = []

func _ready() -> void:
	# Connect to EventBus signals
	EventBus.power_level_changed.connect(_on_power_changed)
	EventBus.gold_changed.connect(_on_gold_changed)
	EventBus.pedometer_changed.connect(_on_steps_changed)
	EventBus.theme_changed.connect(_on_theme_changed)
	EventBus.environment_entered.connect(_on_environment_entered)
	EventBus.show_notification.connect(_on_show_notification)
	EventBus.combat_ended.connect(_on_combat_ended)
	EventBus.mastery_level_up.connect(_on_mastery_level_up)

	# Initial update
	_update_all()

	# Hide notification initially
	if notification_label:
		notification_label.visible = false

func _update_all() -> void:
	if power_label:
		power_label.text = "PWR: %.0f" % GameManager.power_level.value
	if gold_label:
		gold_label.text = "Gold: %d" % GameManager.gold.amount
	if steps_label:
		steps_label.text = "Steps: %d" % GameManager.pedometer.steps
	if theme_label:
		var theme_name = CombatThemes.THEME_DATA[GameManager.current_theme].name
		var level = GameManager.mastery.levels[GameManager.current_theme]
		theme_label.text = "%s Lv.%d" % [theme_name, level]
	if env_label:
		env_label.text = "%s (Tier %d)" % [GameManager.current_environment_name, GameManager.current_environment_tier]

func _on_power_changed(_old: float, new_value: float) -> void:
	if power_label:
		power_label.text = "PWR: %.0f" % new_value

func _on_gold_changed(_old: int, new_value: int) -> void:
	if gold_label:
		gold_label.text = "Gold: %d" % new_value

func _on_steps_changed(steps: int) -> void:
	if steps_label:
		steps_label.text = "Steps: %d" % steps

func _on_theme_changed(_old: String, new_theme: String) -> void:
	_update_all()
	_on_show_notification("Switched to %s!" % new_theme, "info")

func _on_environment_entered(env_name: String, tier: int) -> void:
	if env_label:
		env_label.text = "%s (Tier %d)" % [env_name, tier]
	_on_show_notification("Entered %s!" % env_name, "info")

func _on_combat_ended(result: String, rewards: Dictionary) -> void:
	if result == "victory" and rewards.has("gold"):
		_on_show_notification("+%d Gold" % rewards.gold, "combat")

func _on_mastery_level_up(theme: String, level: int) -> void:
	_on_show_notification("%s reached Level %d!" % [theme, level], "levelup")
	_update_all()

func _on_show_notification(message: String, type: String) -> void:
	notification_queue.append({"message": message, "type": type})
	_show_next_notification()

func _show_next_notification() -> void:
	if notification_queue.is_empty():
		return

	if notification_label and notification_label.visible:
		# Already showing, wait for timer
		return

	var notif = notification_queue.pop_front()

	if notification_label:
		notification_label.text = notif.message

		# Color based on type
		match notif.type:
			"combat":
				notification_label.modulate = Color.GOLD
			"levelup":
				notification_label.modulate = Color.CYAN
			"error":
				notification_label.modulate = Color.RED
			_:
				notification_label.modulate = Color.WHITE

		notification_label.visible = true

		if notification_timer:
			notification_timer.start(2.0)

func _on_notification_timer_timeout() -> void:
	if notification_label:
		notification_label.visible = false
	_show_next_notification()

extends CharacterBody2D
class_name Player
## Player controller with grid-based movement

@export var tile_size: int = 64
@export var move_speed: float = 200.0

var grid_position: Vector2i = Vector2i.ZERO
var is_moving: bool = false
var target_position: Vector2 = Vector2.ZERO

# Touch/mobile support
var touch_start_position: Vector2 = Vector2.ZERO
var is_touching: bool = false
const SWIPE_THRESHOLD: float = 50.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var animation_player: AnimationPlayer = $AnimationPlayer if has_node("AnimationPlayer") else null

func _ready() -> void:
	position = Vector2(grid_position) * tile_size
	target_position = position

func _process(delta: float) -> void:
	if is_moving:
		_process_movement(delta)
	else:
		_handle_input()

func _handle_input() -> void:
	var direction = Vector2i.ZERO

	# Keyboard input
	if Input.is_action_pressed("move_up"):
		direction = Vector2i(0, -1)
	elif Input.is_action_pressed("move_down"):
		direction = Vector2i(0, 1)
	elif Input.is_action_pressed("move_left"):
		direction = Vector2i(-1, 0)
	elif Input.is_action_pressed("move_right"):
		direction = Vector2i(1, 0)

	if direction != Vector2i.ZERO:
		move_grid(direction)

	# Attack/interact
	if Input.is_action_just_pressed("attack"):
		_try_combat()
	if Input.is_action_just_pressed("interact"):
		_try_interact()

func _input(event: InputEvent) -> void:
	# Touch input for mobile
	if event is InputEventScreenTouch:
		if event.pressed:
			touch_start_position = event.position
			is_touching = true
		else:
			if is_touching:
				var swipe = event.position - touch_start_position
				_handle_swipe(swipe)
			is_touching = false

	# Also support touch drag
	if event is InputEventScreenDrag and is_touching:
		var swipe = event.position - touch_start_position
		if swipe.length() > SWIPE_THRESHOLD:
			_handle_swipe(swipe)
			touch_start_position = event.position

func _handle_swipe(swipe: Vector2) -> void:
	if swipe.length() < SWIPE_THRESHOLD:
		return

	var direction = Vector2i.ZERO
	if abs(swipe.x) > abs(swipe.y):
		direction = Vector2i(1, 0) if swipe.x > 0 else Vector2i(-1, 0)
	else:
		direction = Vector2i(0, 1) if swipe.y > 0 else Vector2i(0, -1)

	move_grid(direction)

func move_grid(direction: Vector2i) -> void:
	if is_moving:
		return

	var new_grid_pos = grid_position + direction

	# Check for collision/boundaries (can be extended)
	if _can_move_to(new_grid_pos):
		grid_position = new_grid_pos
		target_position = Vector2(grid_position) * tile_size
		is_moving = true

		# Update game state
		GameManager.move_player(direction)

		# Update sprite direction
		_update_facing(direction)

func _can_move_to(pos: Vector2i) -> bool:
	# Basic boundary check - can be extended for collision detection
	# For now, allow movement anywhere
	return true

func _process_movement(delta: float) -> void:
	var speed = move_speed * GameManager.pedometer.get_speed_multiplier()
	position = position.move_toward(target_position, speed * delta)

	if position.distance_to(target_position) < 1.0:
		position = target_position
		is_moving = false

func _update_facing(direction: Vector2i) -> void:
	if sprite:
		if direction.x < 0:
			sprite.flip_h = true
		elif direction.x > 0:
			sprite.flip_h = false

func _try_combat() -> void:
	# Simple combat trigger - can be extended for enemy detection
	var result = GameManager.farm_mob()
	if result.success:
		EventBus.show_notification.emit("+%d Gold, +%.0f XP" % [result.gold, result.xp], "combat")

func _try_interact() -> void:
	# Placeholder for NPC/object interaction
	pass

# Teleport to a specific grid position
func teleport_to(new_grid_pos: Vector2i) -> void:
	grid_position = new_grid_pos
	position = Vector2(grid_position) * tile_size
	target_position = position
	is_moving = false
	GameManager.player_grid_position = grid_position

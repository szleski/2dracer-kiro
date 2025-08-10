# Car Entity System

The Car entity system provides a complete game-ready car implementation that integrates physics simulation, rendering, and game state management.

## Overview

The `Car` class in `src/entities/car.py` combines:

- **Physics Integration**: Uses `CarBody` for realistic physics simulation
- **Rendering Integration**: Works with `BlackMambaRenderer` for visual display
- **Game State Management**: Tracks race progress, performance metrics, and status
- **Collision Handling**: Manages crashes, recovery, and collision callbacks
- **Performance Tracking**: Records speed, distance, lap times, and achievements

## Architecture

```
Car Entity
├── CarState (dataclass)     # Race state and performance metrics
├── CarBody (physics)        # Physics simulation and controls
├── Rendering Integration    # Visual representation and effects
└── Game Logic              # Lap tracking, crashes, race management
```

## Usage

### Basic Car Creation

```python
from src.entities.car import Car
from src.physics.physics_engine import PhysicsEngine
from src.rendering.black_mamba_renderer import BlackMambaRenderer
import pymunk

# Create physics space and renderer
physics_engine = PhysicsEngine()
renderer = BlackMambaRenderer(800, 600)

# Create player car
player_car = Car(
    car_id="player",
    physics_space=physics_engine.space,
    position=(400, 300),
    angle=0,
    is_player=True
)

# Create AI car
ai_car = Car(
    car_id="ai_1",
    physics_space=physics_engine.space,
    position=(350, 250),
    angle=0,
    is_player=False
)
```

### Game Loop Integration

```python
# Game loop
while running:
    dt = clock.tick(60) / 1000.0  # 60 FPS
    
    # Handle input (for player car)
    keys = pygame.key.get_pressed()
    throttle = 1.0 if keys[pygame.K_w] else 0.0
    steering = -1.0 if keys[pygame.K_a] else (1.0 if keys[pygame.K_d] else 0.0)
    brake = 1.0 if keys[pygame.K_s] else 0.0
    
    player_car.apply_controls(throttle, steering, brake)
    
    # Update all cars
    for car in cars:
        car.update(dt)
    
    # Step physics
    physics_engine.step(dt)
    
    # Render all cars
    renderer.clear_screen()
    for car in cars:
        car.render(renderer)
    renderer.present()
```

### Race Management

```python
# Complete a lap
car.complete_lap(lap_time=45.2)
print(f"Lap {car.state.current_lap} completed!")
print(f"Best lap: {car.state.best_lap_time:.1f}s")

# Finish race
car.finish_race(final_position=2)
print(f"Race finished in position {car.state.position_in_race}")

# Get comprehensive car information
info = car.get_car_info()
print(f"Speed: {info['speed'] * 3.6:.0f} km/h")
print(f"Distance: {info['distance_traveled']:.0f}m")
print(f"Top speed: {info['top_speed'] * 3.6:.0f} km/h")
```

### Collision Handling

```python
def handle_car_collision(car, collision_info):
    impact_force = collision_info['impulse'].length
    if impact_force > 200:
        print(f"Hard collision for {car.state.car_id}!")
        # Custom collision response
    
car.set_collision_callback(handle_car_collision)
```

## Car State Management

### CarState Properties

```python
@dataclass
class CarState:
    # Identity
    car_id: str
    is_player: bool = False
    
    # Race state
    current_lap: int = 0
    lap_time: float = 0.0
    best_lap_time: Optional[float] = None
    position_in_race: int = 1
    
    # Performance metrics
    top_speed: float = 0.0
    distance_traveled: float = 0.0
    
    # Status flags
    is_finished: bool = False
    is_crashed: bool = False
    respawn_timer: float = 0.0
```

### State Queries

```python
# Check car status
if car.state.is_crashed:
    print("Car is crashed, waiting for respawn...")

if car.state.is_finished:
    print(f"Car finished in position {car.state.position_in_race}")

# Performance metrics
print(f"Current lap: {car.state.current_lap}")
print(f"Lap time: {car.state.lap_time:.1f}s")
print(f"Distance traveled: {car.state.distance_traveled:.0f}m")
```

## Visual Features

### Car Colors
- **Player cars**: Red (`(220, 50, 50)`)
- **AI cars**: Gray tones (automatically assigned based on car ID)
- **Crashed cars**: Darker versions of normal colors

### Rendering Effects
- **Normal state**: Full-color geometric arrow sprite
- **Crashed state**: Darkened sprite with visual feedback
- **Rotation**: Sprite rotates to match car orientation
- **Scaling**: Consistent size regardless of physics body dimensions

## Physics Integration

### Physics Models
Cars support both arcade and realistic physics models:

```python
# Switch to realistic physics
car.switch_physics_model('realistic')

# Switch to arcade physics  
car.switch_physics_model('arcade')
```

### Performance Characteristics
- **Arcade Mode**: 
  - Top speed: ~100 km/h
  - Turn rate: ~30°/second
  - Quick acceleration and responsive handling
  
- **Realistic Mode**:
  - Top speed: ~100 km/h  
  - Turn rate: ~13°/second
  - More authentic acceleration curves and handling

### Physics Information
```python
# Get detailed physics data
info = car.get_car_info()
print(f"Forward speed: {info['forward_speed']:.1f} px/s")
print(f"Lateral speed: {info['lateral_speed']:.1f} px/s")
print(f"Is sliding: {info['is_sliding']}")
print(f"Physics model: {info['physics_model']}")
```

## Crash System

### Crash Detection
Cars automatically detect crashes based on collision impact force:

```python
# Crash threshold (configurable)
car.crash_threshold = 300.0  # Impact force threshold

# Crashes trigger automatic recovery
# - Car becomes unresponsive for respawn_timer duration
# - Visual feedback (darker colors)
# - Automatic recovery after timer expires
```

### Recovery Process
1. **Impact Detection**: High-force collision triggers crash state
2. **Respawn Timer**: Car becomes unresponsive (default: 2 seconds)
3. **Visual Feedback**: Darker rendering indicates crashed state
4. **Automatic Recovery**: Car returns to normal operation
5. **Velocity Reset**: Stops car movement but preserves position

## Demo Application

The complete car entity demo showcases all features:

```bash
poetry run python demo_car_entity.py
```

**Features Demonstrated:**
- Player car control (WASD)
- AI car behavior (simple autonomous driving)
- Physics model switching (SPACE key)
- Real-time performance metrics
- Visual rendering with camera following
- Crash detection and recovery

**Controls:**
- **W/A/S/D**: Drive player car
- **Shift**: Brake
- **Space**: Switch physics model
- **Escape**: Exit demo

## Testing

Comprehensive test suite covers all car entity functionality:

```bash
# Run car entity tests
poetry run pytest tests/test_car.py -v

# Test coverage includes:
# - Car state management
# - Physics integration
# - Control input handling
# - Collision detection
# - Performance tracking
# - Race management
# - Rendering integration
```

## Integration Points

### Physics Engine
- Uses `PhysicsEngine` for Pymunk space management
- Integrates with `CarBody` for physics simulation
- Supports physics model switching at runtime

### Rendering System
- Works with `BlackMambaRenderer` for visual display
- Automatic sprite generation and caching
- Camera-relative rendering support

### Input System (Future)
- Will integrate with input management for control mapping
- Support for multiple input devices
- Customizable control schemes

### AI System (Future)
- AI cars will use the same Car entity
- Behavior trees will control AI car inputs
- Racing line following and opponent interaction

## Performance Considerations

- **Memory**: Minimal overhead with efficient state management
- **Physics**: Leverages optimized Pymunk simulation
- **Rendering**: Sprite caching reduces draw call overhead
- **Updates**: Lightweight per-frame updates (< 1ms per car)

## Future Enhancements

Planned improvements for the car entity system:

1. **Damage System**: Visual and performance damage from collisions
2. **Customization**: Car appearance and performance tuning
3. **Telemetry**: Detailed performance data recording
4. **Replay System**: Record and playback car movements
5. **Multiplayer**: Network synchronization support
6. **Audio Integration**: Engine sounds and collision audio
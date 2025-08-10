# Car Physics System

The car physics system provides realistic vehicle simulation using the Pymunk physics engine. It supports multiple physics models and comprehensive car dynamics.

## Overview

The `CarBody` class in `src/physics/car_physics.py` implements a complete car physics simulation with:

- **Dual Physics Models**: Arcade and Realistic configurations
- **Force-Based Controls**: Throttle, steering, and braking
- **Collision Detection**: Track boundaries and car-to-car interactions
- **Speed-Dependent Handling**: Realistic high-speed driving challenges
- **Runtime Configuration**: Switch physics models during gameplay

## Physics Models

### Arcade Physics
- **Mass**: 800kg (lighter for responsiveness)
- **Friction**: 0.9 (high grip for easy control)
- **Max Force**: 6000N (quick acceleration)
- **Max Torque**: 2500Nm (sharp turns)
- **Handling Degradation**: 30% at high speeds
- **Target Experience**: Fun, forgiving, accessible

### Realistic Physics
- **Mass**: 1200kg (heavier, more momentum)
- **Friction**: 0.6 (lower grip, more sliding)
- **Max Force**: 4000N (gradual acceleration)
- **Max Torque**: 1500Nm (wider turning radius)
- **Handling Degradation**: 70% at high speeds
- **Target Experience**: Challenging, authentic simulation

## Usage

### Basic Car Creation

```python
from src.physics.car_physics import CarBody, CarPhysicsPresets
import pymunk

# Create physics space
space = pymunk.Space()

# Create car with arcade physics (default)
car = CarBody(space, position=(100, 100))

# Or create with realistic physics
car = CarBody(space, position=(100, 100), 
              config=CarPhysicsPresets.realistic())
```

### Control Input

```python
# Apply controls (values from -1.0 to 1.0)
car.apply_controls(
    throttle=0.8,   # Forward acceleration
    steering=-0.5,  # Left turn
    brake=0.0       # No braking
)

# Update physics (call every frame)
car.update_physics(dt=1/60.0)
```

### Physics Model Switching

```python
# Switch to realistic physics at runtime
car.switch_physics_config(CarPhysicsPresets.realistic())

# Switch back to arcade physics
car.switch_physics_config(CarPhysicsPresets.arcade())
```

### Collision Detection

```python
def on_collision(collision_info):
    print(f"Collision at {collision_info['point']}")
    print(f"Impact normal: {collision_info['normal']}")

car.set_collision_callback(on_collision)
```

## Key Features

### Speed-Dependent Handling
At high speeds (>200 px/s for arcade, >180 px/s for realistic), steering effectiveness is reduced to simulate realistic driving physics where cars become harder to control at speed.

### Sliding Detection
The system can detect when a car is sliding based on lateral velocity:

```python
if car.is_sliding(threshold=50.0):
    print("Car is sliding!")
```

### Physics Information
Get detailed physics data for debugging or UI display:

```python
info = car.get_physics_info()
print(f"Speed: {info['speed']:.1f} px/s")
print(f"Forward speed: {info['forward_speed']:.1f} px/s")
print(f"Lateral speed: {info['lateral_speed']:.1f} px/s")
print(f"Is sliding: {info['is_sliding']}")
```

## Collision Types

The system uses Pymunk collision types for proper collision handling:

- **Type 1**: Car bodies
- **Type 2**: Track boundaries and static obstacles

## Demo

Run the interactive car physics demo:

```bash
poetry run python demo_car_physics.py
```

**Controls:**
- **WASD/Arrow Keys**: Drive the car
- **Space**: Brake
- **R**: Reset car position
- **P**: Switch between arcade and realistic physics

## Testing

The car physics system includes comprehensive tests:

```bash
# Run car physics tests
poetry run pytest tests/test_car_physics.py -v

# Run all physics tests
poetry run pytest tests/test_*physics* -v
```

**Test Coverage:**
- Physics configuration presets
- Car body creation and management
- Control input handling and clamping
- Force application (throttle, steering, braking)
- Speed calculations and sliding detection
- Collision detection and callbacks
- Physics model switching
- Multi-car scenarios

## Integration

The car physics system integrates with:

- **Physics Engine** (`src/physics/physics_engine.py`): Provides the Pymunk space and simulation
- **Game Entities** (`src/entities/car.py`): Higher-level car entity wrapper
- **Input System** (`src/input/`): Translates player input to control values
- **Rendering System** (`src/rendering/`): Visualizes car position and orientation

## Performance Considerations

- Physics updates run at 60 FPS (1/60.0 second timesteps)
- Collision detection is optimized through Pymunk's spatial hashing
- Force calculations are lightweight vector operations
- Memory usage is minimal with object pooling for collision info

## Future Enhancements

Potential improvements for the car physics system:

1. **Tire Model**: Individual tire physics with grip circles
2. **Suspension**: Vertical dynamics and weight transfer
3. **Aerodynamics**: Downforce and drag effects
4. **Engine Simulation**: RPM, gearing, and power curves
5. **Surface Types**: Different friction for grass, gravel, etc.
6. **Damage System**: Performance degradation from collisions
# Project Structure

## Directory Organization

```
src/
├── core/          # Main game loop and coordination
├── physics/       # Pymunk physics simulation
├── entities/      # Game entities (cars, tracks)
├── ai/            # AI behavior and pathfinding
├── rendering/     # Graphics and visual effects
├── input/         # Input handling and controls
├── audio/         # Sound effects and music
├── editor/        # Track editor interface
├── ui/            # User interface components
└── utils/         # Utility functions
```

## Module Responsibilities

### Core (`src/core/`)
- **game_engine.py**: Main game loop and coordination
- **scene_manager.py**: Scene management (menu, race, editor)
- **event_system.py**: Event handling and messaging

### Physics (`src/physics/`)
- **physics_engine.py**: Pymunk physics world management
- **car_physics.py**: Car body and constraint setup
- **collision_handler.py**: Collision callbacks and responses

### Entities (`src/entities/`)
- **car.py**: Player and AI car entities
- **track.py**: Track representation and logic
- **track_segment.py**: Individual track pieces

### AI (`src/ai/`)
- **ai_driver.py**: AI car behavior and decision making
- **path_finding.py**: Racing line calculation

### Rendering (`src/rendering/`)
- **renderer.py**: Main rendering coordinator
- **sprite_manager.py**: Sprite loading and management
- **retro_effects.py**: Retro visual effects and filters

### Input (`src/input/`)
- **input_manager.py**: Input handling and mapping
- **controls.py**: Control scheme definitions

### Audio (`src/audio/`)
- **audio_manager.py**: Sound effect and music management
- **retro_synth.py**: Chiptune audio generation

### Editor (`src/editor/`)
- **track_editor.py**: Track creation interface
- **editor_tools.py**: Track editing tools and utilities

### UI (`src/ui/`)
- **hud.py**: In-game UI elements
- **menu.py**: Menu system
- **retro_ui.py**: Retro-styled UI components

### Utils (`src/utils/`)
- **math_utils.py**: Vector math and utility functions
- **config.py**: Game configuration and constants

## Coding Conventions

### File Naming
- Use snake_case for all Python files
- Module names should be descriptive and singular
- Avoid abbreviations unless widely understood

### Import Organization
- Standard library imports first
- Third-party imports (pygame, pymunk, numpy) second
- Local project imports last
- Use absolute imports from src/ root

### Class Structure
- Use dataclasses for simple data containers
- Type hints required for all function signatures
- Follow component-based entity patterns where applicable

### Physics Integration
- All physics objects must be properly added/removed from Pymunk space
- Use consistent units throughout (pixels for distance, seconds for time)
- Separate physics simulation from rendering coordinates when necessary
# Retro Racing Game

A top-down 2D racing game with retro aesthetics, featuring physics-based car simulation, AI opponents, and a track editor.

## Features

- Physics-based car simulation using Pymunk
- AI opponents with multiple difficulty levels  
- Track editor for creating custom tracks
- Retro visual styling with Black Mamba Racer aesthetics
- Multiple physics models (arcade vs realistic)
- Clean, minimalist rendering system with geometric car sprites

## Development Setup

This project uses Poetry for dependency management within a conda environment.

### Prerequisites

- Python 3.12.0
- Conda environment: `2dracer-kiro`
- Poetry package manager

### Installation

1. Activate the conda environment:
   ```bash
   conda activate 2dracer-kiro
   ```

2. Install dependencies with Poetry:
   ```bash
   poetry install
   ```

3. Run the game:
   ```bash
   poetry run python src/main.py
   ```

4. Try the demos:
   ```bash
   # Black Mamba Racer rendering demo
   poetry run python demo_black_mamba_renderer.py
   
   # Car physics demo (WASD to drive, P to switch physics, R to reset)
   poetry run python demo_car_physics.py
   ```

## Development

### Code Formatting
```bash
poetry run black src/
```

### Type Checking
```bash
poetry run mypy src/
```

### Testing
```bash
poetry run pytest
```

## Implemented Features

### ✅ Black Mamba Racer Rendering System
- Muted color palette with grays, whites, and selective accents
- Geometric arrow-like car sprites with rotation support
- Tire barriers and checkered pattern track elements
- Clean typography and mini-map system
- Comprehensive test suite with 16 passing tests

### ✅ Car Physics System
- Realistic car simulation using Pymunk physics engine
- Dual physics models: Arcade (responsive, forgiving) and Realistic (challenging, momentum-based)
- Speed-dependent handling degradation for authentic high-speed driving
- Comprehensive collision detection with track boundaries and other cars
- Force-based controls: throttle, steering, braking with proper physics integration
- Runtime physics model switching for experimentation
- Sliding detection and lateral/forward speed calculations
- Comprehensive test suite with 20 passing tests

## Project Structure

```
src/
├── core/          # Main game loop and coordination
├── physics/       # Pymunk physics simulation
├── entities/      # Game entities (cars, tracks)
├── ai/            # AI behavior and pathfinding
├── rendering/     # Graphics and visual effects (Black Mamba Racer style)
├── input/         # Input handling and controls
├── audio/         # Sound effects and music
├── editor/        # Track editor interface
├── ui/            # User interface components
└── utils/         # Utility functions
```
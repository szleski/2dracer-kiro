# Retro Racing Game

A top-down 2D racing game with retro aesthetics, featuring physics-based car simulation, AI opponents, and a track editor.

## Features

- Physics-based car simulation using Pymunk
- AI opponents with multiple difficulty levels  
- Track editor for creating custom tracks
- Retro visual and audio styling
- Multiple physics models (arcade vs realistic)

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

## Project Structure

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
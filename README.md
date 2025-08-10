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

4. Try the Black Mamba Racer rendering demo:
   ```bash
   poetry run python demo_black_mamba_renderer.py
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
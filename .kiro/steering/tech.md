# Technology Stack

## Core Technologies

- **Python 3.12.0** - Primary development language
- **Pygame 2.5.0+** - Graphics rendering and input handling
- **Pymunk 6.5.0+** - Physics simulation engine
- **NumPy 1.24.0+** - Mathematical operations

## Development Environment

- **Conda Environment**: `2dracer-kiro` (pre-configured) - **ALWAYS ACTIVATE THIS ENVIRONMENT**
- **Package Manager**: Poetry for dependency management
- **Code Formatting**: Black (line length: 88, target: py312)
- **Type Checking**: MyPy with strict settings
- **Testing**: Pytest

**IMPORTANT**: All development work must be done within the `2dracer-kiro` conda environment. Always run `conda activate 2dracer-kiro` before executing any commands.

## Build System

Poetry is used within an existing conda environment for optimal dependency management.

### Common Commands

**Environment Setup:**

```bash
conda activate 2dracer-kiro
poetry install
```

**Running the Game:**

```bash
poetry run python src/main.py
```

**Development Tools:**

```bash
# Code formatting
poetry run black src/

# Type checking
poetry run mypy src/

# Testing
poetry run pytest
```

## Architecture Patterns

- Component-based entity system
- Event-driven architecture for game state management
- Modular physics system supporting multiple simulation models
- Scene management pattern for different game states (menu, race, editor)

## Key Libraries Usage

- **Pymunk**: Professional 2D physics simulation with rigid body dynamics
- **Pygame**: Cross-platform graphics, sound, and input handling
- **NumPy**: Vector mathematics and array operations for game calculations

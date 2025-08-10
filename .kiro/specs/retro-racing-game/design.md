# Design Document

## Overview

The retro racing game will be built as a desktop 2D game using Python with Pygame for rendering and input handling, and Pymunk for physics simulation. The architecture follows a component-based entity system with separate modules for physics simulation, rendering, input handling, AI behavior, and track management. The game leverages Pymunk's professional-grade physics engine to support both arcade and realistic physics models, allowing extensive experimentation with different car dynamics approaches.

## Architecture

### Development Environment

**Dependency Management:**
The project uses Poetry for dependency management within an existing conda environment:

**Environment Setup:**
- Conda environment: `2dracer-kiro` (already created)
- Python version: 3.12.0 (already configured)
- Poetry manages dependencies within the conda environment

```toml
# pyproject.toml
[tool.poetry]
name = "retro-racing-game"
version = "0.1.0"
description = "A top-down 2D racing game with retro aesthetics"
authors = ["Developer <dev@example.com>"]

[tool.poetry.dependencies]
python = "^3.12"
pygame = "^2.5.0"
pymunk = "^6.5.0"
numpy = "^1.24.0"  # For mathematical operations

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
black = "^23.0.0"
mypy = "^1.0.0"
```

**Development Workflow:**
1. Activate conda environment: `conda activate 2dracer-kiro`
2. Use Poetry for dependency management: `poetry install`
3. Poetry will respect the existing conda environment
4. Run the game: `poetry run python src/main.py`

**Benefits of Conda + Poetry:**
- Conda handles system-level dependencies and Python version
- Poetry manages Python package dependencies and lock files
- Best of both worlds for scientific/game development
- Reproducible builds with poetry.lock

### Core Game Loop

The game follows a standard game loop pattern:

1. **Input Processing** - Handle player input and AI decision making
2. **Physics Update** - Apply physics simulation to all cars
3. **Game Logic Update** - Handle lap counting, collision detection, race state
4. **Rendering** - Draw all game objects with retro styling
5. **Audio Update** - Play sound effects and background music

### Module Structure

```
src/
├── core/
│   ├── game_engine.py         # Main game loop and coordination
│   ├── scene_manager.py       # Scene management (menu, race, editor)
│   └── event_system.py        # Event handling and messaging
├── physics/
│   ├── physics_engine.py      # Pymunk physics world management
│   ├── car_physics.py         # Car body and constraint setup
│   └── collision_handler.py   # Collision callbacks and responses
├── entities/
│   ├── car.py                 # Player and AI car entities
│   ├── track.py               # Track representation and logic
│   └── track_segment.py       # Individual track pieces
├── ai/
│   ├── ai_driver.py           # AI car behavior and decision making
│   └── path_finding.py        # Racing line calculation
├── rendering/
│   ├── black_mamba_renderer.py # Black Mamba Racer style rendering system
│   ├── sprite_manager.py      # Sprite loading and management
│   └── retro_effects.py       # Retro visual effects and filters
├── input/
│   ├── input_manager.py       # Input handling and mapping
│   └── controls.py            # Control scheme definitions
├── audio/
│   ├── audio_manager.py       # Sound effect and music management
│   └── retro_synth.py         # Chiptune audio generation
├── editor/
│   ├── track_editor.py        # Track creation interface
│   └── editor_tools.py        # Track editing tools and utilities
├── ui/
│   ├── hud.py                 # In-game UI elements
│   ├── menu.py                # Menu system
│   └── retro_ui.py            # Retro-styled UI components
└── utils/
    ├── math_utils.py          # Vector math and utility functions
    └── config.py              # Game configuration and constants
```

## Components and Interfaces

### Car Physics System

The car physics system leverages Pymunk's rigid body physics with multiple simulation models:

**Arcade Physics Model:**

- Higher friction coefficients for easier control
- Reduced angular damping for responsive turning
- Modified force application for immediate response
- Collision damping for forgiving crashes

**Realistic Physics Model:**

- Accurate tire friction simulation using Pymunk's friction
- Four-wheel physics with individual tire forces
- Weight transfer through center of mass adjustments
- Realistic collision responses with momentum conservation

**Pymunk Car Body Setup:**

```python
@dataclass
class CarPhysicsConfig:
    mass: float = 1000.0
    moment: float = pymunk.moment_for_box(1000.0, (40, 20))
    friction: float = 0.7
    max_force: float = 5000.0
    max_torque: float = 2000.0
    linear_damping: float = 0.1
    angular_damping: float = 0.1
    
class CarBody:
    def __init__(self, space: pymunk.Space, config: CarPhysicsConfig):
        self.body = pymunk.Body(config.mass, config.moment)
        self.shape = pymunk.Poly.create_box(self.body, (40, 20))
        self.shape.friction = config.friction
        space.add(self.body, self.shape)
```

### AI System

AI cars use a behavior tree approach with multiple decision layers:

1. **Strategic Layer** - Race strategy, overtaking decisions
2. **Tactical Layer** - Path planning, obstacle avoidance
3. **Operational Layer** - Steering, acceleration, braking inputs

**AI Difficulty Levels:**

- **Novice** - Slower reaction times, suboptimal racing lines
- **Intermediate** - Good racing lines, occasional mistakes
- **Expert** - Optimal racing lines, aggressive but fair racing

### Track System

Tracks are composed of connected segments with different properties:

**Track Segment Types:**

- Straight sections with varying lengths
- Curved sections with different radii and banking
- Start/finish line segments
- Checkpoint segments for lap detection

**Track Properties (Black Mamba Racer Style):**

```python
@dataclass
class TrackSegment:
    id: str
    segment_type: str  # 'straight', 'curve', 'start', 'checkpoint'
    position: Tuple[float, float]
    rotation: float
    length: float
    width: float
    curvature: Optional[float] = None  # For curved segments
    banking: Optional[float] = None    # Track banking angle
    surface: str = 'asphalt'  # 'asphalt', 'dirt', 'grass' - affects friction
    tire_barriers: List[Tuple[float, float]] = None  # Positions for tire barrier sprites
    
    def create_pymunk_bodies(self, space: pymunk.Space) -> List[pymunk.Body]:
        """Create Pymunk static bodies for track boundaries"""
        bodies = []
        # Create left and right boundary walls
        # Implementation details for converting segment to physics bodies
        return bodies
    
    def generate_tire_barriers(self) -> List[Tuple[float, float]]:
        """Generate tire barrier positions along track edges"""
        barriers = []
        # Place tire barriers at regular intervals along track boundaries
        # Following the Black Mamba Racer visual style
        return barriers

@dataclass
class TrackVisuals:
    """Visual elements for Black Mamba Racer style tracks"""
    checkered_start_line: bool = True
    tire_barrier_spacing: float = 30.0  # Distance between tire barriers
    boundary_line_width: int = 2
    surface_texture_intensity: float = 0.1  # Subtle texture variation
    
    # Color scheme matching Black Mamba Racer
    colors = {
        'asphalt': pygame.Color(128, 128, 128),
        'grass': pygame.Color(74, 124, 89),
        'dirt': pygame.Color(139, 69, 19),
        'boundary': pygame.Color(255, 255, 255),
        'tire_barrier': pygame.Color(32, 32, 32),
        'checkered_black': pygame.Color(0, 0, 0),
        'checkered_white': pygame.Color(255, 255, 255)
    }
```

### HUD and Mini-Map System

**Mini-Map Design (Black Mamba Racer Style):**
```python
@dataclass
class MiniMapConfig:
    position: Tuple[int, int] = (10, 10)  # Top-left corner
    size: Tuple[int, int] = (120, 80)     # Compact size
    background_color: pygame.Color = pygame.Color(224, 224, 224, 200)
    border_color: pygame.Color = pygame.Color(0, 0, 0)
    track_color: pygame.Color = pygame.Color(128, 128, 128)
    player_dot_color: pygame.Color = pygame.Color(255, 68, 68)
    ai_dot_color: pygame.Color = pygame.Color(68, 68, 68)
    
class MiniMap:
    def __init__(self, track: Track, config: MiniMapConfig):
        self.track_outline = self.generate_track_outline(track)
        self.config = config
        
    def render(self, surface: pygame.Surface, cars: List[Car]):
        # Draw semi-transparent background
        mini_surface = pygame.Surface(self.config.size, pygame.SRCALPHA)
        mini_surface.fill(self.config.background_color)
        
        # Draw simplified track outline
        pygame.draw.lines(mini_surface, self.config.track_color, False, self.track_outline, 2)
        
        # Draw car positions as colored dots
        for car in cars:
            dot_pos = self.world_to_minimap(car.position)
            color = self.config.player_dot_color if car.is_player else self.config.ai_dot_color
            pygame.draw.circle(mini_surface, color, dot_pos, 3)
        
        surface.blit(mini_surface, self.config.position)
```

**HUD Layout (Matching Black Mamba Racer):**
- **Top-Left**: Mini-map with track outline and car positions
- **Top-Center**: Current lap time in large, clear font
- **Top-Right**: Lap counter (e.g., "LAP 1/3")
- **Bottom**: Speed indicator and position information
- **Clean Typography**: Sans-serif fonts, high contrast, minimal decoration

### Track Editor

The track editor provides a visual interface for creating custom tracks:

**Editor Features:**

- Drag-and-drop track segment placement
- Real-time track validation
- Test drive functionality
- Track export/import system
- Visual grid and snapping tools

## Data Models

### Game State Management

```python
@dataclass
class GameState:
    current_scene: str  # 'menu', 'race', 'editor', 'settings'
    race_state: Optional['RaceState'] = None
    player_progress: Optional['PlayerProgress'] = None
    settings: Optional['GameSettings'] = None

@dataclass
class RaceState:
    cars: List['Car']
    track: 'Track'
    current_lap: int
    total_laps: int
    race_time: float
    positions: List[int]  # Car positions in race order
    is_finished: bool
    pymunk_space: pymunk.Space  # Physics world
```

### Physics Configuration

```python
@dataclass
class PhysicsConfig:
    model: str  # 'arcade' or 'realistic'
    gravity: Tuple[float, float] = (0, 0)  # Top-down view, no gravity
    friction: float = 0.7
    air_resistance: float = 0.1
    collision_damping: float = 0.8
    time_step: float = 1.0 / 60.0  # 60 FPS physics
    iterations: int = 10  # Pymunk solver iterations
    
class PhysicsEngine:
    def __init__(self, config: PhysicsConfig):
        self.space = pymunk.Space()
        self.space.gravity = config.gravity
        self.space.damping = config.air_resistance
        self.config = config
```

### Black Mamba Racer Visual Style

The visual aesthetic follows the clean, minimalist approach of Black Mamba Racer:

**Color Palette:**
- **Primary Colors** - Light gray (#E0E0E0), dark gray (#404040), white (#FFFFFF)
- **Accent Colors** - Red (#FF4444) for player car, yellow (#FFFF44) for checkpoints
- **Track Colors** - Asphalt gray (#808080), grass green (#4A7C59), dirt brown (#8B4513)
- **UI Colors** - Black text (#000000) on light backgrounds for maximum readability

**Car Design:**
```python
# Simple geometric car sprites - arrow-like shapes
CAR_SPRITES = {
    'player': {
        'color': (255, 68, 68),  # Red
        'shape': 'arrow',        # Simple triangular/arrow shape
        'size': (20, 12)         # Small, clean proportions
    },
    'ai_cars': [
        {'color': (68, 68, 68), 'shape': 'arrow', 'size': (20, 12)},   # Dark gray
        {'color': (136, 136, 136), 'shape': 'arrow', 'size': (20, 12)} # Light gray
    ]
}
```

**Track Visual Elements:**
- **Tire Barriers** - Black circular sprites arranged along track edges
- **Checkered Patterns** - Start/finish line with alternating black/white squares
- **Track Boundaries** - Clean white lines separating track from grass
- **Surface Textures** - Subtle noise patterns for asphalt without overwhelming detail

**UI Design:**
- **Mini-Map** - Small track outline in corner showing car positions as colored dots
- **HUD Elements** - Clean sans-serif fonts, minimal borders, high contrast
- **Race Information** - Lap counter, timer, and position displayed unobtrusively
- **Visual Hierarchy** - Important information (current lap time) larger and more prominent

**Rendering Implementation:**

The BlackMambaRenderer class has been implemented with the following key features:

- **Muted Color Palette**: Grays, whites, and selective red/yellow accents
- **Geometric Car Sprites**: Arrow-like shapes with rotation and caching
- **Track Elements**: Tire barriers and checkered patterns
- **Clean UI System**: Typography hierarchy and mini-map functionality
- **Surface Management**: Efficient pygame.Surface handling with UI overlay

```python
# Example usage of the implemented BlackMambaRenderer
from src.rendering.black_mamba_renderer import BlackMambaRenderer

renderer = BlackMambaRenderer(800, 600)
renderer.clear_screen()
renderer.draw_car((400, 300), 45.0, renderer.colors.ACCENT_RED)
renderer.draw_tire_barrier((200, 200), 12)
renderer.draw_hud_text("Lap: 1/3", (20, 20), "medium")
renderer.present()
```

## Error Handling

### Physics Simulation Errors

- **Pymunk Solver Issues** - Adjust iteration count and damping parameters
- **Physics Instability** - Velocity clamping and Pymunk body sleep thresholds
- **NaN/Infinity Values** - Reset body positions and velocities to safe defaults
- **Memory Leaks** - Proper cleanup of Pymunk bodies and shapes from space

### AI Behavior Errors

- **Pathfinding Failures** - Fallback to simple track following
- **Stuck AI Cars** - Automatic unstuck mechanisms
- **Performance Issues** - AI complexity scaling based on frame rate

### Track Editor Errors

- **Invalid Track Configurations** - Real-time validation with user feedback
- **Save/Load Failures** - Graceful error messages and recovery options
- **Performance Issues** - Level-of-detail rendering for complex tracks

### Asset Loading Errors

- **Missing Sprites** - Fallback to pygame.Surface with solid colors
- **Audio Loading Failures** - pygame.mixer error handling with silent fallback
- **Font Loading Issues** - pygame.font.get_default_font() system font fallbacks
- **File Path Issues** - Robust asset path resolution using os.path.join

## Testing Strategy

### Unit Testing

- **Physics Calculations** - Test car movement, collision detection, and physics models
- **AI Decision Making** - Test pathfinding algorithms and behavior trees
- **Track Validation** - Test track segment connections and lap detection
- **Utility Functions** - Test mathematical operations and data structures

### Integration Testing

- **Game Loop Performance** - Test frame rate stability under various conditions
- **Physics-Rendering Sync** - Ensure visual representation matches physics state
- **AI-Player Interaction** - Test AI responses to player actions
- **Track Editor Workflow** - Test complete track creation and testing process

### Performance Testing

- **Frame Rate Analysis** - Target 60 FPS with multiple AI cars
- **Memory Usage** - Monitor for memory leaks during extended gameplay
- **Asset Loading Times** - Optimize sprite and audio loading
- **Physics Simulation Cost** - Profile different physics models for performance

### User Experience Testing

- **Control Responsiveness** - Test input lag and control precision
- **Physics Feel** - Validate that car handling feels engaging
- **AI Behavior** - Ensure AI provides appropriate challenge levels
- **Visual Clarity** - Confirm retro style doesn't impede gameplay

### Platform Compatibility Testing

- **macOS Support** - Primary target platform for development and testing
- **Python Version Compatibility** - Developed with Python 3.12.0 in conda environment
- **Dependency Management** - Test Pygame and Pymunk installation on macOS
- **Performance Scaling** - Test on various Mac hardware capabilities and screen resolutions

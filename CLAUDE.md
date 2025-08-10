# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"방과 후 생존 (After School Survivors)" is a 10-minute hyper-casual roguelike game built with Python and Pygame. Players control a character that automatically moves following the mouse cursor and attacks automatically, with the goal of surviving waves of enemies while collecting items and facing bosses every 1.5 minutes.

## Development Environment Setup

### Prerequisites
- Python 3.13+
- Anaconda (recommended for environment management)

### Environment Setup
```bash
# Create conda environment
conda create -n as-game python=3.13
conda activate as-game

# Install uv (modern pip replacement)
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows: irm https://astral.sh/uv/install.ps1 | iex

# Install dependencies
uv pip install -r requirements.txt
```

### Core Dependencies
- **pygame>=2.6.0**: Main game engine
- **numpy>=2.2.4**: Math operations and array processing optimization  
- **pymunk>=6.8.1**: 2D physics engine for collision detection
- **pygame-menu>=4.5.2**: Game menu system
- **pygame-gui>=0.6.14**: In-game UI widgets
- **pydantic>=2.0.0**: Data validation and settings management
- **numba>=0.60.0**: JIT compilation for performance optimization
- **ruff>=0.6.0**: Modern linting and formatting
- **pytest>=8.0.0**: Testing framework

## Architecture

### ECS (Entity-Component-System) Architecture
The game follows an ECS architecture pattern:

- **Entities**: Game objects (Player, Enemy, Item, etc.)
- **Components**: Data containers (Position, Health, Velocity, etc.)
- **Systems**: Logic processors (Movement, Collision, Rendering, etc.)

### Project Structure
```
src/
├── core/           # ECS framework foundation
│   ├── entity.py
│   ├── component.py
│   ├── system.py
│   ├── entity_manager.py
│   ├── component_registry.py
│   └── system_orchestrator.py
├── systems/        # Game systems
├── components/     # Game components
├── entities/       # Game entities
└── utils/         # Utility functions

tests/             # Test files
docs/              # Documentation
```

## Task Master AI Integration

This project uses Task Master AI for development workflow management. Key commands:

### Initial Setup
```bash
task-master init                    # Initialize Task Master
task-master parse-prd docs/PRD.md  # Generate tasks from PRD
task-master analyze-complexity      # Analyze task complexity
task-master expand --all           # Expand all tasks into subtasks
```

### Daily Workflow
```bash
task-master list                          # Show all tasks
task-master next                          # Get next available task
task-master show <id>                    # View task details
task-master set-status --id=<id> --status=done  # Mark task complete
```

### Task Management
```bash
task-master update-subtask --id=<id> --prompt="implementation notes"
task-master add-task --prompt="description" --research
task-master expand --id=<id> --research --force
```

## Development Commands

### Python Environment
```bash
# Use conda environment Python directly (as-game environment)
/opt/homebrew/anaconda3/envs/as-game/bin/python    # Python interpreter
/opt/homebrew/anaconda3/envs/as-game/bin/python -m pytest  # Run tests
```

### Code Quality
```bash
/opt/homebrew/anaconda3/envs/as-game/bin/python -m ruff check .    # Lint code
/opt/homebrew/anaconda3/envs/as-game/bin/python -m ruff format .   # Format code
/opt/homebrew/anaconda3/envs/as-game/bin/python -m pytest          # Run tests
memory_profiler       # Profile memory usage
```

### Game Execution
The game will be executed through the main entry point once implemented. No specific run commands are defined yet as the codebase is in early development.

## Game Design Core Features

### Player Character
- Mouse-controlled movement (follows cursor)
- Automatic attacks in facing direction
- 6 item slots (items cannot be dropped once acquired)

### Item System
- **Weapons**: Soccer ball, basketball, baseball bat
- **Abilities**: Soccer shoes, basketball shoes, red ginseng, milk
- **Synergies**: Specific item combinations provide bonus effects (e.g., soccer shoes + soccer ball = 15% damage increase)

### Enemy & Boss System
- Progressive difficulty scaling over time
- Boss appears every 1.5 minutes (Principal character)
- Debuff & mission system during boss fights

### Performance Target
- Maintain 40+ FPS during gameplay

## Coding Standards & Conventions

### Core Development Principles

1. **Type Safety First**: All functions require complete type hints using Python 3.13+ native syntax
2. **Performance-Optimized Enums**: Use multi-layer IntEnum pattern for computation/display separation
3. **Pure Function Priority**: Separate state mutation from calculation logic
4. **Interface-Based Design**: ABC classes define contracts, implementations remain swappable
5. **Test-Driven Development**: pytest-based validation for all critical game logic paths

### Modern Python Type Hints (Required)

**✅ Use Native Collections (Python 3.9+)**
```python
def process_entities(entities: list[Entity]) -> dict[str, int]:
    return {}

def handle_input(value: int | float | None) -> str:  # Python 3.10+ union syntax
    return ""
```

**✅ Complete Function Typing (Mandatory)**
```python
def calculate_damage_with_synergy(
    base_damage: int,
    synergy_multiplier: float, 
    target_defense: int
) -> int:
    return int(base_damage * synergy_multiplier - target_defense)
```

### Multi-Layer Enum Performance Pattern

**MUST use IntEnum for all predefined game values with these suffixes:**
- `*_type`: `weapon_type: WeaponType`, `projectile_type: ProjectileType`
- `*_status`: `player_status: PlayerStatus`, `game_status: GameStatus`
- `*_state`: `entity_state: EntityState`, `game_state: GameState`  
- `*_mode`: `difficulty_mode: DifficultyMode`, `render_mode: RenderMode`

**Three-Layer Implementation Pattern:**
```python
from enum import IntEnum

class WeaponType(IntEnum):
    SOCCER_BALL = 0
    BASKETBALL = 1  
    BASEBALL_BAT = 2
    
    @property
    def display_name(self) -> str:
        return self._display_names[self]
    
    @property
    def damage_multiplier(self) -> float:
        return self._damage_multipliers[self.value]  # Performance lookup
    
    _display_names = {
        SOCCER_BALL: "축구공",
        BASKETBALL: "농구공", 
        BASEBALL_BAT: "야구 배트"
    }
    
    _damage_multipliers = [1.2, 1.0, 1.5]  # Index-based fast lookup
```

**Usage by Context:**
```python
# ✅ Business Logic - Use Enum directly
@dataclass
class WeaponComponent:
    weapon_type: WeaponType
    damage: int

# ✅ Performance Critical - Use .value for computations
def calculate_damage(weapon: WeaponComponent, base_damage: int) -> int:
    multiplier = weapon.weapon_type._damage_multipliers[weapon.weapon_type.value]
    return int(base_damage * multiplier)

# ✅ UI/Display - Use .display_name  
def render_weapon_ui(weapon: WeaponComponent) -> str:
    return f"무기: {weapon.weapon_type.display_name}"
```

### Game-Specific Enums (Required)

```python
class PlayerStatus(IntEnum):
    ALIVE = 0
    INVULNERABLE = 1
    DEAD = 2
    
    @property
    def display_name(self) -> str:
        return ["생존", "무적", "사망"][self.value]

class GameState(IntEnum):
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    BOSS_FIGHT = 4

class ItemType(IntEnum):
    SOCCER_SHOES = 0  # 축구화
    BASKETBALL_SHOES = 1  # 농구화  
    RED_GINSENG = 2  # 홍삼
    MILK = 3  # 우유
```

### ECS Architecture Implementation

**Interface Definition with ABC:**
```python
from abc import ABC, abstractmethod

class ISystem(ABC):
    @abstractmethod
    def update(self, entities: list[Entity], delta_time: float) -> None: pass
    
    @abstractmethod
    def initialize(self) -> None: pass
```

**Component Structure (Required dataclass + Enum pattern):**
```python
@dataclass
class HealthComponent:
    current: int
    maximum: int
    status: PlayerStatus  # Enum for type safety
    regeneration_rate: float

@dataclass
class WeaponComponent:
    weapon_type: WeaponType  # Multi-layer Enum
    damage: int
    attack_speed: float
    synergy_items: list[ItemType] = field(default_factory=list)
```

### Performance Optimization Rules

**✅ Pure Functions for Game Calculations:**
```python
def calculate_movement_delta(
    current_pos: tuple[float, float],
    velocity: tuple[float, float],
    delta_time: float
) -> tuple[float, float]:
    return (
        current_pos[0] + velocity[0] * delta_time,
        current_pos[1] + velocity[1] * delta_time
    )
```

**✅ Use enum.value for Performance-Critical Game Loops:**
```python
def apply_boss_debuff(
    player_speed: float,
    debuff_types: list[DebuffType]
) -> float:
    multiplier = 1.0
    for debuff in debuff_types:
        if debuff.value == DebuffType.SLOW.value:  # Fast int comparison
            multiplier *= 0.5
    return player_speed * multiplier
```

### Naming Conventions

- **Classes**: `PascalCase` (PlayerMovementSystem, HealthComponent, ICollisionDetector)
- **Functions/Variables**: `snake_case` (calculate_damage_with_synergy, max_health)
- **Constants**: `UPPER_SNAKE_CASE` (MAX_ENEMIES_COUNT, DEFAULT_PLAYER_SPEED)
- **Component Suffix**: Always end with "Component" (HealthComponent, WeaponComponent)

### Code Quality Requirements

**Before committing, verify:**
- [ ] All functions have complete type hints using Python 3.13+ syntax
- [ ] Game values use appropriate IntEnum types (*_type, *_status, *_state, *_mode)
- [ ] Performance-critical code uses enum.value for integer comparisons
- [ ] UI code uses enum.display_name for Korean text display
- [ ] Components use @dataclass with type hints
- [ ] Pure functions separate from state mutation
- [ ] `ruff check .` and `ruff format .` pass without errors

### Testing Pattern

**MANDATORY: Follow Korean testing conventions when using /write-unit-test command**

```python
import pytest

class TestWeaponComponent:
    def test_무기_시너지_데미지_계산_정확성_성공_시나리오(self) -> None:
        """1. 무기 시너지 적용 시 데미지 계산 정확성 검증 (성공 시나리오)
        
        목적: 시너지 아이템 조합 시 데미지 배율 계산 검증
        테스트할 범위: WeaponComponent의 damage_multiplier 연동
        커버하는 함수 및 데이터: weapon_type 속성들
        기대되는 안정성: 일관된 데미지 배율 계산 보장
        """
        # Given - 축구공과 축구화 조합 설정
        weapon = WeaponComponent(
            weapon_type=WeaponType.SOCCER_BALL,
            damage=10,
            synergy_items=[ItemType.SOCCER_SHOES]
        )
        
        # When - 각 레이어 데이터 조회
        performance_value = weapon.weapon_type.value
        display_name = weapon.weapon_type.display_name  
        damage_multiplier = weapon.weapon_type.damage_multiplier
        
        # Then - 정확한 값 반환 확인
        assert performance_value == 0, "축구공의 성능 인덱스는 0이어야 함"
        assert display_name == "축구공", "축구공의 표시명이 정확해야 함" 
        assert damage_multiplier == 1.2, "축구공의 데미지 배율이 1.2여야 함"
```

**Testing Command Reference:** @/.claude/commands/write-unit-test.md

## Task Master AI Instructions

**Import Task Master's development workflow commands and guidelines, treat as if import is in the main CLAUDE.md file.**
@./.taskmaster/CLAUDE.md

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
The game follows an ECS architecture pattern with advanced features:

- **Entities**: Game objects (Player, Enemy, Item, etc.)
- **Components**: Data containers (Position, Health, Velocity, etc.)
- **Systems**: Logic processors (Movement, Collision, Rendering, etc.)

### Coordinate Transformation System (Core Feature)
A sophisticated world-to-screen coordinate transformation system:

- **CoordinateManager**: Singleton manager for coordinate transformations
- **CachedCameraTransformer**: High-performance cached transformations
- **Observer Pattern**: Systems automatically notified of transformer changes
- **Thread-Safe**: Supports concurrent access across systems
- **World Coordinates**: Game logic operates in infinite world space
- **Screen Coordinates**: Rendering operates in screen pixel space

```python
# Usage example:
manager = CoordinateManager.get_instance()
screen_pos = manager.world_to_screen(Vector2(world_x, world_y))
world_pos = manager.screen_to_world(Vector2(screen_x, screen_y))
```

### Event System Architecture
Decoupled event-driven communication between systems:

- **EventBus**: Central event dispatcher using observer pattern
- **BaseEvent**: Type-safe event base class with generic payload
- **Event Interfaces**: Publisher/Subscriber contracts via ABC
- **Async Support**: Non-blocking event processing
- **Type Safety**: Generic event types with payload validation

```python
# Event usage example:
event_bus = EventBus()
event = EnemyDeathEvent(entity_id=enemy_id, position=pos)
await event_bus.publish_async(event)  # Non-blocking dispatch
```

### Project Structure
```
src/
├── core/           # ECS framework foundation + advanced systems
│   ├── entity.py, component.py, system.py
│   ├── entity_manager.py, component_registry.py, system_orchestrator.py
│   ├── coordinate_manager.py, coordinate_transformer.py  # Coordinate system
│   ├── cached_camera_transformer.py, camera_based_transformer.py
│   ├── coordinate_cache.py  # Performance optimization
│   ├── game_loop.py, time_manager.py  # Game loop management
│   ├── game_state_manager.py, state_handler.py  # State management
│   └── events/     # Event system (observer pattern)
│       ├── event_bus.py, base_event.py
│       └── interfaces.py, event_types.py
├── systems/        # Game systems (16+ implemented)
│   ├── camera_system.py, player_movement_system.py
│   ├── entity_render_system.py, render_system.py
│   ├── collision_system.py, physics_system.py
│   ├── weapon_system.py, projectile_system.py
│   └── map_render_system.py
├── components/     # Game components (13+ implemented)
│   ├── position_component.py, render_component.py
│   ├── player_component.py, camera_component.py
│   ├── weapon_component.py, projectile_component.py
│   ├── health_component.py, collision_component.py
│   └── player_movement_component.py, velocity_component.py
├── data/           # Data management system
│   ├── loader.py, models.py, validator.py
│   └── file_repository.py  # File I/O abstraction
├── entities/       # Game entity factories
└── utils/          # Utility functions
    └── vector2.py  # 2D vector math

tests/              # Comprehensive test suite (40+ test files)
data/               # Game data (JSON configs)
demo_*.py           # Runnable demos
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

### Code Quality & Testing
```bash
# type check
/opt/homebrew/anaconda3/envs/as-game/bin/python -m mypy src/

# Linting and formatting (ALWAYS run before committing)
/opt/homebrew/anaconda3/envs/as-game/bin/python -m ruff check .
/opt/homebrew/anaconda3/envs/as-game/bin/python -m ruff format .
/opt/homebrew/anaconda3/envs/as-game/bin/python -m ruff check --fix .

# Testing commands (comprehensive test suite)
/opt/homebrew/anaconda3/envs/as-game/bin/python -m pytest -v          # Run all tests
/opt/homebrew/anaconda3/envs/as-game/bin/python -m pytest tests/test_core.py -v
/opt/homebrew/anaconda3/envs/as-game/bin/python -m pytest tests/test_entity_manager.py -v

# Specific system testing patterns
/opt/homebrew/anaconda3/envs/as-game/bin/python -m pytest tests/test_coordinate_*.py -v
/opt/homebrew/anaconda3/envs/as-game/bin/python -m pytest tests/test_weapon_*.py -v
/opt/homebrew/anaconda3/envs/as-game/bin/python -m pytest tests/test_*_system.py -v

# Performance and validation
memory_profiler       # Profile memory usage (installed)
```

### Game Execution
```bash
# Main game demo (comprehensive ECS demo with UI)
/opt/homebrew/anaconda3/envs/as-game/bin/python demo_first_move.py

# Alternative demo files
/opt/homebrew/anaconda3/envs/as-game/bin/python demo_player_camera.py
/opt/homebrew/anaconda3/envs/as-game/bin/python demo_map_render.py
/opt/homebrew/anaconda3/envs/as-game/bin/python simple_demo.py
```

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
- [ ] AI 주석 시스템 적절히 적용 (AI-NOTE, AI-DEV)
- [ ] `ruff check .` and `ruff format .` pass without errors

### AI 주석 시스템

#### # AI-NOTE : 비즈니스 로직 & 요구사항

**사용 시점**: 비즈니스 로직, 사용자 요구사항, 도메인 규칙 반영 시

**작성 형식**:
```python
# AI-NOTE : [변경일자] 비즈니스 로직 설명
# - 이유: 왜 이렇게 구현했는지
# - 요구사항: 어떤 요구사항을 반영했는지
# - 히스토리: 이전 버전과의 차이점
```

**예시**:
```python
# AI-NOTE : 2025-01-10 무기별 데미지 배율 시스템 도입
# - 이유: 게임 밸런스 조정을 위한 요구사항 반영
# - 요구사항: 축구공(1.2배), 농구공(1.0배), 야구방망이(1.5배)
# - 히스토리: 기존 고정 데미지에서 무기별 차별화로 변경
def calculate_damage(self, base_damage: int, weapon_type: WeaponType) -> int:
    multiplier = weapon_type.damage_multiplier
    return int(base_damage * multiplier)
```

**히스토리 관리**:
```python
# AI-NOTE : [변경 히스토리]
# - 2025-01-15: 보스전 시 데미지 20% 감소 적용 (난이도 조정 요구사항)
# - 2025-01-10: 무기별 데미지 배율 시스템 도입 (밸런스 요구사항)
# - 2025-01-05: 기본 데미지 계산 로직 구현 (초기 요구사항)
```

#### # AI-DEV : 개발 기술적 사항

**사용 시점**: 기술적 해결책, 성능 최적화, 버그 수정, 개발 환경 이슈

**작성 형식**:
```python
# AI-DEV : [기술적 이유] 구현 설명
# - 문제: 어떤 기술적 문제가 있었는지
# - 해결책: 어떻게 해결했는지
# - 주의사항: 유지보수 시 주의할 점
```

**예시**:
```python
# AI-DEV : 레이스 컨디션 방지를 위한 비동기 저장 완료 대기
# - 문제: async 저장과 sync 저장이 동시 실행되어 파일 충돌 발생
# - 해결책: threading.Event로 비동기 작업 완료 신호 대기
# - 주의사항: timeout 설정으로 무한 대기 방지 (100ms)
def save_config(self) -> bool:
    if not self._async_save_event.is_set():
        self._async_save_event.wait(timeout=0.1)
```

#### 주석 활용 가이드라인

**1. 주석 위치**: 관련 코드 바로 위에 작성
**2. 중첩 사용 가능**:
```python
# AI-NOTE : 사용자 요구사항 - 아이템 시너지 시스템
class ItemSynergy:
    def calculate_bonus(self, items: list[ItemType]) -> float:
        # AI-DEV : 성능을 위한 사전 계산된 시너지 테이블 사용
        # - 이유: 실시간 계산 시 프레임 드롭 발생
        return self._synergy_table.get(tuple(sorted(items)), 1.0)
```

**3. 업데이트 규칙**:
- 코드 변경 시 관련 AI-NOTE/AI-DEV 주석도 함께 업데이트
- 이전 버전 정보는 히스토리로 보존
- 불필요해진 주석은 삭제하되 중요한 결정은 히스토리로 남김

### Testing Pattern

**MANDATORY: Follow Korean testing conventions when using /write-unit-test command**

#### 🚨 pytest 경고 방지 규칙 (Critical)

**❌ 금지사항**: Helper/Mock 클래스에 `Test` 접두사 사용 금지
```python
# 잘못된 예 - pytest가 테스트 클래스로 오인
class TestPositionComponent(Component):  # ❌
class TestMovementSystem(System):        # ❌
```

**✅ 권장사항**: Helper/Mock 클래스는 명확한 접두사 사용
```python
# 올바른 예 - Helper/Mock 클래스임을 명확히 표시
class MockPositionComponent(Component):  # ✅
class FakeMovementSystem(System):        # ✅ 
class DummyHealthComponent(Component):   # ✅
class StubRenderSystem(System):          # ✅
```

**pytest 컬렉션 패턴 이해**:
- pytest가 테스트로 인식: 클래스명 `Test*`, 함수명 `test_*`, 파일명 `test_*.py`
- Helper 클래스가 피해야 할 패턴: `Test`로 시작하는 클래스명 + `__init__` 메서드

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

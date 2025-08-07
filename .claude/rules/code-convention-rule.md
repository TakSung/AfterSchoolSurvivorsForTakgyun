# Python Game Development Coding Convention Rules

## Executive Summary

Apply modern Python 3.13+ conventions with performance-optimized multi-layer Enum patterns for game development. Use native type hints, ECS architecture patterns, and unified tooling (Ruff 0.6+) for maintainable, performant code.

## Core Principles

1. **Type Safety First**: All functions require type hints using Python 3.13+ native syntax
2. **Performance-Optimized Enums**: Multi-layer pattern for computation/display separation  
3. **Pure Function Priority**: Separate state mutation from calculation logic
4. **Interface-Based Design**: ABC classes define contracts, implementations remain swappable
5. **Test-Driven Development**: pytest-based validation for all critical paths

## 1. Type Hints & Modern Syntax

### Use Native Collections (Python 3.9+)
```python
# ✅ Correct - Native generics
def process_entities(entities: list[Entity]) -> dict[str, int]:
    return {}

# ❌ Avoid - typing module imports
from typing import List, Dict
def process_entities(entities: List[Entity]) -> Dict[str, int]:
    return {}
```

### Union Types with | Syntax (Python 3.10+)
```python
# ✅ Correct - Modern union syntax
def handle_input(value: int | float | None) -> str:
    return ""

# ❌ Avoid - typing.Union
from typing import Union
def handle_input(value: Union[int, float, None]) -> str:
    return ""
```

### Mandatory Type Hints
```python
# ✅ Correct - Complete typing
def calculate_damage_with_synergy(
    base_damage: int,
    synergy_multiplier: float,
    target_defense: int
) -> int:
    return int(base_damage * synergy_multiplier - target_defense)

# ❌ Avoid - Missing type hints
def calculate_damage_with_synergy(base_damage, synergy_multiplier, target_defense):
    return int(base_damage * synergy_multiplier - target_defense)
```

## 2. Multi-Layer Enum Performance Pattern

### Required Enum Usage Patterns
Use Enums for ALL predefined value variables with these suffixes:
- `*_type`: `weapon_type: WeaponType`, `projectile_type: ProjectileType`
- `*_status`: `player_status: PlayerStatus`, `game_status: GameStatus`  
- `*_state`: `entity_state: EntityState`, `game_state: GameState`
- `*_mode`: `difficulty_mode: DifficultyMode`, `render_mode: RenderMode`
- `*_phase`: `game_phase: GamePhase`, `battle_phase: BattlePhase`
- `*_priority`: `task_priority: Priority`, `render_priority: RenderPriority`

### Three-Layer Implementation Pattern

**Performance Layer - Integer codes for computation:**
```python
from enum import IntEnum

class WeaponType(IntEnum):
    BASIC = 0
    RAPID_FIRE = 1
    SPREAD_SHOT = 2
    LASER_BEAM = 3
    
    @property
    def display_name(self) -> str:
        """User-friendly display string"""
        return self._display_names[self]
    
    @property
    def damage_multiplier(self) -> float:
        """Performance computation using integer values"""
        return self._damage_multipliers[self.value]
    
    _display_names = {
        BASIC: "Basic Shot",
        RAPID_FIRE: "Rapid Fire",
        SPREAD_SHOT: "Spread Shot", 
        LASER_BEAM: "Laser Beam"
    }
    
    _damage_multipliers = [1.0, 0.7, 0.9, 1.5]  # Index-based lookup
```

**Usage Convention by Context:**
```python
# ✅ DTO/Business Logic - Use Enum directly
@dataclass
class WeaponComponent:
    weapon_type: WeaponType
    damage: int
    attack_speed: float

# ✅ Performance Critical - Use .value for computations  
def calculate_weapon_damage(weapon: WeaponComponent, base_damage: int) -> int:
    # Fast integer comparison and array lookup
    multiplier_index = weapon.weapon_type.value
    return int(base_damage * weapon.weapon_type._damage_multipliers[multiplier_index])

# ✅ UI/Display - Use .display_name for user interface
def render_weapon_info(weapon: WeaponComponent) -> str:
    return f"Weapon: {weapon.weapon_type.display_name}"
```

### Game-Specific Enum Examples

```python
class PlayerStatus(IntEnum):
    ALIVE = 0
    INVULNERABLE = 1  
    DEAD = 2
    
    @property
    def display_name(self) -> str:
        return ["Alive", "Invulnerable", "Dead"][self.value]

class GameState(IntEnum):
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    
    @property
    def display_name(self) -> str:
        return ["Menu", "Playing", "Paused", "Game Over"][self.value]

class DebuffType(IntEnum):
    SLOW = 0
    POISON = 1
    FREEZE = 2
    BURN = 3
    
    @property
    def display_name(self) -> str:
        return ["Slow", "Poison", "Freeze", "Burn"][self.value]
    
    @property
    def stack_limit(self) -> int:
        return [3, 5, 1, 4][self.value]  # Performance-optimized lookup
```

## 3. Naming Conventions

### Classes - PascalCase
```python
class PlayerMovementSystem: pass
class HealthComponent: pass  
class ICollisionDetector(ABC): pass  # Interface prefix
```

### Functions/Variables - snake_case
```python
def calculate_damage_with_synergy() -> int: pass
max_health = 100
current_weapon_type = WeaponType.BASIC
```

### Constants - UPPER_SNAKE_CASE  
```python
MAX_ENEMIES_COUNT = 50
DEFAULT_PLAYER_SPEED = 200.0
WEAPON_DAMAGE_MULTIPLIERS = [1.0, 0.7, 0.9, 1.5]
```

### Component Suffix Convention
```python
class HealthComponent: pass
class MovementComponent: pass
class WeaponComponent: pass
```

## 4. ECS Architecture Patterns

### Interface Definition with ABC
```python
from abc import ABC, abstractmethod

class ISystem(ABC):
    @abstractmethod
    def update(self, entities: list[Entity], delta_time: float) -> None: pass
    
    @abstractmethod  
    def initialize(self) -> None: pass
    
    @abstractmethod
    def cleanup(self) -> None: pass
```

### Component Structure with Enums
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
    projectile_type: ProjectileType
```

### System Implementation Example
```python
class CollisionSystem(ISystem):
    def update(self, entities: list[Entity], delta_time: float) -> None:
        for entity in entities:
            if entity.has_component(CollisionComponent):
                # Use enum.value for performance-critical calculations
                collision_type_code = entity.collision_component.collision_type.value
                self._handle_collision_by_code(collision_type_code)
    
    def _handle_collision_by_code(self, type_code: int) -> None:
        # Fast integer-based logic
        pass
```

## 5. Data Structure Patterns

### Use dataclass with type hints
```python
@dataclass
class GameConfig:
    target_fps: int = 60
    max_enemies: int = 50
    difficulty_mode: DifficultyMode = DifficultyMode.NORMAL
    
@dataclass
class PlayerStats:
    health: int
    damage: int
    speed: float
    current_status: PlayerStatus
```

### JSON Serialization with Enums
```python
# ✅ Correct - Integer serialization for performance
def serialize_component(component: WeaponComponent) -> dict[str, any]:
    return {
        "weapon_type": component.weapon_type.value,  # Integer for size/speed
        "damage": component.damage,
        "attack_speed": component.attack_speed
    }

def deserialize_component(data: dict[str, any]) -> WeaponComponent:
    return WeaponComponent(
        weapon_type=WeaponType(data["weapon_type"]),  # Reconstruct from int
        damage=data["damage"], 
        attack_speed=data["attack_speed"]
    )
```

## 6. Performance Optimization Patterns

### Pure Functions for Calculations
```python
# ✅ Correct - Pure function with type hints
def calculate_movement_delta(
    current_pos: tuple[float, float],
    velocity: tuple[float, float], 
    delta_time: float
) -> tuple[float, float]:
    return (
        current_pos[0] + velocity[0] * delta_time,
        current_pos[1] + velocity[1] * delta_time
    )

# ✅ Use enum values for performance-critical paths  
def apply_debuff_effects(
    base_speed: float,
    debuff_types: list[DebuffType]
) -> float:
    speed_multiplier = 1.0
    for debuff in debuff_types:
        # Fast integer lookup instead of string comparison
        if debuff.value == DebuffType.SLOW.value:
            speed_multiplier *= 0.5
        elif debuff.value == DebuffType.FREEZE.value:
            speed_multiplier = 0.0
    return base_speed * speed_multiplier
```

### Avoid String Comparisons in Game Loops
```python
# ❌ Avoid - String comparison in hot path
def update_entity_by_type(entity: Entity) -> None:
    if entity.type_name == "player":  # Slow string comparison
        update_player(entity)
    elif entity.type_name == "enemy":
        update_enemy(entity)

# ✅ Correct - Integer comparison with Enum
def update_entity_by_type(entity: Entity) -> None:
    if entity.entity_type.value == EntityType.PLAYER.value:  # Fast int comparison
        update_player(entity)
    elif entity.entity_type.value == EntityType.ENEMY.value:
        update_enemy(entity)
```

## 7. Testing Patterns

### pytest Structure with Enum Testing
```python
import pytest
from your_game.components import WeaponComponent, WeaponType

class TestWeaponComponent:
    def test_weapon_damage_calculation(self) -> None:
        weapon = WeaponComponent(
            weapon_type=WeaponType.RAPID_FIRE,
            damage=10,
            attack_speed=0.3
        )
        
        # Test all three layers
        assert weapon.weapon_type.value == 1  # Performance layer
        assert weapon.weapon_type.display_name == "Rapid Fire"  # Display layer
        assert weapon.weapon_type.damage_multiplier == 0.7  # Business layer
    
    @pytest.mark.parametrize("weapon_type,expected_multiplier", [
        (WeaponType.BASIC, 1.0),
        (WeaponType.RAPID_FIRE, 0.7),
        (WeaponType.SPREAD_SHOT, 0.9),
        (WeaponType.LASER_BEAM, 1.5),
    ])
    def test_damage_multipliers(
        self, weapon_type: WeaponType, expected_multiplier: float
    ) -> None:
        assert weapon_type.damage_multiplier == expected_multiplier
```

## 8. Tool Configuration

### Ruff Configuration (pyproject.toml)
```toml
[tool.ruff]
line-length = 88
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "A", "C4", "PT"]
ignore = ["E501"]  # Line length handled by formatter

[tool.ruff.format] 
quote-style = "double"
indent-style = "space"
```

### Type Checking Integration
```bash
# Add to development workflow
ruff check --fix .        # Lint and auto-fix
ruff format .             # Format code  
mypy src/                 # Type checking
pytest tests/             # Run tests
```

## 9. Code Quality Checklist

Before committing, verify:

- [ ] All functions have complete type hints using Python 3.13+ syntax
- [ ] Predefined value variables use appropriate Enum types (*_type, *_status, etc.)
- [ ] Performance-critical code uses enum.value for integer comparisons
- [ ] UI code uses enum.display_name for user-facing strings
- [ ] ABC interfaces define system contracts
- [ ] Components use dataclass with type hints
- [ ] Pure functions separate from state mutation
- [ ] Tests cover all three Enum layers (value, business logic, display)
- [ ] Ruff passes without warnings
- [ ] mypy/pyright type checking passes

## 10. Common Patterns Summary

### Quick Reference - Enum Usage
```python
# Declaration
class StatusType(IntEnum):
    ACTIVE = 0
    INACTIVE = 1
    
    @property
    def display_name(self) -> str:
        return ["Active", "Inactive"][self.value]

# Usage contexts
status: StatusType = StatusType.ACTIVE           # Business logic
performance_code: int = status.value             # Hot path computation  
user_text: str = status.display_name            # UI display
```

### Quick Reference - Component Pattern
```python
@dataclass
class ComponentName:
    typed_field: int
    enum_field: EnumType
    optional_field: str | None = None
```

This convention ensures type-safe, performant, and maintainable game code optimized for modern Python development.
# Write Python Unit Test Command

## Command Purpose
Generate comprehensive Python unit tests following modern testing practices with pytest, type hints, and Given-When-Then pattern for the AfterSchoolSurvivors game project.

## Usage
```
/write-unit-test-for-py <ClassName>
```

## Command Behavior

### Step 1: Code Analysis
- Analyze target class structure and methods using Python introspection
- Identify public methods requiring testing (methods without leading underscore)
- Determine dependencies and mockable components using `unittest.mock`
- Assess potential test scenarios (success, failure, edge cases, type validation)
- Check for async methods requiring special handling

### Step 2: Test Case Generation
Generate test methods following these modern Python patterns:

#### Method Naming Convention
```python
@pytest.mark.parametrize("test_case", [...])
def test_테스트대상_상황_예상결과_시나리오(test_case):
    """N. 상황_설명 (성공/실패 시나리오)"""
```

#### Documentation Structure
```python
"""
N. 테스트 시나리오 명 (성공/실패 시나리오)

목적: [구체적인 테스트 목표]
테스트할 범위: [테스트 대상 메서드나 기능의 범위]  
커버하는 함수 및 데이터: [실제로 호출되는 메서드와 검증할 데이터]
기대되는 안정성: [테스트 통과 시 보장되는 안정성]
[실패 조건]: [실패 시나리오인 경우만 추가]
"""
```

#### Test Body Structure (Given-When-Then)
```python
def test_example():
    """테스트 설명"""
    # Given - [테스트 환경 및 조건 설정]
    
    # When - [테스트 대상 실행]
    
    # Then - [결과 검증]
```

### Step 3: Modern Python Test Scenarios Coverage
Automatically generate tests for:

1. **성공 시나리오**: 정상적인 입력으로 예상되는 결과 검증
2. **실패 시나리오**: 잘못된 입력이나 조건에서의 예외 처리 검증
3. **타입 안전성 테스트**: TypeVar, Generic, Protocol 준수 검증
4. **None 안전성 테스트**: Optional 타입 및 None 입력 안전 처리 검증
5. **비동기 메서드 테스트**: async/await 패턴이 있는 경우
6. **성능 테스트**: @memory_profiler 데코레이터를 활용한 메모리 사용량 검증
7. **ECS 패턴 테스트**: Component, System, Entity 간의 상호작용 검증

### Step 4: Modern Mock Setup with Type Safety
```python
from unittest.mock import Mock, patch, MagicMock
from typing import Protocol
import pytest
from pytest_mock import MockerFixture

class MockDependency(Protocol):
    def method(self, param: str) -> int: ...

@pytest.fixture
def mock_dependency() -> MockDependency:
    """의존성 모킹을 위한 픽스처"""
    mock = Mock(spec=MockDependency)
    mock.method.return_value = 42
    return mock

@pytest.fixture
def target_instance(mock_dependency: MockDependency) -> TargetClass:
    """테스트 대상 인스턴스 생성 픽스처"""
    return TargetClass(dependency=mock_dependency)
```

### Step 5: Advanced Assertion Patterns
Use descriptive Korean assertion messages with modern pytest features:

```python
import pytest
from pytest import approx
from collections.abc import Sequence

def test_assertion_examples():
    # 기본 검증
    assert actual == expected, f"기댓값 {expected}이어야 하나 실제값 {actual}임"
    
    # 타입 검증
    assert isinstance(result, ExpectedType), f"결과가 {ExpectedType} 타입이어야 함"
    
    # 컬렉션 검증
    assert len(result) == expected_length, f"결과 길이가 {expected_length}이어야 함"
    
    # 부동소수점 검증 (pygame Vector2 등)
    assert result.x == approx(expected_x, abs=1e-6), "X 좌표가 예상 값과 일치해야 함"
    
    # 예외 검증
    with pytest.raises(ValueError, match="구체적인 에러 메시지"):
        target_function(invalid_input)
```

## Advanced Python Testing Features

### Parametrized Testing for Multiple Scenarios
```python
@pytest.mark.parametrize("input_data,expected_output,test_description", [
    ("valid_input_1", "expected_1", "첫 번째 유효 입력 테스트"),
    ("valid_input_2", "expected_2", "두 번째 유효 입력 테스트"),
    ("edge_case", "edge_result", "경계값 처리 테스트"),
])
def test_multiple_scenarios(input_data: str, expected_output: str, test_description: str):
    """여러 시나리오를 한 번에 테스트"""
    # Given
    target = TargetClass()
    
    # When  
    result = target.process(input_data)
    
    # Then
    assert result == expected_output, f"{test_description} 실패: {result} != {expected_output}"
```

### Dataclass/Pydantic Model Testing
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class GameEntity:
    id: int
    position: tuple[float, float] 
    health: Optional[int] = None

def test_game_entity_creation():
    """GameEntity 생성 및 기본값 테스트"""
    # Given
    entity_id = 1
    position = (10.0, 20.0)
    
    # When
    entity = GameEntity(id=entity_id, position=position)
    
    # Then
    assert entity.id == entity_id, "엔티티 ID가 올바르게 설정되어야 함"
    assert entity.position == position, "위치가 올바르게 설정되어야 함"
    assert entity.health is None, "기본 체력값은 None이어야 함"
```

### ECS Pattern Testing
```python
class TestPlayerMovementSystem:
    """플레이어 이동 시스템 테스트"""
    
    @pytest.fixture
    def movement_system(self) -> PlayerMovementSystem:
        """이동 시스템 픽스처"""
        return PlayerMovementSystem()
    
    @pytest.fixture 
    def player_entity(self) -> Entity:
        """플레이어 엔티티 픽스처"""
        entity = Entity()
        entity.add_component(PositionComponent(x=0, y=0))
        entity.add_component(VelocityComponent(dx=0, dy=0))
        return entity
    
    def test_이동_시스템_속도_적용_성공(
        self, 
        movement_system: PlayerMovementSystem,
        player_entity: Entity
    ):
        """1. 플레이어 이동 시스템이 속도를 위치에 적용 (성공 시나리오)"""
        # Given - 초기 위치와 속도 설정
        position_comp = player_entity.get_component(PositionComponent)
        velocity_comp = player_entity.get_component(VelocityComponent)
        velocity_comp.dx = 5.0
        velocity_comp.dy = -3.0
        delta_time = 1.0
        
        # When - 이동 시스템 업데이트 실행
        movement_system.update([player_entity], delta_time)
        
        # Then - 위치가 속도만큼 변경되어야 함
        assert position_comp.x == approx(5.0), "X 위치가 속도만큼 증가해야 함"
        assert position_comp.y == approx(-3.0), "Y 위치가 속도만큼 변경되어야 함"
```

### Async Method Testing
```python
import asyncio
import pytest

@pytest.mark.asyncio
async def test_비동기_데이터_로드_성공():
    """1. 비동기 데이터 로딩이 성공적으로 완료 (성공 시나리오)"""
    # Given - 비동기 데이터 로더 준비
    loader = AsyncDataLoader()
    expected_data = {"player": {"level": 1, "exp": 0}}
    
    # When - 비동기 로딩 실행
    result = await loader.load_player_data("player_001")
    
    # Then - 올바른 데이터가 로딩되어야 함
    assert result is not None, "데이터가 성공적으로 로딩되어야 함"
    assert result["player"]["level"] == 1, "플레이어 레벨이 올바르게 로딩되어야 함"
```

### Performance Testing with Memory Profiler
```python
import pytest
from memory_profiler import profile

@pytest.mark.performance
def test_대량_엔티티_처리_성능():
    """성능 테스트: 1000개 엔티티 처리 시 메모리 사용량 검증"""
    # Given - 대량의 엔티티 생성
    entities = [Entity() for _ in range(1000)]
    system = CollisionSystem()
    
    # When - 시스템 처리 실행
    with pytest.warns(None) as warning_list:
        system.process_all(entities)
    
    # Then - 메모리 누수나 성능 저하 없이 처리되어야 함
    assert len(warning_list) == 0, "처리 중 경고가 발생하지 않아야 함"
```

### Property-Based Testing (Hypothesis 활용)
```python
from hypothesis import given, strategies as st
import pytest

@given(
    x=st.floats(min_value=-1000, max_value=1000),
    y=st.floats(min_value=-1000, max_value=1000)
)
def test_벡터_정규화_속성_기반_테스트(x: float, y: float):
    """속성 기반 테스트: 벡터 정규화 결과는 항상 단위벡터"""
    # Given - 임의의 벡터
    if x == 0 and y == 0:
        pytest.skip("영벡터는 정규화할 수 없음")
        
    vector = Vector2(x, y)
    
    # When - 벡터 정규화
    normalized = vector.normalize()
    
    # Then - 정규화된 벡터의 크기는 1이어야 함
    assert normalized.magnitude() == approx(1.0, abs=1e-6), "정규화된 벡터는 단위벡터여야 함"
```

## Integration with Modern Python Tools

### pytest Configuration (pytest.ini)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --verbose
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests  
    performance: Performance tests
    slow: Slow running tests
```

### Type Checking Integration
```python
from typing import Protocol, TypeVar, Generic
from mypy_extensions import TypedDict

T = TypeVar('T')

class ComponentProtocol(Protocol):
    """컴포넌트 인터페이스"""
    def update(self) -> None: ...

def test_타입_안전성_검증():
    """타입 힌트 준수 확인"""
    # Given - 타입이 지정된 객체
    component: ComponentProtocol = ConcreteComponent()
    
    # When & Then - 타입 검사기가 오류를 발생시키지 않아야 함
    component.update()  # mypy가 이를 검증함
```

## Project-Specific Guidelines

### AfterSchoolSurvivors ECS Testing Patterns
```python
class TestECSIntegration:
    """ECS 통합 테스트"""
    
    def test_컴포넌트_시스템_상호작용_검증(self):
        """1. 컴포넌트와 시스템 간 상호작용 정상 동작 (통합 시나리오)"""
        # Given - ECS 월드 및 엔티티 설정
        world = World()
        entity = world.create_entity()
        
        # 컴포넌트 추가
        position = PositionComponent(x=100, y=200)
        velocity = VelocityComponent(dx=10, dy=-5)
        entity.add_component(position)
        entity.add_component(velocity)
        
        # 시스템 등록
        movement_system = MovementSystem()
        world.add_system(movement_system)
        
        # When - 한 프레임 업데이트
        world.update(delta_time=1.0)
        
        # Then - 위치가 속도만큼 변경되어야 함
        updated_position = entity.get_component(PositionComponent)
        assert updated_position.x == approx(110.0), "X 위치가 업데이트되어야 함"
        assert updated_position.y == approx(195.0), "Y 위치가 업데이트되어야 함"
```

### pygame Integration Testing
```python
import pygame
from unittest.mock import patch

class TestPygameIntegration:
    """pygame 통합 테스트"""
    
    @pytest.fixture
    def pygame_surface(self):
        """pygame 서피스 픽스처"""
        pygame.init()
        surface = pygame.Surface((800, 600))
        yield surface
        pygame.quit()
    
    def test_스프라이트_렌더링_정상_동작(self, pygame_surface):
        """1. 스프라이트가 지정된 위치에 정상 렌더링 (성공 시나리오)"""
        # Given - 스프라이트와 위치 설정
        sprite = PlayerSprite()
        position = (100, 150)
        
        # When - 스프라이트 렌더링
        sprite.render(pygame_surface, position)
        
        # Then - 렌더링이 오류 없이 완료되어야 함
        # (실제 픽셀 검사는 통합 테스트에서만 수행)
        assert sprite.rect.center == position, "스프라이트 위치가 올바르게 설정되어야 함"
```

## Error Handling & Edge Cases

### Common Python Anti-Patterns to Avoid
```python
# ❌ WRONG - 예외 무시
try:
    risky_operation()
except:
    pass

# ✅ CORRECT - 구체적 예외 처리 테스트
def test_예외_상황_적절한_처리():
    """예외 상황에서 적절한 에러 메시지와 함께 실패해야 함"""
    with pytest.raises(ValueError, match="구체적인 에러 상황 설명"):
        target.method_that_should_fail(invalid_input)
```

### Resource Management Testing
```python
def test_리소스_정리_보장():
    """리소스가 예외 상황에서도 적절히 정리되는지 검증"""
    # Given - 리소스를 사용하는 객체
    resource_manager = ResourceManager()
    
    try:
        # When - 예외가 발생할 수 있는 작업
        with resource_manager.acquire_resource() as resource:
            # 의도적 예외 발생
            raise RuntimeError("테스트 예외")
    except RuntimeError:
        pass
    
    # Then - 리소스가 정리되었는지 확인
    assert resource_manager.is_resource_cleaned(), "예외 상황에서도 리소스가 정리되어야 함"
```

## Quality Assurance

### Pre-Generation Checks
- 타입 힌트가 올바르게 적용되었는지 확인 (`mypy` 검사)
- 모든 import가 올바른지 확인
- pytest 규칙을 따르는지 확인 (`ruff` 린팅)

### Post-Generation Validation
- 모든 생성된 테스트가 실행 가능한지 확인 (`pytest --collect-only`)
- 커버리지가 적절한지 확인 (`pytest --cov`)
- 성능 테스트가 합리적인 시간 내에 완료되는지 확인

### Coverage Analysis
```bash
# 커버리지 리포트 생성
pytest --cov=src --cov-report=html --cov-report=term-missing

# 특정 모듈 커버리지 확인
pytest --cov=src.systems --cov-report=term-missing tests/test_systems/
```

## Example Usage

### Input
```
/write-unit-test-for-py PlayerMovementSystem
```

### Generated Output Structure
```python
"""PlayerMovementSystem 테스트 모듈"""
import pytest
from unittest.mock import Mock, patch
from typing import Protocol
import numpy as np
from pytest import approx

from src.systems.player_movement_system import PlayerMovementSystem
from src.components.position_component import PositionComponent
from src.components.velocity_component import VelocityComponent
from src.core.entity import Entity

class TestPlayerMovementSystem:
    """플레이어 이동 시스템 테스트 클래스"""
    
    @pytest.fixture
    def movement_system(self) -> PlayerMovementSystem:
        """이동 시스템 인스턴스 픽스처"""
        return PlayerMovementSystem()
    
    @pytest.fixture
    def player_entity(self) -> Entity:
        """플레이어 엔티티 픽스처"""
        entity = Entity()
        entity.add_component(PositionComponent(x=0.0, y=0.0))
        entity.add_component(VelocityComponent(dx=0.0, dy=0.0))
        return entity
    
    def test_정상_속도로_이동_성공_시나리오(
        self, 
        movement_system: PlayerMovementSystem,
        player_entity: Entity
    ):
        """1. 정상적인 속도 값으로 플레이어 이동 처리 (성공 시나리오)"""
        # Generated test implementation with Given-When-Then pattern
        pass
    
    # Additional test methods...
```

## Troubleshooting

### Common Issues
1. **타입 힌트 오류**: `mypy` 실행하여 타입 검사
2. **비동기 테스트 실패**: `pytest-asyncio` 플러그인 확인
3. **Mock 설정 오류**: `spec` 매개변수로 인터페이스 강제
4. **성능 테스트 불안정**: `@pytest.mark.flaky` 데코레이터 활용

### Performance Considerations
- 대규모 클래스의 경우 테스트를 기능별로 분할
- 복잡한 의존성 그래프는 픽스처 스코프 조정 (`session`, `module`, `class`)
- 느린 테스트는 `@pytest.mark.slow`로 표시하여 CI에서 분리 실행

## Maintenance

### Tool Updatest
- `ruff` 설정 업데이트 시 린팅 규칙 재검토
- `pytest` 버전 업그레이드 시 플러그인 호환성 확인
- `mypy` 업데이트 시 타입 검사 규칙 재검토

### Best Practices Evolution
- Python 3.13+ 새 기능 활용 방안 검토
- ECS 패턴 발전에 따른 테스트 패턴 업데이트
- 게임 개발 특화 테스트 도구 도입 검토
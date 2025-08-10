# 단위 테스트 작성 규칙

## Meta-Principle
pytest 경고 없는 안정적인 테스트 코드 작성과 한국어 기반 ECS 게임 아키텍처 테스트 패턴 준수

## Constitutional Constraints
1. MUST: Helper/Mock 클래스는 `Test*` 접두사 사용 금지
2. MUST NOT: pytest가 수집할 수 있는 패턴으로 Helper 클래스 명명
3. IF-THEN: 테스트 Helper 클래스 작성 시 AI-DEV 주석으로 pytest 경고 방지 이유 명시

## Execution Procedure

### Step 1: 클래스 유형 판단
```python
def determine_class_type(class_purpose: str) -> str:
    if class_purpose == "test_class":
        return "Test*"  # 실제 테스트 클래스만 Test* 사용
    elif class_purpose in ["helper", "mock", "fake", "stub"]:
        return "Mock*"  # Helper 클래스는 Mock* 접두사 사용
    else:
        return "pytest 수집 대상 여부를 확인하세요"
```

### Step 2: 테스트 작성 패턴 적용
```python
def write_korean_test(test_name: str, scenario_type: str) -> str:
    return f"""def test_{test_name}_{scenario_type}_시나리오(self) -> None:
        \"\"\"N. {test_name} 검증 ({scenario_type} 시나리오)
        
        목적: 구체적인 테스트 목표
        테스트할 범위: 대상 메서드/기능
        커버하는 함수 및 데이터: 실제 호출 메서드
        기대되는 안정성: 보장되는 안정성
        \"\"\"
        # Given - 테스트 환경 설정
        
        # When - 테스트 실행
        
        # Then - 결과 검증
        assert result is not None, "한국어 검증 메시지\""""
```

### Step 3: AI-DEV 주석 추가
```python
def add_pytest_prevention_comment() -> str:
    return """# AI-DEV : pytest 컬렉션 경고 방지를 위한 Helper 클래스명 변경
# - 문제: Test*로 시작하는 Helper 클래스가 pytest에 의해 테스트 클래스로 수집됨
# - 해결책: Mock* 접두사로 Helper 클래스 명확화
# - 결과: PytestCollectionWarning 제거"""
```

## Few-Shot Examples

### Example 1: 올바른 Helper 클래스 작성
**Input**: 테스트용 Position 컴포넌트 Helper 클래스 필요
**Output**: 
```python
# AI-DEV : pytest 컬렉션 경고 방지를 위한 Helper 클래스명 변경
# - 문제: Test*로 시작하는 Helper 클래스가 pytest에 의해 테스트 클래스로 수집됨
# - 해결책: Mock* 접두사로 Helper 클래스 명확화
# - 결과: PytestCollectionWarning 제거
@dataclass
class MockPositionComponent(Component):
    """Mock position component for testing."""
    x: float = 0.0
    y: float = 0.0
```
**Reasoning**: Helper 클래스이므로 Mock* 접두사를 사용하고 AI-DEV 주석으로 이유 명시

### Example 2: 한국어 테스트 메서드 작성
**Input**: EntityManager의 엔티티 생성 기능 테스트
**Output**:
```python
def test_엔티티_생성_고유ID_할당_정상_동작_성공_시나리오(self) -> None:
    """1. 엔티티 생성 시 고유 ID 할당이 정상적으로 동작 (성공 시나리오)
    
    목적: EntityManager의 create_entity() 메서드가 고유 ID를 할당하는지 검증
    테스트할 범위: create_entity() 메서드와 entity.entity_id 속성
    커버하는 함수 및 데이터: Entity.create(), WeakValueDictionary 저장
    기대되는 안정성: 중복 없는 고유 ID 생성과 메모리 안전 관리 보장
    """
    # Given - 엔티티 매니저 초기화
    entity_manager = EntityManager()
    
    # When - 새로운 엔티티 생성
    created_entity = entity_manager.create_entity()
    
    # Then - 생성된 엔티티가 올바른 속성을 가져야 함
    assert created_entity.entity_id is not None, "생성된 엔티티는 고유 ID를 가져야 함"
    assert created_entity.active is True, "새로 생성된 엔티티는 활성 상태여야 함"
```
**Reasoning**: 한국어 테스트 명명법과 5단계 docstring을 사용한 ECS 패턴 테스트

## pytest 경고 방지 핵심 규칙

### 🚨 클래스 네이밍 패턴 (Critical)

**pytest가 테스트로 인식하는 패턴**:
- 클래스명: `Test*` 
- 함수명: `test_*`
- 파일명: `test_*.py` 또는 `*_test.py`

**Helper 클래스가 피해야 할 패턴**:
- `Test`로 시작하는 클래스명 + `__init__` 메서드
- pytest가 수집할 수 있는 위치의 테스트 패턴

### ✅ 권장 Helper 클래스 접두사

```python
# 올바른 Helper 클래스 명명
class MockPositionComponent(Component):     # ✅ Mock: 모의 객체
class FakeMovementSystem(System):           # ✅ Fake: 가짜 구현
class DummyHealthComponent(Component):      # ✅ Dummy: 더미 데이터
class StubRenderSystem(System):             # ✅ Stub: 스텁 구현
class TestDataBuilder:                      # ✅ Builder 패턴
class ComponentFactory:                     # ✅ Factory 패턴
```

### ❌ 피해야 할 패턴

```python
# 잘못된 예 - pytest가 테스트 클래스로 오인
class TestPositionComponent(Component):     # ❌ pytest 수집 대상
class TestMovementSystem(System):           # ❌ pytest 수집 대상
class TestDataHelper:                       # ❌ pytest 수집 대상
```

## 파일 구조 권장사항

### Helper 클래스 분리 패턴
```python
# tests/helpers/components.py - Helper 클래스들만 분리
@dataclass
class MockPositionComponent(Component):
    x: float = 0.0
    y: float = 0.0

@dataclass
class MockHealthComponent(Component):
    current: int = 100
    maximum: int = 100

# tests/test_entity_manager.py - 실제 테스트
from tests.helpers.components import MockPositionComponent

class TestEntityManager:  # 실제 테스트 클래스만 Test* 사용
    def test_엔티티_생성_성공_시나리오(self):
        pass
```

## 한국어 테스트 명명 규칙

### 메서드 명명 패턴
```python
def test_{대상기능}_{상황설명}_{예상결과}_{시나리오타입}_시나리오(self) -> None:
    pass

# 예시들
def test_엔티티_생성_고유ID_할당_성공_시나리오(self) -> None:
def test_컴포넌트_추가_중복_추가_실패_시나리오(self) -> None:
def test_시스템_업데이트_대량_엔티티_처리_성능_시나리오(self) -> None:
```

### Docstring 5단계 구조 (필수)
```python
def test_example_시나리오(self) -> None:
    """N. 테스트 시나리오 명 (성공/실패/성능 시나리오)
    
    목적: 구체적인 테스트 목표 설명
    테스트할 범위: 대상 메서드나 기능의 범위
    커버하는 함수 및 데이터: 실제로 호출되는 메서드와 검증할 데이터
    기대되는 안정성: 테스트 통과 시 보장되는 안정성
    [실패 조건]: 실패 시나리오인 경우만 추가
    """
```

## ECS 아키텍처 특화 테스트 패턴

### Entity 테스트 패턴
```python
def test_엔티티_생명주기_관리_정상_동작_성공_시나리오(self) -> None:
    """엔티티 생성부터 삭제까지 생명주기 관리 검증"""
    # Given - 엔티티 매니저 초기화
    manager = EntityManager()
    
    # When - 엔티티 생성 및 삭제
    entity = manager.create_entity()
    entity_id = entity.entity_id
    manager.destroy_entity(entity)
    
    # Then - 생명주기가 올바르게 관리되어야 함
    assert entity.active is False, "삭제된 엔티티는 비활성 상태여야 함"
    assert manager.get_entity(entity_id) is None, "삭제된 엔티티는 조회되지 않아야 함"
```

### Component 테스트 패턴
```python
def test_컴포넌트_데이터_무결성_검증_성공_시나리오(self) -> None:
    """컴포넌트 데이터의 타입 안전성과 무결성 검증"""
    # Given - 컴포넌트 데이터 준비
    component = MockHealthComponent(current=80, maximum=100)
    
    # When - 데이터 접근 및 수정
    component.current -= 20
    
    # Then - 데이터 무결성이 유지되어야 함
    assert component.current == 60, "체력 감소가 정확히 적용되어야 함"
    assert component.current <= component.maximum, "현재 체력은 최대 체력을 초과할 수 없음"
```

### System 테스트 패턴
```python
def test_시스템_엔티티_처리_순서_보장_성공_시나리오(self) -> None:
    """시스템이 엔티티들을 올바른 순서로 처리하는지 검증"""
    # Given - 시스템과 다중 엔티티 준비
    system = MockMovementSystem()
    entities = [create_test_entity() for _ in range(5)]
    
    # When - 시스템 업데이트 실행
    system.update(entities, delta_time=0.016)  # 60 FPS
    
    # Then - 모든 엔티티가 처리되어야 함
    assert system.processed_count == 5, "모든 엔티티가 처리되어야 함"
```

## 메모리 관리 및 성능 테스트

### 메모리 누수 방지 테스트
```python
def test_대량_엔티티_생성_삭제_메모리_누수_없음_성능_시나리오(self) -> None:
    """40+ FPS 유지를 위한 메모리 누수 방지 검증"""
    # Given - 메모리 사용량 측정 준비
    manager = EntityManager()
    initial_count = len(manager)
    
    # When - 1000개 엔티티 생성 후 즉시 삭제
    entities = [manager.create_entity() for _ in range(1000)]
    for entity in entities:
        manager.destroy_entity(entity)
    
    # Then - 메모리가 정상적으로 정리되어야 함
    assert len(manager) == initial_count, "모든 엔티티가 정리되어야 함"
```

## Validation Metrics
- **경고 제거율**: 100% (모든 pytest 경고 제거)
- **한국어 명명 준수율**: 95% 이상
- **AI-DEV 주석 적용률**: Helper 클래스 100%
- **ECS 패턴 준수율**: 게임 아키텍처 관련 테스트 90% 이상

## Anti-Pattern Detection

**자주하는 실수들**:
- Helper 클래스에 Test* 접두사 사용
- 영어 테스트 메서드명 사용  
- Docstring 5단계 구조 누락
- Given-When-Then 구조 무시
- 한국어 검증 메시지 누락

**개선 방안**:
- Helper 클래스 작성 전 "이것이 pytest 수집 대상인가?" 자문
- 테스트 메서드명에 한국어와 "_시나리오" 접미사 필수 사용
- 모든 테스트에 5단계 docstring 구조 적용
- AI-DEV 주석으로 기술적 결정 사항 명확히 기록

## 프로젝트별 추가 규칙 (AfterSchoolSurvivors)

### 게임 성능 고려 테스트
- 40+ FPS 목표를 고려한 성능 테스트 포함
- 메모리 사용량 측정이 필요한 대량 데이터 처리 테스트
- ECS 아키텍처의 Entity-Component-System 상호작용 검증

### 한국어 게임 컨텐츠 테스트
- 한국어 UI 텍스트 표시 관련 테스트
- 게임 아이템 및 무기의 한국어 명칭 검증
- 게임 상태 전환 메시지의 한국어 표시 확인
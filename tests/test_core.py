"""
Tests for core ECS classes: Entity, Component, and System.
"""

import pytest
from dataclasses import dataclass
from typing import Any
from pytest import approx

from src.core.entity import Entity
from src.core.component import Component
from src.core.system import System, ISystem


# Mock component implementations for testing (이름 충돌 방지)
@dataclass
class MockHealthComponent(Component):
    """테스트용 Health 컴포넌트"""
    current_hp: int
    max_hp: int = 100
    
    def validate(self) -> bool:
        """HP 유효성 검증"""
        return 0 <= self.current_hp <= self.max_hp


@dataclass
class MockPositionComponent(Component):
    """테스트용 Position 컴포넌트"""
    x: float
    y: float


# Mock system implementation for testing (이름 충돌 방지)
class MockMovementSystem(System):
    """테스트용 Movement 시스템"""
    
    def __init__(self) -> None:
        super().__init__(priority=1)
        self.update_call_count = 0
        self.processed_entities = []
    
    def update(self, entity_manager: Any, delta_time: float) -> None:
        """테스트용 업데이트 메서드"""
        self.update_call_count += 1
        self.processed_entities = entity_manager or []
    
    def get_required_components(self) -> list[type]:
        """필요한 컴포넌트 타입 반환"""
        return [MockHealthComponent]


class TestEntity:
    """Entity 클래스 테스트"""
    
    @pytest.fixture
    def entity_instance(self) -> Entity:
        """테스트용 Entity 인스턴스 픽스처"""
        return Entity.create()
    
    def test_엔티티_생성_고유ID_할당_성공(self) -> None:
        """1. 엔티티 생성 시 고유 ID가 할당됨 (성공 시나리오)
        
        목적: Entity.create() 메서드가 고유한 ID를 가진 엔티티를 생성하는지 검증
        테스트할 범위: Entity 생성 및 ID 할당 로직
        커버하는 함수 및 데이터: Entity.create(), entity_id 속성
        기대되는 안정성: 엔티티마다 고유 식별자 보장
        """
        # Given - 두 개의 엔티티 생성
        entity1 = Entity.create()
        entity2 = Entity.create()
        
        # When - ID 비교
        id1 = entity1.entity_id
        id2 = entity2.entity_id
        
        # Then - 각각 고유한 ID를 가져야 함
        assert id1 != id2, f"엔티티 ID가 중복됨: {id1}"
        assert len(id1) > 0, "엔티티 ID가 비어있음"
        assert entity1.active is True, "새로 생성된 엔티티는 활성 상태여야 함"
        assert entity2.active is True, "새로 생성된 엔티티는 활성 상태여야 함"
    
    def test_엔티티_생명주기_관리_성공(self, entity_instance: Entity) -> None:
        """2. 엔티티 생명주기 관리가 정상 동작 (성공 시나리오)
        
        목적: 엔티티의 활성화/비활성화/파괴 상태 변경이 올바르게 동작하는지 검증
        테스트할 범위: 엔티티 상태 변경 메서드들
        커버하는 함수 및 데이터: activate(), deactivate(), destroy(), active 속성
        기대되는 안정성: 엔티티 상태 변경 시 일관성 보장
        """
        # Given - 활성 상태의 엔티티
        assert entity_instance.active is True, "초기 상태는 활성이어야 함"
        
        # When - 비활성화
        entity_instance.deactivate()
        
        # Then - 비활성 상태로 변경되어야 함
        assert entity_instance.active is False, "비활성화 후 비활성 상태여야 함"
        
        # When - 재활성화
        entity_instance.activate()
        
        # Then - 활성 상태로 변경되어야 함
        assert entity_instance.active is True, "재활성화 후 활성 상태여야 함"
        
        # When - 파괴
        entity_instance.destroy()
        
        # Then - 비활성 상태가 되어야 함
        assert entity_instance.active is False, "파괴 후 비활성 상태여야 함"
    
    def test_엔티티_동등성_검사_ID_기반_성공(self) -> None:
        """3. 엔티티 동등성 검사가 ID 기반으로 동작 (성공 시나리오)
        
        목적: 엔티티 간 동등성 비교가 entity_id를 기준으로 올바르게 동작하는지 검증
        테스트할 범위: __eq__() 메서드와 동등성 비교 로직
        커버하는 함수 및 데이터: __eq__(), entity_id 속성 비교
        기대되는 안정성: 엔티티 식별 및 비교 연산 신뢰성 보장
        """
        # Given - 서로 다른 엔티티와 같은 ID를 가진 엔티티
        entity1 = Entity.create()
        entity2 = Entity.create()
        entity3 = Entity(entity_id=entity1.entity_id)
        
        # When & Then - 동등성 검사
        assert entity1 == entity3, f"같은 ID를 가진 엔티티는 동등해야 함: {entity1.entity_id}"
        assert entity1 != entity2, f"다른 ID를 가진 엔티티는 다르다고 판단되어야 함"
        assert entity1 != "not_an_entity", "엔티티가 아닌 객체와는 다르다고 판단되어야 함"
    
    def test_엔티티_해시_가능성_컬렉션_사용_성공(self) -> None:
        """4. 엔티티가 해시 가능하여 컬렉션에서 사용 가능 (성공 시나리오)
        
        목적: 엔티티가 set, dict의 키로 사용 가능한지 검증
        테스트할 범위: __hash__() 메서드와 해시 기능
        커버하는 함수 및 데이터: __hash__(), set/dict 컬렉션 연산
        기대되는 안정성: 엔티티를 컬렉션 자료구조에서 안전하게 사용 가능
        """
        # Given - 두 개의 서로 다른 엔티티
        entity1 = Entity.create()
        entity2 = Entity.create()
        
        # When - set에 추가 (중복 제거 확인)
        entity_set = {entity1, entity2, entity1}  # entity1 중복 추가
        
        # Then - 중복이 제거되어 2개만 남아야 함
        assert len(entity_set) == 2, f"set에서 중복 엔티티가 제거되어야 함: {len(entity_set)}"
        
        # When - dict의 키로 사용
        entity_dict = {entity1: "value1", entity2: "value2"}
        
        # Then - 키로 정상 접근 가능해야 함
        assert entity_dict[entity1] == "value1", "엔티티를 dict 키로 사용할 수 있어야 함"
        assert entity_dict[entity2] == "value2", "엔티티를 dict 키로 사용할 수 있어야 함"


class TestComponent:
    """Component 기본 클래스 테스트"""
    
    @pytest.fixture
    def health_component(self) -> MockHealthComponent:
        """테스트용 Health 컴포넌트 픽스처"""
        return MockHealthComponent(current_hp=80, max_hp=100)
    
    @pytest.fixture
    def position_component(self) -> MockPositionComponent:
        """테스트용 Position 컴포넌트 픽스처"""
        return MockPositionComponent(x=10.5, y=20.3)
    
    def test_컴포넌트_생성_dataclass_필드_성공(self, health_component: MockHealthComponent) -> None:
        """1. 컴포넌트가 dataclass 필드와 함께 올바르게 생성됨 (성공 시나리오)
        
        목적: Component를 상속한 dataclass가 올바른 필드 값으로 생성되는지 검증
        테스트할 범위: dataclass 생성자와 필드 할당
        커버하는 함수 및 데이터: __init__(), dataclass 필드들
        기대되는 안정성: 컴포넌트 초기화 시 데이터 일관성 보장
        """
        # Given - 컴포넌트 필드 값 확인
        expected_hp = 80
        expected_max_hp = 100
        
        # When & Then - 필드 값이 올바르게 설정되어야 함
        assert health_component.current_hp == expected_hp, f"현재 HP가 올바르게 설정되어야 함: {health_component.current_hp}"
        assert health_component.max_hp == expected_max_hp, f"최대 HP가 올바르게 설정되어야 함: {health_component.max_hp}"
    
    def test_컴포넌트_유효성_검증_성공(self, health_component: MockHealthComponent) -> None:
        """2. 컴포넌트 데이터 유효성 검증이 정상 동작 (성공 시나리오)
        
        목적: Component.validate() 메서드가 데이터 무결성을 올바르게 검증하는지 확인
        테스트할 범위: 컴포넌트별 커스텀 validate() 메서드
        커버하는 함수 및 데이터: validate() 메서드, 필드 값 검증 로직
        기대되는 안정성: 컴포넌트 데이터 무결성 보장
        """
        # Given - 유효한 HP 값을 가진 컴포넌트
        assert 0 <= health_component.current_hp <= health_component.max_hp, "테스트 전제 조건 확인"
        
        # When - 유효성 검증 실행
        is_valid = health_component.validate()
        
        # Then - 유효하다고 판단되어야 함
        assert is_valid is True, f"유효한 HP 값에 대해 True를 반환해야 함: current={health_component.current_hp}, max={health_component.max_hp}"
    
    def test_컴포넌트_유효성_검증_범위_초과_실패(self) -> None:
        """3. 컴포넌트 데이터 유효성 검증 - 범위 초과 시 실패 (실패 시나리오)
        
        목적: 유효하지 않은 데이터에 대해 validate()가 False를 반환하는지 검증
        테스트할 범위: 경계값 및 비정상 값 처리
        커버하는 함수 및 데이터: validate() 메서드의 에러 케이스 처리
        기대되는 안정성: 잘못된 데이터 감지 및 거부
        실패 조건: HP가 음수이거나 최대값 초과 시
        """
        # Given - 유효하지 않은 HP 값들
        invalid_cases = [
            MockHealthComponent(current_hp=-10, max_hp=100),  # 음수 HP
            MockHealthComponent(current_hp=150, max_hp=100),  # 최대값 초과
            MockHealthComponent(current_hp=50, max_hp=-1),    # 음수 최대값
        ]
        
        for invalid_component in invalid_cases:
            # When - 유효성 검증 실행
            is_valid = invalid_component.validate()
            
            # Then - 유효하지 않다고 판단되어야 함
            assert is_valid is False, f"유효하지 않은 HP 값에 대해 False를 반환해야 함: current={invalid_component.current_hp}, max={invalid_component.max_hp}"
    
    def test_컴포넌트_복사_독립성_성공(self, health_component: MockHealthComponent) -> None:
        """4. 컴포넌트 복사 시 독립적인 인스턴스 생성 (성공 시나리오)
        
        목적: Component.copy() 메서드가 독립적인 복사본을 생성하는지 검증
        테스트할 범위: 얕은 복사 동작과 객체 독립성
        커버하는 함수 및 데이터: copy() 메서드, dataclass 필드 복사
        기대되는 안정성: 컴포넌트 복사 시 원본과의 독립성 보장
        """
        # Given - 원본 컴포넌트 데이터
        original_hp = health_component.current_hp
        original_max_hp = health_component.max_hp
        
        # When - 컴포넌트 복사
        copied_component = health_component.copy()
        
        # Then - 독립적인 복사본이 생성되어야 함
        assert copied_component is not health_component, "복사본은 원본과 다른 객체여야 함"
        assert copied_component.current_hp == original_hp, f"복사본의 HP가 원본과 같아야 함: {copied_component.current_hp} != {original_hp}"
        assert copied_component.max_hp == original_max_hp, f"복사본의 최대 HP가 원본과 같아야 함: {copied_component.max_hp} != {original_max_hp}"
        
        # When - 복사본 수정
        copied_component.current_hp = 50
        
        # Then - 원본은 영향받지 않아야 함
        assert health_component.current_hp == original_hp, "원본 컴포넌트는 복사본 수정에 영향받지 않아야 함"
    
    def test_컴포넌트_직렬화_역직렬화_성공(self, position_component: MockPositionComponent) -> None:
        """5. 컴포넌트 데이터 직렬화 후 완전한 복원 (성공 시나리오)
        
        목적: Component.serialize()와 deserialize()가 데이터를 완전히 보존하는지 검증
        테스트할 범위: 컴포넌트 데이터 직렬화/역직렬화 로직
        커버하는 함수 및 데이터: serialize(), deserialize(), 모든 dataclass 필드
        기대되는 안정성: 데이터 저장/로딩 시 무결성 보장
        """
        # Given - 원본 컴포넌트 데이터
        original_x = position_component.x
        original_y = position_component.y
        
        # When - 직렬화 후 역직렬화
        serialized_data = position_component.serialize()
        restored_component = MockPositionComponent.deserialize(serialized_data)
        
        # Then - 데이터가 완전히 복원되어야 함
        assert isinstance(serialized_data, dict), "직렬화된 데이터는 dict 타입이어야 함"
        assert "x" in serialized_data, "직렬화된 데이터에 x 필드가 포함되어야 함"
        assert "y" in serialized_data, "직렬화된 데이터에 y 필드가 포함되어야 함"
        
        assert restored_component.x == approx(original_x), f"X 좌표가 정확히 복원되어야 함: {restored_component.x} != {original_x}"
        assert restored_component.y == approx(original_y), f"Y 좌표가 정확히 복원되어야 함: {restored_component.y} != {original_y}"
        
        # 타입 검증
        assert isinstance(restored_component, MockPositionComponent), "복원된 객체는 올바른 타입이어야 함"


class TestSystem:
    """System 기본 클래스 테스트"""
    
    @pytest.fixture
    def movement_system(self) -> MockMovementSystem:
        """테스트용 Movement 시스템 픽스처"""
        return MockMovementSystem()
    
    def test_시스템_생성_기본값_설정_성공(self, movement_system: MockMovementSystem) -> None:
        """1. 시스템 생성 시 기본값들이 올바르게 설정됨 (성공 시나리오)
        
        목적: System 클래스 생성 시 기본 속성들이 올바른 초기값을 가지는지 검증
        테스트할 범위: System.__init__() 메서드와 기본 속성 초기화
        커버하는 함수 및 데이터: __init__(), priority, enabled, initialized 속성
        기대되는 안정성: 시스템 초기화 시 일관된 기본 상태 보장
        """
        # Given & When - 시스템이 생성됨 (픽스처에서)
        
        # Then - 기본값들이 올바르게 설정되어야 함
        assert movement_system.priority == 1, f"기본 우선순위는 1이어야 함: {movement_system.priority}"
        assert movement_system.enabled is True, f"기본적으로 활성화되어야 함: {movement_system.enabled}"
        assert movement_system.initialized is False, f"초기화되지 않은 상태여야 함: {movement_system.initialized}"
        assert movement_system.update_call_count == 0, "업데이트 호출 횟수는 0이어야 함"
    
    @pytest.mark.parametrize("priority,enabled,expected_order", [
        (0, True, "최우선"),
        (5, True, "보통"), 
        (10, True, "후순위"),
        (1, False, "비활성화됨")
    ])
    def test_시스템_상태_관리_다양한_시나리오(
        self, 
        movement_system: MockMovementSystem,
        priority: int,
        enabled: bool,
        expected_order: str
    ) -> None:
        """2-5. 시스템 상태 관리가 다양한 시나리오에서 정상 동작 (다중 시나리오)
        
        목적: System의 우선순위 설정과 활성화/비활성화가 다양한 값에 대해 올바르게 동작하는지 검증
        테스트할 범위: set_priority(), enable(), disable() 메서드들
        커버하는 함수 및 데이터: 우선순위 설정, 활성화 상태 변경
        기대되는 안정성: 시스템 실행 순서와 활성화 제어 보장
        """
        # Given - 시스템 상태 설정
        movement_system.set_priority(priority)
        if enabled:
            movement_system.enable()
        else:
            movement_system.disable()
        
        # When - 상태 확인
        actual_priority = movement_system.priority
        actual_enabled = movement_system.enabled
        
        # Then - 설정된 값과 일치해야 함
        assert actual_priority == priority, f"우선순위가 올바르게 설정되어야 함: {actual_priority} != {priority}"
        assert actual_enabled == enabled, f"활성화 상태가 올바르게 설정되어야 함: {actual_enabled} != {enabled}"
        
        # 시나리오별 추가 검증
        if expected_order == "최우선":
            assert priority == 0, "최우선 시스템의 우선순위는 0이어야 함"
        elif expected_order == "비활성화됨":
            assert not enabled, "비활성화 시나리오에서는 enabled가 False여야 함"
    
    def test_시스템_초기화_상태_변경_성공(self, movement_system: MockMovementSystem) -> None:
        """6. 시스템 초기화 상태가 올바르게 관리됨 (성공 시나리오)
        
        목적: System.initialize() 메서드가 초기화 상태를 올바르게 변경하는지 검증
        테스트할 범위: initialize() 메서드와 initialized 속성 변경
        커버하는 함수 및 데이터: initialize(), initialized 속성
        기대되는 안정성: 시스템 초기화 상태 추적 신뢰성 보장
        """
        # Given - 초기화되지 않은 시스템
        assert movement_system.initialized is False, "초기 상태는 초기화되지 않은 상태여야 함"
        
        # When - 시스템 초기화
        movement_system.initialize()
        
        # Then - 초기화된 상태로 변경되어야 함
        assert movement_system.initialized is True, "initialize() 호출 후 초기화된 상태여야 함"
    
    def test_시스템_필수_컴포넌트_목록_반환_성공(self, movement_system: MockMovementSystem) -> None:
        """7. 시스템이 필요한 컴포넌트 목록을 올바르게 반환 (성공 시나리오)
        
        목적: System.get_required_components()가 시스템이 처리할 컴포넌트 타입을 반환하는지 검증
        테스트할 범위: get_required_components() 메서드
        커버하는 함수 및 데이터: get_required_components(), 컴포넌트 타입 목록
        기대되는 안정성: 시스템-컴포넌트 매칭 로직 신뢰성 보장
        """
        # Given & When - 필수 컴포넌트 목록 조회
        required_components = movement_system.get_required_components()
        
        # Then - 예상된 컴포넌트 타입들이 반환되어야 함
        assert isinstance(required_components, list), "필수 컴포넌트 목록은 리스트여야 함"
        assert MockHealthComponent in required_components, f"MockHealthComponent가 필수 컴포넌트에 포함되어야 함: {required_components}"
        assert len(required_components) > 0, "최소 하나의 필수 컴포넌트가 있어야 함"
    
    def test_시스템_업데이트_호출_횟수_추적_성공(self, movement_system: MockMovementSystem) -> None:
        """8. 시스템 업데이트 메서드가 정상 호출되고 추적됨 (성공 시나리오)
        
        목적: System.update() 메서드가 올바르게 호출되고 상태가 추적되는지 검증
        테스트할 범위: update() 메서드 호출과 상태 변화 추적
        커버하는 함수 및 데이터: update() 메서드, 업데이트 관련 상태 변수들
        기대되는 안정성: 시스템 업데이트 루프 신뢰성 보장
        """
        # Given - 업데이트되지 않은 시스템
        assert movement_system.update_call_count == 0, "초기 업데이트 호출 횟수는 0이어야 함"
        
        # When - 시스템 업데이트 실행 (60 FPS 간격)
        delta_time = 1.0 / 60
        test_entity_manager = ["mock_entity1", "mock_entity2"]
        movement_system.update(test_entity_manager, delta_time)
        
        # Then - 업데이트가 정상 실행되어야 함
        assert movement_system.update_call_count == 1, f"업데이트가 한 번 호출되어야 함: {movement_system.update_call_count}"
        assert movement_system.processed_entities == test_entity_manager, "전달된 엔티티 매니저가 처리되어야 함"
        
        # When - 추가 업데이트 실행
        movement_system.update(None, delta_time)
        
        # Then - 호출 횟수가 증가해야 함
        assert movement_system.update_call_count == 2, f"두 번째 업데이트 후 호출 횟수는 2여야 함: {movement_system.update_call_count}"


class TestECSIntegration:
    """ECS 컴포넌트 간 통합 테스트"""
    
    @pytest.fixture
    def ecs_setup(self) -> tuple[Entity, MockHealthComponent, MockMovementSystem]:
        """ECS 통합 테스트용 설정 픽스처"""
        entity = Entity.create()
        component = MockHealthComponent(current_hp=75, max_hp=100)
        system = MockMovementSystem()
        return entity, component, system
    
    def test_엔티티_컴포넌트_시스템_통합_동작_성공(
        self, 
        ecs_setup: tuple[Entity, MockHealthComponent, MockMovementSystem]
    ) -> None:
        """1. Entity-Component-System 통합 동작 검증 (통합 시나리오)
        
        목적: ECS 아키텍처의 기본 상호작용이 올바르게 동작하는지 검증
        테스트할 범위: 엔티티 생성 → 컴포넌트 연결 → 시스템 처리 전체 플로우
        커버하는 함수 및 데이터: Entity 생명주기, Component 데이터 관리, System 업데이트
        기대되는 안정성: ECS 패턴의 기본 동작 보장
        """
        # Given - ECS 요소들 준비
        entity, component, system = ecs_setup
        delta_time = 1.0 / 60  # 60 FPS
        
        # When - 시스템 초기화 및 업데이트 실행
        system.initialize()
        system.update(entity_manager=[entity], delta_time=delta_time)
        
        # Then - 모든 ECS 요소가 정상 동작해야 함
        assert system.initialized is True, "시스템이 초기화되어야 함"
        assert system.update_call_count == 1, "시스템 업데이트가 한 번 호출되어야 함"
        assert entity.active is True, "엔티티가 활성 상태를 유지해야 함"
        assert component.validate() is True, "컴포넌트 데이터가 유효해야 함"
        
        # 시스템이 엔티티를 처리했는지 확인
        assert len(system.processed_entities) == 1, "시스템이 하나의 엔티티를 처리해야 함"
        assert system.processed_entities[0] == entity, "시스템이 올바른 엔티티를 처리해야 함"
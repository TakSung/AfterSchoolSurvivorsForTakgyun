"""
Tests for ComponentRegistry class.

This module contains comprehensive tests for the ComponentRegistry class,
verifying component storage, retrieval, and management functionality.
"""

import pytest
from dataclasses import dataclass
from typing import Iterator
from src.core.entity import Entity
from src.core.component import Component
from src.core.component_registry import ComponentRegistry


# Test Components
@dataclass
class HealthComponent(Component):
    """Test health component."""
    max_health: int
    current_health: int
    
    def validate(self) -> bool:
        return self.current_health <= self.max_health and self.current_health >= 0


@dataclass
class PositionComponent(Component):
    """Test position component."""
    x: float
    y: float


@dataclass
class VelocityComponent(Component):
    """Test velocity component."""
    dx: float
    dy: float


@dataclass
class InvalidComponent(Component):
    """Test component that always fails validation."""
    value: int
    
    def validate(self) -> bool:
        return False


class TestComponentRegistry:
    """Test suite for ComponentRegistry."""
    
    @pytest.fixture
    def registry(self) -> ComponentRegistry:
        """Create a fresh component registry for each test."""
        return ComponentRegistry()
    
    @pytest.fixture
    def entity(self) -> Entity:
        """Create a test entity."""
        return Entity.create()
    
    @pytest.fixture
    def health_component(self) -> HealthComponent:
        """Create a test health component."""
        return HealthComponent(max_health=100, current_health=80)
    
    @pytest.fixture
    def position_component(self) -> PositionComponent:
        """Create a test position component."""
        return PositionComponent(x=10.0, y=20.0)
    
    def test_컴포넌트_추가_성공_시나리오(
        self, 
        registry: ComponentRegistry, 
        entity: Entity, 
        health_component: HealthComponent
    ) -> None:
        """1. 컴포넌트 추가 성공 시나리오
        
        목적: 유효한 컴포넌트를 엔티티에 추가하는 기본 기능 검증
        테스트할 범위: add_component 메서드의 정상 동작
        커버하는 함수 및 데이터: ComponentRegistry.add_component()
        기대되는 안정성: 컴포넌트가 올바르게 저장되고 조회 가능해야 함
        """
        # When - 컴포넌트 추가
        registry.add_component(entity, health_component)
        
        # Then - 컴포넌트가 올바르게 추가됨
        assert registry.has_component(entity, HealthComponent), "엔티티에 컴포넌트가 추가되어야 함"
        retrieved = registry.get_component(entity, HealthComponent)
        assert retrieved is health_component, "추가한 컴포넌트와 동일한 인스턴스가 반환되어야 함"
        assert entity in registry, "엔티티가 레지스트리에 등록되어야 함"
    
    def test_중복_컴포넌트_추가_실패_시나리오(
        self, 
        registry: ComponentRegistry, 
        entity: Entity, 
        health_component: HealthComponent
    ) -> None:
        """2. 중복 컴포넌트 추가 실패 시나리오
        
        목적: 같은 타입의 컴포넌트 중복 추가 시 예외 발생 검증
        테스트할 범위: add_component 메서드의 중복 방지 로직
        커버하는 함수 및 데이터: ComponentRegistry.add_component() 예외 처리
        기대되는 안정성: ValueError 예외가 발생해야 함
        """
        # Given - 컴포넌트가 이미 추가된 상태
        registry.add_component(entity, health_component)
        
        # When & Then - 같은 타입 컴포넌트 재추가 시 예외 발생
        duplicate_health = HealthComponent(max_health=50, current_health=30)
        with pytest.raises(ValueError, match="already has component"):
            registry.add_component(entity, duplicate_health)
    
    def test_비활성_엔티티_컴포넌트_추가_실패_시나리오(
        self, 
        registry: ComponentRegistry, 
        entity: Entity, 
        health_component: HealthComponent
    ) -> None:
        """3. 비활성 엔티티 컴포넌트 추가 실패 시나리오
        
        목적: 비활성화된 엔티티에 컴포넌트 추가 시 예외 발생 검증
        테스트할 범위: add_component 메서드의 엔티티 상태 검사
        커버하는 함수 및 데이터: Entity.active 상태와 ComponentRegistry 연동
        기대되는 안정성: 비활성 엔티티는 컴포넌트 추가 불가해야 함
        """
        # Given - 엔티티 비활성화
        entity.deactivate()
        
        # When & Then - 비활성 엔티티에 컴포넌트 추가 시 예외 발생
        with pytest.raises(ValueError, match="inactive entity"):
            registry.add_component(entity, health_component)
    
    def test_잘못된_컴포넌트_추가_실패_시나리오(
        self, 
        registry: ComponentRegistry, 
        entity: Entity
    ) -> None:
        """4. 잘못된 컴포넌트 추가 실패 시나리오
        
        목적: validate() 실패하는 컴포넌트 추가 시 예외 발생 검증
        테스트할 범위: add_component 메서드의 컴포넌트 유효성 검사
        커버하는 함수 및 데이터: Component.validate() 연동
        기대되는 안정성: 유효하지 않은 컴포넌트는 추가 불가해야 함
        """
        # Given - 유효성 검사 실패하는 컴포넌트
        invalid_component = InvalidComponent(value=42)
        
        # When & Then - 유효하지 않은 컴포넌트 추가 시 예외 발생
        with pytest.raises(ValueError, match="failed validation"):
            registry.add_component(entity, invalid_component)
    
    def test_컴포넌트_제거_성공_시나리오(
        self, 
        registry: ComponentRegistry, 
        entity: Entity, 
        health_component: HealthComponent
    ) -> None:
        """5. 컴포넌트 제거 성공 시나리오
        
        목적: 엔티티에서 컴포넌트를 정상적으로 제거하는 기능 검증
        테스트할 범위: remove_component 메서드의 정상 동작
        커버하는 함수 및 데이터: ComponentRegistry.remove_component()
        기대되는 안정성: 컴포넌트가 완전히 제거되고 인스턴스가 반환되어야 함
        """
        # Given - 컴포넌트가 추가된 상태
        registry.add_component(entity, health_component)
        
        # When - 컴포넌트 제거
        removed = registry.remove_component(entity, HealthComponent)
        
        # Then - 컴포넌트가 올바르게 제거됨
        assert removed is health_component, "제거된 컴포넌트 인스턴스가 반환되어야 함"
        assert not registry.has_component(entity, HealthComponent), "컴포넌트가 더 이상 존재하지 않아야 함"
        assert registry.get_component(entity, HealthComponent) is None, "컴포넌트 조회 시 None 반환되어야 함"
    
    def test_존재하지_않는_컴포넌트_제거_시나리오(
        self, 
        registry: ComponentRegistry, 
        entity: Entity
    ) -> None:
        """6. 존재하지 않는 컴포넌트 제거 시나리오
        
        목적: 존재하지 않는 컴포넌트 제거 시 None 반환 검증
        테스트할 범위: remove_component 메서드의 None 반환 로직
        커버하는 함수 및 데이터: ComponentRegistry.remove_component() 예외 처리
        기대되는 안정성: 존재하지 않는 컴포넌트 제거 시 None 반환되어야 함
        """
        # When - 존재하지 않는 컴포넌트 제거 시도
        removed = registry.remove_component(entity, HealthComponent)
        
        # Then - None 반환
        assert removed is None, "존재하지 않는 컴포넌트 제거 시 None 반환되어야 함"
    
    def test_컴포넌트_조회_기능_검증(
        self, 
        registry: ComponentRegistry, 
        entity: Entity, 
        health_component: HealthComponent,
        position_component: PositionComponent
    ) -> None:
        """7. 컴포넌트 조회 기능 검증
        
        목적: 다양한 컴포넌트 조회 메서드들의 정확성 검증
        테스트할 범위: get_component, has_component 메서드
        커버하는 함수 및 데이터: ComponentRegistry 조회 관련 메서드들
        기대되는 안정성: 정확한 컴포넌트 인스턴스와 상태 정보 반환
        """
        # Given - 여러 컴포넌트 추가
        registry.add_component(entity, health_component)
        registry.add_component(entity, position_component)
        
        # Then - 올바른 컴포넌트 조회
        assert registry.get_component(entity, HealthComponent) is health_component
        assert registry.get_component(entity, PositionComponent) is position_component
        assert registry.get_component(entity, VelocityComponent) is None
        
        assert registry.has_component(entity, HealthComponent), "헬스 컴포넌트 존재해야 함"
        assert registry.has_component(entity, PositionComponent), "위치 컴포넌트 존재해야 함"
        assert not registry.has_component(entity, VelocityComponent), "속도 컴포넌트는 존재하지 않아야 함"
    
    def test_엔티티별_모든_컴포넌트_조회_기능(
        self, 
        registry: ComponentRegistry, 
        entity: Entity, 
        health_component: HealthComponent,
        position_component: PositionComponent
    ) -> None:
        """8. 엔티티별 모든 컴포넌트 조회 기능
        
        목적: 특정 엔티티의 모든 컴포넌트를 한 번에 조회하는 기능 검증
        테스트할 범위: get_components_for_entity 메서드
        커버하는 함수 및 데이터: ComponentRegistry.get_components_for_entity()
        기대되는 안정성: 엔티티의 모든 컴포넌트가 올바르게 반환되어야 함
        """
        # Given - 여러 컴포넌트 추가
        registry.add_component(entity, health_component)
        registry.add_component(entity, position_component)
        
        # When - 모든 컴포넌트 조회
        components = registry.get_components_for_entity(entity)
        
        # Then - 모든 컴포넌트가 올바르게 반환됨
        assert len(components) == 2, "두 개의 컴포넌트가 반환되어야 함"
        assert components[HealthComponent] is health_component
        assert components[PositionComponent] is position_component
    
    def test_타입별_엔티티_조회_기능(
        self, 
        registry: ComponentRegistry
    ) -> None:
        """9. 타입별 엔티티 조회 기능
        
        목적: 특정 컴포넌트 타입을 가진 엔티티들을 조회하는 기능 검증
        테스트할 범위: get_entities_with_component 메서드
        커버하는 함수 및 데이터: ComponentRegistry.get_entities_with_component()
        기대되는 안정성: 해당 컴포넌트를 가진 엔티티들만 정확히 반환되어야 함
        """
        # Given - 여러 엔티티와 컴포넌트 설정
        entity1 = Entity.create()
        entity2 = Entity.create()
        entity3 = Entity.create()
        
        health1 = HealthComponent(max_health=100, current_health=80)
        health2 = HealthComponent(max_health=150, current_health=150)
        position1 = PositionComponent(x=1.0, y=2.0)
        
        registry.add_component(entity1, health1)
        registry.add_component(entity2, health2)
        registry.add_component(entity1, position1)
        
        # When - 헬스 컴포넌트를 가진 엔티티들 조회
        health_entities = list(registry.get_entities_with_component(HealthComponent))
        
        # Then - 올바른 엔티티들이 반환됨
        assert len(health_entities) == 2, "헬스 컴포넌트를 가진 엔티티는 2개여야 함"
        entities = [entity for entity, _ in health_entities]
        components = [comp for _, comp in health_entities]
        
        assert entity1 in entities and entity2 in entities
        assert health1 in components and health2 in components
        
        # 위치 컴포넌트 조회
        position_entities = list(registry.get_entities_with_component(PositionComponent))
        assert len(position_entities) == 1, "위치 컴포넌트를 가진 엔티티는 1개여야 함"
        assert position_entities[0][0] == entity1
    
    def test_다중_컴포넌트_타입_엔티티_조회_기능(
        self, 
        registry: ComponentRegistry
    ) -> None:
        """10. 다중 컴포넌트 타입 엔티티 조회 기능
        
        목적: 여러 컴포넌트 타입을 모두 가진 엔티티들을 조회하는 기능 검증
        테스트할 범위: get_entities_with_components 메서드
        커버하는 함수 및 데이터: ComponentRegistry.get_entities_with_components()
        기대되는 안정성: 모든 지정된 컴포넌트를 가진 엔티티만 반환되어야 함
        """
        # Given - 다양한 컴포넌트 조합을 가진 엔티티들
        entity1 = Entity.create()
        entity2 = Entity.create()
        entity3 = Entity.create()
        
        health1 = HealthComponent(max_health=100, current_health=80)
        health2 = HealthComponent(max_health=150, current_health=150)
        position1 = PositionComponent(x=1.0, y=2.0)
        position2 = PositionComponent(x=3.0, y=4.0)
        velocity1 = VelocityComponent(dx=5.0, dy=6.0)
        
        # entity1: health + position
        registry.add_component(entity1, health1)
        registry.add_component(entity1, position1)
        
        # entity2: health + position + velocity
        registry.add_component(entity2, health2)
        registry.add_component(entity2, position2)
        registry.add_component(entity2, velocity1)
        
        # entity3: only health
        registry.add_component(entity3, HealthComponent(max_health=50, current_health=25))
        
        # When - 헬스와 위치 컴포넌트를 모두 가진 엔티티 조회
        entities_with_both = list(registry.get_entities_with_components(HealthComponent, PositionComponent))
        
        # Then - 올바른 엔티티들만 반환됨
        assert len(entities_with_both) == 2, "헬스와 위치 컴포넌트를 모두 가진 엔티티는 2개여야 함"
        
        returned_entities = [entity for entity, _ in entities_with_both]
        assert entity1 in returned_entities and entity2 in returned_entities
        assert entity3 not in returned_entities
        
        # 각 엔티티의 컴포넌트 튜플 검증
        for entity, components in entities_with_both:
            assert len(components) == 2, "반환된 컴포넌트 튜플은 2개 요소를 가져야 함"
            assert isinstance(components[0], HealthComponent)
            assert isinstance(components[1], PositionComponent)
    
    def test_엔티티_모든_컴포넌트_제거_기능(
        self, 
        registry: ComponentRegistry, 
        entity: Entity
    ) -> None:
        """11. 엔티티 모든 컴포넌트 제거 기능
        
        목적: 특정 엔티티의 모든 컴포넌트를 한 번에 제거하는 기능 검증
        테스트할 범위: remove_entity_components 메서드
        커버하는 함수 및 데이터: ComponentRegistry.remove_entity_components()
        기대되는 안정성: 모든 컴포넌트가 제거되고 제거된 컴포넌트들이 반환되어야 함
        """
        # Given - 여러 컴포넌트 추가
        health = HealthComponent(max_health=100, current_health=80)
        position = PositionComponent(x=10.0, y=20.0)
        
        registry.add_component(entity, health)
        registry.add_component(entity, position)
        
        # When - 모든 컴포넌트 제거
        removed_components = registry.remove_entity_components(entity)
        
        # Then - 모든 컴포넌트가 제거되고 반환됨
        assert len(removed_components) == 2, "제거된 컴포넌트는 2개여야 함"
        assert removed_components[HealthComponent] is health
        assert removed_components[PositionComponent] is position
        
        assert not registry.has_component(entity, HealthComponent)
        assert not registry.has_component(entity, PositionComponent)
        assert registry.get_entity_component_count(entity) == 0
    
    def test_레지스트리_통계_및_상태_정보_기능(
        self, 
        registry: ComponentRegistry
    ) -> None:
        """12. 레지스트리 통계 및 상태 정보 기능
        
        목적: 레지스트리의 통계 정보와 상태를 조회하는 기능들 검증
        테스트할 범위: 각종 카운트 및 상태 조회 메서드들
        커버하는 함수 및 데이터: get_component_count, get_entity_component_count 등
        기대되는 안정성: 정확한 통계 정보가 반환되어야 함
        """
        # Given - 여러 엔티티와 컴포넌트 설정
        entity1 = Entity.create()
        entity2 = Entity.create()
        
        health1 = HealthComponent(max_health=100, current_health=80)
        health2 = HealthComponent(max_health=150, current_health=150)
        position1 = PositionComponent(x=1.0, y=2.0)
        
        registry.add_component(entity1, health1)
        registry.add_component(entity2, health2)
        registry.add_component(entity1, position1)
        
        # Then - 정확한 통계 정보 반환
        assert registry.get_component_count(HealthComponent) == 2, "헬스 컴포넌트는 2개여야 함"
        assert registry.get_component_count(PositionComponent) == 1, "위치 컴포넌트는 1개여야 함"
        assert registry.get_component_count(VelocityComponent) == 0, "속도 컴포넌트는 0개여야 함"
        
        assert registry.get_entity_component_count(entity1) == 2, "entity1은 2개 컴포넌트를 가져야 함"
        assert registry.get_entity_component_count(entity2) == 1, "entity2는 1개 컴포넌트를 가져야 함"
        
        assert len(registry) == 3, "전체 컴포넌트 개수는 3개여야 함"
        assert len(registry.get_all_component_types()) == 2, "컴포넌트 타입은 2개여야 함"
        
        assert entity1 in registry and entity2 in registry
    
    def test_레지스트리_일관성_검증_기능(
        self, 
        registry: ComponentRegistry, 
        entity: Entity
    ) -> None:
        """13. 레지스트리 일관성 검증 기능
        
        목적: 레지스트리 내부 데이터 구조의 일관성을 검증하는 기능 테스트
        테스트할 범위: validate_registry 메서드
        커버하는 함수 및 데이터: ComponentRegistry.validate_registry()
        기대되는 안정성: 정상 상태에서는 항상 True를 반환해야 함
        """
        # Given - 정상적인 컴포넌트 추가/제거 시나리오
        health = HealthComponent(max_health=100, current_health=80)
        position = PositionComponent(x=10.0, y=20.0)
        
        # 빈 레지스트리 상태에서 검증
        assert registry.validate_registry(), "빈 레지스트리는 일관성이 유지되어야 함"
        
        # 컴포넌트 추가 후 검증
        registry.add_component(entity, health)
        registry.add_component(entity, position)
        assert registry.validate_registry(), "컴포넌트 추가 후 일관성이 유지되어야 함"
        
        # 컴포넌트 제거 후 검증
        registry.remove_component(entity, HealthComponent)
        assert registry.validate_registry(), "컴포넌트 제거 후 일관성이 유지되어야 함"
        
        # 전체 클리어 후 검증
        registry.clear()
        assert registry.validate_registry(), "클리어 후 일관성이 유지되어야 함"
    
    def test_비활성_엔티티_조회_제외_기능(
        self, 
        registry: ComponentRegistry
    ) -> None:
        """14. 비활성 엔티티 조회 제외 기능
        
        목적: 비활성화된 엔티티는 조회 결과에서 제외되는지 검증
        테스트할 범위: get_entities_with_component 메서드의 active 필터링
        커버하는 함수 및 데이터: Entity.active 상태와 조회 메서드 연동
        기대되는 안정성: 비활성 엔티티는 조회 결과에 포함되지 않아야 함
        """
        # Given - 활성/비활성 엔티티들 설정
        active_entity = Entity.create()
        inactive_entity = Entity.create()
        
        health1 = HealthComponent(max_health=100, current_health=80)
        health2 = HealthComponent(max_health=150, current_health=150)
        
        registry.add_component(active_entity, health1)
        registry.add_component(inactive_entity, health2)
        
        # When - 하나의 엔티티를 비활성화
        inactive_entity.deactivate()
        
        # Then - 활성 엔티티만 조회됨
        health_entities = list(registry.get_entities_with_component(HealthComponent))
        assert len(health_entities) == 1, "활성 엔티티만 조회되어야 함"
        assert health_entities[0][0] == active_entity
        
        # 다중 컴포넌트 조회에서도 확인
        position = PositionComponent(x=1.0, y=2.0)
        registry.add_component(active_entity, position)
        
        multi_entities = list(registry.get_entities_with_components(HealthComponent, PositionComponent))
        assert len(multi_entities) == 1, "활성 엔티티만 다중 컴포넌트 조회되어야 함"
        assert multi_entities[0][0] == active_entity
    
    def test_레지스트리_클리어_기능(
        self, 
        registry: ComponentRegistry
    ) -> None:
        """15. 레지스트리 클리어 기능
        
        목적: 레지스트리의 모든 데이터를 초기화하는 기능 검증
        테스트할 범위: clear 메서드
        커버하는 함수 및 데이터: ComponentRegistry.clear()
        기대되는 안정성: 모든 컴포넌트와 엔티티 정보가 완전히 제거되어야 함
        """
        # Given - 여러 컴포넌트와 엔티티 설정
        entity1 = Entity.create()
        entity2 = Entity.create()
        
        registry.add_component(entity1, HealthComponent(max_health=100, current_health=80))
        registry.add_component(entity2, PositionComponent(x=1.0, y=2.0))
        
        # 초기 상태 확인
        assert len(registry) > 0
        assert len(registry.get_all_component_types()) > 0
        
        # When - 레지스트리 클리어
        registry.clear()
        
        # Then - 모든 데이터가 초기화됨
        assert len(registry) == 0, "전체 컴포넌트 수가 0이어야 함"
        assert len(registry.get_all_component_types()) == 0, "컴포넌트 타입 수가 0이어야 함"
        assert registry.get_component_count(HealthComponent) == 0
        assert registry.get_component_count(PositionComponent) == 0
        assert registry.get_entity_component_count(entity1) == 0
        assert registry.get_entity_component_count(entity2) == 0
        assert registry.validate_registry(), "클리어 후에도 일관성이 유지되어야 함"
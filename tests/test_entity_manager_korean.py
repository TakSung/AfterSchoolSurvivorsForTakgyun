"""
EntityManager 클래스의 한국어 테스트 케이스.

CLAUDE.md 가이드라인에 따라 한국어 테스트 명명법을 사용합니다:
- 테스트_기능_조건_결과_시나리오 형태
- 목적, 테스트 범위, 커버 함수, 기대 안정성을 포함한 독스트링
"""

from dataclasses import dataclass

import pytest

from src.core.component import Component
from src.core.entity import Entity
from src.core.entity_manager import EntityManager


# AI-DEV : pytest 컬렉션 경고 방지를 위한 Helper 클래스명 변경
# - 문제: Test*로 시작하는 Helper 클래스가 pytest에 의해 테스트 클래스로 수집됨
# - 해결책: Mock* 접두사로 Helper 클래스 명확화
# - 결과: 3개 PytestCollectionWarning 제거
@dataclass
class MockPositionComponent(Component):
    x: float
    y: float


@dataclass
class MockHealthComponent(Component):
    current: int
    maximum: int


@dataclass
class MockVelocityComponent(Component):
    dx: float
    dy: float


class TestEntityManager:
    """EntityManager 클래스의 한국어 테스트 스위트"""

    def test_엔티티_생성_고유ID_할당_정상_동작_성공_시나리오(self) -> None:
        """1. 엔티티 생성 시 고유 ID 할당과 정상 동작 검증 (성공 시나리오)

        목적: EntityManager의 create_entity() 메서드가 유효한 엔티티를 생성하는지 검증
        테스트할 범위: 엔티티 생성, ID 할당, 활성 상태 설정
        커버하는 함수 및 데이터: create_entity(), Entity.entity_id, Entity.active
        기대되는 안정성: 항상 유효하고 고유한 ID를 가진 엔티티 생성 보장
        """
        # Given - EntityManager 초기화
        manager = EntityManager()

        # When - 엔티티 생성
        entity = manager.create_entity()

        # Then - 엔티티가 유효하고 고유 ID를 가져야 함
        assert entity is not None, '생성된 엔티티는 None이 아니어야 함'
        assert entity.entity_id is not None, '엔티티 ID가 할당되어야 함'
        assert len(entity.entity_id) > 0, '엔티티 ID는 빈 문자열이 아니어야 함'
        assert entity.active is True, '새로 생성된 엔티티는 활성 상태여야 함'
        assert entity in manager, '생성된 엔티티가 매니저에 등록되어야 함'

    def test_다중_엔티티_생성_고유성_보장_중복없음_성공_시나리오(self) -> None:
        """2. 다중 엔티티 생성 시 고유성 보장 및 중복 없음 검증 (성공 시나리오)

        목적: 여러 엔티티 생성 시 각각 고유한 ID를 가지는지 검증
        테스트할 범위: 다중 엔티티 생성, ID 고유성, 컬렉션 관리
        커버하는 함수 및 데이터: create_entity() 반복 호출, entity_id 고유성
        기대되는 안정성: ID 충돌 없는 안전한 다중 엔티티 생성 보장
        """
        # Given - EntityManager 초기화
        manager = EntityManager()

        # When - 여러 엔티티 생성
        entities = [manager.create_entity() for _ in range(10)]

        # Then - 모든 엔티티가 고유한 ID를 가져야 함
        entity_ids = [entity.entity_id for entity in entities]
        assert len(set(entity_ids)) == len(entities), (
            '모든 엔티티 ID는 고유해야 함'
        )

        for entity in entities:
            assert entity.active is True, '모든 새 엔티티는 활성 상태여야 함'
            assert entity in manager, '모든 엔티티가 매니저에 등록되어야 함'

    def test_엔티티_삭제_완전제거_메모리정리_성공_시나리오(self) -> None:
        """3. 엔티티 삭제 시 완전 제거 및 메모리 정리 검증 (성공 시나리오)

        목적: destroy_entity() 메서드가 엔티티와 관련 데이터를 완전히 제거하는지 검증
        테스트할 범위: 엔티티 삭제, 컴포넌트 정리, 메모리 해제
        커버하는 함수 및 데이터: destroy_entity(), 내부 저장소 정리
        기대되는 안정성: 메모리 누수 없는 완전한 엔티티 삭제 보장
        """
        # Given - 엔티티와 컴포넌트 생성
        manager = EntityManager()
        entity = manager.create_entity()
        component = MockPositionComponent(x=10.0, y=20.0)
        manager.add_component(entity, component)
        entity_id = entity.entity_id

        # When - 엔티티 삭제
        manager.destroy_entity(entity)

        # Then - 엔티티와 관련 데이터가 완전히 제거되어야 함
        assert manager.get_entity(entity_id) is None, (
            '삭제된 엔티티는 조회되지 않아야 함'
        )
        assert entity not in manager, (
            '삭제된 엔티티는 매니저에 존재하지 않아야 함'
        )
        assert entity.active is False, '삭제된 엔티티는 비활성 상태여야 함'
        assert not manager.has_component(entity, MockPositionComponent), (
            '삭제된 엔티티의 컴포넌트도 제거되어야 함'
        )

    def test_존재하지않는_엔티티_삭제_안전처리_오류없음_성공_시나리오(
        self,
    ) -> None:
        """4. 존재하지 않는 엔티티 삭제 시 안전 처리 및 오류 없음 검증 (성공 시나리오)

        목적: 유효하지 않은 엔티티 삭제 시도 시 안전하게 처리되는지 검증
        테스트할 범위: 예외 처리, 방어적 프로그래밍, 안정성
        커버하는 함수 및 데이터: destroy_entity() 방어 로직
        기대되는 안정성: 잘못된 입력에도 시스템 안정성 보장
        """
        # Given - EntityManager 초기화
        manager = EntityManager()
        fake_entity = Entity.create()  # 매니저에 등록되지 않은 엔티티

        # When & Then - 존재하지 않는 엔티티 삭제는 예외 없이 안전하게 처리되어야 함
        try:
            manager.destroy_entity(fake_entity)
            # 예외가 발생하지 않으면 성공
        except Exception as e:
            pytest.fail(
                f'존재하지 않는 엔티티 삭제 시 예외가 발생하면 안 됨: {e}'
            )

    def test_엔티티_ID조회_정확한반환_존재하는경우_성공_시나리오(self) -> None:
        """5. 엔티티 ID 조회 시 정확한 반환 - 존재하는 경우 (성공 시나리오)

        목적: get_entity() 메서드가 유효한 ID로 올바른 엔티티를 반환하는지 검증
        테스트할 범위: 엔티티 조회, ID 기반 검색, 데이터 일관성
        커버하는 함수 및 데이터: get_entity(), 내부 엔티티 저장소
        기대되는 안정성: 정확한 엔티티 조회 및 데이터 무결성 보장
        """
        # Given - 엔티티 생성 및 등록
        manager = EntityManager()
        entity = manager.create_entity()
        entity_id = entity.entity_id

        # When - ID로 엔티티 조회
        found_entity = manager.get_entity(entity_id)

        # Then - 정확한 엔티티가 반환되어야 함
        assert found_entity is not None, (
            '존재하는 엔티티 ID로 조회 시 None이 아니어야 함'
        )
        assert found_entity is entity, (
            '조회된 엔티티는 원본과 동일한 객체여야 함'
        )
        assert found_entity.entity_id == entity_id, (
            '조회된 엔티티의 ID가 일치해야 함'
        )

    def test_존재하지않는_ID조회_None반환_안전처리_성공_시나리오(self) -> None:
        """6. 존재하지 않는 ID 조회 시 None 반환 및 안전 처리 (성공 시나리오)

        목적: get_entity() 메서드가 존재하지 않는 ID에 대해 None을 반환하는지 검증
        테스트할 범위: 예외 처리, 방어적 조회, 안전성
        커버하는 함수 및 데이터: get_entity() 방어 로직
        기대되는 안정성: 잘못된 ID 조회 시에도 안전한 처리 보장
        """
        # Given - EntityManager 초기화
        manager = EntityManager()

        # When - 존재하지 않는 ID로 조회
        found_entity = manager.get_entity('nonexistent-id')

        # Then - None이 반환되어야 함
        assert found_entity is None, (
            '존재하지 않는 ID 조회 시 None을 반환해야 함'
        )

    def test_모든_엔티티_조회_완전한목록_반환_성공_시나리오(self) -> None:
        """7. 모든 엔티티 조회 시 완전한 목록 반환 검증 (성공 시나리오)

        목적: get_all_entities() 메서드가 등록된 모든 엔티티를 반환하는지 검증
        테스트할 범위: 전체 엔티티 조회, 컬렉션 관리, 데이터 완정성
        커버하는 함수 및 데이터: get_all_entities(), 내부 엔티티 컬렉션
        기대되는 안정성: 누락 없는 완전한 엔티티 목록 제공 보장
        """
        # Given - 여러 엔티티 생성
        manager = EntityManager()
        entities = [manager.create_entity() for _ in range(5)]

        # When - 모든 엔티티 조회
        all_entities = manager.get_all_entities()

        # Then - 생성된 모든 엔티티가 포함되어야 함
        assert len(all_entities) == 5, (
            '생성된 엔티티 개수와 조회된 개수가 일치해야 함'
        )
        for entity in entities:
            assert entity in all_entities, (
                '생성된 모든 엔티티가 조회 결과에 포함되어야 함'
            )

    def test_활성_엔티티만_조회_비활성_제외_성공_시나리오(self) -> None:
        """8. 활성 엔티티만 조회하여 비활성 엔티티 제외 검증 (성공 시나리오)

        목적: get_active_entities() 메서드가 활성 엔티티만 필터링하여 반환하는지 검증
        테스트할 범위: 활성 상태 필터링, 조건부 조회, 상태 관리
        커버하는 함수 및 데이터: get_active_entities(), Entity.active 상태
        기대되는 안정성: 정확한 활성 상태 필터링 보장
        """
        # Given - 활성/비활성 엔티티 생성
        manager = EntityManager()
        active_entity = manager.create_entity()
        inactive_entity = manager.create_entity()
        manager.destroy_entity(inactive_entity)  # 비활성화

        # When - 활성 엔티티만 조회
        active_entities = manager.get_active_entities()

        # Then - 활성 엔티티만 포함되어야 함
        assert len(active_entities) == 1, '활성 엔티티만 조회되어야 함'
        assert active_entity in active_entities, (
            '활성 엔티티가 결과에 포함되어야 함'
        )
        assert inactive_entity not in active_entities, (
            '비활성 엔티티는 결과에서 제외되어야 함'
        )

    def test_컴포넌트_추가_정상_등록_검증_성공_시나리오(self) -> None:
        """9. 컴포넌트 추가 시 정상 등록 검증 (성공 시나리오)

        목적: add_component() 메서드가 엔티티에 컴포넌트를 올바르게 등록하는지 검증
        테스트할 범위: 컴포넌트 추가, 엔티티-컴포넌트 연결, 데이터 저장
        커버하는 함수 및 데이터: add_component(), has_component(), get_component()
        기대되는 안정성: 안전한 컴포넌트 등록 및 관리 보장
        """
        # Given - 엔티티와 컴포넌트 준비
        manager = EntityManager()
        entity = manager.create_entity()
        component = MockPositionComponent(x=100.0, y=200.0)

        # When - 컴포넌트 추가
        manager.add_component(entity, component)

        # Then - 컴포넌트가 올바르게 등록되어야 함
        assert manager.has_component(entity, MockPositionComponent), (
            '추가된 컴포넌트를 가지고 있어야 함'
        )
        stored_component = manager.get_component(entity, MockPositionComponent)
        assert stored_component is component, (
            '조회된 컴포넌트는 원본과 동일해야 함'
        )
        assert stored_component.x == 100.0, '컴포넌트 데이터가 보존되어야 함'
        assert stored_component.y == 200.0, '컴포넌트 데이터가 보존되어야 함'

    def test_존재하지않는_엔티티_컴포넌트추가_예외발생_실패_시나리오(
        self,
    ) -> None:
        """10. 존재하지 않는 엔티티에 컴포넌트 추가 시 예외 발생 검증 (실패 시나리오)

        목적: add_component() 메서드가 유효하지 않은 엔티티에 대해 예외를 발생시키는지 검증
        테스트할 범위: 입력 검증, 예외 처리, 방어적 프로그래밍
        커버하는 함수 및 데이터: add_component() 유효성 검사
        기대되는 안정성: 잘못된 입력에 대한 명확한 오류 처리 보장
        """
        # Given - EntityManager와 등록되지 않은 엔티티
        manager = EntityManager()
        fake_entity = Entity.create()  # 매니저에 등록되지 않은 엔티티
        component = MockPositionComponent(x=50.0, y=75.0)

        # When & Then - 존재하지 않는 엔티티에 컴포넌트 추가 시 ValueError 발생해야 함
        with pytest.raises(ValueError, match='does not exist'):
            manager.add_component(fake_entity, component)

    def test_컴포넌트_제거_정상_삭제_검증_성공_시나리오(self) -> None:
        """11. 컴포넌트 제거 시 정상 삭제 검증 (성공 시나리오)

        목적: remove_component() 메서드가 엔티티에서 컴포넌트를 올바르게 제거하는지 검증
        테스트할 범위: 컴포넌트 제거, 데이터 정리, 상태 업데이트
        커버하는 함수 및 데이터: remove_component(), has_component()
        기대되는 안정성: 완전한 컴포넌트 제거 및 데이터 정합성 보장
        """
        # Given - 엔티티와 컴포넌트 추가
        manager = EntityManager()
        entity = manager.create_entity()
        component = MockPositionComponent(x=30.0, y=40.0)
        manager.add_component(entity, component)

        # When - 컴포넌트 제거
        manager.remove_component(entity, MockPositionComponent)

        # Then - 컴포넌트가 완전히 제거되어야 함
        assert not manager.has_component(entity, MockPositionComponent), (
            '제거된 컴포넌트를 가지고 있으면 안 됨'
        )
        assert manager.get_component(entity, MockPositionComponent) is None, (
            '제거된 컴포넌트 조회 시 None 반환해야 함'
        )

    def test_특정_컴포넌트_보유_엔티티_조회_정확한필터링_성공_시나리오(
        self,
    ) -> None:
        """12. 특정 컴포넌트 보유 엔티티 조회 시 정확한 필터링 검증 (성공 시나리오)

        목적: get_entities_with_component() 메서드가 특정 컴포넌트를 가진 엔티티들을 정확히 필터링하는지 검증
        테스트할 범위: 조건부 엔티티 조회, 컴포넌트 기반 필터링, 쿼리 시스템
        커버하는 함수 및 데이터: get_entities_with_component(), 컴포넌트 인덱싱
        기대되는 안정성: 정확한 조건 기반 엔티티 검색 보장
        """
        # Given - 다양한 컴포넌트를 가진 엔티티들 생성
        manager = EntityManager()
        entity_with_position = manager.create_entity()
        entity_with_health = manager.create_entity()
        entity_with_both = manager.create_entity()

        manager.add_component(
            entity_with_position, MockPositionComponent(x=1.0, y=2.0)
        )
        manager.add_component(
            entity_with_health, MockHealthComponent(current=100, maximum=100)
        )
        manager.add_component(
            entity_with_both, MockPositionComponent(x=3.0, y=4.0)
        )
        manager.add_component(
            entity_with_both, MockHealthComponent(current=50, maximum=100)
        )

        # When - Position 컴포넌트를 가진 엔티티들 조회
        entities_with_position = manager.get_entities_with_component(
            MockPositionComponent
        )

        # Then - Position 컴포넌트를 가진 엔티티들만 반환되어야 함
        assert len(entities_with_position) == 2, (
            'Position 컴포넌트를 가진 엔티티는 2개여야 함'
        )
        assert entity_with_position in entities_with_position, (
            'Position만 가진 엔티티가 포함되어야 함'
        )
        assert entity_with_both in entities_with_position, (
            'Position도 가진 엔티티가 포함되어야 함'
        )
        assert entity_with_health not in entities_with_position, (
            'Position이 없는 엔티티는 제외되어야 함'
        )

    def test_다중_컴포넌트_조건_엔티티_조회_교집합필터링_성공_시나리오(
        self,
    ) -> None:
        """13. 다중 컴포넌트 조건 엔티티 조회 시 교집합 필터링 검증 (성공 시나리오)

        목적: get_entities_with_components() 메서드가 여러 컴포넌트를 모두 가진 엔티티만 반환하는지 검증
        테스트할 범위: 복합 조건 쿼리, 교집합 필터링, 고급 검색 기능
        커버하는 함수 및 데이터: get_entities_with_components(), 다중 컴포넌트 인덱싱
        기대되는 안정성: 복잡한 조건의 정확한 엔티티 검색 보장
        """
        # Given - 다양한 컴포넌트 조합을 가진 엔티티들 생성
        manager = EntityManager()
        entity_position_only = manager.create_entity()
        entity_health_only = manager.create_entity()
        entity_both = manager.create_entity()
        entity_all_three = manager.create_entity()

        manager.add_component(
            entity_position_only, MockPositionComponent(x=1.0, y=2.0)
        )
        manager.add_component(
            entity_health_only, MockHealthComponent(current=80, maximum=100)
        )

        manager.add_component(entity_both, MockPositionComponent(x=3.0, y=4.0))
        manager.add_component(
            entity_both, MockHealthComponent(current=60, maximum=100)
        )

        manager.add_component(
            entity_all_three, MockPositionComponent(x=5.0, y=6.0)
        )
        manager.add_component(
            entity_all_three, MockHealthComponent(current=40, maximum=100)
        )
        manager.add_component(
            entity_all_three, MockVelocityComponent(dx=1.5, dy=2.5)
        )

        # When - Position과 Health 컴포넌트를 모두 가진 엔티티들 조회
        entities_with_both = manager.get_entities_with_components(
            MockPositionComponent, MockHealthComponent
        )

        # Then - 두 컴포넌트를 모두 가진 엔티티들만 반환되어야 함
        assert len(entities_with_both) == 2, (
            '두 컴포넌트를 모두 가진 엔티티는 2개여야 함'
        )
        assert entity_both in entities_with_both, (
            '두 컴포넌트를 가진 엔티티가 포함되어야 함'
        )
        assert entity_all_three in entities_with_both, (
            '세 컴포넌트를 모두 가진 엔티티도 포함되어야 함'
        )
        assert entity_position_only not in entities_with_both, (
            'Position만 가진 엔티티는 제외되어야 함'
        )
        assert entity_health_only not in entities_with_both, (
            'Health만 가진 엔티티는 제외되어야 함'
        )

    def test_전체_데이터_초기화_완전한정리_성공_시나리오(self) -> None:
        """14. 전체 데이터 초기화 시 완전한 정리 검증 (성공 시나리오)

        목적: clear_all() 메서드가 모든 엔티티와 컴포넌트를 완전히 정리하는지 검증
        테스트할 범위: 대량 데이터 정리, 메모리 해제, 초기화 완정성
        커버하는 함수 및 데이터: clear_all(), 모든 내부 저장소
        기대되는 안정성: 완전한 데이터 초기화 및 메모리 누수 방지 보장
        """
        # Given - 다양한 엔티티와 컴포넌트들 생성
        manager = EntityManager()
        entities = []
        for i in range(5):
            entity = manager.create_entity()
            manager.add_component(
                entity, MockPositionComponent(x=float(i), y=float(i * 2))
            )
            manager.add_component(
                entity, MockHealthComponent(current=100 - i * 10, maximum=100)
            )
            entities.append(entity)

        # When - 전체 데이터 초기화
        manager.clear_all()

        # Then - 모든 데이터가 완전히 정리되어야 함
        assert len(manager) == 0, '모든 엔티티가 제거되어야 함'
        assert manager.get_entity_count() == 0, '엔티티 개수가 0이어야 함'
        assert manager.get_active_entity_count() == 0, (
            '활성 엔티티 개수가 0이어야 함'
        )
        assert len(manager.get_all_entities()) == 0, (
            '전체 엔티티 목록이 비어있어야 함'
        )
        assert len(manager.get_active_entities()) == 0, (
            '활성 엔티티 목록이 비어있어야 함'
        )

        for entity in entities:
            assert manager.get_entity(entity.entity_id) is None, (
                '모든 엔티티가 조회되지 않아야 함'
            )
            assert not manager.has_component(entity, MockPositionComponent), (
                '모든 컴포넌트가 제거되어야 함'
            )

    def test_대량_엔티티_생성_삭제_메모리_누수없음_성능_시나리오(self) -> None:
        """15. 대량 엔티티 생성/삭제 시 메모리 누수 없음 검증 (성능 시나리오)

        목적: 대량의 엔티티 생성과 삭제가 메모리 누수 없이 안전하게 처리되는지 검증
        테스트할 범위: 대량 데이터 처리, 메모리 관리, 성능 안정성
        커버하는 함수 및 데이터: 대량 create_entity(), destroy_entity() 반복
        기대되는 안정성: 고부하 상황에서도 안정적인 메모리 관리 보장
        """
        # Given - EntityManager 초기화
        manager = EntityManager()
        initial_count = len(manager)

        # When - 대량 엔티티 생성 및 삭제 반복
        for _ in range(1000):
            entities = [manager.create_entity() for _ in range(10)]

            for entity in entities:
                component = MockPositionComponent(x=1.0, y=1.0)
                manager.add_component(entity, component)

            for entity in entities:
                manager.destroy_entity(entity)

        # Then - 최종 상태가 초기 상태와 동일해야 함 (메모리 누수 없음)
        assert len(manager) == initial_count, (
            '대량 생성/삭제 후 엔티티 개수가 초기 상태로 복원되어야 함'
        )
        assert manager.get_entity_count() == initial_count, (
            '엔티티 카운트가 초기값과 일치해야 함'
        )
        assert manager.get_active_entity_count() == initial_count, (
            '활성 엔티티 카운트가 초기값과 일치해야 함'
        )

    def test_컴포넌트_개수_계산_정확한통계_성공_시나리오(self) -> None:
        """16. 컴포넌트 개수 계산 시 정확한 통계 정보 검증 (성공 시나리오)

        목적: get_component_count() 메서드가 특정 컴포넌트 타입의 정확한 개수를 반환하는지 검증
        테스트할 범위: 통계 정보 수집, 컴포넌트 개수 추적, 데이터 분석
        커버하는 함수 및 데이터: get_component_count(), 컴포넌트 통계
        기대되는 안정성: 정확한 컴포넌트 통계 정보 제공 보장
        """
        # Given - 다양한 컴포넌트를 가진 엔티티들 생성
        manager = EntityManager()

        # Position 컴포넌트 3개, Health 컴포넌트 2개 생성
        for i in range(3):
            entity = manager.create_entity()
            manager.add_component(
                entity, MockPositionComponent(x=float(i), y=float(i))
            )
            if i < 2:  # 처음 2개만 Health 컴포넌트 추가
                manager.add_component(
                    entity, MockHealthComponent(current=100, maximum=100)
                )

        # When - 각 컴포넌트 타입별 개수 조회
        position_count = manager.get_component_count(MockPositionComponent)
        health_count = manager.get_component_count(MockHealthComponent)
        velocity_count = manager.get_component_count(MockVelocityComponent)

        # Then - 정확한 개수가 반환되어야 함
        assert position_count == 3, 'Position 컴포넌트 개수는 3개여야 함'
        assert health_count == 2, 'Health 컴포넌트 개수는 2개여야 함'
        assert velocity_count == 0, 'Velocity 컴포넌트 개수는 0개여야 함'

    def test_반복자_프로토콜_모든엔티티_순회_성공_시나리오(self) -> None:
        """17. 반복자 프로토콜로 모든 엔티티 순회 검증 (성공 시나리오)

        목적: EntityManager가 Python의 반복자 프로토콜을 올바르게 구현하는지 검증
        테스트할 범위: 반복자 구현, Pythonic 인터페이스, 순회 기능
        커버하는 함수 및 데이터: __iter__(), __len__() 프로토콜 구현
        기대되는 안정성: 표준 Python 반복 패턴 지원 보장
        """
        # Given - 여러 엔티티 생성
        manager = EntityManager()
        created_entities = [manager.create_entity() for _ in range(4)]

        # When - 반복자를 사용하여 엔티티 순회
        iterated_entities = list(manager)

        # Then - 모든 엔티티가 순회되어야 함
        assert len(iterated_entities) == 4, (
            '순회된 엔티티 개수가 생성된 개수와 일치해야 함'
        )
        assert len(manager) == 4, 'len() 함수가 올바른 개수를 반환해야 함'

        for entity in created_entities:
            assert entity in iterated_entities, (
                '생성된 모든 엔티티가 순회 결과에 포함되어야 함'
            )

    def test_포함_연산자_엔티티_존재성_확인_성공_시나리오(self) -> None:
        """18. 포함 연산자로 엔티티 존재성 확인 검증 (성공 시나리오)

        목적: EntityManager가 Python의 'in' 연산자를 올바르게 지원하는지 검증
        테스트할 범위: 포함 연산자 구현, 멤버십 테스트, Pythonic 인터페이스
        커버하는 함수 및 데이터: __contains__() 프로토콜 구현
        기대되는 안정성: 직관적인 엔티티 존재 확인 기능 보장
        """
        # Given - 엔티티 생성 및 삭제
        manager = EntityManager()
        existing_entity = manager.create_entity()
        deleted_entity = manager.create_entity()
        manager.destroy_entity(deleted_entity)
        external_entity = Entity.create()  # 매니저에 등록되지 않은 엔티티

        # When & Then - 'in' 연산자로 존재성 확인
        assert existing_entity in manager, (
            '등록된 엔티티는 매니저에 포함되어야 함'
        )
        assert deleted_entity not in manager, (
            '삭제된 엔티티는 매니저에 포함되지 않아야 함'
        )
        assert external_entity not in manager, (
            '등록되지 않은 엔티티는 매니저에 포함되지 않아야 함'
        )

    def test_문자열_표현_정보_요약_표시_성공_시나리오(self) -> None:
        """19. 문자열 표현으로 정보 요약 표시 검증 (성공 시나리오)

        목적: EntityManager의 __str__()과 __repr__() 메서드가 유용한 정보를 제공하는지 검증
        테스트할 범위: 문자열 표현, 디버깅 지원, 개발자 경험
        커버하는 함수 및 데이터: __str__(), __repr__() 구현
        기대되는 안정성: 명확하고 유용한 디버깅 정보 제공 보장
        """
        # Given - 엔티티들과 컴포넌트 생성
        manager = EntityManager()
        active_entity = manager.create_entity()
        inactive_entity = manager.create_entity()
        manager.add_component(
            active_entity, MockPositionComponent(x=10.0, y=20.0)
        )
        manager.destroy_entity(inactive_entity)

        # When - 문자열 표현 생성
        str_repr = str(manager)
        detailed_repr = repr(manager)

        # Then - 의미 있는 정보가 포함되어야 함
        assert 'EntityManager' in str_repr, (
            '클래스 이름이 문자열 표현에 포함되어야 함'
        )
        assert 'active entities' in str_repr, (
            '활성 엔티티 정보가 포함되어야 함'
        )

        assert 'EntityManager' in detailed_repr, (
            '클래스 이름이 상세 표현에 포함되어야 함'
        )
        assert 'entities=' in detailed_repr, '엔티티 개수 정보가 포함되어야 함'
        assert 'active=' in detailed_repr, (
            '활성 엔티티 개수 정보가 포함되어야 함'
        )
        assert 'component_types=' in detailed_repr, (
            '컴포넌트 타입 개수 정보가 포함되어야 함'
        )

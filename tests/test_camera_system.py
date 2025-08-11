"""
Tests for CameraSystem class.

카메라 시스템의 업데이트 로직, 엔티티 추적, 마우스 추적,
좌표 변환기 연동 등 핵심 기능을 검증하는 테스트 모음입니다.
"""

from dataclasses import dataclass
from unittest.mock import Mock, patch

from src.components.camera_component import CameraComponent
from src.core.component import Component
from src.core.entity import Entity
from src.core.entity_manager import EntityManager
from src.systems.camera_system import CameraSystem


# Mock PositionComponent for testing (실제 구현 시 교체 필요)
@dataclass
class MockPositionComponent(Component):
    """테스트용 위치 컴포넌트"""

    x: float
    y: float


class TestCameraSystem:
    """CameraSystem에 대한 테스트 클래스"""

    def test_카메라_시스템_초기화_및_기본_설정_검증_성공_시나리오(
        self,
    ) -> None:
        """1. 카메라 시스템 초기화 및 기본 설정 검증 (성공 시나리오)

        목적: CameraSystem이 올바르게 초기화되고 기본 설정이 적용되는지 검증
        테스트할 범위: 시스템 초기화, 우선순위 설정, 컴포넌트 요구사항
        커버하는 함수 및 데이터: __init__, initialize, get_required_components
        기대되는 안정성: 안정적인 초기화 및 설정
        """
        # Given & When - 카메라 시스템 생성
        camera_system = CameraSystem(priority=5)

        # Then - 기본 설정 확인
        assert camera_system.priority == 5, '우선순위가 올바르게 설정되어야 함'
        assert camera_system.enabled is True, (
            '시스템이 기본적으로 활성화되어야 함'
        )
        assert camera_system.initialized is False, '초기화 전에는 False여야 함'

        # 필요한 컴포넌트 확인
        required_components = camera_system.get_required_components()
        assert CameraComponent in required_components, (
            'CameraComponent가 필수 컴포넌트여야 함'
        )

        # 초기화 실행
        camera_system.initialize()
        assert camera_system.initialized is True, '초기화 후에는 True여야 함'

    @patch('src.systems.camera_system.CoordinateManager.get_instance')
    def test_카메라_시스템_엔티티_필터링_검증_성공_시나리오(
        self, mock_coord_manager
    ) -> None:
        """2. 카메라 시스템 엔티티 필터링 검증 (성공 시나리오)

        목적: filter_entities 메서드가 CameraComponent를 가진 엔티티만 필터링하는지 검증
        테스트할 범위: 엔티티 필터링 로직
        커버하는 함수 및 데이터: filter_entities, update
        기대되는 안정성: 올바른 엔티티만 처리
        """
        # Given - Mock 설정
        mock_transformer = Mock()
        mock_coord_manager.return_value.get_transformer.return_value = (
            mock_transformer
        )

        # 카메라 시스템과 엔티티 매니저 생성
        camera_system = CameraSystem()
        camera_system.initialize()
        entity_manager = EntityManager()

        # 카메라 컴포넌트가 있는 엔티티와 없는 엔티티 생성
        camera_entity = entity_manager.create_entity()
        non_camera_entity = entity_manager.create_entity()

        camera_component = CameraComponent()
        entity_manager.add_component(camera_entity, camera_component)

        # When - 엔티티 필터링
        filtered_entities = camera_system.filter_entities(entity_manager)

        # Then - 카메라 엔티티만 필터링되는지 확인
        assert len(filtered_entities) == 1, (
            '카메라 컴포넌트가 있는 엔티티만 필터링되어야 함'
        )
        assert camera_entity in filtered_entities, (
            '카메라 엔티티가 포함되어야 함'
        )
        assert non_camera_entity not in filtered_entities, (
            '카메라 컴포넌트가 없는 엔티티는 제외되어야 함'
        )

    @patch('src.systems.camera_system.CoordinateManager.get_instance')
    def test_카메라_시스템_업데이트_비활성화_상태_검증_성공_시나리오(
        self, mock_coord_manager
    ) -> None:
        """3. 카메라 시스템 비활성화 상태에서 업데이트 무시 검증 (성공 시나리오)

        목적: 비활성화된 시스템이 업데이트를 수행하지 않는지 검증
        테스트할 범위: enabled 상태 확인, 업데이트 건너뛰기
        커버하는 함수 및 데이터: update, enabled property
        기대되는 안정성: 비활성화 시 안전한 업데이트 무시
        """
        # Given - Mock 설정 및 비활성화된 카메라 시스템
        mock_transformer = Mock()
        mock_coord_manager.return_value.get_transformer.return_value = (
            mock_transformer
        )

        camera_system = CameraSystem()
        camera_system.disable()  # 시스템 비활성화
        entity_manager = EntityManager()

        # When - 업데이트 호출
        camera_system.update(entity_manager, 0.016)

        # Then - 좌표 변환기가 호출되지 않았는지 확인
        mock_coord_manager.assert_called_once()  # 초기화 시 한 번만
        mock_transformer.invalidate_cache.assert_not_called()

    @patch('src.systems.camera_system.CoordinateManager.get_instance')
    def test_마우스_위치_설정_및_추적_기능_검증_성공_시나리오(
        self, mock_coord_manager
    ) -> None:
        """4. 마우스 위치 설정 및 추적 기능 검증 (성공 시나리오)

        목적: set_mouse_position과 마우스 추적 기능이 정상 작동하는지 검증
        테스트할 범위: 마우스 위치 설정, 내부 상태 관리
        커버하는 함수 및 데이터: set_mouse_position, _mouse_position
        기대되는 안정성: 마우스 위치 정보 정확한 저장
        """
        # Given - Mock 설정 및 카메라 시스템
        mock_coord_manager.return_value.get_transformer.return_value = Mock()
        camera_system = CameraSystem()

        # When - 마우스 위치 설정
        camera_system.set_mouse_position(250, 180)

        # Then - 내부 상태 확인
        assert camera_system._mouse_position == (250, 180), (
            '마우스 위치가 올바르게 저장되어야 함'
        )

        # 다른 위치로 업데이트
        camera_system.set_mouse_position(400, 300)
        assert camera_system._mouse_position == (400, 300), (
            '마우스 위치가 업데이트되어야 함'
        )

    @patch('src.systems.camera_system.CoordinateManager.get_instance')
    def test_카메라_오프셋_조회_기능_검증_성공_시나리오(
        self, mock_coord_manager
    ) -> None:
        """5. 카메라 오프셋 조회 기능 검증 (성공 시나리오)

        목적: get_camera_offset 메서드가 올바른 오프셋을 반환하는지 검증
        테스트할 범위: 오프셋 조회, None 반환 케이스
        커버하는 함수 및 데이터: get_camera_offset
        기대되는 안정성: 정확한 오프셋 정보 제공
        """
        # Given - Mock 설정 및 카메라 시스템
        mock_coord_manager.return_value.get_transformer.return_value = Mock()
        camera_system = CameraSystem()
        entity_manager = EntityManager()

        # 카메라 엔티티와 컴포넌트 생성
        camera_entity = entity_manager.create_entity()
        test_offset = (150.0, -75.0)
        camera_component = CameraComponent(world_offset=test_offset)

        entity_manager.add_component(camera_entity, camera_component)

        # When - 오프셋 조회
        offset = camera_system.get_camera_offset(entity_manager)

        # Then - 올바른 오프셋 반환 확인
        assert offset == test_offset, '현재 카메라 오프셋이 반환되어야 함'

        # 카메라 엔티티가 없는 경우 None 반환 확인
        entity_manager.destroy_entity(camera_entity)
        offset_none = camera_system.get_camera_offset(entity_manager)
        assert offset_none is None, '카메라 엔티티가 없으면 None을 반환해야 함'

    @patch('src.systems.camera_system.CoordinateManager.get_instance')
    def test_캐시_무효화_임계값_동작_검증_성공_시나리오(
        self, mock_coord_manager
    ) -> None:
        """6. 캐시 무효화 임계값 동작 검증 (성공 시나리오)

        목적: _should_invalidate_cache 메서드의 임계값 기반 동작 검증
        테스트할 범위: 임계값 비교, 캐시 무효화 결정
        커버하는 함수 및 데이터: _should_invalidate_cache
        기대되는 안정성: 성능 최적화를 위한 정확한 임계값 적용
        """
        # Given - Mock 설정 및 카메라 시스템
        mock_coord_manager.return_value.get_transformer.return_value = Mock()
        camera_system = CameraSystem()

        # When & Then - 임계값 이하 변화 (캐시 유지)
        small_change = camera_system._should_invalidate_cache(
            (100.0, 50.0), (100.5, 50.5)
        )
        assert not small_change, '임계값 이하 변화는 캐시 무효화하지 않아야 함'

        # 임계값 이상 변화 (캐시 무효화)
        large_change = camera_system._should_invalidate_cache(
            (100.0, 50.0), (102.0, 50.0)
        )
        assert large_change, '임계값 이상 변화는 캐시 무효화해야 함'

        # X축만 임계값 초과
        x_change = camera_system._should_invalidate_cache(
            (0.0, 0.0), (1.5, 0.0)
        )
        assert x_change, 'X축만 임계값 초과해도 캐시 무효화해야 함'

        # Y축만 임계값 초과
        y_change = camera_system._should_invalidate_cache(
            (0.0, 0.0), (0.0, -1.5)
        )
        assert y_change, 'Y축만 임계값 초과해도 캐시 무효화해야 함'

    @patch('src.systems.camera_system.CoordinateManager.get_instance')
    def test_데드존_내부_마우스_추적_무시_검증_성공_시나리오(
        self, mock_coord_manager
    ) -> None:
        """7. 데드존 내부 마우스 추적 무시 검증 (성공 시나리오)

        목적: 데드존 반지름 내의 마우스 이동이 무시되는지 검증
        테스트할 범위: _handle_mouse_tracking, 데드존 계산
        커버하는 함수 및 데이터: _handle_mouse_tracking with dead zone
        기대되는 안정성: 미세한 마우스 움직임으로 인한 카메라 떨림 방지
        """
        # Given - Mock 설정 및 카메라 시스템
        mock_transformer = Mock()
        mock_coord_manager.return_value.get_transformer.return_value = (
            mock_transformer
        )

        camera_system = CameraSystem()
        camera_system.initialize()
        entity_manager = EntityManager()

        # 카메라 엔티티 생성 (데드존 반지름 10.0)
        camera_entity = entity_manager.create_entity()
        camera_component = CameraComponent(
            screen_center=(400, 300),
            dead_zone_radius=10.0,
            world_offset=(0.0, 0.0),
        )
        entity_manager.add_component(camera_entity, camera_component)

        # 데드존 내부 마우스 위치 설정 (거리 < 10픽셀)
        camera_system.set_mouse_position(
            405, 305
        )  # 거리 = sqrt(25 + 25) ≈ 7.07 < 10

        initial_offset = camera_component.world_offset

        # When - 업데이트 실행
        camera_system.update(entity_manager, 0.016)

        # Then - 오프셋 변화 없음 확인
        assert camera_component.world_offset == initial_offset, (
            '데드존 내부 마우스 이동은 카메라에 영향주지 않아야 함'
        )
        mock_transformer.invalidate_cache.assert_not_called()

    @patch('src.systems.camera_system.CoordinateManager.get_instance')
    def test_데드존_외부_마우스_추적_동작_검증_성공_시나리오(
        self, mock_coord_manager
    ) -> None:
        """8. 데드존 외부 마우스 추적 동작 검증 (성공 시나리오)

        목적: 데드존 외부의 마우스 이동이 카메라에 영향을 주는지 검증
        테스트할 범위: _handle_mouse_tracking 활성화, 오프셋 변경
        커버하는 함수 및 데이터: _handle_mouse_tracking beyond dead zone
        기대되는 안정성: 의미있는 마우스 이동에 대한 적절한 카메라 반응
        """
        # Given - Mock 설정 및 카메라 시스템
        mock_transformer = Mock()
        mock_coord_manager.return_value.get_transformer.return_value = (
            mock_transformer
        )

        camera_system = CameraSystem()
        camera_system.initialize()
        entity_manager = EntityManager()

        # 카메라 엔티티 생성
        camera_entity = entity_manager.create_entity()
        camera_component = CameraComponent(
            screen_center=(400, 300),
            dead_zone_radius=10.0,
            world_offset=(0.0, 0.0),
        )
        entity_manager.add_component(camera_entity, camera_component)

        # 데드존 외부 마우스 위치 설정
        camera_system.set_mouse_position(430, 300)  # 거리 = 30 > 10

        initial_offset = camera_component.world_offset

        # When - 업데이트 실행 (충분한 delta_time으로)
        camera_system.update(entity_manager, 0.1)

        # Then - 오프셋 변화 확인
        assert camera_component.world_offset != initial_offset, (
            '데드존 외부 마우스 이동은 카메라에 영향줘야 함'
        )

    @patch('src.systems.camera_system.CoordinateManager.get_instance')
    def test_엔티티_위치_가져오기_임시_구현_검증_성공_시나리오(
        self, mock_coord_manager
    ) -> None:
        """9. 엔티티 위치 가져오기 임시 구현 검증 (성공 시나리오)

        목적: _get_entity_position 메서드의 임시 구현이 동작하는지 검증
        테스트할 범위: _get_entity_position, 임시 반환값
        커버하는 함수 및 데이터: _get_entity_position (temporary implementation)
        기대되는 안정성: 위치 컴포넌트 구현 전까지의 안정적 동작
        """
        # Given - Mock 설정 및 카메라 시스템
        mock_coord_manager.return_value.get_transformer.return_value = Mock()
        camera_system = CameraSystem()
        entity_manager = EntityManager()
        test_entity = Entity.create()

        # When - 엔티티 위치 조회
        position = camera_system._get_entity_position(
            entity_manager, test_entity
        )

        # Then - 임시 구현값 확인
        assert position == (0.0, 0.0), '임시 구현은 (0.0, 0.0)을 반환해야 함'
        assert isinstance(position[0], float), 'X 좌표는 float 타입이어야 함'
        assert isinstance(position[1], float), 'Y 좌표는 float 타입이어야 함'

    @patch('src.systems.camera_system.CoordinateManager.get_instance')
    def test_카메라_시스템_정리_기능_검증_성공_시나리오(
        self, mock_coord_manager
    ) -> None:
        """10. 카메라 시스템 정리 기능 검증 (성공 시나리오)

        목적: cleanup 메서드가 시스템 자원을 올바르게 정리하는지 검증
        테스트할 범위: cleanup, 내부 상태 초기화
        커버하는 함수 및 데이터: cleanup
        기대되는 안정성: 메모리 누수 방지 및 깨끗한 종료
        """
        # Given - Mock 설정 및 초기화된 카메라 시스템
        mock_coord_manager.return_value.get_transformer.return_value = Mock()
        camera_system = CameraSystem()
        camera_system.set_mouse_position(100, 200)  # 마우스 위치 설정

        # 초기 상태 확인
        assert camera_system._mouse_position == (100, 200), (
            '마우스 위치가 설정되어 있어야 함'
        )

        # When - 정리 실행
        camera_system.cleanup()

        # Then - 상태 초기화 확인
        assert camera_system._mouse_position is None, (
            '마우스 위치가 None으로 초기화되어야 함'
        )

    @patch('src.systems.camera_system.CoordinateManager.get_instance')
    def test_추적_대상_없는_카메라_업데이트_안전성_검증_성공_시나리오(
        self, mock_coord_manager
    ) -> None:
        """11. 추적 대상이 없는 카메라 업데이트 안전성 검증 (성공 시나리오)

        목적: follow_target이 None인 카메라가 안전하게 처리되는지 검증
        테스트할 범위: None 체크, 안전한 업데이트 건너뛰기
        커버하는 함수 및 데이터: update with None follow_target
        기대되는 안정성: None 상태에서도 오류 없는 안전한 동작
        """
        # Given - Mock 설정 및 카메라 시스템
        mock_transformer = Mock()
        mock_coord_manager.return_value.get_transformer.return_value = (
            mock_transformer
        )

        camera_system = CameraSystem()
        camera_system.initialize()
        entity_manager = EntityManager()

        # 추적 대상이 없는 카메라 엔티티 생성
        camera_entity = entity_manager.create_entity()
        camera_component = CameraComponent(follow_target=None)
        entity_manager.add_component(camera_entity, camera_component)

        initial_offset = camera_component.world_offset

        # When - 업데이트 실행
        camera_system.update(entity_manager, 0.016)

        # Then - 안전한 동작 확인 (오류 없이 완료되고 오프셋 유지)
        assert camera_component.world_offset == initial_offset, (
            '추적 대상이 없으면 오프셋이 변경되지 않아야 함'
        )

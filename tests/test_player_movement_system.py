"""
Tests for PlayerMovementSystem class.

플레이어 이동 시스템의 업데이트 로직, 마우스 추적, 회전 처리,
좌표 변환기 연동 등 핵심 기능을 검증하는 테스트 모음입니다.
"""

import math
from unittest.mock import Mock, patch

from src.components.player_component import PlayerComponent
from src.components.player_movement_component import PlayerMovementComponent
from src.components.position_component import PositionComponent
from src.components.rotation_component import RotationComponent
from src.core.entity_manager import EntityManager
from src.systems.player_movement_system import PlayerMovementSystem


class TestPlayerMovementSystem:
    """PlayerMovementSystem에 대한 테스트 클래스"""

    def test_플레이어_이동_시스템_초기화_및_기본_설정_검증_성공_시나리오(
        self,
    ) -> None:
        """1. 플레이어 이동 시스템 초기화 및 기본 설정 검증 (성공 시나리오)

        목적: PlayerMovementSystem이 올바르게 초기화되고 기본 설정이 적용되는지 검증
        테스트할 범위: 시스템 초기화, 우선순위 설정, 컴포넌트 요구사항
        커버하는 함수 및 데이터: __init__, initialize, get_required_components
        기대되는 안정성: 안정적인 초기화 및 설정
        """
        # Given & When - 플레이어 이동 시스템 생성
        movement_system = PlayerMovementSystem(priority=5)

        # Then - 기본 설정 확인
        assert movement_system.priority == 5, (
            '우선순위가 올바르게 설정되어야 함'
        )
        assert movement_system.enabled is True, (
            '시스템이 기본적으로 활성화되어야 함'
        )
        assert movement_system.initialized is False, (
            '초기화 전에는 False여야 함'
        )

        # 필요한 컴포넌트 확인
        required_components = movement_system.get_required_components()
        assert PlayerMovementComponent in required_components, (
            'PlayerMovementComponent가 필수 컴포넌트여야 함'
        )

        # 화면 크기 및 중앙값 확인
        assert movement_system._screen_width == 800, (
            '기본 화면 너비가 800이어야 함'
        )
        assert movement_system._screen_height == 600, (
            '기본 화면 높이가 600이어야 함'
        )
        assert movement_system.get_screen_center() == (400, 300), (
            '화면 중앙이 (400, 300)이어야 함'
        )

    @patch('src.systems.player_movement_system.CoordinateManager.get_instance')
    def test_플레이어_이동_시스템_엔티티_필터링_검증_성공_시나리오(
        self, mock_coord_manager
    ) -> None:
        """2. 플레이어 이동 시스템 엔티티 필터링 검증 (성공 시나리오)

        목적: filter_entities 메서드가 PlayerMovementComponent를 가진 엔티티만 필터링하는지 검증
        테스트할 범위: 엔티티 필터링 로직
        커버하는 함수 및 데이터: filter_entities
        기대되는 안정성: 올바른 엔티티만 처리
        """
        # Given - Mock 설정
        mock_coord_manager.return_value.get_transformer.return_value = Mock()

        # 플레이어 이동 시스템과 엔티티 매니저 생성
        movement_system = PlayerMovementSystem()
        entity_manager = EntityManager()

        # PlayerMovementComponent가 있는 엔티티와 없는 엔티티 생성
        player_entity = entity_manager.create_entity()
        non_player_entity = entity_manager.create_entity()

        movement_component = PlayerMovementComponent()
        position_component = PositionComponent(x=0.0, y=0.0)
        entity_manager.add_component(player_entity, movement_component)
        entity_manager.add_component(player_entity, position_component)

        # When - 엔티티 필터링
        filtered_entities = movement_system.filter_entities(entity_manager)

        # Then - 플레이어 엔티티만 필터링되는지 확인
        assert len(filtered_entities) == 1, (
            'PlayerMovementComponent가 있는 엔티티만 필터링되어야 함'
        )
        assert player_entity in filtered_entities, (
            '플레이어 엔티티가 포함되어야 함'
        )
        assert non_player_entity not in filtered_entities, (
            'PlayerMovementComponent가 없는 엔티티는 제외되어야 함'
        )

    @patch('src.systems.player_movement_system.CoordinateManager.get_instance')
    def test_플레이어_이동_시스템_비활성화_상태_검증_성공_시나리오(
        self, mock_coord_manager
    ) -> None:
        """3. 플레이어 이동 시스템 비활성화 상태에서 업데이트 무시 검증 (성공 시나리오)

        목적: 비활성화된 시스템이 업데이트를 수행하지 않는지 검증
        테스트할 범위: enabled 상태 확인, 업데이트 건너뛰기
        커버하는 함수 및 데이터: update, enabled property
        기대되는 안정성: 비활성화 시 안전한 업데이트 무시
        """
        # Given - Mock 설정 및 비활성화된 플레이어 이동 시스템
        mock_coord_manager.return_value.get_transformer.return_value = Mock()
        movement_system = PlayerMovementSystem()
        movement_system.disable()  # 시스템 비활성화
        entity_manager = EntityManager()

        # When - 업데이트 호출
        movement_system.set_entity_manager(entity_manager)
        movement_system.update(0.016)

        # Then - 마우스 위치가 None으로 유지되는지 확인 (업데이트 안됨)
        assert movement_system.get_mouse_position() is None, (
            '비활성화 상태에서는 마우스 위치가 업데이트되지 않아야 함'
        )

    @patch('pygame.mouse.get_pos')
    @patch('src.systems.player_movement_system.CoordinateManager.get_instance')
    def test_마우스_위치_업데이트_및_캐싱_기능_검증_성공_시나리오(
        self, mock_coord_manager, mock_mouse_pos
    ) -> None:
        """4. 마우스 위치 업데이트 및 캐싱 기능 검증 (성공 시나리오)

        목적: _update_mouse_position과 마우스 위치 캐싱이 정상 작동하는지 검증
        테스트할 범위: 마우스 위치 캐싱, pygame 연동
        커버하는 함수 및 데이터: _update_mouse_position, get_mouse_position
        기대되는 안정성: 마우스 위치 정보 정확한 저장
        """
        # Given - Mock 설정
        from src.utils.vector2 import Vector2
        mock_transformer = Mock()
        mock_transformer.world_to_screen.return_value = Vector2(400, 300)  # 화면 중앙
        mock_coord_manager.return_value.get_transformer.return_value = mock_transformer
        mock_mouse_pos.return_value = (250, 180)

        movement_system = PlayerMovementSystem()
        movement_system.initialize()
        entity_manager = EntityManager()

        # 마우스 위치 테스트를 위한 최소 플레이어 엔티티 생성
        player_entity = entity_manager.create_entity()
        player_comp = PlayerComponent()
        position_comp = PositionComponent(0.0, 0.0)
        movement_comp = PlayerMovementComponent(world_position=(0.0, 0.0))
        rotation_comp = RotationComponent()
        
        entity_manager.add_component(player_entity, player_comp)
        entity_manager.add_component(player_entity, position_comp)
        entity_manager.add_component(player_entity, movement_comp)
        entity_manager.add_component(player_entity, rotation_comp)

        # When - 업데이트 실행 (마우스 위치 업데이트 포함)
        movement_system.set_entity_manager(entity_manager)
        movement_system.update(0.016)

        # Then - 마우스 위치 캐싱 확인
        assert movement_system.get_mouse_position() == (250, 180), (
            '마우스 위치가 올바르게 캐싱되어야 함'
        )

        # 마우스 위치 변경 후 재확인
        mock_mouse_pos.return_value = (400, 300)
        movement_system.force_mouse_update()
        assert movement_system.get_mouse_position() == (400, 300), (
            '강제 업데이트가 정상 작동해야 함'
        )

    def test_화면_크기_설정_및_중앙값_재계산_검증_성공_시나리오(self) -> None:
        """5. 화면 크기 설정 및 중앙값 재계산 검증 (성공 시나리오)

        목적: set_screen_size 메서드가 화면 크기와 중앙값을 올바르게 업데이트하는지 검증
        테스트할 범위: 화면 크기 설정, 중앙값 계산
        커버하는 함수 및 데이터: set_screen_size, get_screen_center
        기대되는 안정성: 정확한 화면 크기 및 중앙값 계산
        """
        # Given - 기본 플레이어 이동 시스템
        movement_system = PlayerMovementSystem()

        # When - 새로운 화면 크기 설정
        movement_system.set_screen_size(1024, 768)

        # Then - 화면 크기 및 중앙값 확인
        assert movement_system._screen_width == 1024, (
            '화면 너비가 업데이트되어야 함'
        )
        assert movement_system._screen_height == 768, (
            '화면 높이가 업데이트되어야 함'
        )
        assert movement_system.get_screen_center() == (512, 384), (
            '화면 중앙이 올바르게 계산되어야 함'
        )

    def test_회전_부드러움_설정_기능_검증_성공_시나리오(self) -> None:
        """6. 회전 부드러움 설정 기능 검증 (성공 시나리오)

        목적: set_rotation_smoothing 메서드의 정상 동작 검증
        테스트할 범위: 회전 부드러움 값 설정, 범위 제한
        커버하는 함수 및 데이터: set_rotation_smoothing
        기대되는 안정성: 정확한 부드러움 값 설정
        """
        # Given - 플레이어 이동 시스템
        movement_system = PlayerMovementSystem()

        # When & Then - 다양한 부드러움 값 테스트
        movement_system.set_rotation_smoothing(0.5)
        assert movement_system._rotation_smoothing_factor == 0.5, (
            '0.5 값이 올바르게 설정되어야 함'
        )

        # 범위 초과 값 테스트 (상한)
        movement_system.set_rotation_smoothing(1.5)
        assert movement_system._rotation_smoothing_factor == 1.0, (
            '상한값 1.0으로 제한되어야 함'
        )

        # 범위 초과 값 테스트 (하한)
        movement_system.set_rotation_smoothing(-0.5)
        assert movement_system._rotation_smoothing_factor == 0.0, (
            '하한값 0.0으로 제한되어야 함'
        )

    @patch('pygame.mouse.get_pos')
    @patch('src.systems.player_movement_system.CoordinateManager.get_instance')
    def test_데드존_내부_이동_정지_처리_검증_성공_시나리오(
        self, mock_coord_manager, mock_mouse_pos
    ) -> None:
        """7. 데드존 내부 이동 정지 처리 검증 (성공 시나리오)

        목적: 데드존 반지름 내의 마우스 이동이 플레이어 이동에 영향주지 않는지 검증
        테스트할 범위: _is_in_dead_zone, 데드존 처리 로직
        커버하는 함수 및 데이터: _process_mouse_movement with dead zone
        기대되는 안정성: 미세한 마우스 움직임으로 인한 플레이어 떨림 방지
        """
        # Given - Mock 설정
        mock_coord_manager.return_value.get_transformer.return_value = Mock()
        mock_mouse_pos.return_value = (
            405,
            305,
        )  # 화면 중앙(400, 300)에서 7픽셀 거리

        movement_system = PlayerMovementSystem()
        movement_system.initialize()
        entity_manager = EntityManager()

        # 플레이어 엔티티 생성 (데드존 반지름 10.0)
        player_entity = entity_manager.create_entity()
        movement_component = PlayerMovementComponent(dead_zone_radius=10.0)
        entity_manager.add_component(player_entity, movement_component)

        initial_direction = movement_component.direction
        initial_position = movement_component.world_position

        # When - 업데이트 실행
        movement_system.set_entity_manager(entity_manager)
        movement_system.update(0.016)

        # Then - 이동 없음 확인
        assert movement_component.direction == initial_direction, (
            '데드존 내부에서는 방향이 변경되지 않아야 함'
        )
        assert movement_component.world_position == initial_position, (
            '데드존 내부에서는 위치가 변경되지 않아야 함'
        )

    @patch('pygame.mouse.get_pos')
    @patch('src.systems.player_movement_system.CoordinateManager.get_instance')
    def test_데드존_외부_마우스_추적_동작_검증_성공_시나리오(
        self, mock_coord_manager, mock_mouse_pos
    ) -> None:
        """8. 데드존 외부 마우스 추적 동작 검증 (성공 시나리오)

        목적: 데드존 외부의 마우스 이동이 플레이어 이동에 올바르게 적용되는지 검증
        테스트할 범위: _process_mouse_movement 활성화, 방향 및 위치 변경
        커버하는 함수 및 데이터: _process_mouse_movement beyond dead zone
        기대되는 안정성: 의미있는 마우스 이동에 대한 적절한 플레이어 반응
        """
        # Given - Mock 설정 (데드존 외부 마우스 위치)
        mock_coord_manager.return_value.get_transformer.return_value = Mock()
        mock_mouse_pos.return_value = (450, 300)  # 화면 중앙에서 50픽셀 거리

        movement_system = PlayerMovementSystem()
        movement_system.initialize()
        entity_manager = EntityManager()

        # 플레이어 엔티티 생성
        player_entity = entity_manager.create_entity()
        movement_component = PlayerMovementComponent(
            dead_zone_radius=10.0, speed=100.0
        )
        position_component = PositionComponent(x=0.0, y=0.0)
        entity_manager.add_component(player_entity, movement_component)
        entity_manager.add_component(player_entity, position_component)

        initial_position = movement_component.world_position

        # When - 업데이트 실행 (충분한 delta_time)
        movement_system.set_entity_manager(entity_manager)
        movement_system.update(0.1)

        # Then - 이동 확인
        assert movement_component.world_position != initial_position, (
            '데드존 외부에서는 위치가 변경되어야 함'
        )

        # 방향이 마우스 쪽으로 향하는지 확인 (우측 방향)
        assert movement_component.direction[0] > 0, (
            '마우스가 우측에 있으면 X방향이 양수여야 함'
        )

    @patch('pygame.mouse.get_pos')
    @patch('src.systems.player_movement_system.CoordinateManager.get_instance')
    def test_부드러운_회전_각속도_제한_검증_성공_시나리오(
        self, mock_coord_manager, mock_mouse_pos
    ) -> None:
        """9. 부드러운 회전 각속도 제한 검증 (성공 시나리오)

        목적: _apply_smooth_rotation이 각속도 제한을 올바르게 적용하는지 검증
        테스트할 범위: 각속도 제한, 부드러운 회전 보간
        커버하는 함수 및 데이터: _apply_smooth_rotation
        기대되는 안정성: 자연스러운 회전 동작
        """
        # Given - Mock 설정 (급격한 방향 전환)
        mock_coord_manager.return_value.get_transformer.return_value = Mock()
        mock_mouse_pos.return_value = (400, 200)  # 위쪽 방향

        movement_system = PlayerMovementSystem()
        movement_system.initialize()
        entity_manager = EntityManager()

        # 플레이어 엔티티 생성 (아래쪽을 향하도록 초기 설정)
        player_entity = entity_manager.create_entity()
        movement_component = PlayerMovementComponent(
            direction=(0.0, 1.0),  # 아래쪽 방향
            rotation_angle=math.pi / 2,  # 90도 (아래쪽)
            angular_velocity_limit=math.pi,  # 180도/초 제한
        )
        entity_manager.add_component(player_entity, movement_component)

        initial_angle = movement_component.rotation_angle

        # When - 짧은 시간으로 업데이트 (각속도 제한이 적용되어야 함)
        movement_system.set_entity_manager(entity_manager)
        movement_system.update(0.1)  # 0.1초

        # Then - 각속도 제한 확인
        angle_change = abs(movement_component.rotation_angle - initial_angle)
        max_allowed_change = (
            movement_component.angular_velocity_limit * 0.1
        )  # π/10 라디안

        # 부드러움 팩터가 적용되므로 실제 변화는 더 작아야 함
        assert angle_change <= max_allowed_change, (
            f'각속도 제한이 적용되어야 함: {angle_change} <= {max_allowed_change}'
        )

    @patch('src.systems.player_movement_system.CoordinateManager.get_instance')
    def test_플레이어_이동_시스템_정리_기능_검증_성공_시나리오(
        self, mock_coord_manager
    ) -> None:
        """10. 플레이어 이동 시스템 정리 기능 검증 (성공 시나리오)

        목적: cleanup 메서드가 시스템 자원을 올바르게 정리하는지 검증
        테스트할 범위: cleanup, 내부 상태 초기화
        커버하는 함수 및 데이터: cleanup
        기대되는 안정성: 메모리 누수 방지 및 깨끗한 종료
        """
        # Given - Mock 설정 및 초기화된 플레이어 이동 시스템
        mock_coord_manager.return_value.get_transformer.return_value = Mock()
        movement_system = PlayerMovementSystem()
        movement_system.initialize()

        # 캐시된 마우스 위치 설정
        movement_system._cached_mouse_pos = (100, 200)

        # 초기 상태 확인
        assert movement_system._cached_mouse_pos == (100, 200), (
            '마우스 위치가 캐시되어 있어야 함'
        )

        # When - 정리 실행
        movement_system.cleanup()

        # Then - 상태 초기화 확인
        assert movement_system._cached_mouse_pos is None, (
            '마우스 위치가 None으로 초기화되어야 함'
        )
        assert movement_system._mouse_pos_dirty is True, (
            '마우스 위치 더티 플래그가 True로 설정되어야 함'
        )

    @patch('pygame.mouse.get_pos')
    @patch('src.systems.player_movement_system.CoordinateManager.get_instance')
    def test_pygame_오류_상황_안전성_처리_검증_성공_시나리오(
        self, mock_coord_manager, mock_mouse_pos
    ) -> None:
        """11. pygame 오류 상황 안전성 처리 검증 (성공 시나리오)

        목적: pygame.error 발생 시 안전하게 처리되는지 검증
        테스트할 범위: pygame 예외 처리, 기본값 설정
        커버하는 함수 및 데이터: _update_mouse_position exception handling
        기대되는 안정성: pygame 오류 상황에서도 시스템 안정성 유지
        """
        # Given - Mock 설정 (pygame.error 발생)
        import pygame
        from src.utils.vector2 import Vector2

        mock_transformer = Mock()
        mock_transformer.world_to_screen.return_value = Vector2(400, 300)  # 화면 중앙
        mock_coord_manager.return_value.get_transformer.return_value = mock_transformer
        mock_mouse_pos.side_effect = pygame.error('pygame not initialized')

        movement_system = PlayerMovementSystem()
        movement_system.initialize()
        entity_manager = EntityManager()

        # pygame 오류 테스트를 위한 최소 플레이어 엔티티 생성
        player_entity = entity_manager.create_entity()
        player_comp = PlayerComponent()
        position_comp = PositionComponent(0.0, 0.0)
        movement_comp = PlayerMovementComponent(world_position=(0.0, 0.0))
        rotation_comp = RotationComponent()
        
        entity_manager.add_component(player_entity, player_comp)
        entity_manager.add_component(player_entity, position_comp)
        entity_manager.add_component(player_entity, movement_comp)
        entity_manager.add_component(player_entity, rotation_comp)

        # When - 업데이트 실행 (pygame 오류 발생)
        movement_system.set_entity_manager(entity_manager)
        movement_system.update(0.016)

        # Then - 기본값으로 안전하게 처리되는지 확인
        mouse_pos = movement_system.get_mouse_position()
        assert mouse_pos == (400, 300), (
            'pygame 오류 시 화면 중앙으로 설정되어야 함'
        )

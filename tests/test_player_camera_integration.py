"""
Integration tests for player movement and camera system.

This module tests the integration between PlayerMovementSystem and CameraSystem
to verify that the camera follows the player correctly and provides the
reverse map movement effect.
"""

import math
from unittest.mock import Mock, patch

from src.components.camera_component import CameraComponent
from src.components.player_component import PlayerComponent
from src.components.player_movement_component import PlayerMovementComponent
from src.components.position_component import PositionComponent
from src.core.entity_manager import EntityManager
from src.core.system_orchestrator import SystemOrchestrator
from src.systems.camera_system import CameraSystem
from src.systems.player_movement_system import PlayerMovementSystem


class TestPlayerCameraIntegration:
    """Integration tests for player movement and camera system."""

    @patch('src.systems.player_movement_system.pygame')
    @patch('src.systems.camera_system.CoordinateManager.get_instance')
    def test_플레이어_이동_시_카메라_역방향_추적_검증_성공_시나리오(
        self, mock_coord_manager, mock_pygame
    ) -> None:
        """1. 플레이어 이동 시 카메라 역방향 추적 검증 (성공 시나리오)

        목적: 플레이어가 이동할 때 카메라가 역방향으로 움직이는지 검증
        테스트할 범위: PlayerMovementSystem, CameraSystem 연동
        커버하는 함수 및 데이터: 시스템 간 연동, 카메라 오프셋 업데이트
        기대되는 안정성: 플레이어 중앙 고정 및 맵 역방향 이동
        """
        # Given - Mock 설정
        mock_pygame.get_init.return_value = True
        mock_pygame.mouse.get_pos.return_value = (450, 300)  # 우측 이동

        mock_transformer = Mock()
        mock_coord_manager.return_value.get_transformer.return_value = (
            mock_transformer
        )

        # 시스템 및 엔티티 매니저 설정
        entity_manager = EntityManager()
        system_orchestrator = SystemOrchestrator()

        player_movement_system = PlayerMovementSystem(priority=5)
        camera_system = CameraSystem(priority=10)

        player_movement_system.set_screen_size(800, 600)

        system_orchestrator.register_system(
            player_movement_system, 'player_movement'
        )
        system_orchestrator.register_system(camera_system, 'camera')

        # 플레이어 엔티티 생성
        player_entity = entity_manager.create_entity()

        player_comp = PlayerComponent()
        position_comp = PositionComponent(0.0, 0.0)
        movement_comp = PlayerMovementComponent(
            world_position=(0.0, 0.0), speed=100.0, dead_zone_radius=10.0
        )

        entity_manager.add_component(player_entity, player_comp)
        entity_manager.add_component(player_entity, position_comp)
        entity_manager.add_component(player_entity, movement_comp)

        # 카메라 엔티티 생성
        camera_entity = entity_manager.create_entity()
        camera_comp = CameraComponent(
            world_offset=(0.0, 0.0),
            screen_center=(400, 300),
            follow_target=player_entity,
        )
        entity_manager.add_component(camera_entity, camera_comp)

        # When - 시스템 업데이트 (0.1초)
        delta_time = 0.1
        system_orchestrator.update_systems(entity_manager, delta_time)

        # Then - 플레이어 월드 위치 변화 확인
        updated_world_pos = movement_comp.world_position
        assert updated_world_pos[0] > 0.0, '플레이어가 우측으로 이동해야 함'

        # 카메라 오프셋이 플레이어 이동의 역방향으로 설정되었는지 확인
        camera_offset = camera_comp.world_offset
        expected_offset_x = (
            400 - updated_world_pos[0]
        )  # 화면 중앙 - 플레이어 위치
        expected_offset_y = 300 - updated_world_pos[1]

        assert abs(camera_offset[0] - expected_offset_x) < 0.1, (
            f'카메라 X 오프셋 불일치: {camera_offset[0]} != {expected_offset_x}'
        )
        assert abs(camera_offset[1] - expected_offset_y) < 0.1, (
            f'카메라 Y 오프셋 불일치: {camera_offset[1]} != {expected_offset_y}'
        )

    @patch('src.systems.player_movement_system.pygame')
    @patch('src.systems.camera_system.CoordinateManager.get_instance')
    def test_마우스_방향_변경_시_플레이어_회전_및_카메라_추적_검증_성공_시나리오(
        self, mock_coord_manager, mock_pygame
    ) -> None:
        """2. 마우스 방향 변경 시 플레이어 회전 및 카메라 추적 검증 (성공 시나리오)

        목적: 마우스 방향 변경이 플레이어 회전과 카메라 추적에 반영되는지 검증
        테스트할 범위: 마우스 입력, 플레이어 회전, 카메라 연동
        커버하는 함수 및 데이터: 마우스 추적, 각도 계산, 카메라 오프셋
        기대되는 안정성: 마우스 위치에 따른 정확한 플레이어 방향 설정
        """
        # Given - Mock 설정 (하단 방향)
        mock_pygame.get_init.return_value = True
        mock_pygame.mouse.get_pos.return_value = (400, 450)  # 하단 이동

        mock_transformer = Mock()
        mock_coord_manager.return_value.get_transformer.return_value = (
            mock_transformer
        )

        # 시스템 설정
        entity_manager = EntityManager()
        system_orchestrator = SystemOrchestrator()

        player_movement_system = PlayerMovementSystem(priority=5)
        camera_system = CameraSystem(priority=10)

        player_movement_system.set_screen_size(800, 600)

        system_orchestrator.register_system(
            player_movement_system, 'player_movement'
        )
        system_orchestrator.register_system(camera_system, 'camera')

        # 엔티티 생성
        player_entity = entity_manager.create_entity()

        player_comp = PlayerComponent()
        position_comp = PositionComponent(0.0, 0.0)
        movement_comp = PlayerMovementComponent(
            world_position=(0.0, 0.0), speed=100.0, dead_zone_radius=10.0
        )

        entity_manager.add_component(player_entity, player_comp)
        entity_manager.add_component(player_entity, position_comp)
        entity_manager.add_component(player_entity, movement_comp)

        camera_entity = entity_manager.create_entity()
        camera_comp = CameraComponent(
            world_offset=(0.0, 0.0),
            screen_center=(400, 300),
            follow_target=player_entity,
        )
        entity_manager.add_component(camera_entity, camera_comp)

        # When - 충분한 시간 동안 시스템 업데이트하여 부드러운 회전 완료
        # AI-DEV : 부드러운 회전을 고려한 충분한 업데이트 시간 제공
        # - 문제: 각속도 제한으로 인해 한 번의 업데이트로 목표각 도달 불가
        # - 해결책: 여러 번 업데이트하여 회전이 완료될 시간 제공
        # - 주의사항: 각속도 2π rad/s, π/2 회전에 약 0.25초 필요
        for _ in range(5):  # 0.5초 시뮬레이션 (0.1초 × 5회)
            system_orchestrator.update_systems(entity_manager, 0.1)

        # Then - 플레이어 방향이 하단을 향하는지 확인
        direction = movement_comp.direction
        assert direction[1] > 0.0, '플레이어가 하단을 향해야 함'

        # 회전각이 하단 방향(π/2)에 가까운지 확인
        delta_x = 0  # 400 - 400 = 0 (X 방향)
        delta_y = 150  # 450 - 300 = 150 (Y 방향)

        # AI-DEV : X=0 특수 케이스 처리로 정확한 각도 계산
        # - 문제: math.atan2(150, 0)가 부정확한 결과 반환
        # - 해결책: X가 0에 가까운 경우 직접 π/2 또는 -π/2 반환
        # - 주의사항: 부동소수점 오차를 고려한 임계값 사용
        if abs(delta_x) < 0.001:  # X가 0에 가까운 경우
            expected_angle = math.pi / 2 if delta_y > 0 else -math.pi / 2
        else:
            expected_angle = math.atan2(delta_y, delta_x)

        actual_angle = movement_comp.rotation_angle
        angle_diff = abs(actual_angle - expected_angle)

        # 각도 차이는 2π를 고려한 최소값으로 계산
        if angle_diff > math.pi:
            angle_diff = 2 * math.pi - angle_diff

        assert angle_diff < 0.1, f'회전각 차이가 큼: {angle_diff}'

    @patch('src.systems.player_movement_system.pygame')
    @patch('src.systems.camera_system.CoordinateManager.get_instance')
    def test_데드존_내부_마우스_위치_시_플레이어_정지_검증_성공_시나리오(
        self, mock_coord_manager, mock_pygame
    ) -> None:
        """3. 데드존 내부 마우스 위치 시 플레이어 정지 검증 (성공 시나리오)

        목적: 마우스가 데드존 내부에 있을 때 플레이어가 정지하는지 검증
        테스트할 범위: 데드존 처리, 이동 정지, 카메라 오프셋 유지
        커버하는 함수 및 데이터: 데드존 계산, 이동 벡터, 카메라 상태
        기대되는 안정성: 데드존에서의 안정적인 정지 상태 유지
        """
        # Given - 데드존 내부 마우스 위치
        mock_pygame.get_init.return_value = True
        mock_pygame.mouse.get_pos.return_value = (
            405,
            305,
        )  # 중앙에서 5픽셀 이내

        mock_transformer = Mock()
        mock_coord_manager.return_value.get_transformer.return_value = (
            mock_transformer
        )

        # 시스템 설정
        entity_manager = EntityManager()
        system_orchestrator = SystemOrchestrator()

        player_movement_system = PlayerMovementSystem(priority=5)
        camera_system = CameraSystem(priority=10)

        player_movement_system.set_screen_size(800, 600)

        system_orchestrator.register_system(
            player_movement_system, 'player_movement'
        )
        system_orchestrator.register_system(camera_system, 'camera')

        # 엔티티 생성
        player_entity = entity_manager.create_entity()

        player_comp = PlayerComponent()
        position_comp = PositionComponent(0.0, 0.0)
        movement_comp = PlayerMovementComponent(
            world_position=(0.0, 0.0),
            speed=100.0,
            dead_zone_radius=20.0,  # 20픽셀 데드존
        )

        entity_manager.add_component(player_entity, player_comp)
        entity_manager.add_component(player_entity, position_comp)
        entity_manager.add_component(player_entity, movement_comp)

        camera_entity = entity_manager.create_entity()

        # AI-DEV : 초기 카메라 오프셋을 플레이어 위치 기준으로 설정
        # - 문제: (0,0) 초기화로 인해 첫 업데이트에서 큰 변화 발생
        # - 해결책: 화면 중앙에서 플레이어 위치를 뺀 값으로 초기화
        # - 주의사항: 테스트와 실제 게임 모두 올바른 초기화 패턴 적용
        initial_offset_x = (
            400 - movement_comp.world_position[0]
        )  # 400 - 0 = 400
        initial_offset_y = (
            300 - movement_comp.world_position[1]
        )  # 300 - 0 = 300

        camera_comp = CameraComponent(
            world_offset=(initial_offset_x, initial_offset_y),
            screen_center=(400, 300),
            follow_target=player_entity,
        )
        entity_manager.add_component(camera_entity, camera_comp)

        # 초기 위치 저장
        initial_world_pos = movement_comp.world_position
        initial_camera_offset = camera_comp.world_offset

        # When - 시스템 업데이트
        delta_time = 0.1
        system_orchestrator.update_systems(entity_manager, delta_time)

        # Then - 플레이어 위치가 변경되지 않았는지 확인
        final_world_pos = movement_comp.world_position
        assert abs(final_world_pos[0] - initial_world_pos[0]) < 0.001, (
            '데드존 내부에서는 X 위치가 변경되지 않아야 함'
        )
        assert abs(final_world_pos[1] - initial_world_pos[1]) < 0.001, (
            '데드존 내부에서는 Y 위치가 변경되지 않아야 함'
        )

        # 카메라 오프셋도 변경되지 않았는지 확인
        final_camera_offset = camera_comp.world_offset
        assert (
            abs(final_camera_offset[0] - initial_camera_offset[0]) < 0.001
        ), '데드존 내부에서는 카메라 X 오프셋이 변경되지 않아야 함'
        assert (
            abs(final_camera_offset[1] - initial_camera_offset[1]) < 0.001
        ), '데드존 내부에서는 카메라 Y 오프셋이 변경되지 않아야 함'

    @patch('src.systems.player_movement_system.pygame')
    @patch('src.systems.camera_system.CoordinateManager.get_instance')
    def test_다중_업데이트_시_연속적인_플레이어_이동_및_카메라_추적_검증_성공_시나리오(
        self, mock_coord_manager, mock_pygame
    ) -> None:
        """4. 다중 업데이트 시 연속적인 플레이어 이동 및 카메라 추적 검증 (성공 시나리오)

        목적: 여러 프레임에 걸친 플레이어 이동과 카메라 추적이 일관되는지 검증
        테스트할 범위: 연속 업데이트, 누적 이동, 카메라 동기화
        커버하는 함수 및 데이터: 시간 기반 이동, 위치 누적, 오프셋 동기화
        기대되는 안정성: 다중 프레임에서의 안정적인 추적 동작
        """
        # Given - 일정한 마우스 위치
        mock_pygame.get_init.return_value = True
        mock_pygame.mouse.get_pos.return_value = (500, 300)  # 우측 방향

        mock_transformer = Mock()
        mock_coord_manager.return_value.get_transformer.return_value = (
            mock_transformer
        )

        # 시스템 설정
        entity_manager = EntityManager()
        system_orchestrator = SystemOrchestrator()

        player_movement_system = PlayerMovementSystem(priority=5)
        camera_system = CameraSystem(priority=10)

        player_movement_system.set_screen_size(800, 600)

        system_orchestrator.register_system(
            player_movement_system, 'player_movement'
        )
        system_orchestrator.register_system(camera_system, 'camera')

        # 엔티티 생성
        player_entity = entity_manager.create_entity()

        player_comp = PlayerComponent()
        position_comp = PositionComponent(0.0, 0.0)
        movement_comp = PlayerMovementComponent(
            world_position=(0.0, 0.0), speed=100.0, dead_zone_radius=10.0
        )

        entity_manager.add_component(player_entity, player_comp)
        entity_manager.add_component(player_entity, position_comp)
        entity_manager.add_component(player_entity, movement_comp)

        camera_entity = entity_manager.create_entity()
        camera_comp = CameraComponent(
            world_offset=(0.0, 0.0),
            screen_center=(400, 300),
            follow_target=player_entity,
        )
        entity_manager.add_component(camera_entity, camera_comp)

        # When - 여러 프레임 업데이트 (총 0.5초)
        delta_time = 0.1
        for _ in range(5):
            system_orchestrator.update_systems(entity_manager, delta_time)

        # Then - 플레이어가 누적적으로 이동했는지 확인
        final_world_pos = movement_comp.world_position
        expected_distance = 100.0 * 0.5  # 속도 * 시간
        actual_distance = math.sqrt(
            final_world_pos[0] ** 2 + final_world_pos[1] ** 2
        )

        assert abs(actual_distance - expected_distance) < 5.0, (
            f'누적 이동 거리 차이: {actual_distance} vs {expected_distance}'
        )

        # 카메라가 플레이어를 정확히 추적하고 있는지 확인
        camera_offset = camera_comp.world_offset
        expected_offset_x = 400 - final_world_pos[0]
        expected_offset_y = 300 - final_world_pos[1]

        assert abs(camera_offset[0] - expected_offset_x) < 0.1, (
            '카메라 X 오프셋이 플레이어 추적에 실패함'
        )
        assert abs(camera_offset[1] - expected_offset_y) < 0.1, (
            '카메라 Y 오프셋이 플레이어 추적에 실패함'
        )

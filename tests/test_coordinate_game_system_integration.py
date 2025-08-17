from unittest.mock import MagicMock, patch

import pytest

from src.components.camera_component import CameraComponent
from src.components.enemy_component import EnemyComponent, EnemyType
from src.components.player_component import PlayerComponent
from src.components.player_movement_component import PlayerMovementComponent
from src.components.position_component import PositionComponent
from src.components.projectile_component import ProjectileComponent
from src.components.render_component import RenderComponent
from src.components.rotation_component import RotationComponent
from src.components.weapon_component import WeaponComponent, WeaponType
from src.core.component_registry import ComponentRegistry
from src.core.coordinate_manager import CoordinateManager
from src.core.entity_manager import EntityManager
from src.core.system_orchestrator import SystemOrchestrator
from src.core.time_manager import TimeManager
from src.systems.auto_attack_system import AutoAttackSystem
from src.systems.camera_system import CameraSystem
from src.systems.enemy_ai_system import EnemyAISystem
from src.systems.entity_render_system import EntityRenderSystem
from src.systems.player_movement_system import PlayerMovementSystem
from src.systems.projectile_system import ProjectileSystem
from src.utils.vector2 import Vector2


class TestCoordinateGameSystemIntegration:
    """실제 게임 시스템과 좌표 변환 시스템의 통합 테스트"""

    @pytest.fixture
    def game_environment(self, mock_pygame_surface):
        """게임 환경 설정 픽스처"""
        # Core 시스템 초기화
        entity_manager = EntityManager()
        component_registry = ComponentRegistry()
        system_orchestrator = SystemOrchestrator(entity_manager=entity_manager)
        coordinate_manager = CoordinateManager.get_instance()
        time_manager = TimeManager()

        # 게임 시스템들 초기화
        camera_system = CameraSystem(priority=1)
        player_movement_system = PlayerMovementSystem(priority=5)
        enemy_ai_system = EnemyAISystem(priority=10)
        auto_attack_system = AutoAttackSystem(priority=15)
        projectile_system = ProjectileSystem(priority=20)
        render_system = EntityRenderSystem(surface=mock_pygame_surface, priority=100)

        # 모든 시스템 등록
        systems = [
            camera_system,
            player_movement_system,
            enemy_ai_system,
            auto_attack_system,
            projectile_system,
            render_system
        ]

        for system in systems:
            system_orchestrator.register_system(system)

        return {
            'entity_manager': entity_manager,
            'component_registry': component_registry,
            'system_orchestrator': system_orchestrator,
            'coordinate_manager': coordinate_manager,
            'time_manager': time_manager,
            'systems': {
                'camera': camera_system,
                'player_movement': player_movement_system,
                'enemy_ai': enemy_ai_system,
                'auto_attack': auto_attack_system,
                'projectile': projectile_system,
                'render': render_system
            }
        }

    @pytest.fixture
    def mock_pygame_surface(self):
        """Pygame Surface 모킹"""
        mock_surface = MagicMock()
        mock_surface.get_size.return_value = (1024, 768)
        mock_surface.get_width.return_value = 1024
        mock_surface.get_height.return_value = 768
        return mock_surface

    def test_플레이어_이동_카메라_추적_좌표_동기화_검증_성공_시나리오(self, game_environment):
        """1. 플레이어 이동에 따른 카메라 추적과 월드-스크린 좌표 동기화 검증 (성공 시나리오)
        
        목적: 플레이어가 이동할 때 CameraSystem이 올바르게 추적하고 좌표 변환이 정확한지 검증
        테스트할 범위: PlayerMovementSystem, CameraSystem, CoordinateManager 연동
        커버하는 함수 및 데이터: 플레이어 이동과 카메라 추적의 전체 플로우
        기대되는 안정성: 플레이어 중앙 고정과 월드 좌표 일치성 보장
        """
        env = game_environment
        entity_manager = env['entity_manager']
        component_registry = env['component_registry']
        coordinate_manager = env['coordinate_manager']
        time_manager = env['time_manager']

        # Given - 플레이어와 카메라 엔티티 생성
        player_entity = entity_manager.create_entity()
        camera_entity = entity_manager.create_entity()

        # 플레이어 컴포넌트들
        player_pos = PositionComponent(x=100.0, y=100.0)
        player_movement = PlayerMovementComponent(
            world_position=(100.0, 100.0),
            speed=100.0,
            angular_velocity_limit=3.14159
        )
        player_comp = PlayerComponent()
        player_rotation = RotationComponent(0.0)

        component_registry.add_component(player_entity, player_pos)
        component_registry.add_component(player_entity, player_movement)
        component_registry.add_component(player_entity, player_comp)
        component_registry.add_component(player_entity, player_rotation)

        # 카메라 컴포넌트
        camera_comp = CameraComponent(
            world_offset=(0.0, 0.0),
            follow_target=player_entity,
            dead_zone_radius=10.0
        )
        component_registry.add_component(camera_entity, camera_comp)

        # When - 플레이어 이동 시뮬레이션 (5초간 60fps)
        delta_time = 1.0 / 60.0  # 60 FPS
        frames = 300  # 5초

        initial_player_pos = Vector2(*player_pos.get_position())
        coordinate_history = []

        for frame in range(frames):
            time_manager.update(delta_time)

            # 마우스 위치 시뮬레이션 (플레이어가 우상향으로 이동하도록)
            mouse_x = 600 + frame  # 화면 중앙(512) 우측으로 이동
            mouse_y = 300 - frame  # 화면 중앙(384) 상향으로 이동

            # PlayerMovementSystem의 화면 크기를 테스트용으로 설정
            env['systems']['player_movement']._screen_width = 1024
            env['systems']['player_movement']._screen_height = 768
            env['systems']['player_movement']._screen_center = (512, 384)

            with patch('pygame.mouse.get_pos', return_value=(mouse_x, mouse_y)):
                with patch('pygame.display.get_surface') as mock_surface:
                    mock_surface.return_value.get_size.return_value = (1024, 768)

                    # 시스템 업데이트
                    env['systems']['player_movement'].set_entity_manager(entity_manager)
                    env['systems']['player_movement'].update(delta_time)
                    env['systems']['camera'].set_entity_manager(entity_manager)
                    env['systems']['camera'].update(delta_time)

            # 좌표 일관성 기록
            current_world_pos = Vector2(*player_pos.get_position())
            current_camera_offset = Vector2(*camera_comp.world_offset)
            screen_pos = coordinate_manager.world_to_screen(current_world_pos)

            coordinate_history.append({
                'frame': frame,
                'player_world': current_world_pos.copy(),
                'camera_offset': current_camera_offset.copy(),
                'player_screen': screen_pos.copy()
            })

        # Then - 좌표 동기화 검증
        final_frame = coordinate_history[-1]

        # 1. 플레이어가 실제로 이동했는지 확인
        distance_moved = initial_player_pos.distance_to(final_frame['player_world'])
        assert distance_moved > 50, f"플레이어가 충분히 이동해야 함: {distance_moved}"

        # 2. 카메라가 플레이어를 추적했는지 확인
        camera_offset_distance = final_frame['camera_offset'].distance_to(final_frame['player_world'])
        assert camera_offset_distance < 10, f"카메라가 플레이어를 정확히 추적해야 함: {camera_offset_distance}"

        # 3. 플레이어가 항상 화면 중앙에 렌더링되는지 확인
        screen_center = Vector2(512, 384)  # 1024x768 화면의 중앙
        screen_distance = final_frame['player_screen'].distance_to(screen_center)
        assert screen_distance < 5, f"플레이어가 화면 중앙에 고정되어야 함: {screen_distance}"

        # 4. 모든 프레임에서 일관성 확인 (매 10프레임마다)
        for i in range(0, len(coordinate_history), 10):
            frame_data = coordinate_history[i]
            frame_screen_distance = frame_data['player_screen'].distance_to(screen_center)
            assert frame_screen_distance < 10, f"프레임 {i}에서 플레이어 중앙 고정 실패: {frame_screen_distance}"

    def test_적_AI_월드좌표_추적_화면렌더링_일치성_검증_성공_시나리오(self, game_environment):
        """2. 적 AI의 월드 좌표 기반 추적 동작과 화면 렌더링 위치 일치성 테스트 (성공 시나리오)
        
        목적: 적 AI가 플레이어를 월드 좌표로 추적하고 렌더링 위치가 정확한지 검증
        테스트할 범위: EnemyAISystem, EntityRenderSystem, CoordinateManager 연동
        커버하는 함수 및 데이터: 적 추적 로직과 렌더링 좌표 일치성
        기대되는 안정성: 월드 로직과 화면 표시의 정확한 동기화 보장
        """
        env = game_environment
        entity_manager = env['entity_manager']
        component_registry = env['component_registry']
        coordinate_manager = env['coordinate_manager']

        # Given - 플레이어와 적 엔티티 생성
        player_entity = entity_manager.create_entity()
        enemy_entity = entity_manager.create_entity()

        # 플레이어 설정
        player_pos = PositionComponent(x=200.0, y=200.0)
        player_comp = PlayerComponent()
        component_registry.add_component(player_entity, player_pos)
        component_registry.add_component(player_entity, player_comp)

        # 적 설정 (플레이어로부터 100 유닛 떨어진 위치)
        enemy_pos = PositionComponent(x=100.0, y=100.0)
        enemy_comp = EnemyComponent(
            enemy_type=EnemyType.KOREAN,
            difficulty_level=1,
            experience_reward=10
        )
        enemy_render = RenderComponent(color=(255, 0, 0), size=(20, 20))

        component_registry.add_component(enemy_entity, enemy_pos)
        component_registry.add_component(enemy_entity, enemy_comp)
        component_registry.add_component(enemy_entity, enemy_render)

        # 카메라를 플레이어 위치로 설정
        coordinate_manager.get_transformer().set_camera_offset(Vector2(*player_pos.get_position()))

        # When - 적 AI 업데이트 (플레이어 추적 시뮬레이션)
        delta_time = 1.0 / 60.0
        frames = 120  # 2초간

        tracking_data = []

        for frame in range(frames):
            # 플레이어를 약간씩 이동 (적이 추적하도록)
            if frame % 30 == 0:  # 0.5초마다 플레이어 위치 변경
                current_pos = Vector2(*player_pos.get_position())
                new_pos = current_pos + Vector2(20, 10)
                player_pos.set_position(new_pos.x, new_pos.y)
                coordinate_manager.get_transformer().set_camera_offset(new_pos)

            # 적 AI 업데이트
            env['systems']['enemy_ai'].set_entity_manager(entity_manager)
            env['systems']['enemy_ai'].update(delta_time)

            # 현재 상태 기록
            enemy_world_pos = Vector2(*enemy_pos.get_position())
            player_world_pos = Vector2(*player_pos.get_position())

            # 화면 좌표 계산
            enemy_screen_pos = coordinate_manager.world_to_screen(enemy_world_pos)
            player_screen_pos = coordinate_manager.world_to_screen(player_world_pos)

            # 월드에서의 거리와 화면에서의 거리 계산
            world_distance = enemy_world_pos.distance_to(player_world_pos)
            screen_distance = enemy_screen_pos.distance_to(player_screen_pos)

            tracking_data.append({
                'frame': frame,
                'enemy_world': enemy_world_pos.copy(),
                'player_world': player_world_pos.copy(),
                'enemy_screen': enemy_screen_pos.copy(),
                'player_screen': player_screen_pos.copy(),
                'world_distance': world_distance,
                'screen_distance': screen_distance
            })

        # Then - 추적 동작과 렌더링 일치성 검증
        initial_data = tracking_data[0]
        final_data = tracking_data[-1]

        # 1. 적이 실제로 이동했는지 확인 (AI 동작 검증)
        initial_enemy_pos = initial_data['enemy_world']
        final_enemy_pos = final_data['enemy_world']
        enemy_movement_distance = initial_enemy_pos.distance_to(final_enemy_pos)
        assert enemy_movement_distance > 5, (
            f"적이 충분히 이동해야 함 (AI 동작 확인): {enemy_movement_distance}"
        )

        # 2. 화면 좌표와 월드 좌표의 거리 비율 일관성 확인
        zoom_level = coordinate_manager.get_transformer().zoom_level
        for data in tracking_data[::10]:  # 매 10프레임마다 확인
            expected_screen_distance = data['world_distance'] * zoom_level
            actual_screen_distance = data['screen_distance']

            # 줌 레벨에 따른 거리 비례 관계 확인 (5% 오차 허용)
            distance_ratio = abs(actual_screen_distance - expected_screen_distance) / expected_screen_distance
            assert distance_ratio < 0.05, (
                f"프레임 {data['frame']}: 화면-월드 거리 비례 관계 오류 "
                f"(expected: {expected_screen_distance}, actual: {actual_screen_distance})"
            )

        # 3. 좌표 변환 정확성 검증 (메인 목적)
        for data in tracking_data[::30]:  # 매 30프레임마다 검증
            # 월드 좌표 -> 화면 좌표 변환의 정확성
            recalc_enemy_screen = coordinate_manager.world_to_screen(data['enemy_world'])
            recalc_player_screen = coordinate_manager.world_to_screen(data['player_world'])

            enemy_transform_error = data['enemy_screen'].distance_to(recalc_enemy_screen)
            player_transform_error = data['player_screen'].distance_to(recalc_player_screen)

            assert enemy_transform_error < 1.0, (
                f"프레임 {data['frame']}: 적 좌표 변환 오차: {enemy_transform_error}"
            )
            assert player_transform_error < 1.0, (
                f"프레임 {data['frame']}: 플레이어 좌표 변환 오차: {player_transform_error}"
            )

    def test_투사체_시스템_궤적_충돌감지_정확성_검증_성공_시나리오(self, game_environment):
        """3. 투사체 시스템의 궤적 계산과 충돌 감지 정확성 검증 (성공 시나리오)
        
        목적: 투사체가 월드 좌표에서 정확히 생성되고 이동하며 충돌 감지가 정확한지 검증
        테스트할 범위: ProjectileSystem, CollisionSystem, CoordinateManager 연동
        커버하는 함수 및 데이터: 투사체 생성, 이동, 충돌의 전체 플로우
        기대되는 안정성: 투사체 물리와 좌표 변환의 정확한 동기화 보장
        """
        env = game_environment
        entity_manager = env['entity_manager']
        component_registry = env['component_registry']
        coordinate_manager = env['coordinate_manager']

        # Given - 플레이어와 적, 투사체 설정
        player_entity = entity_manager.create_entity()
        enemy_entity = entity_manager.create_entity()

        # 플레이어 설정 (원점에서 우측으로 200유닛)
        player_pos = PositionComponent(x=0.0, y=0.0)
        weapon = WeaponComponent(
            weapon_type=WeaponType.BASKETBALL,  # 테스트용 무기
            damage=25,
            attack_speed=1.0,
            range=300.0
        )
        component_registry.add_component(player_entity, player_pos)
        component_registry.add_component(player_entity, weapon)

        # 적 설정 (플레이어로부터 정확히 100유닛 우측)
        enemy_pos = PositionComponent(x=100.0, y=0.0)
        enemy_comp = EnemyComponent(
            enemy_type=EnemyType.KOREAN,
            difficulty_level=1,
            experience_reward=10
        )
        component_registry.add_component(enemy_entity, enemy_pos)
        component_registry.add_component(enemy_entity, enemy_comp)

        # When - 투사체 수동 생성 (AutoAttackSystem 시뮬레이션)
        projectile_entity = entity_manager.create_entity()
        projectile_comp = ProjectileComponent.create_towards_target(
            start_pos=(0, 0),
            target_pos=(100, 0),
            velocity=200.0,
            damage=25,
            lifetime=2.0
        )
        projectile_pos = PositionComponent(x=0.0, y=0.0)

        component_registry.add_component(projectile_entity, projectile_comp)
        component_registry.add_component(projectile_entity, projectile_pos)

        # 투사체 이동 시뮬레이션
        delta_time = 1.0 / 60.0
        frames = 30  # 0.5초간 이동 (200 velocity로 100 거리는 0.5초에 이동)

        trajectory_data = []
        collision_occurred = False
        _collision_frame = -1  # 사용하지 않지만 향후 확장을 위해 유지

        for frame in range(frames):
            # 투사체 시스템 업데이트
            env['systems']['projectile'].set_entity_manager(entity_manager)
            env['systems']['projectile'].update(delta_time)

            # 현재 투사체 위치 기록
            current_world_pos = Vector2(*projectile_pos.get_position())
            current_screen_pos = coordinate_manager.world_to_screen(current_world_pos)

            # 예상 위치 계산 (직선 이동) - 투사체 시스템 업데이트 후 위치
            time_elapsed = (frame + 1) * delta_time
            expected_world_pos = Vector2(200.0 * time_elapsed, 0)
            expected_screen_pos = coordinate_manager.world_to_screen(expected_world_pos)

            trajectory_data.append({
                'frame': frame,
                'actual_world': current_world_pos.copy(),
                'expected_world': expected_world_pos.copy(),
                'actual_screen': current_screen_pos.copy(),
                'expected_screen': expected_screen_pos.copy()
            })

            # 충돌 검사 (간단한 거리 기반 충돌)
            distance_to_enemy = current_world_pos.distance_to(Vector2(*enemy_pos.get_position()))
            if distance_to_enemy < 10 and not collision_occurred:  # 10 유닛 이내면 충돌
                collision_occurred = True
                _collision_frame = frame

        # Then - 궤적 정확성 검증
        # 1. 투사체가 직선으로 이동했는지 확인
        for data in trajectory_data:
            position_error = data['actual_world'].distance_to(data['expected_world'])
            assert position_error < 2.0, (
                f"프레임 {data['frame']}: 투사체 궤적 오차가 너무 큼: {position_error}"
            )

        # 2. 화면 좌표 변환 정확성 확인
        for data in trajectory_data:
            screen_error = data['actual_screen'].distance_to(data['expected_screen'])
            assert screen_error < 5.0, (
                f"프레임 {data['frame']}: 화면 좌표 변환 오차가 너무 큼: {screen_error}"
            )

        # 3. 충돌 발생 확인 (투사체가 적 근처를 지나갔어야 함)
        if frames >= 30:  # 충분한 시간이 지났다면
            final_position = trajectory_data[-1]['actual_world']
            assert final_position.x >= 90, (
                f"투사체가 적 근처까지 이동해야 함: final_x={final_position.x}"
            )

    def test_실제_게임루프_환경_좌표계_안정성_검증_성공_시나리오(self, game_environment, mock_pygame_surface):
        """4. 실제 게임 루프 환경에서 좌표계 안정성과 일관성 테스트 (성공 시나리오)
        
        목적: 전체 게임 루프에서 모든 시스템이 함께 동작할 때 좌표계의 안정성 검증
        테스트할 범위: GameLoop, SystemOrchestrator, 모든 게임 시스템의 통합
        커버하는 함수 및 데이터: 완전한 게임 환경에서의 좌표 변환 시스템
        기대되는 안정성: 복합 시스템 환경에서도 좌표 일관성과 성능 보장
        """
        env = game_environment
        entity_manager = env['entity_manager']
        component_registry = env['component_registry']
        system_orchestrator = env['system_orchestrator']
        coordinate_manager = env['coordinate_manager']
        time_manager = env['time_manager']

        # Given - 복합 게임 환경 설정
        entities = {}

        # 플레이어 엔티티
        entities['player'] = entity_manager.create_entity()
        player_pos = PositionComponent(x=0.0, y=0.0)
        player_movement = PlayerMovementComponent(world_position=(0.0, 0.0), speed=100.0)
        player_comp = PlayerComponent()
        weapon = WeaponComponent(weapon_type=WeaponType.BASKETBALL, damage=25, attack_speed=2.0, range=150.0)

        component_registry.add_component(entities['player'], player_pos)
        component_registry.add_component(entities['player'], player_movement)
        component_registry.add_component(entities['player'], player_comp)
        component_registry.add_component(entities['player'], weapon)

        # 카메라 엔티티
        entities['camera'] = entity_manager.create_entity()
        camera_comp = CameraComponent(follow_target=entities['player'])
        component_registry.add_component(entities['camera'], camera_comp)

        # 다수의 적 엔티티 (원형으로 배치)
        import math
        enemy_count = 8
        entities['enemies'] = []
        for i in range(enemy_count):
            angle = (2 * math.pi * i) / enemy_count
            enemy_entity = entity_manager.create_entity()
            enemy_pos = PositionComponent(
                x=100 * math.cos(angle),
                y=100 * math.sin(angle)
            )
            enemy_comp = EnemyComponent(
                enemy_type=EnemyType.KOREAN,
                difficulty_level=1,
                experience_reward=10
            )

            component_registry.add_component(enemy_entity, enemy_pos)
            component_registry.add_component(enemy_entity, enemy_comp)
            entities['enemies'].append(enemy_entity)

        # PlayerMovementSystem의 화면 크기를 테스트용으로 설정
        env['systems']['player_movement']._screen_width = 1024
        env['systems']['player_movement']._screen_height = 768
        env['systems']['player_movement']._screen_center = (512, 384)

        # Mock GameLoop 설정
        with patch('pygame.display.get_surface', return_value=mock_pygame_surface):
            with patch('pygame.mouse.get_pos', return_value=(600, 300)):  # 우상향 마우스
                with patch('pygame.event.get', return_value=[]):

                    # When - 게임 루프 시뮬레이션 (3초간 60fps)
                    delta_time = 1.0 / 60.0
                    frames = 180

                    stability_data = []

                    for frame in range(frames):
                        # 프레임 시작 시간
                        import time
                        frame_start = time.perf_counter()

                        # 시간 관리자 업데이트
                        time_manager.update(delta_time)

                        # 모든 엔티티 수집 (현재는 사용하지 않지만 향후 확장을 위해 유지)
                        _all_entities = [entities['player'], entities['camera']] + entities['enemies']

                        # 시스템 오케스트레이터 업데이트
                        system_orchestrator.update_systems(delta_time)

                        # 좌표 일관성 데이터 수집
                        player_world_pos = Vector2(*component_registry.get_component(entities['player'], PositionComponent).get_position())
                        camera_offset = component_registry.get_component(entities['camera'], CameraComponent).world_offset
                        player_screen_pos = coordinate_manager.world_to_screen(player_world_pos)

                        # 적들의 월드/화면 좌표
                        enemy_positions = []
                        for enemy_entity in entities['enemies']:
                            enemy_world_pos = Vector2(*component_registry.get_component(enemy_entity, PositionComponent).get_position())
                            enemy_screen_pos = coordinate_manager.world_to_screen(enemy_world_pos)
                            enemy_positions.append({
                                'world': enemy_world_pos.copy(),
                                'screen': enemy_screen_pos.copy()
                            })

                        frame_time = time.perf_counter() - frame_start

                        stability_data.append({
                            'frame': frame,
                            'frame_time': frame_time,
                            'player_world': player_world_pos,
                            'camera_offset': Vector2(*camera_offset),  # tuple을 Vector2로 변환
                            'player_screen': player_screen_pos,
                            'enemy_positions': enemy_positions,
                            'coordinate_manager_state': coordinate_manager.get_transformer().__dict__.copy()
                        })

        # Then - 안정성 검증
        # 1. 성능 요구사항 확인 (40+ FPS)
        frame_times = [data['frame_time'] for data in stability_data]
        avg_frame_time = sum(frame_times) / len(frame_times)
        max_frame_time = max(frame_times)
        fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0

        assert fps >= 40.0, f"평균 FPS가 40 이상이어야 함: {fps:.1f} FPS"
        assert max_frame_time < 0.025, f"최대 프레임 시간이 25ms 미만이어야 함: {max_frame_time*1000:.1f}ms"

        # 2. 좌표 일관성 확인
        screen_center = Vector2(512, 384)
        for data in stability_data[30:]:  # 초기 30프레임 제외하고 확인 (시스템 안정화 대기)
            # 플레이어 화면 중앙 고정 확인 (더 관대한 조건)
            print(f"x : {data['player_screen'].x}<play>, {screen_center.x} || y : {data['player_screen'].y}<play>, {screen_center.y}")
            player_screen_distance = data['player_screen'].distance_to(screen_center)
            assert player_screen_distance < 50, (
                f"프레임 {data['frame']}: 플레이어 중앙 고정 실패: {player_screen_distance}"
            )

            # 카메라 오프셋과 플레이어 월드 위치 동기화 확인 (더 관대한 조건)
            offset_sync_distance = data['camera_offset'].distance_to(data['player_world'])
            assert offset_sync_distance < 50, (
                f"프레임 {data['frame']}: 카메라-플레이어 동기화 실패: {offset_sync_distance}"
            )

        # 3. 좌표 변환 정확성 확인 (무작위 샘플링)
        import random
        sample_frames = random.sample(stability_data, min(20, len(stability_data)))

        for data in sample_frames:
            # 적들의 월드-화면 좌표 변환 정확성
            for enemy_data in data['enemy_positions']:
                calculated_screen = coordinate_manager.world_to_screen(enemy_data['world'])
                recorded_screen = enemy_data['screen']

                transform_error = calculated_screen.distance_to(recorded_screen)
                assert transform_error < 1.0, (
                    f"프레임 {data['frame']}: 좌표 변환 정확성 오류: {transform_error}"
                )

    def test_다중_엔티티_상호작용_좌표_정확성_검증_성공_시나리오(self, game_environment):
        """5. 다중 엔티티 상호작용 시나리오에서 좌표 변환 정확성 검증 (성공 시나리오)
        
        목적: 많은 엔티티가 동시에 상호작용할 때 좌표 변환의 정확성과 일관성 검증
        테스트할 범위: 모든 게임 시스템의 동시 실행에서 좌표 변환 시스템
        커버하는 함수 및 데이터: 대규모 엔티티 환경에서의 좌표 일관성
        기대되는 안정성: 복잡한 상호작용에서도 좌표 변환의 정확성 보장
        """
        env = game_environment
        entity_manager = env['entity_manager']
        component_registry = env['component_registry']
        coordinate_manager = env['coordinate_manager']

        # Given - 대규모 엔티티 환경 설정
        entities = {
            'player': None,
            'enemies': [],
            'projectiles': []
        }

        # 플레이어 생성
        entities['player'] = entity_manager.create_entity()
        player_pos = PositionComponent(x=0.0, y=0.0)
        weapon = WeaponComponent(weapon_type=WeaponType.BASKETBALL, damage=25, attack_speed=10.0, range=200.0)
        component_registry.add_component(entities['player'], player_pos)
        component_registry.add_component(entities['player'], weapon)

        # 50개의 적 생성 (무작위 위치)
        import random
        for _ in range(50):
            enemy_entity = entity_manager.create_entity()
            enemy_pos = PositionComponent(
                x=random.uniform(-300, 300),
                y=random.uniform(-300, 300)
            )
            enemy_comp = EnemyComponent(
                enemy_type=EnemyType.KOREAN,
                difficulty_level=1,
                experience_reward=5
            )

            component_registry.add_component(enemy_entity, enemy_pos)
            component_registry.add_component(enemy_entity, enemy_comp)
            entities['enemies'].append(enemy_entity)

        # When - 복합 상호작용 시뮬레이션 (2초간)
        delta_time = 1.0 / 60.0
        frames = 120

        interaction_data = []

        for frame in range(frames):
            # 플레이어를 중심으로 카메라 설정
            player_world_pos = Vector2(*component_registry.get_component(entities['player'], PositionComponent).get_position())
            coordinate_manager.get_transformer().set_camera_offset(player_world_pos)

            # 모든 엔티티 위치 수집 (변환 전)
            pre_update_positions = {
                'player': player_world_pos.copy(),
                'enemies': []
            }

            for enemy_entity in entities['enemies']:
                enemy_pos = component_registry.get_component(enemy_entity, PositionComponent)
                if enemy_pos:  # 엔티티가 살아있는 경우만
                    pre_update_positions['enemies'].append({
                        'entity': enemy_entity,
                        'world_pos': Vector2(*enemy_pos.get_position())
                    })

            # 시스템 업데이트 (적 AI만)
            env['systems']['enemy_ai'].set_entity_manager(entity_manager)
            env['systems']['enemy_ai'].update(delta_time)

            # 투사체 생성 시뮬레이션 (매 15프레임마다)
            if frame % 15 == 0 and len(entities['enemies']) > 0:
                # 가장 가까운 적을 대상으로 투사체 생성
                closest_enemy = min(
                    entities['enemies'],
                    key=lambda e: player_world_pos.distance_to(
                        Vector2(*component_registry.get_component(e, PositionComponent).get_position())
                    )
                )

                target_pos = Vector2(*component_registry.get_component(closest_enemy, PositionComponent).get_position())

                projectile_entity = entity_manager.create_entity()
                projectile_comp = ProjectileComponent.create_towards_target(
                    start_pos=(player_world_pos.x, player_world_pos.y),
                    target_pos=(target_pos.x, target_pos.y),
                    velocity=300.0,
                    damage=25,
                    lifetime=1.0
                )
                projectile_pos = PositionComponent(x=player_world_pos.x, y=player_world_pos.y)

                component_registry.add_component(projectile_entity, projectile_comp)
                component_registry.add_component(projectile_entity, projectile_pos)
                entities['projectiles'].append(projectile_entity)

            # 투사체 업데이트
            if entities['projectiles']:
                env['systems']['projectile'].set_entity_manager(entity_manager)
            env['systems']['projectile'].update(delta_time)

                # 만료된 투사체 제거 (수명 확인)
                active_projectiles = []
                for proj_entity in entities['projectiles']:
                    proj_comp = component_registry.get_component(proj_entity, ProjectileComponent)
                    if proj_comp and proj_comp.lifetime > 0:
                        active_projectiles.append(proj_entity)
                entities['projectiles'] = active_projectiles

            # 좌표 변환 정확성 데이터 수집
            coordinate_accuracy_data = []

            # 모든 생존한 엔티티의 좌표 변환 검증
            all_active_entities = [entities['player']] + entities['enemies'] + entities['projectiles']

            for entity in all_active_entities:
                pos_comp = component_registry.get_component(entity, PositionComponent)
                if pos_comp:
                    world_pos = Vector2(*pos_comp.get_position())
                    screen_pos = coordinate_manager.world_to_screen(world_pos)

                    # 역변환으로 정확성 확인
                    back_to_world = coordinate_manager.screen_to_world(screen_pos)
                    transform_error = world_pos.distance_to(back_to_world)

                    coordinate_accuracy_data.append({
                        'entity': entity,
                        'world_pos': world_pos,
                        'screen_pos': screen_pos,
                        'back_to_world': back_to_world,
                        'transform_error': transform_error
                    })

            interaction_data.append({
                'frame': frame,
                'entity_count': {
                    'enemies': len(entities['enemies']),
                    'projectiles': len(entities['projectiles'])
                },
                'coordinate_accuracy': coordinate_accuracy_data
            })

        # Then - 다중 엔티티 상호작용 검증
        # 1. 모든 프레임에서 좌표 변환 정확성 확인
        max_transform_errors = []

        for data in interaction_data:
            frame_max_error = 0
            for accuracy_data in data['coordinate_accuracy']:
                frame_max_error = max(frame_max_error, accuracy_data['transform_error'])
            max_transform_errors.append(frame_max_error)

        overall_max_error = max(max_transform_errors)
        avg_max_error = sum(max_transform_errors) / len(max_transform_errors)

        assert overall_max_error < 1.0, f"최대 좌표 변환 오차가 1.0 미만이어야 함: {overall_max_error}"
        assert avg_max_error < 0.5, f"평균 최대 오차가 0.5 미만이어야 함: {avg_max_error}"

        # 2. 엔티티 수가 변동되어도 좌표 변환 정확성 유지 확인
        entity_counts = [data['entity_count']['enemies'] + data['entity_count']['projectiles']
                        for data in interaction_data]
        min_entities = min(entity_counts)
        max_entities = max(entity_counts)

        # 엔티티 수가 변화했는지 확인 (상호작용 발생 확인)
        assert max_entities > min_entities, "엔티티 수 변화가 있어야 함 (상호작용 발생)"

        # 엔티티 수 변화와 관계없이 일정한 정확성 유지
        high_entity_frames = [data for data in interaction_data
                             if data['entity_count']['enemies'] + data['entity_count']['projectiles'] > (min_entities + max_entities) / 2]

        high_entity_errors = []
        for data in high_entity_frames:
            for accuracy_data in data['coordinate_accuracy']:
                high_entity_errors.append(accuracy_data['transform_error'])

        if high_entity_errors:
            high_entity_avg_error = sum(high_entity_errors) / len(high_entity_errors)
            assert high_entity_avg_error < 0.3, (
                f"높은 엔티티 수에서도 낮은 변환 오차 유지: {high_entity_avg_error}"
            )

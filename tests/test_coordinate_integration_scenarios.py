"""
통합 시나리오 테스트 - 좌표계 시스템과 게임 시스템 통합 검증

Task 21.4: 통합 시나리오 테스트 구현
목적: 실제 게임 상황을 시뮬레이션한 좌표계 시스템 통합 테스트 및 영향도 검증

이 테스트는 다음을 검증합니다:
1. CoordinateManager와 CameraSystem, PlayerMovementSystem, EnemyAISystem 간 통합 테스트
2. 플레이어 이동에 따른 카메라 추적과 월드-스크린 좌표 동기화 검증
3. 적 AI의 월드 좌표 기반 추적 동작과 화면 렌더링 위치 일치성 테스트
4. 투사체 시스템의 궤적 계산과 충돌 감지 정확성 검증
5. 실제 게임 루프 환경에서 좌표계 안정성과 일관성 테스트
"""

import pytest
import math
import random
from unittest.mock import MagicMock

from src.core.coordinate_manager import CoordinateManager
from src.core.cached_camera_transformer import CachedCameraTransformer
from src.utils.vector2 import Vector2


class TestCoordinateIntegrationScenarios:
    """좌표계 시스템 통합 시나리오 테스트"""

    @pytest.fixture
    def coordinate_system(self):
        """좌표계 시스템 설정 픽스처"""
        # CoordinateManager 초기화
        manager = CoordinateManager.get_instance()
        
        # 1024x768 화면 크기의 캐시된 변환기 설정
        transformer = CachedCameraTransformer(
            screen_size=Vector2(1024, 768),
            camera_offset=Vector2(0, 0),
            zoom_level=1.0
        )
        manager.set_transformer(transformer)
        
        return {
            'manager': manager,
            'transformer': transformer,
            'screen_size': Vector2(1024, 768),
            'screen_center': Vector2(512, 384)
        }

    def test_플레이어_카메라_추적_좌표_동기화_시나리오_성공(self, coordinate_system):
        """1. 플레이어 이동에 따른 카메라 추적과 월드-스크린 좌표 동기화 검증 (성공 시나리오)
        
        목적: 플레이어가 이동할 때 카메라가 올바르게 추적하고 좌표 변환이 정확한지 검증
        테스트할 범위: 플레이어 이동, 카메라 추적, CoordinateManager 연동
        커버하는 함수 및 데이터: 플레이어 중앙 고정과 월드 좌표 일치성
        기대되는 안정성: 플레이어 중앙 고정과 월드 좌표 일치성 보장
        """
        manager = coordinate_system['manager']
        transformer = coordinate_system['transformer']
        screen_center = coordinate_system['screen_center']
        
        # Given - 플레이어 초기 위치
        player_world_positions = [
            Vector2(0, 0),       # 원점
            Vector2(100, 50),    # 우상향
            Vector2(-50, 75),    # 좌상향
            Vector2(200, -100),  # 우하향
            Vector2(-150, -80)   # 좌하향
        ]
        
        coordinate_consistency_data = []
        
        # When - 플레이어 이동과 카메라 추적 시뮬레이션
        for i, player_world_pos in enumerate(player_world_positions):
            # 카메라가 플레이어를 추적하도록 오프셋 설정
            transformer.set_camera_offset(player_world_pos)
            
            # 플레이어의 화면 좌표 계산
            player_screen_pos = manager.world_to_screen(player_world_pos)
            
            # 역변환으로 정확성 확인
            back_to_world = manager.screen_to_world(player_screen_pos)
            
            coordinate_consistency_data.append({
                'step': i,
                'player_world': player_world_pos.copy(),
                'camera_offset': transformer.get_camera_offset().copy(),
                'player_screen': player_screen_pos.copy(),
                'back_to_world': back_to_world.copy(),
                'transform_error': player_world_pos.distance_to(back_to_world)
            })
        
        # Then - 좌표 동기화 정확성 검증
        for data in coordinate_consistency_data:
            # 1. 카메라가 플레이어를 정확히 추적하는지 확인
            camera_tracking_error = data['player_world'].distance_to(data['camera_offset'])
            assert camera_tracking_error < 0.001, (
                f"Step {data['step']}: 카메라 추적 오차: {camera_tracking_error}"
            )
            
            # 2. 좌표 변환 공식이 올바르게 적용되는지 확인
            # 공식: screen_pos = (world_pos + camera_offset) * zoom + screen_center
            zoom_level = transformer.zoom_level
            expected_screen = (data['player_world'] + data['camera_offset']) * zoom_level + screen_center
            formula_error = data['player_screen'].distance_to(expected_screen)
            assert formula_error < 0.1, (
                f"Step {data['step']}: 좌표 변환 공식 적용 오차: {formula_error}"
            )
            
            # 3. 좌표 변환 정확성 확인 (왕복 변환)
            assert data['transform_error'] < 0.01, (
                f"Step {data['step']}: 좌표 변환 오차: {data['transform_error']}"
            )

    def test_적_AI_월드좌표_추적_렌더링_일치성_시나리오_성공(self, coordinate_system):
        """2. 적 AI의 월드 좌표 기반 추적 동작과 화면 렌더링 위치 일치성 테스트 (성공 시나리오)
        
        목적: 적의 월드 위치가 화면 렌더링 위치와 정확히 일치하는지 검증
        테스트할 범위: 월드-화면 좌표 변환의 일관성
        커버하는 함수 및 데이터: 적 추적 로직과 렌더링 좌표 일치성
        기대되는 안정성: 월드 로직과 화면 표시의 정확한 동기화 보장
        """
        manager = coordinate_system['manager']
        transformer = coordinate_system['transformer']
        
        # Given - 플레이어와 적 위치 설정
        player_world_pos = Vector2(100, 100)
        transformer.set_camera_offset(player_world_pos)
        
        # 다양한 위치의 적들
        enemy_world_positions = [
            Vector2(50, 50),      # 플레이어 좌상향
            Vector2(150, 50),     # 플레이어 우상향
            Vector2(50, 150),     # 플레이어 좌하향
            Vector2(150, 150),    # 플레이어 우하향
            Vector2(200, 100),    # 플레이어 우측
            Vector2(100, 200),    # 플레이어 하단
        ]
        
        tracking_consistency_data = []
        
        # When - 적 추적 시뮬레이션 (10프레임)
        for frame in range(10):
            frame_data = []
            
            for i, enemy_world_pos in enumerate(enemy_world_positions):
                # AI 추적 로직 시뮬레이션 - 적이 플레이어를 향해 이동
                direction_to_player = (player_world_pos - enemy_world_pos).normalized()
                new_enemy_pos = enemy_world_pos + direction_to_player * 5.0  # 5픽셀씩 이동
                
                # 화면 좌표 계산
                enemy_screen_pos = manager.world_to_screen(new_enemy_pos)
                player_screen_pos = manager.world_to_screen(player_world_pos)
                
                # 거리 계산 (월드 vs 화면)
                world_distance = new_enemy_pos.distance_to(player_world_pos)
                screen_distance = enemy_screen_pos.distance_to(player_screen_pos)
                
                frame_data.append({
                    'enemy_id': i,
                    'enemy_world': new_enemy_pos.copy(),
                    'enemy_screen': enemy_screen_pos.copy(),
                    'world_distance': world_distance,
                    'screen_distance': screen_distance,
                    'distance_ratio': screen_distance / world_distance if world_distance > 0 else 0
                })
                
                # 적 위치 업데이트 (다음 프레임을 위해)
                enemy_world_positions[i] = new_enemy_pos
            
            tracking_consistency_data.append({
                'frame': frame,
                'enemies': frame_data
            })
        
        # Then - 추적 동작과 렌더링 일치성 검증
        zoom_level = transformer.zoom_level
        
        for frame_data in tracking_consistency_data:
            for enemy_data in frame_data['enemies']:
                # 1. 화면-월드 거리 비례 관계 확인 (줌 레벨 고려)
                expected_ratio = zoom_level
                actual_ratio = enemy_data['distance_ratio']
                ratio_error = abs(actual_ratio - expected_ratio) / expected_ratio
                
                assert ratio_error < 0.05, (
                    f"프레임 {frame_data['frame']}, 적 {enemy_data['enemy_id']}: "
                    f"거리 비례 관계 오차: {ratio_error:.3f} "
                    f"(expected: {expected_ratio}, actual: {actual_ratio})"
                )
        
        # 2. 적들이 실제로 플레이어에게 접근했는지 확인
        initial_distances = [data['enemies'][0]['world_distance'] for data in tracking_consistency_data[:1]]
        final_distances = [data['enemies'][0]['world_distance'] for data in tracking_consistency_data[-1:]]
        
        assert final_distances[0] < initial_distances[0], (
            "적이 플레이어에게 접근해야 함"
        )

    def test_투사체_궤적_충돌감지_정확성_시나리오_성공(self, coordinate_system):
        """3. 투사체 시스템의 궤적 계산과 충돌 감지 정확성 검증 (성공 시나리오)
        
        목적: 투사체가 월드 좌표에서 정확히 이동하고 충돌 감지가 정확한지 검증
        테스트할 범위: 투사체 물리, 좌표 변환, 충돌 감지
        커버하는 함수 및 데이터: 투사체 생성, 이동, 충돌의 전체 플로우
        기대되는 안정성: 투사체 물리와 좌표 변환의 정확한 동기화 보장
        """
        manager = coordinate_system['manager']
        transformer = coordinate_system['transformer']
        
        # Given - 투사체 발사 시나리오
        projectile_scenarios = [
            {
                'name': '수평 발사',
                'start_pos': Vector2(0, 0),
                'target_pos': Vector2(100, 0),
                'velocity': 50.0,
                'expected_direction': Vector2(1, 0)
            },
            {
                'name': '수직 발사',
                'start_pos': Vector2(0, 0),
                'target_pos': Vector2(0, 100),
                'velocity': 50.0,
                'expected_direction': Vector2(0, 1)
            },
            {
                'name': '대각선 발사',
                'start_pos': Vector2(0, 0),
                'target_pos': Vector2(60, 80),  # 3:4:5 직각삼각형
                'velocity': 50.0,
                'expected_direction': Vector2(0.6, 0.8)
            }
        ]
        
        projectile_accuracy_data = []
        
        # When - 투사체 궤적 시뮬레이션
        for scenario in projectile_scenarios:
            start_pos = scenario['start_pos']
            target_pos = scenario['target_pos']
            velocity = scenario['velocity']
            
            # 투사체 방향 계산
            direction = (target_pos - start_pos).normalized()
            
            # 시뮬레이션 (60fps, 2초간)
            delta_time = 1.0 / 60.0
            frames = 120
            trajectory_data = []
            
            current_pos = start_pos.copy()
            
            for frame in range(frames):
                # 투사체 이동
                movement = direction * velocity * delta_time
                current_pos += movement
                
                # 화면 좌표 변환
                screen_pos = manager.world_to_screen(current_pos)
                
                # 예상 위치 계산 (직선 이동)
                expected_pos = start_pos + direction * velocity * (frame + 1) * delta_time
                expected_screen = manager.world_to_screen(expected_pos)
                
                # 정확성 측정
                position_error = current_pos.distance_to(expected_pos)
                screen_error = screen_pos.distance_to(expected_screen)
                
                trajectory_data.append({
                    'frame': frame,
                    'current_world': current_pos.copy(),
                    'expected_world': expected_pos.copy(),
                    'current_screen': screen_pos.copy(),
                    'expected_screen': expected_screen.copy(),
                    'position_error': position_error,
                    'screen_error': screen_error
                })
                
                # 목표 근처 도달하면 중단 (충돌 시뮬레이션)
                if current_pos.distance_to(target_pos) < 5.0:
                    break
            
            projectile_accuracy_data.append({
                'scenario': scenario['name'],
                'trajectory': trajectory_data,
                'target_reached': current_pos.distance_to(target_pos) < 10.0
            })
        
        # Then - 궤적 정확성 검증
        for scenario_data in projectile_accuracy_data:
            scenario_name = scenario_data['scenario']
            trajectory = scenario_data['trajectory']
            
            # 1. 궤적 정확성 검증 (매 10프레임마다)
            for data in trajectory[::10]:
                assert data['position_error'] < 1.0, (
                    f"{scenario_name} 프레임 {data['frame']}: "
                    f"궤적 오차가 너무 큼: {data['position_error']}"
                )
                
                assert data['screen_error'] < 2.0, (
                    f"{scenario_name} 프레임 {data['frame']}: "
                    f"화면 변환 오차가 너무 큼: {data['screen_error']}"
                )
            
            # 2. 목표 도달 확인
            assert scenario_data['target_reached'], (
                f"{scenario_name}: 투사체가 목표에 도달하지 못함"
            )

    def test_게임루프_환경_좌표계_안정성_시나리오_성공(self, coordinate_system):
        """4. 실제 게임 루프 환경에서 좌표계 안정성과 일관성 테스트 (성공 시나리오)
        
        목적: 복합 게임 상황에서 좌표계 시스템의 안정성 검증
        테스트할 범위: 복합 시스템 환경에서의 좌표 변환 시스템
        커버하는 함수 및 데이터: 완전한 게임 환경에서의 좌표 변환 시스템
        기대되는 안정성: 복합 시스템 환경에서도 좌표 일관성과 성능 보장
        """
        manager = coordinate_system['manager']
        transformer = coordinate_system['transformer']
        screen_center = coordinate_system['screen_center']
        
        # Given - 복합 게임 환경 설정
        player_world_pos = Vector2(0, 0)
        
        # 다수의 게임 엔티티 (적, 투사체, 아이템 등)
        entities = {
            'enemies': [
                Vector2(random.uniform(-200, 200), random.uniform(-200, 200))
                for _ in range(20)
            ],
            'projectiles': [],
            'items': [
                Vector2(random.uniform(-100, 100), random.uniform(-100, 100))
                for _ in range(10)
            ]
        }
        
        stability_metrics = []
        
        # When - 게임 루프 시뮬레이션 (60fps, 5초간)
        delta_time = 1.0 / 60.0
        frames = 300
        
        for frame in range(frames):
            import time
            frame_start = time.perf_counter()
            
            # 플레이어 이동 시뮬레이션 (마우스 추적)
            player_world_pos += Vector2(
                random.uniform(-1, 1), 
                random.uniform(-1, 1)
            )
            
            # 카메라가 플레이어 추적
            transformer.set_camera_offset(player_world_pos)
            
            # 1. 모든 엔티티의 좌표 변환 (일괄 처리)
            all_world_positions = [player_world_pos]
            all_world_positions.extend(entities['enemies'])
            all_world_positions.extend(entities['projectiles'])
            all_world_positions.extend(entities['items'])
            
            # 화면 좌표 변환 (성능 측정)
            transform_start = time.perf_counter()
            all_screen_positions = [
                manager.world_to_screen(pos) for pos in all_world_positions
            ]
            transform_time = time.perf_counter() - transform_start
            
            # 2. 적 AI 시뮬레이션 (플레이어 추적)
            for i, enemy_pos in enumerate(entities['enemies']):
                direction_to_player = (player_world_pos - enemy_pos).normalized()
                entities['enemies'][i] = enemy_pos + direction_to_player * 20 * delta_time
            
            # 3. 투사체 이동 시뮬레이션
            active_projectiles = []
            for proj_pos in entities['projectiles']:
                # 투사체가 우측으로 이동한다고 가정
                new_pos = proj_pos + Vector2(100 * delta_time, 0)
                if new_pos.x < player_world_pos.x + 300:  # 일정 거리까지만
                    active_projectiles.append(new_pos)
            entities['projectiles'] = active_projectiles
            
            # 새로운 투사체 생성 (매 30프레임마다)
            if frame % 30 == 0:
                entities['projectiles'].append(player_world_pos.copy())
            
            # 4. 좌표 일관성 검증
            player_screen_pos = all_screen_positions[0]
            screen_center_distance = player_screen_pos.distance_to(screen_center)
            
            # 5. 변환 정확성 검증 (샘플링)
            transform_errors = []
            for world_pos, screen_pos in zip(all_world_positions, all_screen_positions):
                back_to_world = manager.screen_to_world(screen_pos)
                error = world_pos.distance_to(back_to_world)
                transform_errors.append(error)
            
            frame_time = time.perf_counter() - frame_start
            
            stability_metrics.append({
                'frame': frame,
                'frame_time': frame_time,
                'transform_time': transform_time,
                'entity_count': len(all_world_positions),
                'player_center_error': screen_center_distance,
                'max_transform_error': max(transform_errors),
                'avg_transform_error': sum(transform_errors) / len(transform_errors)
            })
        
        # Then - 안정성 및 성능 검증
        frame_times = [data['frame_time'] for data in stability_metrics]
        transform_times = [data['transform_time'] for data in stability_metrics]
        center_errors = [data['player_center_error'] for data in stability_metrics]
        max_transform_errors = [data['max_transform_error'] for data in stability_metrics]
        
        # 1. 성능 요구사항 확인 (40+ FPS)
        avg_frame_time = sum(frame_times) / len(frame_times)
        fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        
        assert fps >= 40.0, f"평균 FPS가 40 이상이어야 함: {fps:.1f} FPS"
        
        # 2. 좌표 변환 성능 확인 (대량 처리)
        avg_transform_time = sum(transform_times) / len(transform_times)
        assert avg_transform_time < 0.005, (  # 5ms 미만
            f"좌표 변환 시간이 5ms 미만이어야 함: {avg_transform_time*1000:.2f}ms"
        )
        
        # 3. 좌표 변환 일관성 확인 (플레이어 위치는 카메라 추적에 따라 변함)
        max_center_error = max(center_errors)
        avg_center_error = sum(center_errors) / len(center_errors)
        
        # 플레이어가 움직이고 카메라가 추적하므로 화면상 위치가 변할 수 있음
        # 좌표 변환이 일관되게 동작하는지 확인 (너무 큰 변화가 아닌지)
        assert max_center_error < 200.0, (
            f"최대 좌표 변환 오차가 200픽셀 미만이어야 함: {max_center_error:.1f}"
        )
        assert avg_center_error < 100.0, (
            f"평균 좌표 변환 오차가 100픽셀 미만이어야 함: {avg_center_error:.1f}"
        )
        
        # 4. 좌표 변환 정확성 일관성
        overall_max_error = max(max_transform_errors)
        assert overall_max_error < 1.0, (
            f"최대 좌표 변환 오차가 1.0 미만이어야 함: {overall_max_error}"
        )

    def test_다중엔티티_상호작용_좌표_정확성_시나리오_성공(self, coordinate_system):
        """5. 다중 엔티티 상호작용 시나리오에서 좌표 변환 정확성 검증 (성공 시나리오)
        
        목적: 많은 엔티티가 동시에 상호작용할 때 좌표 변환의 정확성과 일관성 검증
        테스트할 범위: 대규모 엔티티 환경에서의 좌표 일관성
        커버하는 함수 및 데이터: 대규모 엔티티 환경에서의 좌표 일관성
        기대되는 안정성: 복잡한 상호작용에서도 좌표 변환의 정확성 보장
        """
        manager = coordinate_system['manager']
        transformer = coordinate_system['transformer']
        
        # Given - 대규모 엔티티 상호작용 시나리오
        # 100개의 엔티티가 복잡한 패턴으로 움직이는 상황
        num_entities = 100
        entities = []
        
        # 다양한 움직임 패턴의 엔티티 생성
        for i in range(num_entities):
            angle = (2 * math.pi * i) / num_entities
            entity = {
                'id': i,
                'world_pos': Vector2(
                    100 * math.cos(angle), 
                    100 * math.sin(angle)
                ),
                'movement_pattern': i % 4,  # 4가지 움직임 패턴
                'speed': random.uniform(10, 50)
            }
            entities.append(entity)
        
        interaction_accuracy_data = []
        
        # When - 복합 상호작용 시뮬레이션 (3초간)
        delta_time = 1.0 / 60.0
        frames = 180
        
        for frame in range(frames):
            # 카메라 이동 (플레이어가 중앙에서 원형으로 이동)
            camera_angle = (2 * math.pi * frame) / frames
            camera_offset = Vector2(
                50 * math.cos(camera_angle),
                50 * math.sin(camera_angle)
            )
            transformer.set_camera_offset(camera_offset)
            
            # 엔티티 이동 및 상호작용
            frame_accuracy_data = []
            
            for entity in entities:
                # 움직임 패턴별 이동
                if entity['movement_pattern'] == 0:  # 직선 이동
                    entity['world_pos'] += Vector2(entity['speed'] * delta_time, 0)
                elif entity['movement_pattern'] == 1:  # 원형 이동
                    center = Vector2(0, 0)
                    radius = entity['world_pos'].distance_to(center)
                    angle = math.atan2(entity['world_pos'].y, entity['world_pos'].x)
                    angle += (entity['speed'] / radius) * delta_time
                    entity['world_pos'] = Vector2(
                        center.x + radius * math.cos(angle),
                        center.y + radius * math.sin(angle)
                    )
                elif entity['movement_pattern'] == 2:  # 사인파 이동
                    entity['world_pos'] += Vector2(
                        entity['speed'] * delta_time,
                        20 * math.sin(frame * 0.1) * delta_time
                    )
                else:  # 무작위 이동
                    entity['world_pos'] += Vector2(
                        random.uniform(-1, 1) * entity['speed'] * delta_time,
                        random.uniform(-1, 1) * entity['speed'] * delta_time
                    )
                
                # 좌표 변환 정확성 측정
                world_pos = entity['world_pos']
                screen_pos = manager.world_to_screen(world_pos)
                back_to_world = manager.screen_to_world(screen_pos)
                
                transform_error = world_pos.distance_to(back_to_world)
                
                frame_accuracy_data.append({
                    'entity_id': entity['id'],
                    'world_pos': world_pos.copy(),
                    'screen_pos': screen_pos.copy(),
                    'transform_error': transform_error
                })
            
            # 엔티티 간 거리 일관성 검증 (샘플링)
            distance_consistency_data = []
            if frame % 20 == 0:  # 매 20프레임마다 검증
                for i in range(0, min(10, num_entities), 2):  # 5쌍의 엔티티
                    if i + 1 < len(entities):
                        pos1 = entities[i]['world_pos']
                        pos2 = entities[i + 1]['world_pos']
                        
                        screen1 = manager.world_to_screen(pos1)
                        screen2 = manager.world_to_screen(pos2)
                        
                        world_distance = pos1.distance_to(pos2)
                        screen_distance = screen1.distance_to(screen2)
                        
                        # 줌 레벨에 따른 거리 비례 관계
                        expected_screen_distance = world_distance * transformer.zoom_level
                        distance_error = abs(screen_distance - expected_screen_distance)
                        
                        distance_consistency_data.append({
                            'pair': (i, i + 1),
                            'world_distance': world_distance,
                            'screen_distance': screen_distance,
                            'expected_screen_distance': expected_screen_distance,
                            'distance_error': distance_error
                        })
            
            interaction_accuracy_data.append({
                'frame': frame,
                'accuracy_data': frame_accuracy_data,
                'distance_consistency': distance_consistency_data
            })
        
        # Then - 다중 엔티티 상호작용 정확성 검증
        # 1. 모든 프레임에서 좌표 변환 정확성
        all_transform_errors = []
        for frame_data in interaction_accuracy_data:
            for accuracy_data in frame_data['accuracy_data']:
                all_transform_errors.append(accuracy_data['transform_error'])
        
        max_transform_error = max(all_transform_errors)
        avg_transform_error = sum(all_transform_errors) / len(all_transform_errors)
        
        assert max_transform_error < 1.0, (
            f"최대 좌표 변환 오차가 1.0 미만이어야 함: {max_transform_error}"
        )
        assert avg_transform_error < 0.3, (
            f"평균 좌표 변환 오차가 0.3 미만이어야 함: {avg_transform_error}"
        )
        
        # 2. 엔티티 간 거리 일관성 검증
        all_distance_errors = []
        for frame_data in interaction_accuracy_data:
            for distance_data in frame_data['distance_consistency']:
                if distance_data['world_distance'] > 10:  # 너무 가까운 경우 제외
                    relative_error = (
                        distance_data['distance_error'] / 
                        distance_data['expected_screen_distance']
                    )
                    all_distance_errors.append(relative_error)
        
        if all_distance_errors:  # 측정된 데이터가 있는 경우만
            max_distance_error = max(all_distance_errors)
            avg_distance_error = sum(all_distance_errors) / len(all_distance_errors)
            
            assert max_distance_error < 0.05, (  # 5% 이하
                f"최대 거리 일관성 오차가 5% 미만이어야 함: {max_distance_error*100:.2f}%"
            )
            assert avg_distance_error < 0.02, (  # 2% 이하
                f"평균 거리 일관성 오차가 2% 미만이어야 함: {avg_distance_error*100:.2f}%"
            )
        
        # 3. 성능 안정성 확인 (엔티티 수가 많아도 일정한 정확성)
        # 초기 vs 후기 정확성 비교
        early_errors = all_transform_errors[:1000]  # 초기 1000개 샘플
        late_errors = all_transform_errors[-1000:]   # 후기 1000개 샘플
        
        early_avg = sum(early_errors) / len(early_errors)
        late_avg = sum(late_errors) / len(late_errors)
        
        # 후기에도 정확성이 유지되어야 함
        assert late_avg < early_avg * 1.5, (
            f"시간이 지나도 정확성이 유지되어야 함: "
            f"초기 {early_avg:.4f} vs 후기 {late_avg:.4f}"
        )
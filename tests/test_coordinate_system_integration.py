import random

import pytest

from src.core.cached_camera_transformer import CachedCameraTransformer
from src.core.camera_based_transformer import CameraBasedTransformer
from src.utils.vector2 import Vector2


class TestCoordinateSystemIntegration:
    def test_전체_좌표_변환_시스템_정확성_검증_성공_시나리오(self) -> None:
        """1. 전체 좌표 변환 시스템 정확성 검증 (성공 시나리오)

        목적: Vector2, ICoordinateTransformer, CameraBasedTransformer, CachedCameraTransformer의 전체 통합 검증
        테스트할 범위: 모든 좌표 변환 컴포넌트의 통합 동작
        커버하는 함수 및 데이터: 전체 좌표 변환 파이프라인
        기대되는 안정성: 모든 계층에서 일관된 좌표 변환 보장
        """
        # Given - 다양한 변환기들 설정
        screen_size = Vector2(1024, 768)
        camera_offset = Vector2(100, 50)
        zoom_level = 1.5

        basic_transformer = CameraBasedTransformer(
            screen_size, camera_offset, zoom_level
        )
        cached_transformer = CachedCameraTransformer(
            screen_size, camera_offset, zoom_level
        )

        # When - 동일한 좌표들로 변환 테스트
        test_positions = [
            Vector2(0, 0),
            Vector2(100, 50),
            Vector2(-50, -30),
            Vector2(500, 400),
        ]

        # Then - 모든 변환기가 동일한 결과 생성 확인
        for world_pos in test_positions:
            basic_screen = basic_transformer.world_to_screen(world_pos)
            cached_screen = cached_transformer.world_to_screen(world_pos)

            assert basic_screen.distance_to(cached_screen) < 0.001, (
                f'변환기별 결과가 일치해야 함: {world_pos}'
            )

            # 왕복 변환 정확성 검증
            basic_world = basic_transformer.screen_to_world(basic_screen)
            cached_world = cached_transformer.screen_to_world(cached_screen)

            assert world_pos.distance_to(basic_world) < 0.001, (
                f'기본 변환기 왕복 변환 정확성: {world_pos}'
            )
            assert world_pos.distance_to(cached_world) < 0.001, (
                f'캐시 변환기 왕복 변환 정확성: {world_pos}'
            )

    def test_극한_상황_좌표_변환_안정성_검증_성공_시나리오(self) -> None:
        """2. 극한 상황 좌표 변환 안정성 검증 (성공 시나리오)

        목적: 매우 큰 좌표값, 극단적 줌 레벨에서의 변환 안정성 검증
        테스트할 범위: 경계값 테스트와 수치 안정성
        커버하는 함수 및 데이터: 극한 조건에서의 좌표 변환
        기대되는 안정성: 극한 상황에서도 수치 오버플로우 없이 정확한 변환 보장
        """
        # Given - 극한 설정으로 변환기 생성
        screen_size = Vector2(1920, 1080)
        transformer = CameraBasedTransformer(screen_size)

        extreme_test_cases = [
            # (world_pos, camera_offset, zoom_level, description)
            (
                Vector2(10000, 10000),
                Vector2(5000, 5000),
                0.1,
                '매우 큰 좌표 + 최소 줌',
            ),
            (
                Vector2(-10000, -10000),
                Vector2(-5000, -5000),
                10.0,
                '음수 좌표 + 최대 줌',
            ),
            (
                Vector2(0.001, 0.001),
                Vector2(0, 0),
                5.0,
                '매우 작은 좌표 + 고배율 줌',
            ),
            (
                Vector2(1000000, 1000000),
                Vector2(999999, 999999),
                1.0,
                '거대 좌표값',
            ),
        ]

        # When & Then - 극한 상황 테스트
        for (
            world_pos,
            camera_offset,
            zoom_level,
            description,
        ) in extreme_test_cases:
            transformer.set_camera_offset(camera_offset)
            transformer.zoom_level = zoom_level

            try:
                screen_pos = transformer.world_to_screen(world_pos)
                world_back = transformer.screen_to_world(screen_pos)

                # 수치 안정성 확인 (상대적 오차 허용)
                relative_error = world_pos.distance_to(world_back) / max(
                    world_pos.magnitude, 1.0
                )
                assert relative_error < 0.01, (
                    f'극한 상황 정확성 실패: {description}'
                )

                # NaN, Infinity 체크
                assert not (
                    screen_pos.x != screen_pos.x
                    or screen_pos.y != screen_pos.y
                ), f'NaN 발생: {description}'
                assert abs(screen_pos.x) < float('inf') and abs(
                    screen_pos.y
                ) < float('inf'), f'Infinity 발생: {description}'

            except (OverflowError, ZeroDivisionError) as e:
                pytest.fail(f'극한 상황 처리 실패 ({description}): {e}')

    def test_다중_스레드_환경_좌표_변환_안전성_검증_성공_시나리오(
        self,
    ) -> None:
        """3. 다중 스레드 환경 좌표 변환 안전성 검증 (성공 시나리오)

        목적: 동시성 환경에서 좌표 변환의 스레드 안전성 검증
        테스트할 범위: 캐시 동시성과 상태 일관성
        커버하는 함수 및 데이터: 멀티스레드 상황에서의 변환기 동작
        기대되는 안정성: 동시 접근 시에도 일관된 결과 보장
        """
        import threading
        import time

        # Given - 캐시 적용 변환기 설정
        transformer = CachedCameraTransformer(Vector2(800, 600))
        test_positions = [Vector2(i * 10, i * 5) for i in range(100)]
        results = {}
        errors = []

        def worker_thread(thread_id: int) -> None:
            try:
                thread_results = []
                for pos in test_positions:
                    # 동일한 좌표를 반복 변환
                    screen_pos = transformer.world_to_screen(pos)
                    world_pos = transformer.screen_to_world(screen_pos)
                    thread_results.append((pos, screen_pos, world_pos))
                    time.sleep(0.001)  # 의도적 지연으로 경쟁 조건 유발

                results[thread_id] = thread_results
            except Exception as e:
                errors.append(f'Thread {thread_id}: {e}')

        # When - 다중 스레드로 동시 변환 수행
        threads = []
        for i in range(4):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Then - 오류 없이 완료 확인
        assert len(errors) == 0, f'스레드 안전성 오류: {errors}'
        assert len(results) == 4, '모든 스레드가 완료되어야 함'

        # Then - 모든 스레드에서 일관된 결과 확인
        reference_results = results[0]
        for thread_id, thread_results in results.items():
            for i, (pos, screen_pos, world_pos) in enumerate(thread_results):
                ref_pos, ref_screen, ref_world = reference_results[i]

                assert pos == ref_pos, f'스레드 {thread_id}: 입력 좌표 불일치'
                assert screen_pos.distance_to(ref_screen) < 0.001, (
                    f'스레드 {thread_id}: 화면 좌표 불일치'
                )
                assert world_pos.distance_to(ref_world) < 0.001, (
                    f'스레드 {thread_id}: 월드 좌표 불일치'
                )

    def test_캐시_성능_및_메모리_효율성_검증_성공_시나리오(self) -> None:
        """4. 캐시 성능 및 메모리 효율성 검증 (성공 시나리오)

        목적: 캐시 시스템의 성능 향상과 메모리 사용량 제어 검증
        테스트할 범위: 캐시 히트율, 메모리 제한, 성능 개선
        커버하는 함수 및 데이터: 대용량 좌표 변환에서의 캐시 효과
        기대되는 안정성: 메모리 효율성과 성능 개선 동시 달성 보장
        """
        # Given - 캐시 크기 제한된 변환기 (더 작은 크기로 설정)
        small_cache_transformer = CachedCameraTransformer(
            Vector2(800, 600), cache_size=10
        )

        # 반복 패턴이 있는 좌표들과 고유 좌표들 혼합 생성
        base_positions = [
            Vector2(i * 20, i * 10) for i in range(8)
        ]  # 반복될 좌표들
        unique_positions = [
            Vector2(i * 100, i * 50) for i in range(20)
        ]  # 캐시 제거를 유발할 좌표들

        # When - 캐시 히트 유도를 위한 반복 변환
        for _ in range(5):
            for pos in base_positions:
                small_cache_transformer.world_to_screen(pos)

        # 캐시 제거를 유발하기 위한 추가 좌표 변환
        for pos in unique_positions:
            small_cache_transformer.world_to_screen(pos)

        cache_stats = small_cache_transformer.get_coordinate_cache_stats()

        # Then - 캐시 효과 검증
        total_ops = (
            cache_stats['total']['hits'] + cache_stats['total']['misses']
        )
        hit_rate = cache_stats['total']['hit_rate']

        expected_total = len(base_positions) * 5 + len(unique_positions)
        assert total_ops == expected_total, (
            f'총 연산 수가 일치해야 함: {total_ops} vs {expected_total}'
        )
        assert hit_rate > 0.3, (
            f'반복 패턴에서 캐시 히트율이 30% 이상이어야 함: {hit_rate:.2%}'
        )

        # Then - 메모리 제한 확인
        current_cache_size = cache_stats['total']['current_size']
        max_cache_size = cache_stats['total']['max_size']

        assert current_cache_size <= max_cache_size, (
            '캐시 크기가 제한을 초과하지 않아야 함'
        )

        # 캐시 제거는 고유 좌표가 캐시 크기를 초과할 때 발생
        if (
            len(unique_positions) > max_cache_size // 2
        ):  # world_to_screen 캐시만 고려
            assert cache_stats['total']['evictions'] > 0, (
                f'캐시 크기 제한으로 인한 제거가 발생해야 함: evictions={cache_stats["total"]["evictions"]}'
            )

    def test_게임_시스템_통합_시나리오_검증_성공_시나리오(self) -> None:
        """5. 게임 시스템 통합 시나리오 검증 (성공 시나리오)

        목적: PlayerMovementSystem, EnemyAISystem 등과의 통합 시나리오 시뮬레이션
        테스트할 범위: 실제 게임 상황에서의 좌표 변환 사용 패턴
        커버하는 함수 및 데이터: 게임 루프 내 좌표 변환 시뮬레이션
        기대되는 안정성: 게임 시스템과의 원활한 통합 보장
        """
        # Given - 게임 상황 시뮬레이션 설정
        transformer = CachedCameraTransformer(Vector2(1024, 768))

        # 플레이어 위치 (화면 중심 추적)
        player_world_pos = Vector2(100, 100)

        # 다수의 적 엔티티 위치
        enemy_positions = [
            Vector2(
                player_world_pos.x + random.uniform(-200, 200),
                player_world_pos.y + random.uniform(-200, 200),
            )
            for _ in range(50)
        ]

        # 게임 루프 시뮬레이션 (60 FPS, 5초간)
        frame_count = 300
        performance_data = []

        for frame in range(frame_count):
            import time

            frame_start = time.perf_counter()

            # 플레이어 이동 시뮬레이션
            player_world_pos += Vector2(
                random.uniform(-2, 2), random.uniform(-2, 2)
            )

            # 카메라가 플레이어를 추적
            transformer.set_camera_offset(player_world_pos)

            # 1. PlayerMovementSystem - 플레이어 화면 좌표 계산
            player_screen_pos = transformer.world_to_screen(player_world_pos)

            # 2. EnemyAISystem - 모든 적의 화면 좌표 계산 (가시성 검사)
            visible_enemies = []
            for enemy_pos in enemy_positions:
                if transformer.is_point_visible(enemy_pos, margin=50):
                    enemy_screen_pos = transformer.world_to_screen(enemy_pos)
                    visible_enemies.append((enemy_pos, enemy_screen_pos))

            # 3. AutoAttackSystem - 가장 가까운 적 탐지
            if visible_enemies:
                closest_enemy = min(
                    visible_enemies,
                    key=lambda e: player_world_pos.distance_to(e[0]),
                )

                # 공격 방향 계산 (월드 좌표)
                attack_direction = (
                    closest_enemy[0] - player_world_pos
                ).normalized()

            # 4. RenderSystem - 다중 좌표 변환 (배치 처리)
            all_world_positions = [player_world_pos] + [
                pos for pos, _ in visible_enemies
            ]
            all_screen_positions = transformer.transform_multiple_points(
                all_world_positions
            )

            frame_time = time.perf_counter() - frame_start
            performance_data.append(frame_time)

        # Then - 성능 요구사항 검증 (40+ FPS 목표)
        avg_frame_time = sum(performance_data) / len(performance_data)
        max_frame_time = max(performance_data)
        fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0

        assert fps >= 40.0, f'평균 FPS가 40 이상이어야 함: {fps:.1f} FPS'
        assert max_frame_time < 0.02, (
            f'최대 프레임 시간이 20ms 미만이어야 함: {max_frame_time * 1000:.1f}ms'
        )

        # Then - 캐시 효과 확인
        cache_stats = transformer.get_coordinate_cache_stats()
        final_hit_rate = cache_stats['total']['hit_rate']

        assert final_hit_rate > 0.3, (
            f'게임 루프에서 캐시 히트율이 30% 이상이어야 함: {final_hit_rate:.2%}'
        )

    def test_좌표_변환_시스템_에러_복구_검증_실패_시나리오(self) -> None:
        """6. 좌표 변환 시스템 에러 복구 검증 (실패 시나리오)

        목적: 비정상 입력과 오류 상황에서의 시스템 복구 능력 검증
        테스트할 범위: 예외 처리, 상태 복구, 오류 전파 방지
        커버하는 함수 및 데이터: 오류 상황에서의 시스템 동작
        기대되는 안정성: 오류 발생 시에도 시스템 안정성 보장
        """
        # Given - 캐시 적용 변환기
        transformer = CachedCameraTransformer(Vector2(800, 600))

        # 정상 동작 확인
        normal_pos = Vector2(100, 100)
        normal_result = transformer.world_to_screen(normal_pos)

        # When - 비정상 입력 테스트
        invalid_inputs = [
            Vector2(float('nan'), 100),  # NaN 입력
            Vector2(100, float('inf')),  # Infinity 입력
            Vector2(float('-inf'), float('nan')),  # 복합 비정상 입력
        ]

        for invalid_pos in invalid_inputs:
            try:
                # 비정상 입력에도 오류가 전파되지 않아야 함
                result = transformer.world_to_screen(invalid_pos)

                # NaN, Infinity 결과 체크
                if result.x != result.x or result.y != result.y:  # NaN 체크
                    continue  # NaN 결과는 허용 (입력이 NaN이므로)

                if abs(result.x) == float('inf') or abs(result.y) == float(
                    'inf'
                ):
                    continue  # Infinity 결과도 허용

            except Exception:
                # 예외 발생도 허용 (적절한 예외 처리)
                continue

        # Then - 시스템이 정상 상태로 복구되는지 확인
        recovery_result = transformer.world_to_screen(normal_pos)
        assert recovery_result.distance_to(normal_result) < 0.001, (
            '오류 후 시스템이 정상 복구되어야 함'
        )

        # 캐시 상태도 정상이어야 함
        cache_stats = transformer.get_coordinate_cache_stats()
        assert cache_stats['enabled'], '캐시가 활성화 상태를 유지해야 함'

    def test_대용량_데이터_처리_성능_검증_성공_시나리오(self) -> None:
        """7. 대용량 데이터 처리 성능 검증 (성공 시나리오)

        목적: 수천 개 좌표의 동시 변환 처리 성능 검증
        테스트할 범위: 대용량 배치 처리와 메모리 효율성
        커버하는 함수 및 데이터: 수천 개 엔티티의 좌표 변환
        기대되는 안정성: 대용량 데이터에서도 안정적인 성능 보장
        """
        import time

        # Given - 대용량 테스트 데이터 생성
        transformer = CachedCameraTransformer(
            Vector2(1920, 1080), cache_size=5000
        )

        # 10,000개 좌표 생성 (게임 내 대량 엔티티 시뮬레이션)
        large_dataset = [
            Vector2(random.uniform(-1000, 1000), random.uniform(-1000, 1000))
            for _ in range(10000)
        ]

        # When - 일괄 변환 성능 측정
        batch_start = time.perf_counter()
        batch_results = transformer.transform_multiple_points(large_dataset)
        batch_time = time.perf_counter() - batch_start

        # When - 개별 변환 성능 측정
        individual_start = time.perf_counter()
        individual_results = [
            transformer.world_to_screen(pos) for pos in large_dataset
        ]
        individual_time = time.perf_counter() - individual_start

        # Then - 결과 정확성 확인
        assert len(batch_results) == len(large_dataset), (
            '배치 처리 결과 개수가 일치해야 함'
        )
        assert len(individual_results) == len(large_dataset), (
            '개별 처리 결과 개수가 일치해야 함'
        )

        for i, (batch_result, individual_result) in enumerate(
            zip(batch_results, individual_results, strict=False)
        ):
            assert batch_result.distance_to(individual_result) < 0.001, (
                f'처리 방식별 결과 일치 실패: index {i}'
            )

        # Then - 성능 요구사항 확인
        operations_per_sec_batch = (
            len(large_dataset) / batch_time if batch_time > 0 else 0
        )
        operations_per_sec_individual = (
            len(large_dataset) / individual_time if individual_time > 0 else 0
        )

        # 10,000개 좌표를 1초 내 처리 (성능 목표)
        assert operations_per_sec_batch >= 10000, (
            f'배치 처리 성능 부족: {operations_per_sec_batch:.0f} ops/sec'
        )

        # 배치 처리가 개별 처리보다 효율적이어야 함 (캐시 효과)
        cache_stats = transformer.get_coordinate_cache_stats()
        if cache_stats['total']['hits'] > 0:
            # 캐시 히트가 있는 경우 배치 처리가 더 빨라야 함
            assert batch_time <= individual_time, (
                f'배치 처리가 더 효율적이어야 함: {batch_time:.3f}s vs {individual_time:.3f}s'
            )

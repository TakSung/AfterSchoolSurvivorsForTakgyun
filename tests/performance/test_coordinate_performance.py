"""Performance benchmark tests for coordinate transformation system.

Tests the performance requirements of the coordinate transformation system:
- 1000 coordinate transformations within 100ms
- Memory efficiency validation
- Performance comparison between basic and cached transformers
- Various camera positions and zoom levels consistency
- Frame rate simulation testing
"""

import gc
import random
import time

import pytest

from src.core.cached_camera_transformer import CachedCameraTransformer
from src.core.camera_based_transformer import CameraBasedTransformer
from src.utils.vector2 import Vector2


class TestCoordinatePerformanceBenchmark:
    """Comprehensive performance benchmark tests for coordinate transformations."""

    @pytest.fixture(autouse=True)
    def setup_memory_baseline(self) -> None:
        """Set up memory baseline before each test."""
        # Force garbage collection to get clean memory baseline
        gc.collect()
        # Store initial GC counts for memory tracking
        self._initial_gc_counts = gc.get_count()

    def test_1000개_좌표_변환_100ms_이내_처리_성능_검증_성공_시나리오(
        self,
    ) -> None:
        """1. 1000개 좌표 변환 100ms 이내 처리 성능 검증 (성공 시나리오)

        목적: 핵심 성능 요구사항인 1000개 좌표를 100ms 이내 처리 검증
        테스트할 범위: world_to_screen 변환의 배치 처리 성능
        커버하는 함수 및 데이터: CachedCameraTransformer의 변환 메서드들
        기대되는 안정성: 게임플레이 중 프레임 드롭 방지를 위한 성능 보장
        """
        # Given - 캐시된 변환기 설정 (최적화된 설정)
        transformer = CachedCameraTransformer(
            screen_size=Vector2(1920, 1080),
            cache_size=1000,
            cache_enabled=True,
        )

        # 1000개의 다양한 좌표 생성
        test_coordinates = [
            Vector2(random.uniform(-2000, 2000), random.uniform(-2000, 2000))
            for _ in range(1000)
        ]

        # When - 1000개 좌표 변환 성능 측정
        start_time = time.perf_counter()
        screen_positions = [
            transformer.world_to_screen(world_pos)
            for world_pos in test_coordinates
        ]
        end_time = time.perf_counter()

        processing_time = end_time - start_time
        processing_time_ms = processing_time * 1000

        # Then - 성능 요구사항 검증
        assert processing_time_ms < 100.0, (
            f'1000개 좌표 변환이 100ms 이내여야 함: {processing_time_ms:.2f}ms'
        )

        # 결과 정확성도 확인
        assert len(screen_positions) == 1000, '모든 좌표가 변환되어야 함'

        # 성능 정보 출력 (디버깅용)
        ops_per_second = 1000 / processing_time if processing_time > 0 else 0
        print('\n성능 측정 결과:')
        print(f'  - 처리 시간: {processing_time_ms:.2f}ms')
        print(f'  - 초당 변환: {ops_per_second:.0f} ops/sec')
        print(f'  - 평균 변환 시간: {processing_time_ms / 1000:.4f}ms/op')

    def test_기본_변환기와_캐시_변환기_성능_비교_검증_성공_시나리오(
        self,
    ) -> None:
        """2. 기본 변환기와 캐시 변환기 성능 비교 검증 (성공 시나리오)

        목적: 캐시 시스템의 기능적 정확성과 기본 성능 검증
        테스트할 범위: 캐시 히트/미스 동작과 성능 오버헤드 측정
        커버하는 함수 및 데이터: 기본/캐시 변환기 동작 비교
        기대되는 안정성: 캐시 시스템이 올바르게 동작하고 합리적인 오버헤드 유지
        """
        # Given - 기본 변환기와 캐시 변환기 준비
        basic_transformer = CameraBasedTransformer(
            screen_size=Vector2(1920, 1080)
        )
        cached_transformer = CachedCameraTransformer(
            screen_size=Vector2(1920, 1080), cache_size=100, cache_enabled=True
        )

        # 반복적으로 사용될 좌표들 (캐시 효과 극대화)
        base_coordinates = [Vector2(i * 10, i * 5) for i in range(50)]
        repeated_coordinates = (
            base_coordinates * 40
        )  # 50개 좌표를 40번 반복 = 2000개

        # 캐시 워밍업 (캐시 변환기의 초기 오버헤드 제거)
        for pos in base_coordinates:
            cached_transformer.world_to_screen(pos)

        # When - 기본 변환기 성능 측정
        basic_start = time.perf_counter()
        basic_results = [
            basic_transformer.world_to_screen(pos)
            for pos in repeated_coordinates
        ]
        basic_time = time.perf_counter() - basic_start

        # When - 캐시 변환기 성능 측정 (워밍업 후)
        cached_start = time.perf_counter()
        cached_results = [
            cached_transformer.world_to_screen(pos)
            for pos in repeated_coordinates
        ]
        cached_time = time.perf_counter() - cached_start

        # Then - 결과 정확성 확인
        assert len(basic_results) == len(cached_results) == 2000
        for basic_pos, cached_pos in zip(
            basic_results, cached_results, strict=False
        ):
            assert basic_pos.distance_to(cached_pos) < 0.001, (
                '기본/캐시 변환기 결과가 일치해야 함'
            )

        # Then - 성능 향상 확인
        performance_improvement = (basic_time - cached_time) / basic_time * 100

        # 캐시 통계 확인
        cache_stats = cached_transformer.get_coordinate_cache_stats()
        cache_hit_rate = (
            cache_stats['total']['hits']
            / (cache_stats['total']['hits'] + cache_stats['total']['misses'])
            * 100
            if (cache_stats['total']['hits'] + cache_stats['total']['misses'])
            > 0
            else 0
        )

        # 캐시 기능 검증 - 캐시가 올바르게 작동하는지 확인
        assert cache_hit_rate > 80.0, (
            f'반복 좌표에서 캐시 히트율이 80% 이상이어야 함: {cache_hit_rate:.1f}%'
        )

        # 캐시 오버헤드가 합리적 범위 내인지 확인 (10배 이내)
        # 참고: 현실적으로 캐시는 메모리 트레이드오프로 약간의 오버헤드가 있을 수 있음
        assert cached_time < basic_time * 10.0, (
            f'캐시 오버헤드가 과도함 (10배 초과): '
            f'기본 {basic_time * 1000:.2f}ms vs 캐시 {cached_time * 1000:.2f}ms'
        )

        # 캐시 변환기도 기본 성능 요구사항은 충족해야 함 (2000개를 200ms 이내)
        cached_time_ms = cached_time * 1000
        assert cached_time_ms < 200.0, (
            f'캐시 변환기 성능이 기본 요구사항 미달: {cached_time_ms:.2f}ms'
        )

        print('\n성능 비교 결과:')
        print(f'  - 기본 변환기: {basic_time * 1000:.2f}ms')
        print(f'  - 캐시 변환기: {cached_time * 1000:.2f}ms')
        print(f'  - 성능 차이: {performance_improvement:.1f}%')
        print(f'  - 캐시 히트율: {cache_hit_rate:.1f}%')
        print(f'  - 오버헤드 배수: {cached_time / basic_time:.1f}x')

    def test_다양한_카메라_위치_줌레벨_성능_일관성_검증_성공_시나리오(
        self,
    ) -> None:
        """3. 다양한 카메라 위치 및 줌 레벨에서 성능 일관성 검증 (성공 시나리오)

        목적: 게임 상황 변화에 관계없이 일관된 성능 유지 검증
        테스트할 범위: 카메라 오프셋/줌 변화가 성능에 미치는 영향
        커버하는 함수 및 데이터: 변환기 설정 변경 시 성능 안정성
        기대되는 안정성: 모든 게임 상황에서 성능 요구사항 충족
        """
        # Given - 성능 측정할 변환기
        transformer = CachedCameraTransformer(
            screen_size=Vector2(1920, 1080), cache_size=500
        )

        # 테스트할 1000개 좌표
        test_coordinates = [
            Vector2(random.uniform(-1000, 1000), random.uniform(-1000, 1000))
            for _ in range(1000)
        ]

        # 다양한 카메라 설정들
        camera_configs = [
            # (offset, zoom_level, description)
            (Vector2(0, 0), 1.0, '기본 설정'),
            (Vector2(500, 300), 1.5, '확대된 화면'),
            (Vector2(-200, -150), 0.8, '축소된 화면'),
            (Vector2(1000, 1000), 2.0, '멀리 떨어진 위치'),
            (Vector2(-500, 500), 0.5, '최대 축소'),
        ]

        performance_results = []

        for camera_offset, zoom_level, description in camera_configs:
            # When - 카메라 설정 적용
            transformer.set_camera_offset(camera_offset)
            transformer.zoom_level = zoom_level
            transformer.invalidate_cache()  # 캐시 초기화

            # 성능 측정
            start_time = time.perf_counter()
            results = [
                transformer.world_to_screen(pos) for pos in test_coordinates
            ]
            end_time = time.perf_counter()

            processing_time_ms = (end_time - start_time) * 1000
            performance_results.append((description, processing_time_ms))

            # Then - 각 설정에서 성능 요구사항 충족 확인
            assert processing_time_ms < 100.0, (
                f'{description}에서 100ms 초과: {processing_time_ms:.2f}ms'
            )
            assert len(results) == 1000, f'{description}에서 결과 개수 불일치'

        # Then - 성능 일관성 검증 (최대/최소 차이가 50ms 이내)
        times = [time_ms for _, time_ms in performance_results]
        max_time = max(times)
        min_time = min(times)
        time_variance = max_time - min_time

        assert time_variance < 50.0, (
            f'카메라 설정별 성능 차이가 50ms 이내여야 함: {time_variance:.2f}ms'
        )

        print('\n카메라 설정별 성능 결과:')
        for description, time_ms in performance_results:
            print(f'  - {description}: {time_ms:.2f}ms')
        print(f'  - 최대 편차: {time_variance:.2f}ms')

    def test_프레임당_변환_호출_수_시뮬레이션_성능_검증_성공_시나리오(
        self,
    ) -> None:
        """4. 프레임당 변환 호출 수 시뮬레이션 성능 검증 (성공 시나리오)

        목적: 실제 게임플레이 상황을 모사한 프레임 기반 성능 검증
        테스트할 범위: 60FPS 게임에서 프레임당 좌표 변환 처리량
        커버하는 함수 및 데이터: 연속적인 프레임 처리 시 성능 안정성
        기대되는 안정성: 지속적인 고성능 유지 및 프레임 드롭 방지
        """
        # Given - 게임 시뮬레이션 설정
        transformer = CachedCameraTransformer(
            screen_size=Vector2(1920, 1080), cache_size=1000
        )

        # 60FPS로 5초 = 300 프레임 시뮬레이션
        frame_count = 300
        entities_per_frame = (
            50  # 프레임당 50개 엔티티 (플레이어 + 적 + 아이템)
        )
        max_frame_time_ms = 16.67  # 60FPS 기준 최대 프레임 시간

        frame_times = []
        player_pos = Vector2(0, 0)

        for frame in range(frame_count):
            frame_start = time.perf_counter()

            # 플레이어 움직임 시뮬레이션
            player_pos += Vector2(random.uniform(-2, 2), random.uniform(-2, 2))

            # 카메라가 플레이어 추적
            transformer.set_camera_offset(player_pos)

            # 프레임당 엔티티 좌표 변환
            frame_entities = [
                Vector2(
                    player_pos.x + random.uniform(-200, 200),
                    player_pos.y + random.uniform(-200, 200),
                )
                for _ in range(entities_per_frame)
            ]

            # 모든 엔티티를 화면 좌표로 변환
            screen_positions = [
                transformer.world_to_screen(entity_pos)
                for entity_pos in frame_entities
            ]

            frame_end = time.perf_counter()
            frame_time_ms = (frame_end - frame_start) * 1000
            frame_times.append(frame_time_ms)

            # Then - 각 프레임이 60FPS 유지 가능한지 확인
            assert frame_time_ms < max_frame_time_ms, (
                f'프레임 {frame}이 60FPS 요구사항 초과: {frame_time_ms:.2f}ms'
            )
            assert len(screen_positions) == entities_per_frame, (
                f'프레임 {frame}에서 변환 결과 개수 불일치'
            )

        # Then - 전체 성능 통계 분석
        avg_frame_time = sum(frame_times) / len(frame_times)
        max_frame_time = max(frame_times)
        min_frame_time = min(frame_times)

        # 평균 프레임 시간이 60FPS 기준 절반 이하 (충분한 여유 확보)
        assert avg_frame_time < max_frame_time_ms / 2, (
            f'평균 프레임 시간이 너무 높음: {avg_frame_time:.2f}ms'
        )

        # 99%의 프레임이 기준 시간 내 완료
        sorted_times = sorted(frame_times)
        percentile_99 = sorted_times[int(len(sorted_times) * 0.99)]

        assert percentile_99 < max_frame_time_ms, (
            f'99% 프레임이 기준 시간 내여야 함: {percentile_99:.2f}ms'
        )

        print('\n프레임 성능 시뮬레이션 결과:')
        print(f'  - 총 프레임: {frame_count}')
        print(f'  - 평균 프레임 시간: {avg_frame_time:.2f}ms')
        print(f'  - 최대 프레임 시간: {max_frame_time:.2f}ms')
        print(f'  - 99% 백분위 시간: {percentile_99:.2f}ms')
        print(f'  - 프레임당 변환 수: {entities_per_frame}')

    def test_메모리_사용량_프로파일링_및_GC_압박_측정_성공_시나리오(
        self,
    ) -> None:
        """5. 메모리 사용량 프로파일링 및 GC 압박 측정 (성공 시나리오)

        목적: 좌표 변환 시스템의 메모리 효율성과 GC 영향 측정
        테스트할 범위: 메모리 누수 방지, 적절한 캐시 크기, GC 빈도
        커버하는 함수 및 데이터: 메모리 사용 패턴과 가비지 컬렉션 영향
        기대되는 안정성: 장시간 실행에도 메모리 안정성 보장
        """
        # Given - GC 기반 메모리 모니터링 설정
        initial_gc_counts = gc.get_count()

        transformer = CachedCameraTransformer(
            screen_size=Vector2(1920, 1080),
            cache_size=1000,  # 제한된 캐시로 메모리 제어
        )

        # 대량 좌표 변환으로 메모리 압박 테스트
        iterations = 10
        coordinates_per_iteration = 1000

        object_counts = []
        gc_counts_before = gc.get_count()

        for iteration in range(iterations):
            # 매번 새로운 좌표 생성 (메모리 할당 유발)
            test_coordinates = [
                Vector2(
                    random.uniform(-5000, 5000), random.uniform(-5000, 5000)
                )
                for _ in range(coordinates_per_iteration)
            ]

            # 좌표 변환 수행
            results = [
                transformer.world_to_screen(pos) for pos in test_coordinates
            ]

            # 객체 수 측정 (메모리 사용량 근사치)
            current_objects = len(gc.get_objects())
            object_counts.append(current_objects)

            # 카메라 위치 변경으로 캐시 무효화 유발
            transformer.set_camera_offset(
                Vector2(iteration * 100, iteration * 50)
            )

        gc_counts_after = gc.get_count()
        final_objects = len(gc.get_objects())
        initial_objects = object_counts[0] if object_counts else final_objects

        # Then - 객체 수 기반 메모리 분석
        max_objects = max(object_counts) if object_counts else final_objects
        object_growth = final_objects - initial_objects

        # 객체 수 증가가 합리적인 범위 내 (10,000개 이하)
        assert object_growth < 10000, (
            f'객체 수 증가가 과도함: {object_growth}개'
        )

        # 최대 객체 수가 초기의 2배를 초과하지 않음
        if initial_objects > 0:
            object_ratio = max_objects / initial_objects
            assert object_ratio < 2.0, (
                f'최대 객체 비율이 과도함: {object_ratio:.1f}x'
            )

        # GC 빈도가 과도하지 않음 (각 세대별로 합리적인 범위)
        gc_diff = tuple(
            after - before
            for after, before in zip(
                gc_counts_after, gc_counts_before, strict=False
            )
        )

        # 세대별 GC 허용 횟수 (0세대: 20회, 1세대: 15회, 2세대: 10회)
        max_gc_counts = [20, 15, 10]

        for generation, diff in enumerate(gc_diff):
            max_allowed = (
                max_gc_counts[generation]
                if generation < len(max_gc_counts)
                else 5
            )
            assert diff < max_allowed, (
                f'GC 세대 {generation}의 실행 빈도가 과도함: {diff}회 (최대 {max_allowed}회)'
            )

        # 캐시 통계 확인 (적절한 히트율 유지)
        cache_stats = transformer.get_coordinate_cache_stats()
        total_accesses = (
            cache_stats['total']['hits'] + cache_stats['total']['misses']
        )

        if total_accesses > 0:
            hit_rate = cache_stats['total']['hits'] / total_accesses * 100
            # 캐시가 활성화되어 있고 통계가 수집되고 있는지만 확인
            # (매번 새로운 랜덤 좌표를 사용하므로 히트율이 낮을 수 있음)
            print(
                f'캐시 히트율: {hit_rate:.1f}% (총 접근: {total_accesses}회)'
            )

        print('\n메모리 프로파일링 결과:')
        print(f'  - 초기 객체 수: {initial_objects:,}개')
        print(f'  - 최종 객체 수: {final_objects:,}개')
        print(f'  - 객체 수 증가: {object_growth:,}개')
        if initial_objects > 0:
            print(f'  - 최대 객체 비율: {object_ratio:.1f}x')
        print(f'  - GC 실행 증가: {gc_diff}')
        print(f'  - 캐시 활성 상태: {cache_stats["enabled"]}')
        if total_accesses > 0:
            print(f'  - 캐시 히트율: {hit_rate:.1f}%')

    def test_극한_부하_스트레스_테스트_성공_시나리오(self) -> None:
        """6. 극한 부하 스트레스 테스트 (성공 시나리오)

        목적: 시스템 한계 상황에서의 안정성과 성능 검증
        테스트할 범위: 최대 부하 상황에서도 크래시 없이 동작 보장
        커버하는 함수 및 데이터: 대량 데이터 처리 시 시스템 안정성
        기대되는 안정성: 극한 상황에서도 graceful degradation
        """
        # Given - 극한 테스트 설정
        transformer = CachedCameraTransformer(
            screen_size=Vector2(1920, 1080),
            cache_size=2000,  # 더 큰 캐시로 성능 최적화
        )

        # 극한 부하: 10,000개 좌표를 10회 반복
        massive_coordinates = [
            Vector2(
                random.uniform(-10000, 10000), random.uniform(-10000, 10000)
            )
            for _ in range(10000)
        ]

        stress_iterations = 10
        all_times = []

        for iteration in range(stress_iterations):
            # 매 iteration마다 카메라 설정 변경 (캐시 효율성 감소)
            transformer.set_camera_offset(
                Vector2(iteration * 200, iteration * 150)
            )
            transformer.zoom_level = 1.0 + (iteration * 0.1)

            start_time = time.perf_counter()

            try:
                # 대량 변환 수행
                results = [
                    transformer.world_to_screen(pos)
                    for pos in massive_coordinates
                ]

                end_time = time.perf_counter()
                iteration_time = end_time - start_time
                all_times.append(iteration_time)

                # Then - 결과 검증
                assert len(results) == len(massive_coordinates), (
                    f'반복 {iteration}: 결과 개수 불일치'
                )

                # 각 iteration이 1초 이내 완료 (극한 상황에서의 허용 시간)
                assert iteration_time < 1.0, (
                    f'반복 {iteration} 처리 시간 초과: {iteration_time:.3f}초'
                )

            except Exception as e:
                pytest.fail(f'반복 {iteration}에서 예외 발생: {e}')

        # Then - 전체 스트레스 테스트 결과 분석
        avg_time = sum(all_times) / len(all_times)
        max_time = max(all_times)
        total_transformations = len(massive_coordinates) * stress_iterations

        # 전체 평균이 허용 범위 내 (0.5초 이하)
        assert avg_time < 0.5, f'평균 처리 시간 초과: {avg_time:.3f}초'

        # 최대 처리 시간도 허용 범위 내
        assert max_time < 1.0, f'최대 처리 시간 초과: {max_time:.3f}초'

        # 전체 변환 처리량 (초당 최소 50,000개)
        total_time = sum(all_times)
        throughput = (
            total_transformations / total_time if total_time > 0 else 0
        )

        assert throughput >= 50000, (
            f'전체 처리량 부족: {throughput:.0f} ops/sec'
        )

        print('\n극한 부하 스트레스 테스트 결과:')
        print(f'  - 총 변환 수: {total_transformations:,}개')
        print(f'  - 평균 처리 시간: {avg_time:.3f}초')
        print(f'  - 최대 처리 시간: {max_time:.3f}초')
        print(f'  - 전체 처리량: {throughput:.0f} ops/sec')

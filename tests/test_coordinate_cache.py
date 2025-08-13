from src.core.cached_camera_transformer import CachedCameraTransformer
from src.core.coordinate_cache import (
    CacheKey,
    CoordinateTransformCache,
    LRUCache,
)
from src.utils.vector2 import Vector2


class TestCacheKey:
    def test_캐시_키_생성_및_해싱_정확성_검증_성공_시나리오(self) -> None:
        """1. 캐시 키 생성 및 해싱 정확성 검증 (성공 시나리오)

        목적: CacheKey의 생성자와 해싱 메커니즘 검증
        테스트할 범위: __init__, __hash__, __eq__ 메서드
        커버하는 함수 및 데이터: 좌표값 기반 캐시 키 생성과 비교
        기대되는 안정성: 동일한 좌표는 같은 키, 다른 좌표는 다른 키 보장
        """
        # Given - 동일한 좌표로 캐시 키 생성
        key1 = CacheKey(100.0, 200.0, 10.0, 20.0, 1.5, 800.0, 600.0)
        key2 = CacheKey(100.0, 200.0, 10.0, 20.0, 1.5, 800.0, 600.0)

        # Then - 동일성 확인
        assert key1 == key2, '동일한 좌표의 키는 같아야 함'
        assert hash(key1) == hash(key2), (
            '동일한 좌표의 키는 같은 해시를 가져야 함'
        )

        # Given - 다른 좌표로 캐시 키 생성
        key3 = CacheKey(100.1, 200.0, 10.0, 20.0, 1.5, 800.0, 600.0)

        # Then - 차이 확인
        assert key1 != key3, '다른 좌표의 키는 달라야 함'

    def test_캐시_키_부동소수점_허용오차_검증_성공_시나리오(self) -> None:
        """2. 캐시 키 부동소수점 허용오차 검증 (성공 시나리오)

        목적: 부동소수점 정밀도 문제로 인한 캐시 미스 방지 검증
        테스트할 범위: __eq__ 메서드의 허용오차 처리
        커버하는 함수 및 데이터: 0.001 허용오차 내 좌표 비교
        기대되는 안정성: 미세한 차이는 같은 키로 인식하여 캐시 효율성 보장
        """
        # Given - 미세한 차이를 가진 키들 생성
        key1 = CacheKey(100.0, 200.0, 10.0, 20.0, 1.5, 800.0, 600.0)
        key2 = CacheKey(
            100.0005, 200.0002, 10.0001, 20.0003, 1.5001, 800.0, 600.0
        )

        # Then - 허용오차 내에서는 동일하게 인식
        assert key1 == key2, '허용오차 내 좌표는 같은 키로 인식되어야 함'

        # Given - 허용오차를 초과하는 차이
        key3 = CacheKey(100.002, 200.0, 10.0, 20.0, 1.5, 800.0, 600.0)

        # Then - 허용오차 초과 시 다른 키로 인식
        assert key1 != key3, '허용오차를 초과한 좌표는 다른 키로 인식되어야 함'


class TestLRUCache:
    def test_LRU_캐시_기본_동작_검증_성공_시나리오(self) -> None:
        """3. LRU 캐시 기본 동작 검증 (성공 시나리오)

        목적: LRU 캐시의 저장, 조회, 통계 기능 검증
        테스트할 범위: get, put, get_stats 메서드
        커버하는 함수 및 데이터: 캐시 히트/미스 동작과 통계
        기대되는 안정성: 정확한 캐시 동작과 통계 추적 보장
        """
        # Given - LRU 캐시 생성
        cache = LRUCache[str, int](max_size=3)

        # When - 캐시에 값 저장
        cache.put('key1', 100)
        cache.put('key2', 200)

        # Then - 저장된 값 조회 성공
        assert cache.get('key1') == 100, '저장된 값이 정확히 조회되어야 함'
        assert cache.get('key2') == 200, '저장된 값이 정확히 조회되어야 함'

        # When - 존재하지 않는 키 조회
        result = cache.get('key3')

        # Then - None 반환
        assert result is None, '존재하지 않는 키는 None을 반환해야 함'

        # When - 통계 확인
        stats = cache.get_stats()

        # Then - 정확한 통계
        assert stats.hits == 2, '히트 수가 정확해야 함'
        assert stats.misses == 1, '미스 수가 정확해야 함'
        assert stats.hit_rate == 2 / 3, '히트율이 정확해야 함'

    def test_LRU_캐시_용량_초과_시_제거_검증_성공_시나리오(self) -> None:
        """4. LRU 캐시 용량 초과 시 제거 검증 (성공 시나리오)

        목적: 캐시 용량 초과 시 가장 오래된 항목 제거 동작 검증
        테스트할 범위: put 메서드의 LRU 제거 로직
        커버하는 함수 및 데이터: 최대 용량 초과 시 오래된 항목 제거
        기대되는 안정성: 정확한 LRU 순서로 항목 제거 보장
        """
        # Given - 최대 크기 2인 캐시
        cache = LRUCache[str, int](max_size=2)

        # When - 캐시를 가득 채움
        cache.put('key1', 100)
        cache.put('key2', 200)

        # When - 용량 초과 항목 추가
        cache.put('key3', 300)

        # Then - 가장 오래된 항목 제거 확인
        assert cache.get('key1') is None, '가장 오래된 항목이 제거되어야 함'
        assert cache.get('key2') == 200, '최근 사용된 항목은 유지되어야 함'
        assert cache.get('key3') == 300, '새로 추가된 항목은 존재해야 함'

        # When - 통계 확인
        stats = cache.get_stats()

        # Then - 제거 통계 확인
        assert stats.evictions == 1, '제거 횟수가 정확해야 함'

    def test_LRU_캐시_접근_순서_업데이트_검증_성공_시나리오(self) -> None:
        """5. LRU 캐시 접근 순서 업데이트 검증 (성공 시나리오)

        목적: 항목 접근 시 LRU 순서 업데이트 동작 검증
        테스트할 범위: get 메서드의 LRU 순서 갱신
        커버하는 함수 및 데이터: 접근한 항목의 최근 사용 위치로 이동
        기대되는 안정성: 접근 빈도에 따른 정확한 LRU 순서 유지 보장
        """
        # Given - 최대 크기 2인 캐시에 항목 저장
        cache = LRUCache[str, int](max_size=2)
        cache.put('key1', 100)
        cache.put('key2', 200)

        # When - key1 접근하여 최근 사용으로 변경
        cache.get('key1')

        # When - 새 항목 추가로 용량 초과
        cache.put('key3', 300)

        # Then - 접근하지 않은 key2가 제거되어야 함
        assert cache.get('key1') == 100, '접근한 항목은 유지되어야 함'
        assert cache.get('key2') is None, '접근하지 않은 항목이 제거되어야 함'
        assert cache.get('key3') == 300, '새 항목은 존재해야 함'


class TestCoordinateTransformCache:
    def test_좌표_변환_캐시_기본_동작_검증_성공_시나리오(self) -> None:
        """6. 좌표 변환 캐시 기본 동작 검증 (성공 시나리오)

        목적: CoordinateTransformCache의 저장과 조회 기능 검증
        테스트할 범위: get/put world_to_screen, screen_to_world
        커버하는 함수 및 데이터: 좌표 변환 결과 캐싱과 조회
        기대되는 안정성: 정확한 좌표 변환 캐싱 보장
        """
        # Given - 좌표 변환 캐시 생성
        cache = CoordinateTransformCache(max_size=100)
        world_pos = Vector2(100, 50)
        camera_offset = Vector2(10, 20)
        zoom_level = 1.5
        screen_size = Vector2(800, 600)
        screen_result = Vector2(540, 445)

        # When - 캐시에 저장
        cache.put_world_to_screen(
            world_pos, camera_offset, zoom_level, screen_size, screen_result
        )

        # When - 캐시에서 조회
        cached_result = cache.get_world_to_screen(
            world_pos, camera_offset, zoom_level, screen_size
        )

        # Then - 저장된 값 정확히 조회
        assert cached_result is not None, '캐시된 결과가 존재해야 함'
        assert cached_result.distance_to(screen_result) < 0.001, (
            '캐시된 결과가 정확해야 함'
        )

        # When - 다른 좌표로 조회
        other_result = cache.get_world_to_screen(
            Vector2(200, 100), camera_offset, zoom_level, screen_size
        )

        # Then - 캐시 미스
        assert other_result is None, '캐시되지 않은 좌표는 None을 반환해야 함'

    def test_좌표_변환_캐시_통계_추적_검증_성공_시나리오(self) -> None:
        """7. 좌표 변환 캐시 통계 추적 검증 (성공 시나리오)

        목적: 캐시 히트율과 성능 통계의 정확성 검증
        테스트할 범위: get_cache_stats 메서드
        커버하는 함수 및 데이터: 히트율, 미스율, 캐시 크기 통계
        기대되는 안정성: 정확한 성능 모니터링을 위한 통계 제공 보장
        """
        # Given - 좌표 변환 캐시 설정
        cache = CoordinateTransformCache(max_size=10)
        world_pos = Vector2(100, 50)
        camera_offset = Vector2.zero()
        zoom_level = 1.0
        screen_size = Vector2(800, 600)
        screen_result = Vector2(500, 350)

        # When - 캐시에 저장 후 여러 번 조회
        cache.put_world_to_screen(
            world_pos, camera_offset, zoom_level, screen_size, screen_result
        )
        cache.get_world_to_screen(
            world_pos, camera_offset, zoom_level, screen_size
        )  # 히트
        cache.get_world_to_screen(
            world_pos, camera_offset, zoom_level, screen_size
        )  # 히트
        cache.get_world_to_screen(
            Vector2(200, 100), camera_offset, zoom_level, screen_size
        )  # 미스

        # When - 통계 조회
        stats = cache.get_cache_stats()

        # Then - 정확한 통계 확인
        assert stats['total']['hits'] == 2, '총 히트 수가 정확해야 함'
        assert stats['total']['misses'] == 1, '총 미스 수가 정확해야 함'
        assert abs(stats['total']['hit_rate'] - 2 / 3) < 0.001, (
            '히트율이 정확해야 함'
        )
        assert stats['enabled'], '캐시가 활성화되어 있어야 함'

    def test_좌표_변환_캐시_비활성화_동작_검증_성공_시나리오(self) -> None:
        """8. 좌표 변환 캐시 비활성화 동작 검증 (성공 시나리오)

        목적: 캐시 비활성화 시 저장/조회 무시 동작 검증
        테스트할 범위: set_enabled, is_enabled 메서드
        커버하는 함수 및 데이터: 캐시 활성/비활성 상태 전환
        기대되는 안정성: 캐시 비활성화 시 완전한 우회 보장
        """
        # Given - 캐시 생성 및 비활성화
        cache = CoordinateTransformCache()
        cache.set_enabled(False)

        # When - 비활성 상태에서 저장 시도
        world_pos = Vector2(100, 50)
        camera_offset = Vector2.zero()
        zoom_level = 1.0
        screen_size = Vector2(800, 600)
        screen_result = Vector2(500, 350)

        cache.put_world_to_screen(
            world_pos, camera_offset, zoom_level, screen_size, screen_result
        )

        # Then - 비활성 상태 확인
        assert not cache.is_enabled(), '캐시가 비활성화되어 있어야 함'

        # When - 조회 시도
        result = cache.get_world_to_screen(
            world_pos, camera_offset, zoom_level, screen_size
        )

        # Then - 캐시 우회 확인
        assert result is None, '비활성화된 캐시는 항상 None을 반환해야 함'


class TestCachedCameraTransformer:
    def test_캐시_적용_변환기_기본_동작_검증_성공_시나리오(self) -> None:
        """9. 캐시 적용 변환기 기본 동작 검증 (성공 시나리오)

        목적: CachedCameraTransformer의 캐시 기능 통합 검증
        테스트할 범위: world_to_screen의 캐싱 동작
        커버하는 함수 및 데이터: 변환 결과 자동 캐싱과 재사용
        기대되는 안정성: 투명한 캐싱으로 성능 향상과 정확성 동시 보장
        """
        # Given - 캐시 적용 변환기 생성
        transformer = CachedCameraTransformer(
            Vector2(800, 600), cache_size=100
        )
        world_pos = Vector2(100, 50)

        # When - 첫 번째 변환 (캐시 미스)
        result1 = transformer.world_to_screen(world_pos)

        # When - 동일 좌표 두 번째 변환 (캐시 히트)
        result2 = transformer.world_to_screen(world_pos)

        # Then - 결과 일치 확인
        assert result1.distance_to(result2) < 0.001, (
            '캐시된 결과가 원본과 일치해야 함'
        )

        # When - 캐시 통계 확인
        stats = transformer.get_coordinate_cache_stats()

        # Then - 캐시 동작 확인
        assert stats['total']['hits'] >= 1, '캐시 히트가 발생해야 함'
        assert stats['total']['misses'] >= 1, '캐시 미스가 발생해야 함'

    def test_캐시_무효화_동작_검증_성공_시나리오(self) -> None:
        """10. 캐시 무효화 동작 검증 (성공 시나리오)

        목적: 카메라 설정 변경 시 캐시 자동 무효화 검증
        테스트할 범위: set_camera_offset 등의 캐시 무효화
        커버하는 함수 및 데이터: 설정 변경 시 캐시 클리어
        기대되는 안정성: 설정 변경 시 올바른 결과 보장을 위한 캐시 무효화
        """
        # Given - 캐시 적용 변환기로 캐시 데이터 생성
        transformer = CachedCameraTransformer(Vector2(800, 600))
        world_pos = Vector2(100, 50)

        # When - 변환 수행하여 캐시 생성
        transformer.world_to_screen(world_pos)
        initial_stats = transformer.get_coordinate_cache_stats()

        # When - 카메라 오프셋 변경
        transformer.set_camera_offset(Vector2(50, 30))

        # When - 동일 좌표 변환
        transformer.world_to_screen(world_pos)
        updated_stats = transformer.get_coordinate_cache_stats()

        # Then - 캐시 무효화로 인한 새로운 미스 확인
        assert (
            updated_stats['total']['misses'] > initial_stats['total']['misses']
        ), '캐시 무효화로 새로운 미스가 발생해야 함'

    def test_캐시_성능_벤치마크_검증_성공_시나리오(self) -> None:
        """11. 캐시 성능 벤치마크 검증 (성공 시나리오)

        목적: 캐시 활성/비활성 시 성능 차이 측정 기능 검증
        테스트할 범위: benchmark_cache_performance 메서드
        커버하는 함수 및 데이터: 캐시 성능 측정 결과
        기대되는 안정성: 캐시 효과 정량적 측정을 통한 최적화 지원
        """
        # Given - 캐시 적용 변환기와 테스트 좌표들
        transformer = CachedCameraTransformer(Vector2(800, 600))
        test_positions = [Vector2(i * 10, i * 5) for i in range(10)]

        # When - 성능 벤치마크 실행
        benchmark_result = transformer.benchmark_cache_performance(
            test_positions, iterations=10
        )

        # Then - 벤치마크 결과 구조 확인
        assert 'test_config' in benchmark_result, (
            '테스트 설정 정보가 있어야 함'
        )
        assert 'performance' in benchmark_result, '성능 측정 결과가 있어야 함'
        assert 'cache_stats' in benchmark_result, '캐시 통계가 있어야 함'

        # Then - 기본적인 성능 지표 확인
        assert benchmark_result['performance']['no_cache_time'] > 0, (
            '캐시 없는 실행 시간이 측정되어야 함'
        )
        assert benchmark_result['performance']['cache_time'] > 0, (
            '캐시 있는 실행 시간이 측정되어야 함'
        )
        assert benchmark_result['test_config']['total_operations'] == 100, (
            '총 연산 수가 정확해야 함'
        )

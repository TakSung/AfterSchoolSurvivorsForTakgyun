from ..utils.vector2 import Vector2
from .camera_based_transformer import CameraBasedTransformer
from .coordinate_cache import CoordinateTransformCache


class CachedCameraTransformer(CameraBasedTransformer):
    __slots__ = ('_cache_enabled', '_coordinate_cache')

    def __init__(
        self,
        screen_size: Vector2,
        camera_offset: Vector2 | None = None,
        zoom_level: float = 1.0,
        cache_size: int = 1000,
        cache_enabled: bool = True,
    ) -> None:
        super().__init__(screen_size, camera_offset, zoom_level)
        self._coordinate_cache = CoordinateTransformCache(cache_size)
        self._cache_enabled = cache_enabled
        self._coordinate_cache.set_enabled(cache_enabled)

    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        if not self._cache_enabled:
            return super().world_to_screen(world_pos)

        # 캐시에서 조회
        cached_result = self._coordinate_cache.get_world_to_screen(
            world_pos, self._camera_offset, self._zoom_level, self._screen_size
        )

        if cached_result is not None:
            return cached_result

        # 캐시 미스 - 계산 후 캐시에 저장
        result = super().world_to_screen(world_pos)
        self._coordinate_cache.put_world_to_screen(
            world_pos,
            self._camera_offset,
            self._zoom_level,
            self._screen_size,
            result,
        )

        return result

    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        if not self._cache_enabled:
            return super().screen_to_world(screen_pos)

        # 캐시에서 조회
        cached_result = self._coordinate_cache.get_screen_to_world(
            screen_pos,
            self._camera_offset,
            self._zoom_level,
            self._screen_size,
        )

        if cached_result is not None:
            return cached_result

        # 캐시 미스 - 계산 후 캐시에 저장
        result = super().screen_to_world(screen_pos)
        self._coordinate_cache.put_screen_to_world(
            screen_pos,
            self._camera_offset,
            self._zoom_level,
            self._screen_size,
            result,
        )

        return result

    def set_camera_offset(self, offset: Vector2) -> None:
        if self._camera_offset != offset:
            super().set_camera_offset(offset)
            self._coordinate_cache.clear()  # 카메라 변경 시 캐시 무효화

    @property
    def zoom_level(self) -> float:
        return super().zoom_level

    @zoom_level.setter
    def zoom_level(self, value: float) -> None:
        old_zoom = self._zoom_level
        super(CachedCameraTransformer, self.__class__).zoom_level.fset(
            self, value
        )
        if old_zoom != self._zoom_level:
            self._coordinate_cache.clear()  # 줌 변경 시 캐시 무효화

    @property
    def screen_size(self) -> Vector2:
        return super().screen_size

    @screen_size.setter
    def screen_size(self, size: Vector2) -> None:
        old_size = self._screen_size
        super(CachedCameraTransformer, self.__class__).screen_size.fset(
            self, size
        )
        if old_size != self._screen_size:
            self._coordinate_cache.clear()  # 화면 크기 변경 시 캐시 무효화

    def invalidate_cache(self) -> None:
        super().invalidate_cache()
        self._coordinate_cache.clear()

    def set_cache_enabled(self, enabled: bool) -> None:
        self._cache_enabled = enabled
        self._coordinate_cache.set_enabled(enabled)

    def is_cache_enabled(self) -> bool:
        return self._cache_enabled

    def resize_cache(self, new_size: int) -> None:
        self._coordinate_cache.resize(new_size)

    def get_coordinate_cache_stats(self) -> dict[str, any]:
        return self._coordinate_cache.get_cache_stats()

    def reset_cache_stats(self) -> None:
        self._coordinate_cache.reset_stats()

    def get_cache_stats(self) -> dict[str, any]:
        base_stats = super().get_cache_stats()
        coordinate_stats = self.get_coordinate_cache_stats()

        return {
            **base_stats,
            'coordinate_cache': coordinate_stats,
            'cache_enabled': self._cache_enabled,
        }

    def transform_multiple_points(
        self, world_positions: list[Vector2]
    ) -> list[Vector2]:
        if not self._cache_enabled or not world_positions:
            return super().transform_multiple_points(world_positions)

        screen_positions = []
        uncached_positions = []
        uncached_indices = []

        # 캐시된 결과와 캐시되지 않은 좌표 분리
        for i, world_pos in enumerate(world_positions):
            cached_result = self._coordinate_cache.get_world_to_screen(
                world_pos,
                self._camera_offset,
                self._zoom_level,
                self._screen_size,
            )
            if cached_result is not None:
                screen_positions.append(cached_result)
            else:
                screen_positions.append(None)  # 임시 플레이스홀더
                uncached_positions.append(world_pos)
                uncached_indices.append(i)

        # 캐시되지 않은 좌표들을 일괄 변환
        if uncached_positions:
            uncached_results = super().transform_multiple_points(
                uncached_positions
            )

            # 결과를 캐시에 저장하고 리스트에 반영
            for idx, (world_pos, screen_pos) in enumerate(
                zip(uncached_positions, uncached_results, strict=False)
            ):
                self._coordinate_cache.put_world_to_screen(
                    world_pos,
                    self._camera_offset,
                    self._zoom_level,
                    self._screen_size,
                    screen_pos,
                )
                screen_positions[uncached_indices[idx]] = screen_pos

        return screen_positions

    def benchmark_cache_performance(
        self, test_positions: list[Vector2], iterations: int = 1000
    ) -> dict[str, any]:
        import time

        # 캐시 통계 초기화
        self.reset_cache_stats()

        # 캐시 비활성화 벤치마크
        self.set_cache_enabled(False)
        start_time = time.perf_counter()

        for _ in range(iterations):
            for pos in test_positions:
                self.world_to_screen(pos)

        no_cache_time = time.perf_counter() - start_time

        # 캐시 활성화 벤치마크
        self.set_cache_enabled(True)
        self.reset_cache_stats()

        start_time = time.perf_counter()

        for _ in range(iterations):
            for pos in test_positions:
                self.world_to_screen(pos)

        cache_time = time.perf_counter() - start_time

        cache_stats = self.get_coordinate_cache_stats()

        return {
            'test_config': {
                'positions_count': len(test_positions),
                'iterations': iterations,
                'total_operations': len(test_positions) * iterations,
            },
            'performance': {
                'no_cache_time': no_cache_time,
                'cache_time': cache_time,
                'speedup_ratio': no_cache_time / cache_time
                if cache_time > 0
                else 0,
                'operations_per_second_no_cache': (
                    len(test_positions) * iterations
                )
                / no_cache_time
                if no_cache_time > 0
                else 0,
                'operations_per_second_cache': (
                    len(test_positions) * iterations
                )
                / cache_time
                if cache_time > 0
                else 0,
            },
            'cache_stats': cache_stats,
        }

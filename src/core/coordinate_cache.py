from collections import OrderedDict
from dataclasses import dataclass
from typing import Generic, TypeVar

from ..utils.vector2 import Vector2

T = TypeVar('T')
K = TypeVar('K')


@dataclass(frozen=True)
class CacheKey:
    world_x: float
    world_y: float
    camera_x: float
    camera_y: float
    zoom: float
    screen_width: float
    screen_height: float

    def __hash__(self) -> int:
        return hash(
            (
                round(self.world_x, 3),
                round(self.world_y, 3),
                round(self.camera_x, 3),
                round(self.camera_y, 3),
                round(self.zoom, 3),
                round(self.screen_width),
                round(self.screen_height),
            )
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CacheKey):
            return False
        return (
            abs(self.world_x - other.world_x) < 0.001
            and abs(self.world_y - other.world_y) < 0.001
            and abs(self.camera_x - other.camera_x) < 0.001
            and abs(self.camera_y - other.camera_y) < 0.001
            and abs(self.zoom - other.zoom) < 0.001
            and abs(self.screen_width - other.screen_width) < 0.001
            and abs(self.screen_height - other.screen_height) < 0.001
        )


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    max_size: int = 0
    current_size: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    @property
    def miss_rate(self) -> float:
        return 1.0 - self.hit_rate

    def reset(self) -> None:
        self.hits = 0
        self.misses = 0
        self.evictions = 0


class LRUCache(Generic[K, T]):
    __slots__ = ('_cache', '_max_size', '_stats')

    def __init__(self, max_size: int = 1000):
        self._cache: OrderedDict[K, T] = OrderedDict()
        self._max_size = max_size
        self._stats = CacheStats(max_size=max_size)

    def get(self, key: K) -> T | None:
        if key in self._cache:
            # LRU: 최근 사용된 항목을 끝으로 이동
            value = self._cache.pop(key)
            self._cache[key] = value
            self._stats.hits += 1
            return value

        self._stats.misses += 1
        return None

    def put(self, key: K, value: T) -> None:
        if key in self._cache:
            # 기존 키 업데이트
            self._cache.pop(key)
        elif len(self._cache) >= self._max_size:
            # 캐시가 가득 찬 경우 가장 오래된 항목 제거
            self._cache.popitem(last=False)
            self._stats.evictions += 1

        self._cache[key] = value
        self._stats.current_size = len(self._cache)

    def clear(self) -> None:
        self._cache.clear()
        self._stats.current_size = 0

    def get_stats(self) -> CacheStats:
        self._stats.current_size = len(self._cache)
        return self._stats

    def resize(self, new_max_size: int) -> None:
        self._max_size = new_max_size
        self._stats.max_size = new_max_size

        # 새로운 크기가 현재 크기보다 작으면 초과 항목 제거
        while len(self._cache) > new_max_size:
            self._cache.popitem(last=False)
            self._stats.evictions += 1

        self._stats.current_size = len(self._cache)


class CoordinateTransformCache:
    __slots__ = (
        '_enabled',
        '_screen_to_world_cache',
        '_world_to_screen_cache',
    )

    def __init__(self, max_size: int = 1000):
        self._world_to_screen_cache = LRUCache[CacheKey, Vector2](max_size)
        self._screen_to_world_cache = LRUCache[CacheKey, Vector2](max_size)
        self._enabled = True

    def get_world_to_screen(
        self,
        world_pos: Vector2,
        camera_offset: Vector2,
        zoom_level: float,
        screen_size: Vector2,
    ) -> Vector2 | None:
        if not self._enabled:
            return None

        key = CacheKey(
            world_pos.x,
            world_pos.y,
            camera_offset.x,
            camera_offset.y,
            zoom_level,
            screen_size.x,
            screen_size.y,
        )
        return self._world_to_screen_cache.get(key)

    def put_world_to_screen(
        self,
        world_pos: Vector2,
        camera_offset: Vector2,
        zoom_level: float,
        screen_size: Vector2,
        screen_pos: Vector2,
    ) -> None:
        if not self._enabled:
            return

        key = CacheKey(
            world_pos.x,
            world_pos.y,
            camera_offset.x,
            camera_offset.y,
            zoom_level,
            screen_size.x,
            screen_size.y,
        )
        self._world_to_screen_cache.put(key, screen_pos.copy())

    def get_screen_to_world(
        self,
        screen_pos: Vector2,
        camera_offset: Vector2,
        zoom_level: float,
        screen_size: Vector2,
    ) -> Vector2 | None:
        if not self._enabled:
            return None

        key = CacheKey(
            screen_pos.x,
            screen_pos.y,
            camera_offset.x,
            camera_offset.y,
            zoom_level,
            screen_size.x,
            screen_size.y,
        )
        return self._screen_to_world_cache.get(key)

    def put_screen_to_world(
        self,
        screen_pos: Vector2,
        camera_offset: Vector2,
        zoom_level: float,
        screen_size: Vector2,
        world_pos: Vector2,
    ) -> None:
        if not self._enabled:
            return

        key = CacheKey(
            screen_pos.x,
            screen_pos.y,
            camera_offset.x,
            camera_offset.y,
            zoom_level,
            screen_size.x,
            screen_size.y,
        )
        self._screen_to_world_cache.put(key, world_pos.copy())

    def clear(self) -> None:
        self._world_to_screen_cache.clear()
        self._screen_to_world_cache.clear()

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        if not enabled:
            self.clear()

    def is_enabled(self) -> bool:
        return self._enabled

    def resize(self, new_max_size: int) -> None:
        self._world_to_screen_cache.resize(new_max_size)
        self._screen_to_world_cache.resize(new_max_size)

    def get_cache_stats(self) -> dict[str, any]:
        w2s_stats = self._world_to_screen_cache.get_stats()
        s2w_stats = self._screen_to_world_cache.get_stats()

        return {
            'enabled': self._enabled,
            'world_to_screen': {
                'hits': w2s_stats.hits,
                'misses': w2s_stats.misses,
                'hit_rate': w2s_stats.hit_rate,
                'evictions': w2s_stats.evictions,
                'current_size': w2s_stats.current_size,
                'max_size': w2s_stats.max_size,
            },
            'screen_to_world': {
                'hits': s2w_stats.hits,
                'misses': s2w_stats.misses,
                'hit_rate': s2w_stats.hit_rate,
                'evictions': s2w_stats.evictions,
                'current_size': s2w_stats.current_size,
                'max_size': s2w_stats.max_size,
            },
            'total': {
                'hits': w2s_stats.hits + s2w_stats.hits,
                'misses': w2s_stats.misses + s2w_stats.misses,
                'hit_rate': (w2s_stats.hits + s2w_stats.hits)
                / max(
                    1,
                    w2s_stats.hits
                    + s2w_stats.hits
                    + w2s_stats.misses
                    + s2w_stats.misses,
                ),
                'evictions': w2s_stats.evictions + s2w_stats.evictions,
                'current_size': w2s_stats.current_size
                + s2w_stats.current_size,
                'max_size': w2s_stats.max_size + s2w_stats.max_size,
            },
        }

    def reset_stats(self) -> None:
        self._world_to_screen_cache.get_stats().reset()
        self._screen_to_world_cache.get_stats().reset()

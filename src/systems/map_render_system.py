"""
MapRenderSystem for rendering map tiles and background with camera offset.

This system processes entities with MapComponent and renders the visible
map tiles with proper camera offset integration.
"""

from typing import TYPE_CHECKING

from ..components.map_component import MapComponent
from ..core.coordinate_manager import CoordinateManager
from ..core.system import System

if TYPE_CHECKING:
    from ..core.entity_manager import EntityManager


class MapRenderSystem(System):
    """
    System that renders map tiles and background based on camera position.

    The MapRenderSystem processes entities with MapComponent to:
    - Calculate visible tile range based on camera offset
    - Render background tiles with pattern variation
    - Apply camera offset for proper world-to-screen transformation
    - Optimize rendering by culling off-screen tiles
    """

    def __init__(self, priority: int = 15) -> None:
        """
        Initialize the MapRenderSystem.

        Args:
            priority: System execution priority (15 = after camera update)
        """
        super().__init__(priority=priority)
        self._coordinate_manager = CoordinateManager.get_instance()

        # AI-NOTE : 2025-08-11 렌더링 대상 화면 크기 설정
        # - 이유: 타일 가시성 계산을 위한 화면 크기 정보 필요
        # - 요구사항: 카메라 시스템과 동일한 화면 해상도
        # - 히스토리: 하드코딩에서 설정 가능한 값으로 확장 예정
        self._screen_width = 800
        self._screen_height = 600

        # AI-DEV : 렌더링 성능 최적화를 위한 캐시 시스템
        # - 문제: 매 프레임 타일 계산으로 인한 성능 저하
        # - 해결책: 이전 프레임의 가시 타일 범위 캐시
        # - 주의사항: 카메라 이동 시 캐시 무효화 필요
        self._cached_tile_range: tuple[tuple[int, int], tuple[int, int]] | None = None
        self._last_camera_offset: tuple[float, float] | None = None

    def initialize(self) -> None:
        """Initialize the map render system."""
        super().initialize()

        # 좌표 변환 시스템 확인
        transformer = self._coordinate_manager.get_transformer()
        if transformer is None:
            pass  # 좌표 변환기 상태 확인만

    def get_required_components(self) -> tuple[type, ...]:
        """
        Get the required component types for this system.

        Returns:
            Tuple containing MapComponent type.
        """
        return (MapComponent,)

    def update(
        self, entity_manager: 'EntityManager', delta_time: float
    ) -> None:
        """
        Update map rendering (no actual rendering here, just data preparation).

        This method prepares tile data for rendering. Actual rendering
        would be handled by a separate rendering pipeline.

        Args:
            entity_manager: Entity manager for accessing entities and components
            delta_time: Time elapsed since last update in seconds
        """
        if not self.enabled:
            return

        # 맵 엔티티들을 필터링
        map_entities = self.filter_entities(entity_manager)

        for map_entity in map_entities:
            map_comp = entity_manager.get_component(map_entity, MapComponent)
            if map_comp is None:
                continue

            # 현재 카메라 오프셋 가져오기
            camera_offset = self._get_current_camera_offset()
            if camera_offset is None:
                continue

            # 가시 타일 범위 계산 (캐시 활용)
            tile_range = self._get_visible_tile_range_cached(
                map_comp, camera_offset
            )

            # AI-NOTE : 2025-08-11 실제 렌더링은 별도 시스템에서 처리
            # - 이유: ECS 아키텍처에서 시스템 간 책임 분리
            # - 요구사항: 렌더링 데이터 준비와 실제 그리기 분리
            # - 히스토리: 단일 시스템에서 책임 분리 아키텍처로 개선

            # 렌더링 데이터를 준비하고 다른 시스템이 사용할 수 있도록 저장
            self._prepare_render_data(map_comp, camera_offset, tile_range)

    def _get_current_camera_offset(self) -> tuple[float, float] | None:
        """
        Get the current camera offset from coordinate manager.

        Returns:
            Camera offset as (x, y) tuple, or None if not available
        """
        transformer = self._coordinate_manager.get_transformer()
        if transformer is None:
            return None

        # AI-DEV : 좌표 변환기에서 카메라 오프셋 추출
        # - 문제: 카메라 오프셋 정보에 접근하는 표준 인터페이스 필요
        # - 해결책: 좌표 변환기의 카메라 오프셋 속성 활용
        # - 주의사항: 좌표 변환기 구현에 따른 인터페이스 의존성
        if hasattr(transformer, 'camera_offset'):
            offset = transformer.camera_offset
            return (offset.x, offset.y) if offset else (0.0, 0.0)

        return (0.0, 0.0)

    def _get_visible_tile_range_cached(
        self,
        map_comp: MapComponent,
        camera_offset: tuple[float, float],
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        """
        Get visible tile range with caching optimization.

        Args:
            map_comp: Map component for tile calculations
            camera_offset: Current camera offset

        Returns:
            ((min_tile_x, min_tile_y), (max_tile_x, max_tile_y))
        """
        # 캐시 유효성 검사
        if (
            self._cached_tile_range is not None
            and self._last_camera_offset is not None
            and self._camera_offset_unchanged(camera_offset)
        ):
            return self._cached_tile_range

        # 새로운 타일 범위 계산
        tile_range = map_comp.get_visible_tile_range(
            camera_offset, self._screen_width, self._screen_height
        )

        # 캐시 업데이트
        self._cached_tile_range = tile_range
        self._last_camera_offset = camera_offset

        return tile_range

    def _camera_offset_unchanged(
        self, current_offset: tuple[float, float]
    ) -> bool:
        """
        Check if camera offset has changed significantly.

        Args:
            current_offset: Current camera offset

        Returns:
            True if offset is unchanged (within threshold), False otherwise
        """
        if self._last_camera_offset is None:
            return False

        # 1픽셀 이하의 변화는 무시
        threshold = 1.0
        dx = abs(current_offset[0] - self._last_camera_offset[0])
        dy = abs(current_offset[1] - self._last_camera_offset[1])

        return dx < threshold and dy < threshold

    def _prepare_render_data(
        self,
        map_comp: MapComponent,
        camera_offset: tuple[float, float],
        tile_range: tuple[tuple[int, int], tuple[int, int]],
    ) -> None:
        """
        Prepare tile rendering data for the rendering pipeline.

        Args:
            map_comp: Map component with tile configuration
            camera_offset: Current camera offset
            tile_range: Range of visible tiles to render
        """
        (min_tile_x, min_tile_y), (max_tile_x, max_tile_y) = tile_range

        # AI-DEV : 타일 렌더링 데이터 준비를 위한 최적화된 루프
        # - 문제: 대량의 타일 데이터 처리 시 성능 고려 필요
        # - 해결책: 필요한 타일만 선별하여 렌더링 데이터 생성
        # - 주의사항: 메모리 사용량과 계산 시간의 균형 고려

        render_tiles = []
        for tile_y in range(min_tile_y, max_tile_y + 1):
            for tile_x in range(min_tile_x, max_tile_x + 1):
                # 맵 경계 검사 (무한 스크롤이 비활성화된 경우)
                if not map_comp.enable_infinite_scroll:
                    world_pos = map_comp.get_tile_world_position(tile_x, tile_y)
                    if not map_comp.is_within_world_bounds(
                        world_pos[0], world_pos[1]
                    ):
                        continue

                # 타일 패턴 타입 계산
                pattern_type = map_comp.get_tile_pattern_type(tile_x, tile_y)

                # 화면 좌표 계산
                world_pos = map_comp.get_tile_world_position(tile_x, tile_y)
                screen_x = world_pos[0] + camera_offset[0]
                screen_y = world_pos[1] + camera_offset[1]

                render_tile_data = {
                    'tile_x': tile_x,
                    'tile_y': tile_y,
                    'screen_x': screen_x,
                    'screen_y': screen_y,
                    'pattern_type': pattern_type,
                    'tile_size': map_comp.tile_size,
                    'grid_color': map_comp.grid_color,
                    'background_color': map_comp.background_color,
                }

                render_tiles.append(render_tile_data)

        # 렌더링 데이터를 시스템에 저장 (다른 시스템에서 접근 가능)
        self._current_render_tiles = render_tiles

    def get_render_tiles(self) -> list[dict]:
        """
        Get the current frame's tile render data.

        Returns:
            List of tile render data dictionaries
        """
        return getattr(self, '_current_render_tiles', [])

    def set_screen_size(self, width: int, height: int) -> None:
        """
        Set screen size for tile visibility calculations.

        Args:
            width: Screen width in pixels
            height: Screen height in pixels
        """
        self._screen_width = width
        self._screen_height = height

        # 화면 크기 변경 시 캐시 무효화
        self._cached_tile_range = None
        self._last_camera_offset = None

    def invalidate_cache(self) -> None:
        """Invalidate tile range cache to force recalculation."""
        self._cached_tile_range = None
        self._last_camera_offset = None

    def cleanup(self) -> None:
        """Clean up map render system resources."""
        super().cleanup()
        self._cached_tile_range = None
        self._last_camera_offset = None
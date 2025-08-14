"""
MapRenderSystem for rendering map tiles and background with camera offset.

This system processes entities with MapComponent and renders the visible
map tiles with proper camera offset integration using pygame.draw.rect.
"""

from typing import TYPE_CHECKING

import pygame

from ..components.map_component import MapComponent
from ..core.coordinate_manager import CoordinateManager
from ..core.events.event_types import EventType
from ..core.events.interfaces import IEventSubscriber
from ..core.system import System

if TYPE_CHECKING:
    from ..core.entity_manager import EntityManager
    from ..core.events.base_event import BaseEvent


class MapRenderSystem(System, IEventSubscriber):
    """
    System that renders map tiles and background based on camera position.

    The MapRenderSystem processes entities with MapComponent to:
    - Calculate visible tile range based on camera offset
    - Render background tiles with pattern variation
    - Apply camera offset for proper world-to-screen transformation
    - Optimize rendering by culling off-screen tiles
    """

    def __init__(self, screen: pygame.Surface, priority: int = 15) -> None:
        """
        Initialize the MapRenderSystem.

        Args:
            priority: System execution priority (15 = after camera update)
            screen: Pygame screen surface for rendering
        """
        assert isinstance(screen, pygame.Surface), (
            'screen must be pygame.Surface'
        )
        super().__init__(priority=priority)
        self._coordinate_manager = CoordinateManager.get_instance()

        # AI-NOTE : 2025-08-13 pygame 렌더링 표면 설정 (Task 17.2)
        # - 이유: 실제 pygame.draw.rect를 사용한 타일 렌더링 필요
        # - 요구사항: 체스판 패턴 타일과 1픽셀 경계선 렌더링
        # - 히스토리: 데이터 준비에서 실제 렌더링으로 확장
        self._screen = screen
        self._screen_width = 800
        self._screen_height = 600

        # AI-DEV : 렌더링 성능 최적화를 위한 캐시 시스템
        # - 문제: 매 프레임 타일 계산으로 인한 성능 저하
        # - 해결책: 이전 프레임의 가시 타일 범위 캐시
        # - 주의사항: 카메라 이동 시 캐시 무효화 필요
        self._cached_tile_range: (
            tuple[tuple[int, int], tuple[int, int]] | None
        ) = None
        self._last_camera_offset: tuple[float, float] | None = None

        # AI-NOTE : 2025-08-13 visible_tiles 세트 기반 최적화 (Task 17.3 준비)
        # - 이유: 중복 렌더링 방지와 메모리 효율성 향상
        # - 요구사항: 현재 보이는 타일만 관리하여 성능 최적화
        # - 히스토리: 전체 타일 관리에서 가시 타일만 관리로 개선
        self._visible_tiles: set[tuple[int, int]] = set()

        # AI-NOTE : 2025-08-13 이벤트 기반 카메라 오프셋 캐싱 시스템 도입
        # - 이유: 직접 엔티티 순회 제거로 성능 향상 (O(n) → O(1))
        # - 요구사항: CameraOffsetChangedEvent 구독하여 오프셋 캐시
        # - 히스토리: 매 프레임 엔티티 순회에서 이벤트 기반 캐싱으로 개선
        self._cached_camera_offset: tuple[float, float] = (0.0, 0.0)
        self._camera_offset_valid: bool = False

    def initialize(self) -> None:
        """Initialize the map render system."""
        super().initialize()

        # 좌표 변환 시스템 확인
        transformer = self._coordinate_manager.get_transformer()
        if transformer is None:
            pass  # 좌표 변환기 상태 확인만

    def get_required_components(self) -> list[type]:
        """
        Get the required component types for this system.

        Returns:
            List containing MapComponent type.
        """
        return [MapComponent]

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
        print(f"MapRenderSystem: 맵 엔티티 수 = {len(map_entities)}")

        for map_entity in map_entities:
            map_comp = entity_manager.get_component(map_entity, MapComponent)
            if map_comp is None:
                continue

            # 현재 카메라 오프셋 가져오기
            camera_offset = self._get_current_camera_offset(entity_manager)
            # AI-DEV : 카메라 오프셋이 없어도 맵 렌더링은 계속 진행
            # - 문제: 이벤트 기반 캐시가 아직 초기화되지 않아 렌더링 중단
            # - 해결책: 기본 오프셋 (0, 0)으로도 맵 렌더링 수행
            # - 주의사항: 첫 프레임에서도 맵이 보이도록 보장
            if camera_offset is None:
                camera_offset = (0.0, 0.0)  # 기본 오프셋으로 렌더링 계속

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

    def _get_current_camera_offset(
        self, entity_manager: 'EntityManager'
    ) -> tuple[float, float] | None:
        """
        Get the current camera offset from cached event data.

        Args:
            entity_manager: Entity manager (now unused, kept for compatibility)

        Returns:
            Cached camera offset as (x, y) tuple
        """
        # AI-NOTE : 2025-08-13 이벤트 기반 캐시 사용으로 성능 개선
        # - 이유: 직접 엔티티 순회 제거로 O(n) → O(1) 성능 향상
        # - 요구사항: CameraOffsetChangedEvent로 캐시된 오프셋 사용
        # - 히스토리: 매 프레임 엔티티 순회에서 이벤트 기반 캐싱으로 개선

        if self._camera_offset_valid:
            return self._cached_camera_offset

        # 폴백: 캐시가 유효하지 않은 경우 기본값 반환
        # (첫 번째 프레임이거나 아직 이벤트를 받지 못한 경우)
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

        # AI-DEV : visible_tiles 세트 기반 최적화된 타일 관리 (Task 17.3)
        # - 문제: 매 프레임 대량의 타일 데이터 생성으로 인한 메모리 낭비
        # - 해결책: 가시 타일 세트로 중복 제거 및 메모리 효율성 향상
        # - 주의사항: 카메라 이동 시 세트 업데이트와 성능 모니터링

        # 현재 프레임의 가시 타일 세트 계산
        current_visible_tiles = set()
        render_tiles: list[dict[str, int | float]] = []

        for tile_y in range(min_tile_y, max_tile_y + 1):
            for tile_x in range(min_tile_x, max_tile_x + 1):
                tile_coord = (tile_x, tile_y)
                current_visible_tiles.add(tile_coord)

                # 맵 경계 검사 (무한 스크롤이 비활성화된 경우)
                if not map_comp.enable_infinite_scroll:
                    world_pos = map_comp.get_tile_world_position(
                        tile_x, tile_y
                    )
                    if not map_comp.is_within_world_bounds(
                        world_pos[0], world_pos[1]
                    ):
                        continue

                # 타일 패턴 타입 계산
                pattern_type = map_comp.get_tile_pattern_type(tile_x, tile_y)

                # 화면 좌표 계산 (카메라 오프셋 역방향 적용)
                world_pos = map_comp.get_tile_world_position(tile_x, tile_y)
                screen_x = world_pos[0] + camera_offset[0]
                screen_y = world_pos[1] + camera_offset[1]

                render_tile_data: dict[str, int | float] = {
                    'tile_x': tile_x,
                    'tile_y': tile_y,
                    'screen_x': screen_x,
                    'screen_y': screen_y,
                    'pattern_type': pattern_type,
                    'tile_size': map_comp.tile_size,
                }

                render_tiles.append(render_tile_data)

        # visible_tiles 세트 업데이트 (메모리 최적화)
        self._update_visible_tiles(current_visible_tiles)

        # 렌더링 데이터를 시스템에 저장 (다른 시스템에서 접근 가능)
        self._current_render_tiles = render_tiles

        # AI-NOTE : 2025-08-13 실제 pygame 렌더링 수행 (Task 17.2)
        # - 이유: 체스판 패턴 타일과 경계선을 화면에 그리기
        # - 요구사항: pygame.draw.rect를 사용한 64x64 타일 렌더링
        # - 히스토리: 데이터 준비에서 실제 렌더링 구현으로 확장
        if self._screen is not None:
            self._render_tiles_to_screen(render_tiles, map_comp)

    def _render_tiles_to_screen(
        self,
        render_tiles: list[dict[str, int | float]],
        map_comp: MapComponent,
    ) -> None:
        """
        Render tiles to pygame screen surface with checkerboard pattern.

        Args:
            render_tiles: List of tile render data
            map_comp: Map component for tile configuration
        """
        # AI-NOTE : 2025-08-14 맵 렌더링 시작 시 배경 클리어 - 격자 가시성 확보
        # - 이유: 잔상 제거를 맵 렌더링과 통합하여 격자 패턴 가시성 보장
        # - 요구사항: 맵 타일과 조화로운 밝은 회색으로 배경 클리어
        # - 히스토리: demo 메인루프 클리어에서 맵 시스템 내부 클리어로 이동
        self._screen.fill((230, 230, 230))  # 맵 타일과 조화로운 밝은 회색
        
        # AI-DEV : 디버그용 렌더링 확인 로그
        print(f"MapRenderSystem: 렌더링 타일 수 = {len(render_tiles)}")
        
        # AI-DEV : pygame.draw.rect를 사용한 효율적인 타일 렌더링
        # - 문제: 대량의 타일을 매 프레임 렌더링 시 성능 고려 필요
        # - 해결책: 화면 클리핑과 배치 렌더링으로 최적화
        # - 주의사항: 화면 경계 검사를 통한 불필요한 렌더링 방지

        for tile_data in render_tiles:
            tile_x = int(tile_data['tile_x'])
            tile_y = int(tile_data['tile_y'])
            screen_x = int(tile_data['screen_x'])
            screen_y = int(tile_data['screen_y'])
            tile_size = tile_data['tile_size']

            # 화면 경계 검사 (클리핑)
            if (
                screen_x + tile_size < 0
                or screen_y + tile_size < 0
                or screen_x >= self._screen_width
                or screen_y >= self._screen_height
            ):
                continue

            # 체스판 패턴에 따른 타일 색상 결정
            tile_color = map_comp.get_tile_color(tile_x, tile_y)

            # 타일 사각형 렌더링 (64x64 픽셀)
            tile_rect = pygame.Rect(screen_x, screen_y, tile_size, tile_size)
            pygame.draw.rect(self._screen, tile_color, tile_rect)

            # 1픽셀 검은색 경계선 렌더링
            pygame.draw.rect(
                self._screen, map_comp.grid_color, tile_rect, width=1
            )

    def get_render_tiles(self) -> list[dict[str, int]]:
        """
        Get the current frame's tile render data.

        Returns:
            List of tile render data dictionaries
        """
        return getattr(self, '_current_render_tiles', [])

    def set_screen(self, screen: pygame.Surface) -> None:
        """
        Set pygame screen surface for rendering.

        Args:
            screen: Pygame screen surface
        """
        self._screen = screen
        if screen:
            self._screen_width = screen.get_width()
            self._screen_height = screen.get_height()
            # 화면 변경 시 캐시 무효화
            self.invalidate_cache()

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

    def _update_visible_tiles(
        self, current_visible_tiles: set[tuple[int, int]]
    ) -> None:
        """
        Update visible tiles set for memory optimization.

        Args:
            current_visible_tiles: Set of currently visible tile coordinates
        """
        # AI-DEV : 메모리 효율적인 가시 타일 세트 관리 (Task 17.3)
        # - 문제: 이전 프레임의 타일 데이터가 메모리에 누적
        # - 해결책: 현재 가시 타일만 유지하고 불필요한 타일 제거
        # - 주의사항: 세트 연산 비용과 메모리 절약 효과의 균형

        # 새로 보이는 타일과 사라진 타일 계산
        new_tiles = current_visible_tiles - self._visible_tiles
        removed_tiles = self._visible_tiles - current_visible_tiles

        # 통계 정보 업데이트 (성능 모니터링용)
        self._tile_stats = {
            'total_visible': len(current_visible_tiles),
            'new_tiles': len(new_tiles),
            'removed_tiles': len(removed_tiles),
            'total_managed': len(self._visible_tiles),
        }

        # 가시 타일 세트 업데이트
        self._visible_tiles = current_visible_tiles.copy()

    def get_visible_tiles(self) -> set[tuple[int, int]]:
        """
        Get the current set of visible tile coordinates.

        Returns:
            Set of (tile_x, tile_y) coordinates currently visible
        """
        return self._visible_tiles.copy()

    def get_tile_stats(self) -> dict[str, int]:
        """
        Get tile management statistics for performance monitoring.

        Returns:
            Dictionary with tile statistics
        """
        return getattr(
            self,
            '_tile_stats',
            {
                'total_visible': 0,
                'new_tiles': 0,
                'removed_tiles': 0,
                'total_managed': 0,
            },
        )

    def invalidate_cache(self) -> None:
        """Invalidate tile range cache to force recalculation."""
        self._cached_tile_range = None
        self._last_camera_offset = None
        # 캐시 무효화 시 가시 타일도 초기화
        self._visible_tiles.clear()

    def cleanup(self) -> None:
        """Clean up map render system resources."""
        super().cleanup()
        self._cached_tile_range = None
        self._last_camera_offset = None
        self._visible_tiles.clear()
        # 이벤트 기반 캐시도 정리
        self._cached_camera_offset = (0.0, 0.0)
        self._camera_offset_valid = False

    # AI-NOTE : 2025-08-13 IEventSubscriber 인터페이스 구현
    # - 이유: 카메라 오프셋 변경 이벤트를 구독하여 캐시 업데이트
    # - 요구사항: CameraOffsetChangedEvent 처리로 성능 최적화
    # - 히스토리: 직접 엔티티 순회에서 이벤트 기반 시스템으로 개선

    def handle_event(self, event: 'BaseEvent') -> None:
        """
        Handle incoming events, specifically camera offset change events.

        Args:
            event: The event to handle. Expected to be CameraOffsetChangedEvent.
        """
        # 타입 체크를 통한 안전한 이벤트 처리
        if event.get_event_type() != EventType.CAMERA_OFFSET_CHANGED:
            return

        # TYPE_CHECKING을 위한 import 처리
        from ..core.events.camera_offset_changed_event import (
            CameraOffsetChangedEvent,
        )

        if not isinstance(event, CameraOffsetChangedEvent):
            return

        try:
            # 카메라 오프셋 캐시 업데이트
            self._cached_camera_offset = event.world_offset
            self._camera_offset_valid = True

            # 캐시된 타일 범위 무효화 (카메라가 움직였으므로)
            self._cached_tile_range = None
            self._last_camera_offset = None

        except Exception as e:
            # 이벤트 처리 중 오류가 발생해도 렌더링 시스템에 영향을 주지 않도록 처리
            print(
                f'Warning: MapRenderSystem failed to handle camera offset event: {e}'
            )

    def get_subscribed_events(self) -> list[EventType]:
        """
        Get the list of event types this subscriber wants to receive.

        Returns:
            List containing CAMERA_OFFSET_CHANGED event type.
        """
        return [EventType.CAMERA_OFFSET_CHANGED]

    def get_subscriber_name(self) -> str:
        """
        Get a human-readable name for this subscriber.

        Returns:
            String identifying this subscriber for debugging purposes.
        """
        return 'MapRenderSystem'

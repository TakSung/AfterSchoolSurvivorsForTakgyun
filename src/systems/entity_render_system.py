"""
EntityRenderSystem for rendering entities using ECS components and coordinate transformation.

This system processes entities with render-related components and renders them
to the screen using world-to-screen coordinate transformation, with special
handling for player center-screen rendering and performance optimizations.
"""

from typing import TYPE_CHECKING, Any

import pygame

from ..components.player_component import PlayerComponent
from ..components.position_component import PositionComponent
from ..components.render_component import RenderComponent, RenderLayer
from ..components.rotation_component import RotationComponent
from ..core.coordinate_manager import CoordinateManager
from ..core.system import System
from ..utils.vector2 import Vector2

if TYPE_CHECKING:
    from ..core.entity import Entity
    from ..core.entity_manager import EntityManager


class EntityRenderSystem(System):
    """
    System that renders entities using coordinate transformation and ECS components.

    The EntityRenderSystem processes entities with PositionComponent and RenderComponent
    to render them on screen with proper coordinate transformation, culling, and
    special player handling.
    """

    def __init__(
        self,
        surface: pygame.Surface,
        priority: int = 50,
        cull_margin: int = 50,
    ) -> None:
        """
        Initialize the EntityRenderSystem.

        Args:
            surface: Pygame surface to render on
            priority: System execution priority (50 = after most systems)
            cull_margin: Margin in pixels for off-screen culling
        """
        super().__init__(priority=priority)
        self._surface = surface
        self._coordinate_manager = CoordinateManager.get_instance()

        # AI-NOTE : 2025-08-11 화면 밖 컬링을 위한 여유분 설정
        # - 이유: 엔티티가 화면 경계에서 깜빡이는 현상 방지
        # - 요구사항: 50픽셀 여유분으로 부드러운 등장/사라짐 효과
        # - 히스토리: 정확한 컬링에서 여유분 적용으로 개선
        self._cull_margin = cull_margin

        # 화면 크기 캐시
        self._screen_width = surface.get_width()
        self._screen_height = surface.get_height()
        self._screen_center = (
            self._screen_width // 2,
            self._screen_height // 2,
        )

        # AI-DEV : 성능 통계 추적을 위한 카운터들
        # - 문제: 렌더링 성능 병목 지점을 파악하기 어려움
        # - 해결책: 렌더링 통계를 수집하여 성능 모니터링
        # - 주의사항: 디버그 모드에서만 활성화 권장
        self._render_stats = {
            'total_entities': 0,
            'visible_entities': 0,
            'culled_entities': 0,
            'rotated_sprites': 0,
            'player_entities': 0,
        }

        # 회전된 스프라이트 캐시 (성능 최적화용)
        self._rotation_cache: dict[tuple[int, float], pygame.Surface] = {}
        self._max_cache_size = 100

    def initialize(self) -> None:
        """Initialize the entity render system."""
        super().initialize()

        # 좌표 변환기가 설정되어 있는지 확인
        transformer = self._coordinate_manager.get_transformer()
        if transformer is None:
            print(
                'Warning: No coordinate transformer found in CoordinateManager'
            )

    def get_required_components(self) -> list[type]:
        """
        Get the required component types for this system.

        Returns:
            List containing PositionComponent and RenderComponent types.
        """
        return [PositionComponent, RenderComponent]

    def update(
        self, entity_manager: 'EntityManager', delta_time: float
    ) -> None:
        """
        Update and render all visible entities.

        Args:
            entity_manager: Entity manager for accessing entities and components
            delta_time: Time elapsed since last update in seconds
        """
        if not self.enabled:
            return

        # 통계 초기화
        self._render_stats = {
            'total_entities': 0,
            'visible_entities': 0,
            'culled_entities': 0,
            'rotated_sprites': 0,
            'player_entities': 0,
        }

        # 렌더링 가능한 엔티티들 필터링
        renderable_entities = self.filter_entities(entity_manager)
        self._render_stats['total_entities'] = len(renderable_entities)

        if not renderable_entities:
            return

        # AI-NOTE : 2025-08-11 깊이 정렬을 위한 Y좌표 기준 정렬
        # - 이유: 2D 게임에서 자연스러운 깊이감 구현
        # - 요구사항: Y값이 클수록 앞쪽에 렌더링 (화면 하단이 앞쪽)
        # - 히스토리: 무작위 렌더링에서 깊이 기반 정렬로 개선
        sorted_entities = self._sort_entities_by_depth(
            entity_manager, renderable_entities
        )

        # 플레이어와 일반 엔티티 분리 처리
        for entity in sorted_entities:
            if self._is_player_entity(entity_manager, entity):
                self._render_player(entity_manager, entity)
            else:
                self._render_entity(entity_manager, entity)

    def _sort_entities_by_depth(
        self,
        entity_manager: 'EntityManager',
        entities: list['Entity'],
    ) -> list['Entity']:
        """
        Sort entities by depth (Y coordinate) for proper layering.

        Args:
            entity_manager: Entity manager for component access
            entities: List of entities to sort

        Returns:
            Sorted list of entities (back to front).
        """

        def get_render_priority(entity: 'Entity') -> tuple[int, float]:
            # 렌더 레이어가 우선순위
            render_comp = entity_manager.get_component(entity, RenderComponent)
            layer_priority = (
                render_comp.layer.value
                if render_comp
                else RenderLayer.ENTITIES.value
            )

            # Y 좌표가 보조 정렬 기준
            pos_comp = entity_manager.get_component(entity, PositionComponent)
            y_position = pos_comp.y if pos_comp else 0.0

            return (layer_priority, y_position)

        return sorted(entities, key=get_render_priority)

    def _is_player_entity(
        self, entity_manager: 'EntityManager', entity: 'Entity'
    ) -> bool:
        """
        Check if an entity is a player entity.

        Args:
            entity_manager: Entity manager for component access
            entity: Entity to check

        Returns:
            True if entity has PlayerComponent, False otherwise.
        """
        return (
            entity_manager.get_component(entity, PlayerComponent) is not None
        )

    def _render_player(
        self, entity_manager: 'EntityManager', player_entity: 'Entity'
    ) -> None:
        """
        Render player entity at screen center with special handling.

        Args:
            entity_manager: Entity manager for component access
            player_entity: Player entity to render
        """
        render_comp = entity_manager.get_component(
            player_entity, RenderComponent
        )
        if not render_comp or not render_comp.visible:
            return

        # AI-NOTE : 2025-08-11 플레이어 중앙 고정 렌더링
        # - 이유: 플레이어는 월드 좌표와 무관하게 항상 화면 중앙에 표시
        # - 요구사항: 화면 중앙 좌표에 플레이어 스프라이트 렌더링
        # - 히스토리: 일반 엔티티 렌더링에서 특별한 플레이어 처리로 분리

        # 화면 중앙 위치에 렌더링
        screen_position = Vector2(
            self._screen_center[0], self._screen_center[1]
        )

        # 회전 처리
        rotation_comp = entity_manager.get_component(
            player_entity, RotationComponent
        )
        surface_to_render = self._get_rotated_surface(
            render_comp, rotation_comp
        )

        # 중앙 정렬로 렌더링
        rect = surface_to_render.get_rect(
            center=(int(screen_position.x), int(screen_position.y))
        )
        self._surface.blit(surface_to_render, rect)

        self._render_stats['player_entities'] += 1
        self._render_stats['visible_entities'] += 1

    def _render_entity(
        self, entity_manager: 'EntityManager', entity: 'Entity'
    ) -> None:
        """
        Render a regular entity with coordinate transformation.

        Args:
            entity_manager: Entity manager for component access
            entity: Entity to render
        """
        pos_comp = entity_manager.get_component(entity, PositionComponent)
        render_comp = entity_manager.get_component(entity, RenderComponent)

        if not pos_comp or not render_comp or not render_comp.visible:
            return

        # AI-NOTE : 2025-08-11 좌표 변환 시스템 통합 적용
        # - 이유: 월드 좌표를 스크린 좌표로 변환하여 정확한 위치에 렌더링
        # - 요구사항: CoordinateManager.world_to_screen() 메서드 활용
        # - 히스토리: 직접 좌표 계산에서 변환 시스템 활용으로 개선

        # 월드 좌표를 스크린 좌표로 변환
        world_pos = Vector2(pos_comp.x, pos_comp.y)
        transformer = self._coordinate_manager.get_transformer()

        if transformer is None:
            return

        screen_pos = transformer.world_to_screen(world_pos)

        # 화면 밖 컬링 검사
        if not self._is_on_screen(screen_pos, render_comp):
            self._render_stats['culled_entities'] += 1
            return

        # 회전 처리
        rotation_comp = entity_manager.get_component(entity, RotationComponent)
        surface_to_render = self._get_rotated_surface(
            render_comp, rotation_comp
        )

        # 렌더링
        rect = surface_to_render.get_rect(
            center=(int(screen_pos.x), int(screen_pos.y))
        )
        self._surface.blit(surface_to_render, rect)

        self._render_stats['visible_entities'] += 1

    def _is_on_screen(
        self, screen_pos: Vector2, render_comp: RenderComponent
    ) -> bool:
        """
        Check if entity is visible on screen with culling margin.

        Args:
            screen_pos: Screen position of the entity
            render_comp: Render component for size information

        Returns:
            True if entity should be rendered, False if culled.
        """
        # AI-NOTE : 2025-08-11 화면 밖 컬링 최적화 시스템
        # - 이유: 화면에 보이지 않는 엔티티 렌더링으로 인한 성능 저하 방지
        # - 요구사항: 50픽셀 여유분으로 자연스러운 등장/사라짐 효과
        # - 히스토리: 정확한 경계 검사에서 여유분 적용으로 개선

        half_width = render_comp.size[0] // 2
        half_height = render_comp.size[1] // 2

        # 여유분을 포함한 경계 검사
        return (
            screen_pos.x + half_width + self._cull_margin >= 0
            and screen_pos.x - half_width - self._cull_margin
            <= self._screen_width
            and screen_pos.y + half_height + self._cull_margin >= 0
            and screen_pos.y - half_height - self._cull_margin
            <= self._screen_height
        )

    def _get_rotated_surface(
        self,
        render_comp: RenderComponent,
        rotation_comp: RotationComponent | None,
    ) -> pygame.Surface:
        """
        Get surface with rotation applied if needed.

        Args:
            render_comp: Render component with surface data
            rotation_comp: Optional rotation component

        Returns:
            Surface ready for rendering (rotated if necessary).
        """
        base_surface = render_comp.get_effective_surface()

        if rotation_comp is None or rotation_comp.angle == 0:
            return base_surface

        # AI-DEV : 회전된 스프라이트 캐싱으로 성능 최적화
        # - 문제: pygame.transform.rotate() 호출이 매 프레임마다 발생
        # - 해결책: 회전 각도별로 결과를 캐싱하여 재사용
        # - 주의사항: 캐시 크기 제한으로 메모리 사용량 관리

        # 캐시 키 생성 (스프라이트 ID + 각도)
        sprite_id = id(base_surface)
        angle = round(rotation_comp.angle, 1)  # 0.1도 단위로 반올림
        cache_key = (sprite_id, angle)

        if cache_key in self._rotation_cache:
            return self._rotation_cache[cache_key]

        # 회전된 스프라이트 생성
        rotated_surface = pygame.transform.rotate(
            base_surface, -rotation_comp.angle
        )  # pygame은 시계 반대방향

        # 캐시에 저장 (크기 제한 적용)
        if len(self._rotation_cache) >= self._max_cache_size:
            # 가장 오래된 항목 제거
            oldest_key = next(iter(self._rotation_cache))
            del self._rotation_cache[oldest_key]

        self._rotation_cache[cache_key] = rotated_surface
        self._render_stats['rotated_sprites'] += 1

        return rotated_surface

    def set_surface(self, surface: pygame.Surface) -> None:
        """
        Set new rendering surface and update screen size cache.

        Args:
            surface: New pygame surface to render on
        """
        self._surface = surface
        self._screen_width = surface.get_width()
        self._screen_height = surface.get_height()
        self._screen_center = (
            self._screen_width // 2,
            self._screen_height // 2,
        )

    def set_cull_margin(self, margin: int) -> None:
        """
        Set culling margin for off-screen optimization.

        Args:
            margin: Margin in pixels for culling boundary
        """
        self._cull_margin = max(0, margin)

    def clear_rotation_cache(self) -> None:
        """Clear the rotation sprite cache to free memory."""
        self._rotation_cache.clear()

    def get_render_stats(self) -> dict[str, Any]:
        """
        Get rendering statistics for performance monitoring.

        Returns:
            Dictionary containing rendering statistics.
        """
        return self._render_stats.copy()

    def cleanup(self) -> None:
        """Clean up system resources."""
        super().cleanup()
        self._rotation_cache.clear()

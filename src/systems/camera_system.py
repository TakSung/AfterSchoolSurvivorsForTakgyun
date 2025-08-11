"""
CameraSystem for managing camera movement and viewport in the game.

This system processes entities with CameraComponent and updates the camera
position to follow the target entity while respecting world boundaries.
"""

import math
from typing import TYPE_CHECKING

from ..components.camera_component import CameraComponent
from ..core.coordinate_manager import CoordinateManager
from ..core.system import System

if TYPE_CHECKING:
    from ..core.entity import Entity
    from ..core.entity_manager import EntityManager


class CameraSystem(System):
    """
    System that manages camera movement and viewport positioning.

    The CameraSystem processes entities with CameraComponent to:
    - Update world offset to keep the follow target centered on screen
    - Apply dead zone for mouse tracking to prevent camera jitter
    - Enforce world boundaries to prevent showing empty space
    - Integrate with CoordinateManager for cache invalidation
    """

    def __init__(self, priority: int = 10) -> None:
        """
        Initialize the CameraSystem.

        Args:
            priority: System execution priority (10 = after movement systems)
        """
        super().__init__(priority=priority)
        self._coordinate_manager = CoordinateManager.get_instance()

        # AI-NOTE : 2025-08-11 카메라 성능 최적화를 위한 캐시 무효화 임계값
        # - 이유: 미세한 카메라 이동으로 인한 불필요한 캐시 무효화 방지
        # - 요구사항: 1픽셀 이하의 변화는 캐시를 유지하여 성능 향상
        # - 히스토리: 매번 캐시 무효화에서 임계값 기반 최적화로 변경
        self._cache_invalidation_threshold = 1.0

        # AI-DEV : 마우스 위치 추적을 위한 내부 상태 관리
        # - 문제: 마우스 위치는 외부에서 제공되어야 하는 정보
        # - 해결책: 시스템 내부에서 마우스 위치 상태 추적
        # - 주의사항: 실제 구현 시 입력 시스템과 연동 필요
        self._mouse_position: tuple[int, int] | None = None

    def initialize(self) -> None:
        """Initialize the camera system."""
        super().initialize()
        # 카메라 시스템 초기화 시 좌표 변환기 설정 확인
        transformer = self._coordinate_manager.get_transformer()
        if transformer is None:
            print(
                'Warning: No coordinate transformer found in CoordinateManager'
            )

    def get_required_components(self) -> list[type]:
        """
        Get the required component types for this system.

        Returns:
            List containing CameraComponent type.
        """
        return [CameraComponent]

    def update(
        self, entity_manager: 'EntityManager', delta_time: float
    ) -> None:
        """
        Update camera positions and manage viewport.

        Args:
            entity_manager: Entity manager for accessing entities and components
            delta_time: Time elapsed since last update in seconds
        """
        if not self.enabled:
            return

        # 카메라 엔티티들을 필터링
        camera_entities = self.filter_entities(entity_manager)

        for camera_entity in camera_entities:
            camera_comp = entity_manager.get_component(
                camera_entity, CameraComponent
            )
            if camera_comp is None:
                continue

            # 추적 대상이 있는 경우 카메라 업데이트
            if camera_comp.follow_target is not None:
                self._update_camera_for_target(
                    entity_manager,
                    camera_comp,
                    camera_comp.follow_target,
                    delta_time,
                )

            # 마우스 추적 처리 (데드존 적용)
            if self._mouse_position is not None:
                self._handle_mouse_tracking(camera_comp, delta_time)

    def _update_camera_for_target(
        self,
        entity_manager: 'EntityManager',
        camera_comp: CameraComponent,
        target: 'Entity',
        delta_time: float,
    ) -> None:
        """
        Update camera position to follow a target entity.

        Args:
            entity_manager: Entity manager for component access
            camera_comp: Camera component to update
            target: Target entity to follow
            delta_time: Time elapsed since last update
        """
        # 타겟의 위치 컴포넌트 가져오기 (위치 컴포넌트가 있다고 가정)
        # 실제 구현에서는 PositionComponent 등을 확인해야 함
        target_position = self._get_entity_position(entity_manager, target)
        if target_position is None:
            return

        # AI-NOTE : 2025-08-11 플레이어 중앙 고정을 위한 역방향 카메라 이동
        # - 이유: 플레이어가 화면 중앙에 고정되도록 월드를 반대방향으로 이동
        # - 요구사항: 플레이어 이동 시 카메라가 역방향으로 동일한 거리 이동
        # - 히스토리: 기본 추적에서 중앙 고정 방식으로 변경

        # 화면 중앙에서 타겟 위치를 뺀 값이 새로운 월드 오프셋
        new_offset_x = camera_comp.screen_center[0] - target_position[0]
        new_offset_y = camera_comp.screen_center[1] - target_position[1]
        new_offset = (new_offset_x, new_offset_y)

        # 월드 경계 제한 적용하여 오프셋 업데이트
        offset_changed = camera_comp.update_world_offset(new_offset)

        # 캐시 무효화 (임계값 기반 최적화)
        if offset_changed and self._should_invalidate_cache(
            camera_comp.world_offset, new_offset
        ):
            self._coordinate_manager.get_transformer().invalidate_cache()

    def _handle_mouse_tracking(
        self, camera_comp: CameraComponent, delta_time: float
    ) -> None:
        """
        Handle mouse tracking with dead zone to prevent camera jitter.

        Args:
            camera_comp: Camera component to update
            delta_time: Time elapsed since last update
        """
        if self._mouse_position is None:
            return

        # 화면 중앙과 마우스 위치 사이의 거리 계산
        mouse_x, mouse_y = self._mouse_position
        center_x, center_y = camera_comp.screen_center

        distance = math.sqrt(
            (mouse_x - center_x) ** 2 + (mouse_y - center_y) ** 2
        )

        # 데드존 내부에 있으면 카메라 이동하지 않음
        if distance <= camera_comp.dead_zone_radius:
            return

        # AI-DEV : 데드존 외부의 마우스 이동에 대한 카메라 추적
        # - 문제: 데드존 경계에서 갑작스러운 카메라 이동 발생 가능
        # - 해결책: 부드러운 보간을 통한 점진적 카메라 이동
        # - 주의사항: delta_time 기반 이동으로 프레임율 독립적 동작

        # 마우스 방향으로의 카메라 이동 (부드러운 추적)
        direction_x = (mouse_x - center_x) / distance
        direction_y = (mouse_y - center_y) / distance

        # 데드존 밖의 거리만큼 비례하여 카메라 이동
        excess_distance = distance - camera_comp.dead_zone_radius
        move_speed = min(excess_distance * 2.0, 100.0)  # 최대 속도 제한

        # 현재 오프셋에서 마우스 방향으로 이동
        current_offset = camera_comp.world_offset
        new_offset_x = (
            current_offset[0] - direction_x * move_speed * delta_time
        )
        new_offset_y = (
            current_offset[1] - direction_y * move_speed * delta_time
        )

        new_offset = (new_offset_x, new_offset_y)
        offset_changed = camera_comp.update_world_offset(new_offset)

        # 캐시 무효화
        if offset_changed and self._should_invalidate_cache(
            current_offset, new_offset
        ):
            self._coordinate_manager.get_transformer().invalidate_cache()

    def _get_entity_position(
        self, entity_manager: 'EntityManager', entity: 'Entity'
    ) -> tuple[float, float] | None:
        """
        Get the position of an entity.

        Args:
            entity_manager: Entity manager for component access
            entity: Entity to get position from

        Returns:
            Entity position as (x, y) tuple, or None if no position component
        """
        # AI-DEV : 위치 컴포넌트 인터페이스 가정
        # - 문제: PositionComponent가 아직 구현되지 않음
        # - 해결책: 임시로 더미 위치 반환, 실제 구현 시 교체 필요
        # - 주의사항: PositionComponent 구현 후 이 메서드 수정 필요

        # 임시 구현: 실제로는 PositionComponent를 확인해야 함
        # position_comp = entity_manager.get_component(entity, PositionComponent)
        # if position_comp is None:
        #     return None
        # return (position_comp.x, position_comp.y)

        # 임시로 (0, 0) 반환
        return (0.0, 0.0)

    def _should_invalidate_cache(
        self, old_offset: tuple[float, float], new_offset: tuple[float, float]
    ) -> bool:
        """
        Check if cache invalidation is needed based on offset change.

        Args:
            old_offset: Previous world offset
            new_offset: New world offset

        Returns:
            True if cache should be invalidated, False otherwise
        """
        # 오프셋 변화량 계산
        delta_x = abs(new_offset[0] - old_offset[0])
        delta_y = abs(new_offset[1] - old_offset[1])

        # 임계값을 넘는 변화가 있으면 캐시 무효화
        return (
            delta_x >= self._cache_invalidation_threshold
            or delta_y >= self._cache_invalidation_threshold
        )

    def set_mouse_position(self, mouse_x: int, mouse_y: int) -> None:
        """
        Set the current mouse position for camera tracking.

        Args:
            mouse_x: Mouse X coordinate in screen space
            mouse_y: Mouse Y coordinate in screen space
        """
        self._mouse_position = (mouse_x, mouse_y)

    def get_camera_offset(
        self, entity_manager: 'EntityManager'
    ) -> tuple[float, float] | None:
        """
        Get the current camera world offset.

        Args:
            entity_manager: Entity manager for accessing camera entities

        Returns:
            Current world offset as (x, y) tuple, or None if no camera found
        """
        camera_entities = self.filter_entities(entity_manager)

        if not camera_entities:
            return None

        # 첫 번째 카메라 엔티티의 오프셋 반환
        camera_entity = camera_entities[0]
        camera_comp = entity_manager.get_component(
            camera_entity, CameraComponent
        )

        if camera_comp is None:
            return None

        return camera_comp.world_offset

    def cleanup(self) -> None:
        """Clean up camera system resources."""
        super().cleanup()
        self._mouse_position = None

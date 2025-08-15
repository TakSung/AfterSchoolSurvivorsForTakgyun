"""
PlayerMovementSystem for handling player movement and mouse tracking.

This system processes player movement based on mouse position, handles smooth
rotation, dead zone detection, and integrates with the camera system.
"""

import math
from typing import TYPE_CHECKING

import pygame

from ..components.player_movement_component import PlayerMovementComponent
from ..components.position_component import PositionComponent
from ..components.rotation_component import RotationComponent
from ..core.coordinate_manager import CoordinateManager
from ..core.system import System

if TYPE_CHECKING:
    from ..core.entity_manager import EntityManager


class PlayerMovementSystem(System):
    """
    System that manages player movement based on mouse tracking.

    The PlayerMovementSystem processes entities with PlayerMovementComponent:
    - Track mouse position using pygame.mouse.get_pos()
    - Calculate direction from screen center to mouse cursor
    - Apply smooth rotation with angular velocity limits
    - Handle dead zone for small mouse movements
    - Update world position based on movement
    """

    def __init__(self, priority: int = 5) -> None:
        """
        Initialize the PlayerMovementSystem.

        Args:
            priority: System execution priority (5 = before rendering)
        """
        super().__init__(priority=priority)
        self._coordinate_manager = CoordinateManager.get_instance()

        # AI-NOTE : 2025-08-11 화면 크기 설정 - 게임 해상도 기준
        # - 이유: 화면 중앙 계산을 위한 화면 크기 필요
        # - 요구사항: 800x600 해상도 기준으로 개발
        # - 히스토리: 하드코딩에서 설정 가능한 값으로 확장 예정
        self._screen_width = 800
        self._screen_height = 600
        self._screen_center = (
            self._screen_width // 2,
            self._screen_height // 2,
        )

        # AI-DEV : 마우스 위치 캐싱으로 성능 최적화
        # - 문제: 매 프레임 pygame.mouse.get_pos() 호출 시 성능 영향
        # - 해결책: 시스템 내부에서 마우스 위치 캐싱
        # - 주의사항: 실제 pygame 이벤트와 동기화 필요
        self._cached_mouse_pos: tuple[int, int] | None = None
        self._mouse_pos_dirty = True

        # AI-NOTE : 2025-08-11 부드러운 회전을 위한 보간 설정
        # - 이유: 급작스러운 방향 전환 방지를 위한 회전 보간
        # - 요구사항: 자연스러운 플레이어 회전 애니메이션
        # - 히스토리: 즉시 회전에서 보간 기반 회전으로 개선
        self._rotation_smoothing_factor = 0.8  # 0.0 ~ 1.0 (1.0 = 즉시 회전)

    def initialize(self) -> None:
        """Initialize the player movement system."""
        super().initialize()

        # pygame 마우스 시스템 초기화 확인
        if not pygame.get_init():
            pass  # pygame 초기화 상태 확인만

        # 좌표 변환기 확인
        transformer = self._coordinate_manager.get_transformer()
        if transformer is None:
            pass  # 좌표 변환기 상태 확인만

    def get_required_components(
        self,
    ) -> tuple[PlayerMovementComponent, PositionComponent]:
        """
        Get the required component types for this system.

        Returns:
            PlayerMovementComponent and PositionComponent types.
        """
        return (PlayerMovementComponent, PositionComponent)

    def update(
        self, entity_manager: 'EntityManager', delta_time: float
    ) -> None:
        """
        Update player movement based on mouse position.

        Args:
            entity_manager: Entity manager for accessing entities/components
            delta_time: Time elapsed since last update in seconds
        """
        if not self.enabled:
            return

        # 마우스 위치 업데이트
        self._update_mouse_position()

        # 플레이어 엔티티들을 필터링
        player_entities = self.filter_entities(entity_manager)

        for player_entity in player_entities:
            movement_comp = entity_manager.get_component(
                player_entity, PlayerMovementComponent
            )
            position_comp = entity_manager.get_component(
                player_entity, PositionComponent
            )
            rotation_comp = entity_manager.get_component(
                player_entity, RotationComponent
            )
            if movement_comp is None or position_comp is None:
                continue

            # 마우스 기반 이동 처리
            self._process_mouse_movement(movement_comp, delta_time)

            # 월드 위치 업데이트
            self._update_world_position(movement_comp, delta_time)

            # PositionComponent에 위치 동기화
            position_comp.set_position(
                movement_comp.world_position[0],
                movement_comp.world_position[1]
            )
            
            # RotationComponent 업데이트 (마우스 방향으로)
            if rotation_comp is not None:
                self._update_player_rotation(
                    player_entity, movement_comp, rotation_comp, entity_manager
                )

    def _update_mouse_position(self) -> None:
        """Update cached mouse position from pygame."""
        try:
            # pygame에서 마우스 위치 가져오기
            self._cached_mouse_pos = pygame.mouse.get_pos()
            self._mouse_pos_dirty = False
        except pygame.error:
            # pygame 초기화되지 않은 경우 기본값 사용
            self._cached_mouse_pos = self._screen_center

    def _process_mouse_movement(
        self, movement_comp: PlayerMovementComponent, delta_time: float
    ) -> None:
        """
        Process mouse movement and update player direction.

        Args:
            movement_comp: Player movement component to update
            delta_time: Time elapsed since last frame
        """
        if self._cached_mouse_pos is None:
            return

        # 마우스와 화면 중앙 사이의 벡터 계산
        mouse_x, mouse_y = self._cached_mouse_pos
        center_x, center_y = self._screen_center

        dx = mouse_x - center_x
        dy = mouse_y - center_y

        # 데드존 체크
        distance_to_center = math.sqrt(dx * dx + dy * dy)

        if distance_to_center <= movement_comp.dead_zone_radius:
            # 데드존 내부 - 이동 정지
            self._stop_movement(movement_comp)
            return

        # AI-NOTE : 2025-08-11 pygame 좌표계에서의 올바른 각도 계산
        # - 이유: pygame에서 Y축 아래쪽이 양수이므로 그대로 사용
        # - 요구사항: 마우스 위치에 따른 자연스러운 플레이어 방향
        # - 히스토리: Y축 반전에서 pygame 좌표계 직접 사용으로 수정

        # pygame 좌표계에서 직접 각도 계산 (Y축 아래쪽이 양수)
        target_angle = math.atan2(dy, dx)

        # 부드러운 회전 적용
        self._apply_smooth_rotation(movement_comp, target_angle, delta_time)

        # 방향 벡터 업데이트
        movement_comp.set_direction_from_angle(movement_comp.rotation_angle)

    def _stop_movement(self, movement_comp: PlayerMovementComponent) -> None:
        """
        Stop player movement (used in dead zone).

        Args:
            movement_comp: Player movement component to update
        """
        # 현재 각도와 방향은 유지하되, 실제 이동은 정지
        # 속도를 0으로 설정하는 대신 direction을 (0, 0)으로 설정할 수도 있지만,
        # 일관성을 위해 현재 방향을 유지하고 이동 벡터 계산에서 처리
        pass

    def _apply_smooth_rotation(
        self,
        movement_comp: PlayerMovementComponent,
        target_angle: float,
        delta_time: float,
    ) -> None:
        """
        Apply smooth rotation towards target angle.

        Args:
            movement_comp: Player movement component to update
            target_angle: Target rotation angle in radians
            delta_time: Time elapsed since last frame
        """
        # 현재 각도와 목표 각도 사이의 차이 계산
        angle_diff = movement_comp.calculate_angular_difference(target_angle)

        # 각속도 제한 적용
        max_angular_change = movement_comp.angular_velocity_limit * delta_time

        if abs(angle_diff) <= max_angular_change:
            # 목표 각도에 도달 가능
            movement_comp.rotation_angle = target_angle
        else:
            # 각속도 제한 적용하여 점진적 회전
            rotation_direction = 1.0 if angle_diff > 0 else -1.0
            angular_change = max_angular_change * rotation_direction

            # 부드러운 회전을 위한 보간 적용
            angular_change *= self._rotation_smoothing_factor

            new_angle = movement_comp.rotation_angle + angular_change
            movement_comp.rotation_angle = movement_comp._normalize_angle(
                new_angle
            )

    def _update_world_position(
        self, movement_comp: PlayerMovementComponent, delta_time: float
    ) -> None:
        """
        Update player's world position based on movement.

        Args:
            movement_comp: Player movement component to update
            delta_time: Time elapsed since last frame
        """
        # 데드존 내부에서는 이동하지 않음
        if self._is_in_dead_zone(movement_comp):
            return

        # 이동 벡터 계산
        movement_vector = movement_comp.get_movement_vector(delta_time)

        # 새로운 월드 위치 계산
        current_x, current_y = movement_comp.world_position
        new_x = current_x + movement_vector[0]
        new_y = current_y + movement_vector[1]

        # 위치 업데이트
        movement_comp.update_position((new_x, new_y))

    def _is_in_dead_zone(self, movement_comp: PlayerMovementComponent) -> bool:
        """
        Check if mouse cursor is within dead zone.

        Args:
            movement_comp: Player movement component to check

        Returns:
            True if mouse is in dead zone, False otherwise
        """
        if self._cached_mouse_pos is None:
            return True

        mouse_x, mouse_y = self._cached_mouse_pos
        center_x, center_y = self._screen_center

        dx = mouse_x - center_x
        dy = mouse_y - center_y
        distance = math.sqrt(dx * dx + dy * dy)

        return distance <= movement_comp.dead_zone_radius

    def get_screen_center(self) -> tuple[int, int]:
        """
        Get the screen center coordinates.

        Returns:
            Screen center as (x, y) tuple
        """
        return self._screen_center

    def set_screen_size(self, width: int, height: int) -> None:
        """
        Set screen size and recalculate screen center.

        Args:
            width: Screen width in pixels
            height: Screen height in pixels
        """
        self._screen_width = width
        self._screen_height = height
        self._screen_center = (width // 2, height // 2)

    def get_mouse_position(self) -> tuple[int, int] | None:
        """
        Get current cached mouse position.

        Returns:
            Mouse position as (x, y) tuple, or None if not available
        """
        return self._cached_mouse_pos

    def force_mouse_update(self) -> None:
        """Force update of mouse position cache."""
        self._mouse_pos_dirty = True
        self._update_mouse_position()

    def set_rotation_smoothing(self, factor: float) -> None:
        """
        Set rotation smoothing factor.

        Args:
            factor: Smoothing factor (0.0 = no rotate, 1.0 = instant)
        """
        self._rotation_smoothing_factor = max(0.0, min(1.0, factor))

    def _update_player_rotation(
        self,
        player_entity,
        movement_comp: PlayerMovementComponent,
        rotation_comp: RotationComponent,
        entity_manager: 'EntityManager',
    ) -> None:
        """
        Update player rotation to face mouse direction.
        
        Args:
            player_entity: Player entity
            movement_comp: Player movement component
            rotation_comp: Player rotation component
            entity_manager: Entity manager
        """
        if not self._cached_mouse_pos:
            return
            
        # 현재 플레이어 위치를 화면 좌표로 변환
        transformer = self._coordinate_manager.get_transformer()
        if not transformer:
            return
            
        from ..utils.vector2 import Vector2
        
        # 플레이어 월드 위치
        player_world_pos = Vector2(
            movement_comp.world_position[0],
            movement_comp.world_position[1]
        )
        
        # 플레이어 화면 위치
        player_screen_pos = transformer.world_to_screen(player_world_pos)
        
        # 마우스 위치
        mouse_x, mouse_y = self._cached_mouse_pos
        
        # 마우스 방향 벡터 계산
        dx = mouse_x - player_screen_pos.x
        dy = mouse_y - player_screen_pos.y
        
        # 마우스 방향으로의 각도 계산
        if dx != 0 or dy != 0:
            target_angle = math.atan2(dy, dx)
            rotation_comp.angle = target_angle

    def cleanup(self) -> None:
        """Clean up player movement system resources."""
        super().cleanup()
        self._cached_mouse_pos = None
        self._mouse_pos_dirty = True

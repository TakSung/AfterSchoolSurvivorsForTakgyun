"""
ProjectileSystem for handling projectile physics and lifecycle management.

This system processes projectile entities for movement, lifetime management,
collision detection, and cleanup of expired projectiles.
"""

from typing import TYPE_CHECKING

import pygame

from ..components.position_component import PositionComponent
from ..components.projectile_component import ProjectileComponent
from ..core.system import System

if TYPE_CHECKING:
    from ..core.entity import Entity
    from ..core.entity_manager import EntityManager


class ProjectileSystem(System):
    """
    System that manages projectile physics, movement, and lifecycle.

    The ProjectileSystem processes entities with ProjectileComponent:
    - Update projectile positions based on velocity and direction
    - Manage projectile lifetime and remove expired projectiles
    - Handle screen boundary checks and cleanup
    - Process projectile physics calculations
    """

    def __init__(self, priority: int = 15) -> None:
        """
        Initialize the ProjectileSystem.

        Args:
            priority: System execution priority (15 = after weapons)
        """
        super().__init__(priority=priority)

        # AI-NOTE : 2025-08-12 투사체 시스템 초기화 - 화면 경계 관리
        # - 이유: 화면 밖으로 나간 투사체 자동 정리로 메모리 누수 방지
        # - 요구사항: 투사체가 화면 경계를 벗어나면 자동으로 제거
        # - 히스토리: pygame 화면 크기 기반 경계 검사 구현
        self._screen_bounds: pygame.Rect | None = None
        self._expired_projectiles: list[Entity] = []

    def initialize(self) -> None:
        """Initialize the projectile system."""
        super().initialize()

        # AI-DEV : 화면 크기 동적 감지를 위한 pygame 의존성
        # - 문제: 화면 크기를 미리 알 수 없어 경계 검사 불가
        # - 해결책: pygame.display.get_surface()로 동적 화면 크기 감지
        # - 주의사항: pygame이 초기화되지 않았을 경우 None 반환 가능
        screen = pygame.display.get_surface()
        if screen:
            self._screen_bounds = screen.get_rect()
            # 여유 공간을 둬서 화면 경계 근처에서 즉시 사라지지 않도록 함
            self._screen_bounds = self._screen_bounds.inflate(100, 100)

    def get_required_components(self) -> list[type]:
        """
        Get required component types for projectile entities.

        Returns:
            List of required component types.
        """
        return [ProjectileComponent, PositionComponent]

    def update(
        self, entity_manager: 'EntityManager', delta_time: float
    ) -> None:
        """
        Update projectile system logic.

        Args:
            entity_manager: Entity manager to access entities and components
            delta_time: Time elapsed since last update in seconds
        """
        if not self.enabled:
            return

        projectile_entities = self.filter_entities(entity_manager)
        self._expired_projectiles.clear()

        for entity in projectile_entities:
            self._update_projectile(entity, entity_manager, delta_time)

        # 만료된 투사체들 제거
        self._cleanup_expired_projectiles(entity_manager)

    def _update_projectile(
        self,
        entity: 'Entity',
        entity_manager: 'EntityManager',
        delta_time: float,
    ) -> None:
        """
        Update a single projectile entity.

        Args:
            entity: Projectile entity to update
            entity_manager: Entity manager to access components
            delta_time: Time elapsed since last update
        """
        projectile = entity_manager.get_component(entity, ProjectileComponent)
        position = entity_manager.get_component(entity, PositionComponent)

        if not projectile or not position:
            return

        # 수명 업데이트
        projectile.update_lifetime(delta_time)

        # 수명이 다한 투사체는 제거 대상으로 표시
        if projectile.is_expired():
            self._expired_projectiles.append(entity)
            return

        # 위치 업데이트
        velocity_vector = projectile.get_velocity_vector()
        position.x += velocity_vector.x * delta_time
        position.y += velocity_vector.y * delta_time

        # 화면 경계 검사
        if self._is_out_of_bounds(position):
            self._expired_projectiles.append(entity)

    def _is_out_of_bounds(self, position: PositionComponent) -> bool:
        """
        Check if projectile is outside screen boundaries.

        Args:
            position: Position component to check

        Returns:
            True if projectile is out of bounds, False otherwise.
        """
        if not self._screen_bounds:
            return False

        return not self._screen_bounds.collidepoint(position.x, position.y)

    def _cleanup_expired_projectiles(
        self, entity_manager: 'EntityManager'
    ) -> None:
        """
        Remove all expired projectiles from the entity manager.

        Args:
            entity_manager: Entity manager to remove entities from
        """
        for entity in self._expired_projectiles:
            entity_manager.remove_entity(entity.entity_id)

    def get_projectile_count(self, entity_manager: 'EntityManager') -> int:
        """
        Get the current number of active projectiles.

        Args:
            entity_manager: Entity manager to query entities from

        Returns:
            Number of active projectile entities.
        """
        return len(self.filter_entities(entity_manager))

    def get_projectiles_by_owner(
        self, entity_manager: 'EntityManager', owner_id: str
    ) -> list['Entity']:
        """
        Get all projectiles created by a specific owner.

        Args:
            entity_manager: Entity manager to query entities from
            owner_id: ID of the entity that created the projectiles

        Returns:
            List of projectile entities owned by the specified entity.
        """
        projectile_entities = self.filter_entities(entity_manager)
        owner_projectiles = []

        for entity in projectile_entities:
            projectile = entity_manager.get_component(
                entity, ProjectileComponent
            )
            if projectile and projectile.owner_id == owner_id:
                owner_projectiles.append(entity)

        return owner_projectiles

    def clear_projectiles_by_owner(
        self, entity_manager: 'EntityManager', owner_id: str
    ) -> int:
        """
        Remove all projectiles created by a specific owner.

        Args:
            entity_manager: Entity manager to remove entities from
            owner_id: ID of the entity that created the projectiles

        Returns:
            Number of projectiles removed.
        """
        owner_projectiles = self.get_projectiles_by_owner(
            entity_manager, owner_id
        )
        for entity in owner_projectiles:
            entity_manager.remove_entity(entity.entity_id)
        return len(owner_projectiles)

    def update_screen_bounds(self, screen: pygame.Surface) -> None:
        """
        Update the screen bounds for boundary checking.

        Args:
            screen: Pygame surface representing the game screen
        """
        if screen:
            self._screen_bounds = screen.get_rect().inflate(100, 100)

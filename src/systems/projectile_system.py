"""
ProjectileSystem for handling projectile physics and lifecycle management.

This system processes projectile entities for movement, lifetime management,
collision detection, and cleanup of expired projectiles.
"""

import time
from typing import TYPE_CHECKING

import pygame

from ..components.collision_component import CollisionComponent
from ..components.enemy_component import EnemyComponent
from ..components.health_component import HealthComponent
from ..components.position_component import PositionComponent
from ..components.projectile_component import ProjectileComponent
from ..core.system import System
from ..systems.collision_system import BruteForceCollisionDetector

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
    - Detect collisions with enemies and apply damage
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

        # AI-NOTE : 2025-08-12 투사체 충돌 감지 시스템 - 적과의 충돌 처리
        # - 이유: 투사체가 적에게 닿았을 때 데미지 적용 및 투사체 제거
        # - 요구사항: 효율적인 충돌 감지, 데미지 적용, 관통 투사체 지원
        # - 히스토리: 기존 충돌 시스템과 연동하여 AABB 충돌 검사 활용
        self._collision_detector = BruteForceCollisionDetector()
        self._collision_pairs: list[tuple[Entity, Entity]] = []

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
        return [ProjectileComponent, PositionComponent, CollisionComponent]

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
        self._collision_pairs.clear()

        # 투사체 물리 업데이트
        for entity in projectile_entities:
            self._update_projectile(entity, entity_manager, delta_time)

        # 투사체-적 충돌 검사
        self._process_projectile_collisions(
            entity_manager, projectile_entities
        )

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
            entity_manager.destroy_entity(entity)

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
            entity_manager.destroy_entity(entity)
        return len(owner_projectiles)

    def update_screen_bounds(self, screen: pygame.Surface) -> None:
        """
        Update the screen bounds for boundary checking.

        Args:
            screen: Pygame surface representing the game screen
        """
        if screen:
            self._screen_bounds = screen.get_rect().inflate(100, 100)

    def _process_projectile_collisions(
        self,
        entity_manager: 'EntityManager',
        projectile_entities: list['Entity'],
    ) -> None:
        """
        Process collisions between projectiles and enemies.

        Args:
            entity_manager: Entity manager to access components
            projectile_entities: List of projectile entities to check
        """
        # 적 엔티티들 가져오기
        enemy_entities = entity_manager.get_entities_with_components(
            EnemyComponent,
            PositionComponent,
            CollisionComponent,
            HealthComponent,
        )

        if not enemy_entities or not projectile_entities:
            return

        # 모든 충돌 가능한 엔티티들을 함께 검사
        all_entities = projectile_entities + enemy_entities
        collisions = self._collision_detector.detect_collisions(
            entity_manager, all_entities
        )

        # 투사체-적 충돌만 필터링하여 처리
        for entity1, entity2 in collisions:
            projectile_entity, enemy_entity = self._identify_collision_pair(
                entity_manager, entity1, entity2
            )

            if projectile_entity and enemy_entity:
                self._handle_projectile_enemy_collision(
                    entity_manager, projectile_entity, enemy_entity
                )

    def _identify_collision_pair(
        self,
        entity_manager: 'EntityManager',
        entity1: 'Entity',
        entity2: 'Entity',
    ) -> tuple['Entity', 'Entity'] | tuple[None, None]:
        """
        Identify which entity is projectile and which is enemy.

        Args:
            entity_manager: Entity manager to access components
            entity1: First collision entity
            entity2: Second collision entity

        Returns:
            Tuple of (projectile_entity, enemy_entity) or (None, None)
                if not applicable
        """
        proj1 = entity_manager.get_component(entity1, ProjectileComponent)
        proj2 = entity_manager.get_component(entity2, ProjectileComponent)
        enemy1 = entity_manager.get_component(entity1, EnemyComponent)
        enemy2 = entity_manager.get_component(entity2, EnemyComponent)

        # entity1이 투사체이고 entity2가 적인 경우
        if proj1 and enemy2:
            return entity1, entity2
        # entity2가 투사체이고 entity1이 적인 경우
        elif proj2 and enemy1:
            return entity2, entity1
        # 둘 다 해당 없음
        else:
            return None, None

    def _handle_projectile_enemy_collision(
        self,
        entity_manager: 'EntityManager',
        projectile_entity: 'Entity',
        enemy_entity: 'Entity',
    ) -> None:
        """
        Handle collision between a projectile and an enemy.

        Args:
            entity_manager: Entity manager to access components
            projectile_entity: The projectile entity
            enemy_entity: The enemy entity
        """
        projectile = entity_manager.get_component(
            projectile_entity, ProjectileComponent
        )
        enemy_health = entity_manager.get_component(
            enemy_entity, HealthComponent
        )

        if not projectile or not enemy_health:
            return

        # 이미 충돌한 타겟인지 확인 (관통 투사체의 경우)
        if projectile.has_hit_target(enemy_entity.entity_id):
            return

        # 데미지 적용
        current_time = time.time()
        enemy_health.take_damage(projectile.damage, current_time)

        # 충돌 타겟 기록 (관통 투사체의 경우)
        projectile.add_hit_target(enemy_entity.entity_id)

        # AI-DEV : 데미지 적용 성공 시 효과 처리
        # - 문제: 충돌 효과나 사운드 등 추가 처리가 필요할 수 있음
        # - 해결책: 이벤트 시스템 구현 시 충돌 이벤트 발생
        # - 주의사항: 현재는 기본적인 데미지 적용만 수행

        # 적이 죽었는지 확인
        if enemy_health.is_dead():
            self._handle_enemy_death(entity_manager, enemy_entity)

        # 관통하지 않는 투사체는 즉시 제거
        if not projectile.piercing:
            self._expired_projectiles.append(projectile_entity)

    def _handle_enemy_death(
        self, entity_manager: 'EntityManager', enemy_entity: 'Entity'
    ) -> None:
        """
        Handle enemy death effects.

        Args:
            entity_manager: Entity manager to access components
            enemy_entity: The enemy entity that died
        """
        # AI-NOTE : 2025-08-12 적 사망 처리 - 경험치 및 보상 시스템
        # - 이유: 적 처치 시 플레이어 경험치 증가 및 아이템 드롭
        # - 요구사항: 경험치 계산, 아이템 드롭 확률, 사망 효과
        # - 히스토리: 향후 게임 진행 시스템과 연동 예정

        enemy = entity_manager.get_component(enemy_entity, EnemyComponent)
        if enemy:
            # 경험치 보상 계산 (현재는 로깅만, 향후 플레이어 시스템과 연동)
            # experience_reward = enemy.get_experience_reward()
            # TODO: 플레이어 시스템에 경험치 전달
            pass

        # 적 엔티티 제거
        entity_manager.destroy_entity(enemy_entity)

    def get_collision_count(self) -> int:
        """
        Get the number of collisions processed in the last update.

        Returns:
            Number of projectile-enemy collisions processed.
        """
        return len(self._collision_pairs)

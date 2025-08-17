"""
ProjectileSystem for handling projectile physics and lifecycle management.

This system processes projectile entities for movement, lifetime management,
collision detection, and cleanup of expired projectiles.
"""

import logging
import time
from typing import TYPE_CHECKING, Optional

import pygame

from ..components.collision_component import CollisionComponent
from ..components.enemy_component import EnemyComponent
from ..components.health_component import HealthComponent
from ..components.position_component import PositionComponent
from ..components.projectile_component import ProjectileComponent
from ..core.coordinate_manager import CoordinateManager
from ..core.events.enemy_death_event import EnemyDeathEvent
from ..core.projectile_manager import ProjectileManager
from ..core.system import System
from ..systems.collision_system import BruteForceCollisionDetector
from ..utils.vector2 import Vector2

if TYPE_CHECKING:
    from ..core.entity import Entity
    from ..core.entity_manager import EntityManager
    from ..core.events.event_bus import EventBus


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

    def __init__(self, priority: int = 15, projectile_manager: Optional[ProjectileManager] = None, event_bus: Optional['EventBus'] = None) -> None:
        """
        Initialize the ProjectileSystem.

        Args:
            priority: System execution priority (15 = after weapons)
            projectile_manager: ProjectileManager for event-based projectile tracking
            event_bus: EventBus for publishing enemy death events
        """
        super().__init__(priority=priority)

        # AI-NOTE : 2025-08-15 ProjectileManager 기반 투사체 추적으로 변경
        # - 이유: ECS 컴포넌트 필터링 문제로 투사체를 찾지 못하는 이슈 해결
        # - 요구사항: 이벤트 기반 투사체 등록 및 추적으로 안정적인 관리
        # - 히스토리: 사용자 제안으로 기존 컴포넌트 필터링 방식에서 변경
        self._projectile_manager = projectile_manager or ProjectileManager()
        
        # 경험치 시스템 연동을 위한 EventBus
        self._event_bus = event_bus

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

        # 좌표 변환 시스템
        self._coordinate_manager: CoordinateManager | None = None

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

        # 좌표 변환 시스템 초기화
        self._coordinate_manager = CoordinateManager.get_instance()

    def set_projectile_manager(self, projectile_manager: ProjectileManager) -> None:
        """
        Set the projectile manager for event-based projectile tracking.
        
        Args:
            projectile_manager: ProjectileManager instance
        """
        self._projectile_manager = projectile_manager

    def get_required_components(self) -> list[type]:
        """
        Get required component types for projectile entities.

        Returns:
            List of required component types.
        """
        # AI-NOTE: RenderComponent 추가 - 투사체 렌더링 및 시스템 필터링에 필요
        from ..components.render_component import RenderComponent
        return [ProjectileComponent, PositionComponent, CollisionComponent, RenderComponent]

    def update(
        self, delta_time: float
    ) -> None:
        """
        Update projectile system logic.

        Args:
            delta_time: Time elapsed since last update in seconds
        """
        if not self.enabled:
            return

        # AI-NOTE : 2025-08-15 ProjectileManager를 통한 투사체 조회로 변경
        # - 이유: ECS 컴포넌트 필터링 대신 이벤트 기반 관리로 안정적인 투사체 추적
        # - 요구사항: ProjectileManager에 등록된 투사체들을 Entity 객체로 변환
        # - 히스토리: 기존 filter_entities() 방식에서 변경
        
        # ProjectileManager 상태 디버깅
        logging.info(f"ProjectileSystem: ProjectileManager status: {self._projectile_manager}")
        
        projectile_entity_ids = self._projectile_manager.get_active_projectiles()
        projectile_entities = []
        
        logging.info(f"ProjectileSystem: Retrieved {len(projectile_entity_ids)} projectile IDs from manager")
        for i, entity_id in enumerate(projectile_entity_ids):
            logging.info(f"  ID {i+1}: {entity_id}")
        
        # Entity ID를 실제 Entity 객체로 변환
        for entity_id in projectile_entity_ids:
            entity = self._entity_manager.get_entity(entity_id)
            if entity:
                projectile_entities.append(entity)
                logging.info(f"✅ Found entity for ID {entity_id}, active: {entity.active}")
            else:
                # 더 자세한 디버깅: EntityManager 내부 상태 확인
                all_entities = self._entity_manager.get_all_entities()
                entity_ids_in_manager = [e.entity_id for e in all_entities]
                logging.error(f"❌ Entity {entity_id} not found in entity manager")
                logging.error(f"   Total entities in manager: {len(all_entities)}")
                logging.error(f"   EntityManager contains IDs: {entity_ids_in_manager[:5]}...")  # 처음 5개만 표시
                logging.error(f"   Looking for ID: {entity_id}")
                
                # Entity가 더 이상 존재하지 않으면 ProjectileManager에서 제거
                logging.warning(f"Removing projectile {entity_id} from ProjectileManager")
                self._projectile_manager.unregister_projectile(entity_id)
        
        self._expired_projectiles.clear()
        self._collision_pairs.clear()

        # 투사체 추적 진단 정보
        if projectile_entity_ids or projectile_entities:
            logging.info(f"ProjectileSystem: ProjectileManager has {len(projectile_entity_ids)} registered projectiles")
            logging.info(f"ProjectileSystem: Found {len(projectile_entities)} valid projectile entities")
            
            if projectile_entities:
                logging.info(f"ProjectileSystem: Processing {len(projectile_entities)} projectiles")
                for i, entity in enumerate(projectile_entities):
                    pos = self._entity_manager.get_component(entity, PositionComponent)
                    if pos:
                        logging.info(f"  Projectile {i+1}: {entity.entity_id} at ({pos.x:.1f}, {pos.y:.1f})")

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
        projectile = self._entity_manager.get_component(entity, ProjectileComponent)
        position = self._entity_manager.get_component(entity, PositionComponent)

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
        if not self._screen_bounds or not self._coordinate_manager:
            return False

        # AI-NOTE : 2025-08-15 월드 좌표를 화면 좌표로 변환하여 경계 검사
        # - 이유: 투사체 위치는 월드 좌표이지만 _screen_bounds는 화면 좌표 기준
        # - 요구사항: 좌표 변환 후 화면 경계와 비교
        # - 히스토리: 기존에는 좌표계 불일치로 경계 검사가 작동하지 않았음
        transformer = self._coordinate_manager.get_transformer()
        if not transformer:
            return False

        try:
            # 월드 좌표를 화면 좌표로 변환
            world_pos = Vector2(position.x, position.y)
            screen_pos = transformer.world_to_screen(world_pos)
            
            # 화면 경계 내에 있는지 확인
            return not self._screen_bounds.collidepoint(screen_pos.x, screen_pos.y)
        except:
            # 변환 실패 시 제거하지 않음 (안전한 선택)
            return False

    def _cleanup_expired_projectiles(
        self, entity_manager: 'EntityManager'
    ) -> None:
        """
        Remove all expired projectiles from the entity manager.

        Args:
            entity_manager: Entity manager to remove entities from
        """
        if self._expired_projectiles:
            logging.info(f"Removing {len(self._expired_projectiles)} expired projectiles")
            
        for entity in self._expired_projectiles:
            # ProjectileManager에서도 제거
            self._projectile_manager.unregister_projectile(entity.entity_id)
            self._entity_manager.destroy_entity(entity)
            logging.info(f"Removed expired projectile {entity.entity_id}")

    def get_projectile_count(self, entity_manager: 'EntityManager') -> int:
        """
        Get the current number of active projectiles.

        Args:
            entity_manager: Entity manager to query entities from

        Returns:
            Number of active projectile entities.
        """
        return self._projectile_manager.get_projectile_count()

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
        # ProjectileManager를 통해 owner별 투사체 ID 조회
        projectile_entity_ids = self._projectile_manager.get_projectiles_by_owner(owner_id)
        owner_projectiles = []

        # Entity ID를 실제 Entity 객체로 변환
        for entity_id in projectile_entity_ids:
            entity = self._entity_manager.get_entity_by_id(entity_id)
            if entity:
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
            self._entity_manager.destroy_entity(entity)
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
        enemy_entities = self._entity_manager.get_entities_with_components(
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
        proj1 = self._entity_manager.get_component(entity1, ProjectileComponent)
        proj2 = self._entity_manager.get_component(entity2, ProjectileComponent)
        enemy1 = self._entity_manager.get_component(entity1, EnemyComponent)
        enemy2 = self._entity_manager.get_component(entity2, EnemyComponent)

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
        projectile = self._entity_manager.get_component(
            projectile_entity, ProjectileComponent
        )
        enemy_health = self._entity_manager.get_component(
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
        # AI-NOTE : 2025-08-16 투사체로 적 처치 시 경험치 시스템 연동
        # - 이유: 투사체로 적을 죽였을 때 플레이어가 경험치를 얻도록 함
        # - 요구사항: EnemyDeathEvent 발생으로 ExperienceSystem 알림
        # - 히스토리: 기존 TODO에서 실제 경험치 시스템 연동으로 개선

        # EnemyDeathEvent 발생으로 경험치 시스템에 알림
        if self._event_bus:
            death_event = EnemyDeathEvent.create_from_id(
                enemy_entity_id=enemy_entity.entity_id,
                timestamp=time.time()
            )
            self._event_bus.publish(death_event)
            logging.info(f"Published EnemyDeathEvent for enemy {enemy_entity.entity_id}")

        # 적 엔티티 제거
        entity_manager.destroy_entity(enemy_entity)
        logging.info(f"Enemy {enemy_entity.entity_id} killed by projectile")

    def get_collision_count(self) -> int:
        """
        Get the number of collisions processed in the last update.

        Returns:
            Number of projectile-enemy collisions processed.
        """
        return len(self._collision_pairs)

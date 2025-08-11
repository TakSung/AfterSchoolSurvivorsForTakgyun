"""
Collision detection system for ECS architecture.

Implements AABB (Axis-Aligned Bounding Box) collision detection
for game entities with collision components.
"""

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..core.system import System

if TYPE_CHECKING:
    from ..components.collision_component import CollisionComponent
    from ..core.entity import Entity
    from ..core.entity_manager import EntityManager

logger = logging.getLogger(__name__)


class ICollisionDetector(ABC):
    """
    Interface for collision detection algorithms.

    Allows for different collision detection strategies to be used
    interchangeably, such as brute force, spatial partitioning, etc.
    """

    @abstractmethod
    def detect_collisions(
        self, entity_manager: 'EntityManager', entities: list['Entity']
    ) -> list[tuple['Entity', 'Entity']]:
        """
        Detect all collision pairs among the given entities.

        Args:
            entity_manager: Manager to access entity components.
            entities: List of entities to check for collisions.

        Returns:
            List of entity pairs that are colliding.
        """
        pass

    @abstractmethod
    def check_point_collision(
        self,
        point_x: float,
        point_y: float,
        entity_manager: 'EntityManager',
        entity: 'Entity',
    ) -> bool:
        """
        Check if a point collides with an entity.

        Args:
            point_x: X coordinate of the point.
            point_y: Y coordinate of the point.
            entity_manager: Manager to access entity components.
            entity: Entity to check collision against.

        Returns:
            True if point is inside entity bounds, False otherwise.
        """
        pass


class BruteForceCollisionDetector(ICollisionDetector):
    """
    Brute force collision detector using O(n²) approach.

    Checks every entity against every other entity for collisions.
    Simple but inefficient for large numbers of entities.
    """

    def __init__(self) -> None:
        """Initialize brute force collision detector."""
        self._collision_checks_count = 0

    def detect_collisions(
        self, entity_manager: 'EntityManager', entities: list['Entity']
    ) -> list[tuple['Entity', 'Entity']]:
        """
        Detect collisions using brute force O(n²) approach.

        Args:
            entity_manager: Manager to access entity components.
            entities: List of entities to check for collisions.

        Returns:
            List of entity pairs that are colliding.
        """
        collisions = []
        self._collision_checks_count = 0

        # AI-NOTE : 2025-01-11 브루트포스 충돌 감지 알고리즘 구현
        # - 이유: 단순하고 확실한 충돌 감지, 초기 구현에 적합
        # - 요구사항: 모든 엔티티 쌍에 대해 AABB 충돌 검사
        # - 히스토리: 확장성을 위한 인터페이스 기반 구현

        for i, entity1 in enumerate(entities):
            for entity2 in entities[i + 1 :]:  # 중복 검사 방지
                self._collision_checks_count += 1

                if self._check_entity_collision(
                    entity_manager, entity1, entity2
                ):
                    collisions.append((entity1, entity2))

        return collisions

    def check_point_collision(
        self,
        point_x: float,
        point_y: float,
        entity_manager: 'EntityManager',
        entity: 'Entity',
    ) -> bool:
        """
        Check if a point is inside an entity's collision bounds.

        Args:
            point_x: X coordinate of the point.
            point_y: Y coordinate of the point.
            entity_manager: Manager to access entity components.
            entity: Entity to check collision against.

        Returns:
            True if point is inside entity bounds, False otherwise.
        """
        from ..components.collision_component import CollisionComponent
        from ..components.position_component import PositionComponent

        position = entity_manager.get_component(entity, PositionComponent)
        collision = entity_manager.get_component(entity, CollisionComponent)

        if not position or not collision:
            return False

        left, top, right, bottom = collision.get_bounds(position.x, position.y)

        return left <= point_x <= right and top <= point_y <= bottom

    def _check_entity_collision(
        self,
        entity_manager: 'EntityManager',
        entity1: 'Entity',
        entity2: 'Entity',
    ) -> bool:
        """
        Check if two entities are colliding using AABB method.

        Args:
            entity_manager: Manager to access entity components.
            entity1: First entity to check.
            entity2: Second entity to check.

        Returns:
            True if entities are colliding, False otherwise.
        """
        from ..components.collision_component import CollisionComponent
        from ..components.position_component import PositionComponent

        pos1 = entity_manager.get_component(entity1, PositionComponent)
        pos2 = entity_manager.get_component(entity2, PositionComponent)
        col1 = entity_manager.get_component(entity1, CollisionComponent)
        col2 = entity_manager.get_component(entity2, CollisionComponent)

        if not all([pos1, pos2, col1, col2]):
            return False

        return self._check_aabb_collision(
            pos1.x,
            pos1.y,
            col1.width,
            col1.height,
            pos2.x,
            pos2.y,
            col2.width,
            col2.height,
        )

    def _check_aabb_collision(
        self,
        x1: float,
        y1: float,
        w1: float,
        h1: float,
        x2: float,
        y2: float,
        w2: float,
        h2: float,
    ) -> bool:
        """
        Check AABB (Axis-Aligned Bounding Box) collision between two rectangles.

        Args:
            x1, y1: Position of first rectangle center.
            w1, h1: Width and height of first rectangle (must be >= 0).
            x2, y2: Position of second rectangle center.
            w2, h2: Width and height of second rectangle (must be >= 0).

        Returns:
            True if rectangles overlap, False otherwise.
        """
        # AI-DEV : 입력 검증 추가 - 타입과 크기 검증
        # - 문제: 잘못된 타입이나 음수 크기는 예상치 못한 결과 발생 가능
        # - 해결책: assert로 사전 조건 검증하여 개발 시점에 오류 발견
        # - 주의사항: 점 충돌(크기 0)은 허용하되 음수는 금지
        assert isinstance(x1, (int, float)), (
            f'x1 must be numeric, got {type(x1)}'
        )
        assert isinstance(y1, (int, float)), (
            f'y1 must be numeric, got {type(y1)}'
        )
        assert isinstance(x2, (int, float)), (
            f'x2 must be numeric, got {type(x2)}'
        )
        assert isinstance(y2, (int, float)), (
            f'y2 must be numeric, got {type(y2)}'
        )
        assert isinstance(w1, (int, float)), (
            f'w1 must be numeric, got {type(w1)}'
        )
        assert isinstance(h1, (int, float)), (
            f'h1 must be numeric, got {type(h1)}'
        )
        assert isinstance(w2, (int, float)), (
            f'w2 must be numeric, got {type(w2)}'
        )
        assert isinstance(h2, (int, float)), (
            f'h2 must be numeric, got {type(h2)}'
        )
        assert w1 >= 0, f'Width w1 must be non-negative, got {w1}'
        assert h1 >= 0, f'Height h1 must be non-negative, got {h1}'
        assert w2 >= 0, f'Width w2 must be non-negative, got {w2}'
        assert h2 >= 0, f'Height h2 must be non-negative, got {h2}'

        # 각 사각형의 경계 계산 (중심점 기준)
        left1 = x1 - w1 / 2
        right1 = x1 + w1 / 2
        top1 = y1 - h1 / 2
        bottom1 = y1 + h1 / 2

        left2 = x2 - w2 / 2
        right2 = x2 + w2 / 2
        top2 = y2 - h2 / 2
        bottom2 = y2 + h2 / 2

        # X축과 Y축 모두에서 겹침이 있어야 충돌 (모서리 접촉도 포함)
        x_overlap = left1 <= right2 and right1 >= left2
        y_overlap = top1 <= bottom2 and bottom1 >= top2

        return x_overlap and y_overlap

    def get_collision_checks_count(self) -> int:
        """Get number of collision checks performed in last detection."""
        return self._collision_checks_count


class CollisionSystem(System):
    """
    System that handles collision detection between entities using configurable detectors.

    This system processes entities that have both PositionComponent and
    CollisionComponent, checking for overlaps and handling collision responses.
    Uses Strategy pattern to allow different collision detection algorithms.
    """

    def __init__(
        self, priority: int = 100, detector: ICollisionDetector | None = None
    ) -> None:
        """
        Initialize the collision system.

        Args:
            priority: System execution priority (higher number = later execution).
            detector: Collision detector to use. Defaults to BruteForceCollisionDetector.
        """
        super().__init__(priority)
        self._detector = detector or BruteForceCollisionDetector()
        self._collision_count = 0

    def initialize(self) -> None:
        """Initialize the collision system."""
        super().initialize()
        self._collision_count = 0
        logger.info('CollisionSystem initialized')

    def get_required_components(self) -> list[type]:
        """
        Get required component types for collision detection.

        Returns:
            List containing PositionComponent and CollisionComponent types.
        """
        from ..components.collision_component import CollisionComponent
        from ..components.position_component import PositionComponent

        return [PositionComponent, CollisionComponent]

    def update(
        self, entity_manager: 'EntityManager', delta_time: float
    ) -> None:
        """
        Update collision detection for all entities.

        Args:
            entity_manager: Manager to access entities and components.
            delta_time: Time elapsed since last update in seconds.
        """
        if not self.enabled:
            return

        entities = self.filter_entities(entity_manager)
        self._collision_count = 0

        # AI-DEV : Strategy 패턴으로 충돌 감지 알고리즘 교체 가능
        # - 문제: 다양한 충돌 감지 방법(브루트포스, 공간 분할 등) 지원 필요
        # - 해결책: ICollisionDetector 인터페이스로 알고리즘 추상화
        # - 주의사항: 런타임에 detector 교체 시 상태 관리 필요
        collision_pairs = self._detector.detect_collisions(
            entity_manager, entities
        )

        for entity1, entity2 in collision_pairs:
            self._handle_collision(entity_manager, entity1, entity2)
            self._collision_count += 1

    def set_collision_detector(self, detector: ICollisionDetector) -> None:
        """
        Set a new collision detector for the system.

        Args:
            detector: New collision detector to use.
        """
        self._detector = detector
        logger.info(
            f'Collision detector changed to {detector.__class__.__name__}'
        )

    def get_collision_detector(self) -> ICollisionDetector:
        """
        Get the current collision detector.

        Returns:
            Current collision detector instance.
        """
        return self._detector

    def check_point_collision(
        self,
        point_x: float,
        point_y: float,
        entity_manager: 'EntityManager',
        entity: 'Entity',
    ) -> bool:
        """
        Check if a point collides with an entity using current detector.

        Args:
            point_x: X coordinate of the point.
            point_y: Y coordinate of the point.
            entity_manager: Manager to access entity components.
            entity: Entity to check collision against.

        Returns:
            True if point collides with entity, False otherwise.
        """
        return self._detector.check_point_collision(
            point_x, point_y, entity_manager, entity
        )

    def _handle_collision(
        self,
        entity_manager: 'EntityManager',
        entity1: 'Entity',
        entity2: 'Entity',
    ) -> None:
        """
        Handle collision response between two entities.

        Args:
            entity_manager: Manager to access entity components.
            entity1: First colliding entity.
            entity2: Second colliding entity.
        """
        from ..components.collision_component import CollisionComponent

        col1 = entity_manager.get_component(entity1, CollisionComponent)
        col2 = entity_manager.get_component(entity2, CollisionComponent)

        if not col1 or not col2:
            return

        # AI-NOTE : 2025-01-11 충돌 레이어 기반 충돌 처리 시스템
        # - 이유: 특정 레이어 간에만 충돌 처리가 필요함 (플레이어-적, 투사체-적 등)
        # - 요구사항: 충돌 마스크를 확인하여 실제 충돌 처리 여부 결정
        # - 히스토리: 기본 충돌 감지 후 레이어별 처리 로직 분기

        # 양방향 충돌 마스크 확인
        can_collide = col1.can_collide_with(
            col2.layer
        ) or col2.can_collide_with(col1.layer)

        if not can_collide:
            return

        # 충돌 이벤트 처리
        self._process_collision_event(
            entity_manager, entity1, entity2, col1, col2
        )

        # 물리적 충돌 응답 (solid 객체만)
        if col1.is_solid and col2.is_solid:
            self._apply_collision_physics(entity_manager, entity1, entity2)

    def _process_collision_event(
        self,
        entity_manager: 'EntityManager',
        entity1: 'Entity',
        entity2: 'Entity',
        col1: 'CollisionComponent',
        col2: 'CollisionComponent',
    ) -> None:
        """
        Process collision event based on collision layers.

        Args:
            entity_manager: Manager to access entity components.
            entity1: First colliding entity.
            entity2: Second colliding entity.
            col1: Collision component of first entity.
            col2: Collision component of second entity.
        """
        from ..components.collision_component import CollisionLayer

        # AI-DEV : 충돌 타입별 처리 로직 분기
        # - 문제: 각 레이어 조합마다 다른 처리가 필요함
        # - 해결책: 레이어 조합별 처리 메서드 분기
        # - 주의사항: 새로운 레이어 추가 시 이 부분 업데이트 필요

        layer_pair = tuple(sorted([col1.layer, col2.layer]))

        if layer_pair == (CollisionLayer.PLAYER, CollisionLayer.ENEMY):
            self._handle_player_enemy_collision(
                entity_manager, entity1, entity2, col1, col2
            )
        elif layer_pair == (CollisionLayer.PLAYER, CollisionLayer.ITEM):
            self._handle_player_item_collision(
                entity_manager, entity1, entity2, col1, col2
            )
        elif layer_pair == (CollisionLayer.PROJECTILE, CollisionLayer.ENEMY):
            self._handle_projectile_enemy_collision(
                entity_manager, entity1, entity2, col1, col2
            )
        else:
            # 기본 충돌 처리 (로깅만)
            logger.debug(
                f'Collision between {col1.layer.display_name} and {col2.layer.display_name}: '
                f'entities {entity1.id} and {entity2.id}'
            )

    def _handle_player_enemy_collision(
        self,
        entity_manager: 'EntityManager',
        entity1: 'Entity',
        entity2: 'Entity',
        col1: 'CollisionComponent',
        col2: 'CollisionComponent',
    ) -> None:
        """Handle collision between player and enemy."""
        # TODO: 플레이어 피해 처리 구현 예정
        logger.info(
            f'Player-Enemy collision: player={entity1.id if col1.layer.value == 0 else entity2.id}'
        )

    def _handle_player_item_collision(
        self,
        entity_manager: 'EntityManager',
        entity1: 'Entity',
        entity2: 'Entity',
        col1: 'CollisionComponent',
        col2: 'CollisionComponent',
    ) -> None:
        """Handle collision between player and item."""
        # TODO: 아이템 획득 처리 구현 예정
        logger.info('Player-Item collision: item acquired')

    def _handle_projectile_enemy_collision(
        self,
        entity_manager: 'EntityManager',
        entity1: 'Entity',
        entity2: 'Entity',
        col1: 'CollisionComponent',
        col2: 'CollisionComponent',
    ) -> None:
        """Handle collision between projectile and enemy."""
        # TODO: 적 피해 처리 및 투사체 제거 구현 예정
        logger.info('Projectile-Enemy collision: damage applied')

    def _apply_collision_physics(
        self,
        entity_manager: 'EntityManager',
        entity1: 'Entity',
        entity2: 'Entity',
    ) -> None:
        """
        Apply physical collision response (separation, bounce, etc.).

        Args:
            entity_manager: Manager to access entity components.
            entity1: First colliding entity.
            entity2: Second colliding entity.
        """
        # AI-DEV : 물리적 충돌 응답 로직 (추후 구현)
        # - 문제: 객체들이 겹쳤을 때 분리시키는 로직 필요
        # - 해결책: 최소 분리 거리 계산하여 객체 위치 조정
        # - 주의사항: 연쇄 충돌이나 진동 현상 방지 필요
        pass

    def get_collision_count(self) -> int:
        """
        Get the number of collisions detected in the last update.

        Returns:
            Number of collisions detected.
        """
        return self._collision_count

    def cleanup(self) -> None:
        """Clean up collision system resources."""
        super().cleanup()
        logger.info('CollisionSystem cleanup completed')

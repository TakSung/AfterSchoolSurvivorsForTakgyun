"""
Attack strategies for the auto attack system.

This module implements the Strategy pattern for different attack behaviors:
- Direction-based attacks (player rotation direction)
- World target attacks (specific enemy targeting)
- Nearest enemy attacks (automatic targeting)
"""

import logging
import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from ..utils.vector2 import Vector2

if TYPE_CHECKING:
    from ..components.position_component import PositionComponent
    from ..components.weapon_component import WeaponComponent
    from ..core.entity import Entity
    from ..core.entity_manager import EntityManager

logger = logging.getLogger(__name__)


class IAttackStrategy(ABC):
    """공격 전략 인터페이스"""

    @abstractmethod
    def calculate_direction(
        self,
        weapon: 'WeaponComponent',
        start_pos: 'PositionComponent',
        weapon_entity: 'Entity',
        **kwargs,
    ) -> Vector2 | None:
        """
        공격 방향 계산

        Args:
            weapon: 무기 컴포넌트
            start_pos: 시작 위치
            weapon_entity: 무기를 소유한 엔티티
            **kwargs: 전략별 추가 파라미터

        Returns:
            정규화된 방향 벡터 또는 None (공격 불가 시)
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """전략 이름 반환"""
        pass


class DirectionAttackStrategy(IAttackStrategy):
    """방향 기반 공격 전략 (플레이어 회전 방향)"""

    def calculate_direction(
        self,
        weapon: 'WeaponComponent',
        start_pos: 'PositionComponent',
        weapon_entity: 'Entity',
        direction_angle: float = 0.0,
        **kwargs,
    ) -> Vector2 | None:
        """플레이어가 바라보는 방향으로 공격"""
        logger.debug(
            f'DirectionAttackStrategy: calculating direction for angle {direction_angle}'
        )
        return Vector2(math.cos(direction_angle), math.sin(direction_angle))

    def get_strategy_name(self) -> str:
        return 'direction_attack'


class WorldTargetAttackStrategy(IAttackStrategy):
    """월드 좌표 타겟 공격 전략 (적 추적)"""

    def calculate_direction(
        self,
        weapon: 'WeaponComponent',
        start_pos: 'PositionComponent',
        weapon_entity: 'Entity',
        target_pos: Optional['PositionComponent'] = None,
        **kwargs,
    ) -> Vector2 | None:
        """특정 타겟을 향해 공격"""
        if not target_pos:
            logger.warning('WorldTargetAttackStrategy: No target_pos provided')
            return None

        direction_vector = Vector2(
            target_pos.x - start_pos.x, target_pos.y - start_pos.y
        )

        if direction_vector.magnitude == 0:
            logger.debug(
                'WorldTargetAttackStrategy: Target at same position as start'
            )
            return None  # 동일 위치면 공격 불가

        logger.debug(
            f'WorldTargetAttackStrategy: direction from {start_pos.x},{start_pos.y} to {target_pos.x},{target_pos.y}'
        )
        return direction_vector.normalized()

    def get_strategy_name(self) -> str:
        return 'world_target_attack'


class NearestEnemyAttackStrategy(IAttackStrategy):
    """가장 가까운 적 공격 전략"""

    def calculate_direction(
        self,
        weapon: 'WeaponComponent',
        start_pos: 'PositionComponent',
        weapon_entity: 'Entity',
        entity_manager: Optional['EntityManager'] = None,
        **kwargs,
    ) -> Vector2 | None:
        """가장 가까운 적을 향해 공격"""
        if not entity_manager:
            logger.warning(
                'NearestEnemyAttackStrategy: No entity_manager provided'
            )
            return None

        # 가장 가까운 적 찾기
        nearest_enemy = self._find_nearest_enemy_in_world(
            start_pos, weapon.range, entity_manager
        )

        if not nearest_enemy:
            logger.debug('NearestEnemyAttackStrategy: No enemy found in range')
            return None

        from ..components.position_component import PositionComponent

        target_pos = entity_manager.get_component(
            nearest_enemy, PositionComponent
        )
        if not target_pos:
            logger.warning(
                'NearestEnemyAttackStrategy: Target enemy has no position component'
            )
            return None

        # WorldTargetAttackStrategy 로직 재사용
        world_strategy = WorldTargetAttackStrategy()
        return world_strategy.calculate_direction(
            weapon, start_pos, weapon_entity, target_pos=target_pos
        )

    def _find_nearest_enemy_in_world(
        self,
        weapon_pos: 'PositionComponent',
        weapon_range: float,
        entity_manager: 'EntityManager',
    ) -> Optional['Entity']:
        """
        Find the closest enemy within weapon range using world coordinates.
        (복사된 로직 - 기존 AutoAttackSystem과 동일)
        """
        from ..components.enemy_component import EnemyComponent
        from ..components.position_component import PositionComponent

        # 적 엔티티 필터링 (EnemyComponent를 가진 엔티티)
        enemy_entities = entity_manager.get_entities_with_components(
            EnemyComponent, PositionComponent
        )

        closest_enemy = None
        closest_distance = weapon_range

        weapon_world_pos = Vector2(weapon_pos.x, weapon_pos.y)

        for enemy in enemy_entities:
            enemy_pos = entity_manager.get_component(enemy, PositionComponent)
            if not enemy_pos:
                continue

            # 월드 좌표에서 직접 거리 계산
            enemy_world_pos = Vector2(enemy_pos.x, enemy_pos.y)
            distance = (weapon_world_pos - enemy_world_pos).magnitude

            if distance < closest_distance:
                closest_distance = distance
                closest_enemy = enemy

        return closest_enemy

    def get_strategy_name(self) -> str:
        return 'nearest_enemy_attack'

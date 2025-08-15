"""
AutoAttackSystem for handling automatic attacks based on world coordinates.

This system processes weapon-equipped entities for automatic targeting,
cooldown management, and projectile creation using world coordinate system.
"""

import logging
from typing import TYPE_CHECKING, Optional

import pygame

from ..components.enemy_component import EnemyComponent
from ..components.position_component import PositionComponent
from ..components.weapon_component import WeaponComponent
from ..core.coordinate_manager import CoordinateManager
from ..core.system import System
from ..utils.vector2 import Vector2

if TYPE_CHECKING:
    from ..core.entity import Entity
    from ..core.entity_manager import EntityManager

logger = logging.getLogger(__name__)


class AutoAttackSystem(System):
    """
    System that manages automatic attacks using world coordinates.

    The AutoAttackSystem processes entities with WeaponComponent to:
    - Manage time-based attack cooldowns (FPS independent)
    - Find closest enemy within weapon range using world coordinates
    - Create projectiles with world coordinate based targeting
    """

    def __init__(self, priority: int = 15) -> None:
        """
        Initialize the AutoAttackSystem.

        Args:
            priority: System execution priority (15 = after movement/camera)
        """
        super().__init__(priority=priority)

        # AI-NOTE : 2025-08-13 월드 좌표 기반 자동 공격 시스템
        # - 이유: 화면 기준이 아닌 월드 좌표 기준으로 정확한 타겟팅 구현
        # - 요구사항: FPS 독립적 쿨다운, 월드 좌표 거리 계산, 좌표계 변환
        # - 히스토리: 기존 WeaponSystem과 분리하여 더 명확한 책임 분할

        self._coordinate_manager: CoordinateManager | None = None

    def initialize(self) -> None:
        """Initialize the auto attack system."""
        super().initialize()

        # AI-DEV : 좌표 관리자 지연 초기화
        # - 문제: 싱글톤 초기화 순서 이슈 방지
        # - 해결책: 시스템 초기화 시점에 좌표 관리자 설정
        # - 주의사항: 매번 호출 시 get_instance() 사용하여 안전성 보장
        self._coordinate_manager = CoordinateManager.get_instance()

    def get_required_components(self) -> list[type]:
        """
        Get required component types for auto attack entities.

        Returns:
            List of required component types.
        """
        return [WeaponComponent, PositionComponent]

    def update(
        self, entity_manager: 'EntityManager', delta_time: float
    ) -> None:
        """
        Update auto attack system logic.

        Args:
            entity_manager: Entity manager to access entities and components
            delta_time: Time elapsed since last update in seconds
        """
        if not self.enabled:
            return

        weapon_entities = self.filter_entities(entity_manager)
        # logger.info(f"AutoAttackSystem: Found {len(weapon_entities)} weapon entities.")

        for entity in weapon_entities:
            self._process_auto_attack(entity, entity_manager, delta_time)

    def _process_auto_attack(
        self,
        weapon_entity: 'Entity',
        entity_manager: 'EntityManager',
        delta_time: float,
    ) -> None:
        """
        Process auto attack for a weapon entity.

        Args:
            weapon_entity: Entity with weapon component
            entity_manager: Entity manager to access components
            delta_time: Time elapsed since last update in seconds
        """
        weapon = entity_manager.get_component(weapon_entity, WeaponComponent)
        weapon_pos = entity_manager.get_component(
            weapon_entity, PositionComponent
        )

        if not weapon or not weapon_pos:
            logger.warning(
                f'Missing weapon or position component for entity {weapon_entity.entity_id}'
            )
            return

        # logger.info(f"Processing auto attack for entity {weapon_entity.entity_id}")

        # AI-NOTE : 2025-08-13 시간 기반 공격 쿨다운 시스템 구현
        # - 이유: FPS와 독립적인 안정적인 공격 주기 제공
        # - 요구사항: attack_speed를 초당 공격 횟수로 처리
        # - 히스토리: time.time() 대신 delta_time 누적으로 정확성 향상

        # 공격 쿨다운 업데이트 (delta_time 누적 방식)
        self._update_attack_cooldown(weapon, delta_time)

        # 쿨다운이 완료되었으면 공격 시도
        if self._can_attack(weapon):
            # logger.info("Attack cooldown completed, attempting attack")
            # 플레이어의 회전 방향 가져오기
            from ..components.rotation_component import RotationComponent

            rotation_comp = entity_manager.get_component(
                weapon_entity, RotationComponent
            )

            if rotation_comp:
                # logger.info(f"Player rotation angle: {rotation_comp.angle}")
                # 플레이어가 바라보는 방향으로 발사
                self._execute_direction_attack(
                    weapon, weapon_pos, rotation_comp.angle, entity_manager
                )
                self._reset_attack_cooldown(weapon)
                # logger.info("Projectile created successfully")
            else:
                logger.warning('No rotation component found on weapon entity')
        # else:
        # logger.debug(f"Attack on cooldown. Time: {weapon.last_attack_time:.2f}, Required: {weapon.get_cooldown_duration():.2f}")

    def _update_attack_cooldown(
        self, weapon: WeaponComponent, delta_time: float
    ) -> None:
        """
        Update weapon attack cooldown using delta time.

        Args:
            weapon: Weapon component to update
            delta_time: Time elapsed since last update in seconds
        """
        # AI-DEV : 쿨다운 누적 방식으로 정확성 보장
        # - 문제: time.time() 사용 시 시스템 시간 변경에 영향받을 수 있음
        # - 해결책: delta_time 누적으로 게임 내부 시간 기준 쿨다운 관리
        # - 주의사항: last_attack_time을 누적 시간으로 활용

        # last_attack_time을 내부 타이머로 활용 (매 프레임 delta_time 누적)
        weapon.last_attack_time += delta_time

    def _can_attack(self, weapon: WeaponComponent) -> bool:
        """
        Check if the weapon can attack based on cooldown.

        Args:
            weapon: Weapon component to check

        Returns:
            True if weapon is ready to attack, False otherwise
        """
        cooldown_duration = weapon.get_cooldown_duration()
        return weapon.last_attack_time >= cooldown_duration

    def _reset_attack_cooldown(self, weapon: WeaponComponent) -> None:
        """
        Reset weapon attack cooldown after attack.

        Args:
            weapon: Weapon component to reset
        """
        # AI-DEV : 남은 시간 보존으로 정확한 주기 유지
        # - 문제: 쿨다운을 0으로 리셋하면 프레임 간격에 따라 공격 주기 불규칙
        # - 해결책: 초과된 시간을 다음 쿨다운에 반영하여 일정한 주기 보장
        # - 주의사항: attack_speed가 높을 때 연속 공격 가능성 고려

        cooldown_duration = weapon.get_cooldown_duration()
        weapon.last_attack_time -= cooldown_duration

    def _find_nearest_enemy_in_world(
        self,
        weapon_pos: PositionComponent,
        weapon_range: float,
        entity_manager: 'EntityManager',
    ) -> Optional['Entity']:
        """
        Find the closest enemy within weapon range using world coordinates.

        Args:
            weapon_pos: Position of the weapon entity in world coordinates
            weapon_range: Maximum range for targeting
            entity_manager: Entity manager to access entities

        Returns:
            Closest enemy entity within range, or None if no valid target.
        """
        # AI-NOTE : 2025-08-13 월드 좌표 기반 타겟 탐색 시스템
        # - 이유: 좌표계 확장으로 인한 정확한 거리 계산 필요
        # - 요구사항: Vector2.length()로 거리 계산, EnemyComponent 식별
        # - 히스토리: 화면 좌표에서 월드 좌표 기반으로 변경

        # 적 엔티티 필터링 (EnemyComponent를 가진 엔티티)
        enemy_entities = entity_manager.get_entities_with_components(
            EnemyComponent, PositionComponent
        )
        # logger.info(f"Found {len(enemy_entities)} enemies to check.")

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

    def _execute_direction_attack(
        self,
        weapon: WeaponComponent,
        start_pos: PositionComponent,
        direction_angle: float,
        entity_manager: 'EntityManager',
    ) -> None:
        """
        Execute an attack by creating a projectile in a specific direction.

        Args:
            weapon: Weapon component with attack properties
            start_pos: Starting position for the projectile (world coordinates)
            direction_angle: Angle in radians for the projectile direction
            entity_manager: Entity manager for creating projectiles
        """
        # logger.info(f"Executing direction attack from {start_pos} at angle {direction_angle}")
        # AI-NOTE : 2025-08-13 월드 좌표 기반 투사체 생성 구현
        # - 이유: 월드 좌표에서 스크린 좌표 독립적인 투사체 생성
        # - 요구사항: 월드 좌표 방향 계산, Vector2 정규화 활용
        # - 히스토리: ProjectileComponent.create_towards_target 활용

        # Import modules needed for projectile creation
        from ..components.collision_component import (
            CollisionComponent,
            CollisionLayer,
        )
        from ..components.projectile_component import ProjectileComponent
        from ..components.render_component import RenderComponent, RenderLayer

        try:
            # logger.info(f"Creating projectile from position ({start_pos.x:.1f}, {start_pos.y:.1f}) at angle {direction_angle:.2f}")

            # 1. 투사체 엔티티 생성
            projectile_entity = entity_manager.create_entity()
            # logger.info(f"Created projectile entity: {projectile_entity.entity_id}")

            # 2. 방향 기반 ProjectileComponent 생성
            import math
            from ..utils.vector2 import Vector2

            # 방향 벡터 계산
            direction = Vector2(
                math.cos(direction_angle), math.sin(direction_angle)
            )

            projectile_comp = ProjectileComponent(
                direction=direction,
                velocity=400.0,  # 기본 투사체 속도
                damage=weapon.get_effective_damage(),
                lifetime=2.5,  # 기본 수명 2.5초
                owner_id=None,  # TODO: 향후 owner 엔티티 ID 추가
            )
            entity_manager.add_component(projectile_entity, projectile_comp)
            # logger.info(f"Added ProjectileComponent with direction: {direction}, velocity: 400.0")

            # 3. PositionComponent 추가 (월드 좌표 시작 위치)
            position_comp = PositionComponent(x=start_pos.x, y=start_pos.y)
            entity_manager.add_component(projectile_entity, position_comp)

            # 4. RenderComponent 추가 (투사체 시각화)
            # 투사체 스프라이트 생성
            projectile_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
            projectile_surface.fill((255, 255, 0))  # 노란색 투사체
            pygame.draw.circle(
                projectile_surface, (255, 255, 255), (3, 3), 2, 1
            )  # 흰색 테두리

            render_comp = RenderComponent(
                sprite=projectile_surface,
                size=(6, 6),  # 6x6 픽셀 크기
                layer=RenderLayer.PROJECTILES,
                visible=True,
            )
            entity_manager.add_component(projectile_entity, render_comp)

            # 5. CollisionComponent 추가 (충돌 감지용)
            collision_comp = CollisionComponent(
                width=6.0,
                height=6.0,
                layer=CollisionLayer.PROJECTILE,
                collision_mask={CollisionLayer.ENEMY},  # 적과만 충돌
                is_trigger=True,  # 트리거 충돌 (관통 가능)
                is_solid=False,  # 비고체 (다른 객체를 밀어내지 않음)
            )
            entity_manager.add_component(projectile_entity, collision_comp)

            # AI-DEV : 투사체 생성 성공 시 안전한 처리
            # - 문제: 투사체 생성 실패 시에도 시스템이 계속 동작해야 함
            # - 해결책: 예외 처리로 개별 투사체 생성 실패 격리
            # - 주의사항: 실패 시에도 게임플레이에 영향을 주지 않도록 함

        except Exception as e:
            # 투사체 생성 실패 시 안전한 처리 (게임 계속 진행)
            logger.error(f'Failed to create projectile: {e}')
            import traceback

            logger.error(f'Traceback: {traceback.format_exc()}')

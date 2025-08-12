"""
WeaponSystem for handling automatic targeting and weapon attacks.

This system processes weapon-equipped entities for automatic targeting,
cooldown management, and projectile creation based on weapon types.
"""

import time
from typing import TYPE_CHECKING, Optional

from ..components.position_component import PositionComponent
from ..components.projectile_component import ProjectileComponent
from ..components.render_component import RenderComponent, RenderLayer
from ..components.weapon_component import ProjectileType, WeaponComponent
from ..core.system import System

if TYPE_CHECKING:
    from ..core.entity import Entity
    from ..core.entity_manager import EntityManager


class IProjectileHandler:
    """
    Interface for handling different projectile types.

    This interface defines the contract for creating and managing
    different types of projectiles based on weapon configuration.
    """

    def create_projectile(
        self,
        weapon: WeaponComponent,
        start_pos: tuple[float, float],
        target_pos: tuple[float, float],
        entity_manager: 'EntityManager',
    ) -> Optional['Entity']:
        """
        Create a projectile entity.

        Args:
            weapon: Weapon component with projectile configuration
            start_pos: Starting position (x, y)
            target_pos: Target position (x, y)
            entity_manager: Entity manager for creating entities

        Returns:
            Created projectile entity or None if creation failed.
        """
        raise NotImplementedError


class BasicProjectileHandler(IProjectileHandler):
    """Handler for basic projectile type."""

    def create_projectile(
        self,
        weapon: WeaponComponent,
        start_pos: tuple[float, float],
        target_pos: tuple[float, float],
        entity_manager: 'EntityManager',
    ) -> Optional['Entity']:
        """
        Create a basic projectile entity.

        Args:
            weapon: Weapon component with projectile configuration
            start_pos: Starting position (x, y)
            target_pos: Target position (x, y)
            entity_manager: Entity manager for creating entities

        Returns:
            Created projectile entity or None.
        """
        # AI-NOTE : 2025-08-12 기본 투사체 엔티티 생성 구현
        # - 이유: 실제 투사체 엔티티 생성으로 자동 공격 시스템 완성
        # - 요구사항: ProjectileComponent, PositionComponent, RenderComponent 조합
        # - 히스토리: 이전 TODO에서 실제 구현으로 변경
        try:
            # 투사체 엔티티 생성
            projectile_entity = entity_manager.create_entity()

            # PositionComponent 추가 (시작 위치 설정)
            position_comp = PositionComponent(x=start_pos[0], y=start_pos[1])
            entity_manager.add_component(projectile_entity, position_comp)

            # ProjectileComponent 추가 (방향과 속도 계산)
            projectile_comp = ProjectileComponent.create_towards_target(
                start_pos=start_pos,
                target_pos=target_pos,
                velocity=400.0,  # 기본 투사체 속도
                damage=weapon.get_effective_damage(),
                lifetime=2.5,  # 기본 수명 2.5초
                owner_id=None,  # TODO: 무기를 가진 엔티티 ID 전달 필요
            )
            entity_manager.add_component(projectile_entity, projectile_comp)

            # RenderComponent 추가 (작은 원형 투사체)
            render_comp = RenderComponent(
                color=(255, 255, 0),  # 노란색 투사체
                size=(6, 6),  # 6x6 픽셀 크기
                layer=RenderLayer.PROJECTILES,
                visible=True,
            )
            entity_manager.add_component(projectile_entity, render_comp)

            return projectile_entity

        except Exception as e:
            # AI-DEV : 투사체 생성 실패 시 안전한 처리
            # - 문제: 엔티티 생성 중 예외 발생 가능성
            # - 해결책: 예외 캐치하여 None 반환으로 안전한 실패 처리
            # - 주의사항: 로깅 시스템 구현 시 여기서 오류 기록
            return None


class WeaponSystem(System):
    """
    System that manages automatic targeting and weapon attacks.

    The WeaponSystem processes entities with WeaponComponent:
    - Find closest enemy within weapon range
    - Handle weapon cooldown timing
    - Create projectiles when attacking
    - Update target selection periodically
    """

    def __init__(self, priority: int = 10) -> None:
        """
        Initialize the WeaponSystem.

        Args:
            priority: System execution priority (10 = after movement)
        """
        super().__init__(priority=priority)

        # AI-NOTE : 2025-08-11 투사체 핸들러 등록 - State 패턴
        # - 이유: 투사체 타입별로 다른 생성 로직 지원
        # - 요구사항: 무기 타입에 따른 다양한 투사체 효과
        # - 히스토리: 확장 가능한 핸들러 시스템 구조
        self._projectile_handlers: dict[ProjectileType, IProjectileHandler] = {
            ProjectileType.BASIC: BasicProjectileHandler()
        }

        self._target_update_interval = 0.1  # 타겟 재선택 간격 (초)
        self._last_target_update = 0.0

    def initialize(self) -> None:
        """Initialize the weapon system."""
        super().initialize()

    def get_required_components(self) -> list[type]:
        """
        Get required component types for weapon entities.

        Returns:
            List of required component types.
        """
        return [WeaponComponent, PositionComponent]

    def update(
        self, entity_manager: 'EntityManager', delta_time: float
    ) -> None:
        """
        Update weapon system logic.

        Args:
            entity_manager: Entity manager to access entities and components
            delta_time: Time elapsed since last update in seconds
        """
        if not self.enabled:
            return

        current_time = time.time()
        weapon_entities = self.filter_entities(entity_manager)

        # 주기적으로 타겟 업데이트
        if (
            current_time - self._last_target_update
            >= self._target_update_interval
        ):
            self._update_targets(weapon_entities, entity_manager)
            self._last_target_update = current_time

        # 공격 처리
        for entity in weapon_entities:
            self._process_weapon_attack(entity, entity_manager, current_time)

    def _update_targets(
        self, weapon_entities: list['Entity'], entity_manager: 'EntityManager'
    ) -> None:
        """
        Update target selection for weapon entities.

        Args:
            weapon_entities: List of entities with weapons
            entity_manager: Entity manager to access entities
        """
        # AI-DEV : 타겟 엔티티 필터링을 위한 임시 구현
        # - 문제: 적 엔티티를 구별하는 컴포넌트가 아직 미정의
        # - 해결책: 현재는 빈 리스트 반환, 향후 EnemyComponent 등으로 확장
        # - 주의사항: 적 컴포넌트 구현 후 이 부분 업데이트 필요
        enemy_entities: list[Entity] = []  # TODO: 적 엔티티 필터링 로직

        for weapon_entity in weapon_entities:
            weapon = entity_manager.get_component(
                weapon_entity, WeaponComponent
            )
            weapon_pos = entity_manager.get_component(
                weapon_entity, PositionComponent
            )

            if weapon and weapon_pos:
                closest_enemy = self._find_closest_enemy(
                    weapon_pos, weapon.range, enemy_entities, entity_manager
                )
                weapon.current_target_id = (
                    closest_enemy.entity_id if closest_enemy else None
                )

    def _find_closest_enemy(
        self,
        weapon_pos: PositionComponent,
        weapon_range: float,
        enemy_entities: list['Entity'],
        entity_manager: 'EntityManager',
    ) -> Optional['Entity']:
        """
        Find the closest enemy within weapon range.

        Args:
            weapon_pos: Position of the weapon entity
            weapon_range: Maximum range for targeting
            enemy_entities: List of potential enemy entities
            entity_manager: Entity manager to access components

        Returns:
            Closest enemy entity within range, or None if no valid target.
        """
        # AI-DEV : 성능 최적화를 위한 거리 제곱 비교
        # - 문제: 제곱근 연산은 비용이 높아 성능에 영향
        # - 해결책: 거리의 제곱값으로 비교하여 연산 비용 절약
        # - 주의사항: 실제 거리가 필요한 경우에만 제곱근 계산
        closest_enemy = None
        closest_distance_squared = weapon_range * weapon_range

        for enemy in enemy_entities:
            enemy_pos = entity_manager.get_component(enemy, PositionComponent)
            if not enemy_pos:
                continue

            # 거리 제곱 계산 (제곱근 연산 생략)
            dx = weapon_pos.x - enemy_pos.x
            dy = weapon_pos.y - enemy_pos.y
            distance_squared = dx * dx + dy * dy

            if distance_squared < closest_distance_squared:
                closest_distance_squared = distance_squared
                closest_enemy = enemy

        return closest_enemy

    def _process_weapon_attack(
        self,
        weapon_entity: 'Entity',
        entity_manager: 'EntityManager',
        current_time: float,
    ) -> None:
        """
        Process attack for a weapon entity.

        Args:
            weapon_entity: Entity with weapon component
            entity_manager: Entity manager to access components
            current_time: Current game time in seconds
        """
        weapon = entity_manager.get_component(weapon_entity, WeaponComponent)
        weapon_pos = entity_manager.get_component(
            weapon_entity, PositionComponent
        )

        if not weapon or not weapon_pos:
            return

        # 타겟이 있고 쿨다운이 완료된 경우 공격
        if weapon.current_target_id and weapon.can_attack(current_time):
            target_entity = entity_manager.get_entity(weapon.current_target_id)
            if target_entity:
                target_pos = entity_manager.get_component(
                    target_entity, PositionComponent
                )
                if target_pos:
                    self._execute_attack(
                        weapon, weapon_pos, target_pos, entity_manager
                    )
                    weapon.set_last_attack_time(current_time)

    def _execute_attack(
        self,
        weapon: WeaponComponent,
        start_pos: PositionComponent,
        target_pos: PositionComponent,
        entity_manager: 'EntityManager',
    ) -> None:
        """
        Execute an attack by creating a projectile.

        Args:
            weapon: Weapon component with attack properties
            start_pos: Starting position for the projectile
            target_pos: Target position for the projectile
            entity_manager: Entity manager for creating projectiles
        """
        handler = self._projectile_handlers.get(weapon.projectile_type)
        if handler:
            projectile = handler.create_projectile(
                weapon,
                start_pos.get_position(),
                target_pos.get_position(),
                entity_manager,
            )

            if projectile:
                # AI-NOTE : 2025-08-11 투사체 생성 성공 로깅
                # - 이유: 디버깅과 개발 중 동작 확인을 위함
                # - 요구사항: 투사체 생성 성공 시 로그 출력
                # - 히스토리: 개발 단계에서만 사용, 배포 시 제거 예정
                pass  # TODO: 로깅 시스템 구현 후 활용

"""
WeaponManager for centralized weapon component management and stat modifications.

This manager provides a unified interface for weapon-related operations,
including stat modifications from level-ups and item synergies.
"""

from typing import TYPE_CHECKING, Optional

from ..components.player_component import PlayerComponent
from ..components.weapon_component import WeaponComponent
from ..core.events.base_event import BaseEvent
from ..core.events.event_types import EventType
from ..core.events.interfaces import IEventSubscriber
from ..core.events.level_up_event import LevelUpEvent
from ..interfaces import IWeaponManager

if TYPE_CHECKING:
    from ..core.entity import Entity
    from ..core.entity_manager import EntityManager
    from ..interfaces import IEntityManager
    from ..managers.dto import WeaponDTO


class WeaponManager(IEventSubscriber, IWeaponManager):
    """
    Manager for centralized weapon component operations and stat modifications.

    The WeaponManager provides:
    - Centralized weapon component access and modification
    - Level-up based attack speed bonuses
    - Future weapon enhancement features
    - Event-driven weapon stat updates
    """

    def __init__(self, entity_manager: 'IEntityManager') -> None:
        """Initialize the WeaponManager."""
        # AI-NOTE : 2025-08-16 무기 매니저 초기화 - 중앙집중식 무기 관리
        # - 이유: WeaponComponent 접근을 통일하고 레벨업 이벤트 처리
        # - 요구사항: 경험치 획득 시 공격 속도 10% 증가
        # - 히스토리: WeaponSystem에서 분리된 독립적인 관리자 구조

        self._entity_manager: IEntityManager = entity_manager

        # 레벨업당 공격 속도 증가율 (10%)
        self._attack_speed_bonus_per_level = 0.1

        # 무기 스탯 캐시 (성능 최적화용)
        self._weapon_stat_cache: dict[str, dict[str, float]] = {}

    @classmethod
    def create(cls, entity_manager: 'IEntityManager') -> 'IWeaponManager':
        """WeaponManager 구현체를 생성하는 정적 팩토리 메서드"""
        return cls(entity_manager)

    def set_entity_manager(self, entity_manager: 'EntityManager') -> None:
        """
        Set the entity manager for component access.

        Args:
            entity_manager: Entity manager instance.
        """
        self._entity_manager = entity_manager

    def get_subscribed_events(self) -> list[EventType]:
        """
        Get the list of event types this subscriber wants to receive.

        Returns:
            List of EventType values for LEVEL_UP events.
        """
        return [EventType.LEVEL_UP]

    def handle_event(self, event: BaseEvent) -> None:
        """
        Handle incoming events.

        Args:
            event: The event to handle.
        """
        if isinstance(event, LevelUpEvent):
            self._handle_level_up(event)

    def _handle_level_up(self, event: LevelUpEvent) -> None:
        """
        Handle level up events by increasing attack speed.

        Args:
            event: The level up event to process.
        """
        if not self._entity_manager:
            return

        # 플레이어 엔티티 찾기
        player_entity = self._find_player_by_id(event.player_entity_id)
        if not player_entity:
            return

        # 무기 컴포넌트 가져오기
        weapon_comp = self._entity_manager.get_component(
            player_entity, WeaponComponent
        )
        if not weapon_comp:
            return

        # AI-NOTE : 2025-08-16 레벨업 시 공격 속도 증가 적용
        # - 이유: 경험치 획득에 따른 플레이어 성장 보상 시스템
        # - 요구사항: 레벨업마다 공격 속도 10% 증가
        # - 히스토리: 기본 공격 속도에서 누적 보너스 계산

        # 현재 레벨에 따른 총 공격 속도 보너스 계산
        level_bonus = (
            event.new_level - 1
        ) * self._attack_speed_bonus_per_level

        # 기본 공격 속도에 보너스 적용 (캐시에서 기본값 가져오기)
        base_attack_speed = self._get_base_attack_speed(player_entity)
        new_attack_speed = base_attack_speed * (1.0 + level_bonus)

        # 무기 컴포넌트 업데이트
        weapon_comp.attack_speed = new_attack_speed

        # 캐시 무효화 (다음 조회 시 새로운 값 반영)
        self._invalidate_weapon_cache(player_entity)

    def _find_player_by_id(self, entity_id: str) -> Optional['Entity']:
        """
        Find player entity by ID.

        Args:
            entity_id: Entity ID to search for.

        Returns:
            Player entity if found, None otherwise.
        """
        if not self._entity_manager:
            return None

        for entity in self._entity_manager.get_all_entities():
            if (
                hasattr(entity, 'entity_id')
                and entity.entity_id == entity_id
                and self._entity_manager.has_component(entity, PlayerComponent)
            ):
                return entity

        return None

    def _get_base_attack_speed(self, entity: 'Entity') -> float:
        """
        Get the base attack speed for an entity's weapon.

        Args:
            entity: Entity to get base attack speed for.

        Returns:
            Base attack speed value.
        """
        if not self._entity_manager:
            return 2.0  # 기본값

        # 캐시에서 기본 공격 속도 확인
        entity_id = getattr(entity, 'entity_id', str(id(entity)))
        if entity_id in self._weapon_stat_cache:
            cached_stats = self._weapon_stat_cache[entity_id]
            if 'base_attack_speed' in cached_stats:
                return cached_stats['base_attack_speed']

        # 무기 컴포넌트에서 현재 설정된 값을 기본값으로 사용
        weapon_comp = self._entity_manager.get_component(
            entity, WeaponComponent
        )
        base_speed = 2.0  # 기본값
        if weapon_comp:
            # 첫 번째 조회 시에는 현재 attack_speed를 기본값으로 캐시
            base_speed = weapon_comp.attack_speed

        # 캐시에 저장
        if entity_id not in self._weapon_stat_cache:
            self._weapon_stat_cache[entity_id] = {}
        self._weapon_stat_cache[entity_id]['base_attack_speed'] = base_speed

        return base_speed

    def _invalidate_weapon_cache(self, entity: 'Entity') -> None:
        """
        Invalidate weapon stat cache for an entity.

        Args:
            entity: Entity to invalidate cache for.
        """
        entity_id = getattr(entity, 'entity_id', str(id(entity)))
        if entity_id in self._weapon_stat_cache:
            # 기본 공격 속도는 유지하고 다른 캐시만 무효화
            base_speed = self._weapon_stat_cache[entity_id].get(
                'base_attack_speed'
            )
            self._weapon_stat_cache[entity_id] = {}
            if base_speed is not None:
                self._weapon_stat_cache[entity_id]['base_attack_speed'] = (
                    base_speed
                )

    def get_weapon_component(
        self, entity: 'Entity'
    ) -> WeaponComponent | None:
        """
        Get weapon component for an entity.

        Args:
            entity: Entity to get weapon component for.

        Returns:
            WeaponComponent if exists, None otherwise.
        """
        if not self._entity_manager:
            return None

        return self._entity_manager.get_component(entity, WeaponComponent)

    def update_weapon_stats(self, entity: 'Entity') -> None:
        """
        Update weapon stats based on current level and items.

        Args:
            entity: Entity to update weapon stats for.
        """
        # AI-NOTE : 미래 확장 포인트 - 아이템 시너지 및 추가 보너스
        # - 목적: 아이템 조합에 따른 무기 스탯 보너스 적용
        # - 구현 예시: 축구공 + 축구화 조합 시 데미지 15% 증가
        # - 확장성: 레벨, 아이템, 임시 버프 등 모든 보너스 통합 계산

        # 현재는 레벨업 이벤트에서만 처리, 향후 확장 예정
        pass

    def cleanup(self) -> None:
        """Clean up manager resources."""
        self._weapon_stat_cache.clear()
        self._entity_manager = None

    # ========================================
    # IWeaponManager 인터페이스 구현 메서드들
    # ========================================

    def get_weapon_components(self, entity: 'Entity') -> list[WeaponComponent]:
        """엔티티의 모든 무기 컴포넌트들을 반환 (다중 무기 지원)"""
        if not self._entity_manager:
            return []

        return self._entity_manager.get_components(entity, WeaponComponent)

    def get_primary_weapon(self, entity: 'Entity') -> WeaponComponent | None:
        """주 무기 컴포넌트 반환"""
        weapons = self.get_weapon_components(entity)
        return weapons[0] if weapons else None

    def get_effective_attack_speed(self, entity: 'Entity', weapon_index: int = 0) -> float:
        """특정 무기의 유효 공격속도 반환"""
        weapons = self.get_weapon_components(entity)
        if weapon_index >= len(weapons):
            return 2.0  # 기본값

        return weapons[weapon_index].attack_speed

    def get_effective_damage(self, entity: 'Entity', weapon_index: int = 0) -> int:
        """특정 무기의 유효 데미지 반환"""
        weapons = self.get_weapon_components(entity)
        if weapon_index >= len(weapons):
            return 25  # 기본값

        return weapons[weapon_index].get_effective_damage()

    def get_total_dps(self, entity: 'Entity') -> float:
        """모든 무기의 합계 DPS 계산"""
        weapons = self.get_weapon_components(entity)
        total_dps = 0.0

        for weapon in weapons:
            damage = weapon.get_effective_damage()
            attack_speed = weapon.attack_speed
            dps = damage * attack_speed
            total_dps += dps

        return total_dps

    def entity_to_weapon_dto(self, entity: 'Entity') -> 'WeaponDTO':
        """엔티티를 WeaponDTO로 변환"""
        from ..managers.dto import WeaponDTO

        weapons = self.get_weapon_components(entity)
        if not weapons:
            raise ValueError(f"Entity {entity.entity_id} has no weapon components")

        weapon_data = []
        for weapon in weapons:
            weapon_info = {
                'weapon_type': weapon.weapon_type.name,
                'damage': weapon.get_effective_damage(),
                'attack_speed': weapon.attack_speed,
                'attack_range': weapon.attack_range
            }
            weapon_data.append(weapon_info)

        return WeaponDTO(
            entity_id=entity.entity_id,
            weapons=weapon_data,
            primary_weapon_index=0,
            total_dps=self.get_total_dps(entity)
        )

    def weapon_dto_to_entity(self, dto: 'WeaponDTO') -> 'Entity':
        """WeaponDTO를 기반으로 무기 엔티티를 생성"""
        from ..components.weapon_component import WeaponType

        entity = self._entity_manager.create_entity()

        for _i, weapon_data in enumerate(dto.weapons):
            weapon_type = WeaponType[weapon_data['weapon_type']]
            weapon_component = WeaponComponent(
                weapon_type=weapon_type,
                damage=weapon_data['damage'],
                attack_speed=weapon_data['attack_speed'],
                attack_range=weapon_data['attack_range']
            )
            self._entity_manager.add_component(entity, weapon_component)

        return entity

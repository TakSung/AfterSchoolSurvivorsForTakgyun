"""
PlayerStatsSystem for handling level-up benefits and stat management.

This system processes LEVEL_UP events and applies appropriate stat increases
to players, managing the progression mechanics for the game.
"""

import time
from typing import TYPE_CHECKING

from ..components.experience_component import ExperienceComponent
from ..components.health_component import HealthComponent
from ..components.player_component import PlayerComponent
from ..core.events.event_types import EventType
from ..core.events.interfaces import IEventSubscriber
from ..core.events.level_up_event import LevelUpEvent
from ..core.system import System

if TYPE_CHECKING:
    from ..core.entity import Entity
    from ..core.entity_manager import EntityManager
    from ..core.events.base_event import BaseEvent


class PlayerStatsSystem(System, IEventSubscriber):
    """
    System that manages player stat progression through level-ups.

    The PlayerStatsSystem processes:
    - LEVEL_UP events to apply stat increases
    - Health and stat scaling based on level
    - Level-up benefit calculations and application
    """

    def __init__(self, priority: int = 30) -> None:
        """
        Initialize the PlayerStatsSystem.

        Args:
            priority: System execution priority (30 = after experience systems)
        """
        super().__init__(priority=priority)

        # AI-NOTE : 2025-08-15 플레이어 스탯 시스템 초기화 - 레벨업 혜택 적용
        # - 이유: 레벨업 시 플레이어 능력치 증가로 성장감 제공 필요
        # - 요구사항: LEVEL_UP 이벤트 수신, 체력/데미지 등 스탯 증가 적용
        # - 히스토리: 로그라이크 게임의 핵심 진행 시스템 구현

        self._last_update_time = 0.0

        # 레벨업 시 스탯 증가 공식 설정
        self._stat_growth = {
            'health_per_level': 20,  # 레벨당 최대 체력 증가량
            'health_heal_ratio': 0.5,  # 레벨업 시 체력 회복 비율 (50%)
            # 미래 확장: 'damage_per_level': 5, 'speed_per_level': 2
        }

    def initialize(self) -> None:
        """Initialize the player stats system."""
        super().initialize()
        self._last_update_time = time.time()

    def get_subscribed_events(self) -> list[EventType]:
        """
        Get the list of event types this subscriber wants to receive.

        Returns:
            List of EventType values for LEVEL_UP events.
        """
        return [EventType.LEVEL_UP]

    def handle_event(self, event: 'BaseEvent') -> None:
        """
        Handle incoming events.

        Args:
            event: The event to handle.
        """
        if isinstance(event, LevelUpEvent):
            self._handle_level_up(event)

    def _handle_level_up(self, event: LevelUpEvent) -> None:
        """
        Handle level-up events by applying stat increases to the player.

        Args:
            event: The level-up event to process.
        """
        if not self._entity_manager:
            return

        # 레벨업한 플레이어 엔티티 찾기
        player_entity = self._find_player_by_id(event.get_player_id())
        if not player_entity:
            return

        # 레벨 차이에 따른 스탯 증가 적용
        level_gained = event.get_level_difference()
        new_level = event.get_new_level()

        # 체력 증가 및 일부 회복 적용
        self._apply_health_increase(player_entity, level_gained, new_level)

        # 미래 확장: 데미지, 속도, 특수 능력 등 증가 적용
        # self._apply_damage_increase(player_entity, level_gained, new_level)
        # self._apply_special_abilities(player_entity, new_level)

    def _find_player_by_id(self, player_entity_id: str) -> 'Entity | None':
        """
        Find a player entity by its ID.

        Args:
            player_entity_id: The player entity ID to search for.

        Returns:
            Player entity if found, None otherwise.
        """
        if not self._entity_manager:
            return None

        # 모든 엔티티 검사하여 플레이어 ID와 일치하는 것 찾기
        for entity in self._entity_manager.get_all_entities():
            if (
                entity.entity_id == player_entity_id
                and self._entity_manager.has_component(entity, PlayerComponent)
                and self._entity_manager.has_component(
                    entity, ExperienceComponent
                )
            ):
                return entity

        return None

    def _apply_health_increase(
        self, player_entity: 'Entity', levels_gained: int, new_level: int
    ) -> None:
        """
        Apply health increase and partial healing on level-up.

        Args:
            player_entity: The player entity to apply health changes to.
            levels_gained: Number of levels gained.
            new_level: New player level.
        """
        if not self._entity_manager:
            return

        # 플레이어의 체력 컴포넌트 가져오기
        health_component = self._entity_manager.get_component(
            player_entity, HealthComponent
        )
        if not health_component:
            # 체력 컴포넌트가 없으면 새로 생성
            health_component = HealthComponent(
                current_health=100, max_health=100
            )
            self._entity_manager.add_component(player_entity, health_component)

        # 레벨당 체력 증가 적용
        health_increase = levels_gained * self._stat_growth['health_per_level']
        new_max_health = health_component.max_health + health_increase

        # AI-NOTE : 레벨업 시 체력 증가와 부분 회복 시스템
        # - 이유: 플레이어의 성장감 제공과 레벨업 보상으로 즉시 혜택 제공
        # - 요구사항: 최대 체력 증가 + 현재 체력 일부 회복으로 레벨업 효과 체감
        # - 공식: 최대 체력 20/레벨 증가, 증가분의 50% 즉시 회복

        # 현재 체력 비율 저장 (레벨업 전)
        old_health_ratio = health_component.get_health_ratio()

        # 최대 체력 증가
        health_component.set_max_health(new_max_health)

        # 레벨업 보상으로 체력 회복 (증가분의 일정 비율)
        heal_amount = int(
            health_increase * self._stat_growth['health_heal_ratio']
        )
        if heal_amount > 0:
            health_component.heal(heal_amount)

        # 로그를 위한 정보 (미래 확장용)
        # print(f"Player {player_entity.entity_id} leveled up to {new_level}!")
        # print(f"Max health: {health_component.max_health} (+{health_increase})")
        # print(f"Healed: {heal_amount} HP")

    def _get_level_up_benefits(self, level: int) -> dict[str, int]:
        """
        Calculate level-up benefits based on player level.

        Args:
            level: Current player level.

        Returns:
            Dictionary containing stat increases for this level.
        """
        # AI-NOTE : 레벨별 혜택 계산 공식 - 확장 가능한 설계
        # - 이유: 레벨에 따른 차별화된 성장과 밸런스 조정 용이성
        # - 요구사항: 기본 스탯 증가 + 특정 레벨 마일스톤 보너스
        # - 확장성: 무기 해금, 스킬 획득, 특수 능력 등 추가 가능

        base_benefits = {
            'health': self._stat_growth['health_per_level'],
            'health_heal': int(
                self._stat_growth['health_per_level']
                * self._stat_growth['health_heal_ratio']
            ),
        }

        # 특정 레벨에서 추가 보너스 (마일스톤 시스템)
        milestone_bonuses = {}

        if level % 5 == 0:  # 5레벨마다 추가 보너스
            milestone_bonuses['bonus_health'] = 10

        if level % 10 == 0:  # 10레벨마다 특별 보너스
            milestone_bonuses['regeneration_boost'] = 1.0

        # 보스 레벨 (15, 30, 45레벨)에서 대폭 강화
        if level in [15, 30, 45]:
            milestone_bonuses['major_health_boost'] = 50

        return {**base_benefits, **milestone_bonuses}

    def update(
        self, entity_manager: 'EntityManager', delta_time: float
    ) -> None:
        """
        Update the player stats system.

        Args:
            entity_manager: The entity manager containing all entities.
            delta_time: Time elapsed since last update in seconds.
        """
        self._entity_manager = entity_manager
        self._last_update_time = time.time()

        # 현재 시스템은 주로 이벤트 기반으로 동작하므로
        # 정기적인 업데이트에서는 특별한 처리 없음

        # 미래 확장: 시간 기반 스탯 버프, 임시 효과 관리 등
        # self._update_temporary_effects(delta_time)
        # self._process_stat_buffs(delta_time)

    def get_system_name(self) -> str:
        """Get the name of this system."""
        return 'PlayerStatsSystem'

    def get_subscriber_name(self) -> str:
        """Get the subscriber name for event bus registration."""
        return 'PlayerStatsSystem'

    def cleanup(self) -> None:
        """Clean up system resources."""
        # 이벤트 버스 정리는 상위 시스템에서 처리
        super().cleanup()

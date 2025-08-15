"""
ExperienceSystem for handling experience gain and level up mechanics.

This system processes experience gain events and manages player leveling,
providing the core progression mechanics for the game.
"""

import time
from typing import TYPE_CHECKING

from ..components.experience_component import ExperienceComponent
from ..components.player_component import PlayerComponent
from ..core.events.enemy_death_event import EnemyDeathEvent
from ..core.events.event_bus import EventBus
from ..core.events.event_types import EventType
from ..core.events.experience_gain_event import ExperienceGainEvent
from ..core.events.interfaces import IEventSubscriber
from ..core.events.level_up_event import LevelUpEvent
from ..core.system import System

if TYPE_CHECKING:
    from ..core.entity import Entity
    from ..core.entity_manager import EntityManager
    from ..core.events.base_event import BaseEvent


class ExperienceSystem(System, IEventSubscriber):
    """
    System that manages experience gain and level progression.

    The ExperienceSystem processes:
    - Enemy death events to award experience
    - Experience component updates and level calculations
    - Level up event generation and notification
    - Experience-related game mechanics
    """

    def __init__(self, priority: int = 25) -> None:
        """
        Initialize the ExperienceSystem.

        Args:
            priority: System execution priority (25 = after combat systems)
        """
        super().__init__(priority=priority)

        # AI-NOTE : 2025-08-15 경험치 시스템 초기화 - 이벤트 기반 설계
        # - 이유: 적 처치와 경험치 획득을 느슨하게 결합하여 확장성 확보
        # - 요구사항: ENEMY_DEATH 이벤트 수신, EXPERIENCE_GAIN/LEVEL_UP 발생
        # - 히스토리: 옵저버 패턴을 통한 시스템 간 통신 구현

        self._event_bus: EventBus | None = None
        self._last_update_time = 0.0

        # 적 타입별 기본 경험치 테이블 (ExperienceComponent의 정책과 연동)
        self._base_enemy_experience = {
            'basic': 50,  # 기본 적
            'enhanced': 75,  # 강화 적
            'boss': 200,  # 보스
            'mini_boss': 150,  # 미니 보스
        }

    def initialize(self) -> None:
        """Initialize the experience system."""
        super().initialize()
        self._last_update_time = time.time()

    def set_event_bus(self, event_bus: EventBus) -> None:
        """
        Set the event bus for this system.

        Args:
            event_bus: The event bus to use for event communication.
        """
        self._event_bus = event_bus
        # ENEMY_DEATH 이벤트를 구독
        if self._event_bus:
            self._event_bus.subscribe(self)

    def get_subscribed_events(self) -> list[EventType]:
        """
        Get the list of event types this subscriber wants to receive.

        Returns:
            List of EventType values for ENEMY_DEATH events.
        """
        return [EventType.ENEMY_DEATH]

    def handle_event(self, event: 'BaseEvent') -> None:
        """
        Handle incoming events.

        Args:
            event: The event to handle.
        """
        if isinstance(event, EnemyDeathEvent):
            self._handle_enemy_death(event)

    def _handle_enemy_death(self, event: EnemyDeathEvent) -> None:
        """
        Handle enemy death events by awarding experience to players.

        Args:
            event: The enemy death event to process.
        """
        if not self._entity_manager:
            return

        # 플레이어 엔티티들 찾기
        player_entities = self._find_player_entities()
        if not player_entities:
            return

        # 적 정보 가져오기 (간단한 구현으로 적 타입을 추정)
        enemy_type = self._determine_enemy_type(event.enemy_entity_id)
        enemy_level = self._determine_enemy_level(event.enemy_entity_id)
        base_experience = self._base_enemy_experience.get(enemy_type, 50)

        # 각 플레이어에게 경험치 부여
        for player_entity in player_entities:
            # 경험치 획득 이벤트 생성 및 발송
            exp_gain_event = ExperienceGainEvent.create_from_enemy_kill(
                player_entity_id=player_entity.entity_id,
                enemy_entity_id=event.enemy_entity_id,
                base_experience=base_experience,
                enemy_type=enemy_type,
                enemy_level=enemy_level,
                timestamp=event.timestamp,
            )

            if self._event_bus:
                self._event_bus.publish(exp_gain_event)

            # 플레이어의 경험치 컴포넌트 업데이트
            self._award_experience_to_player(
                player_entity, base_experience, enemy_type, enemy_level
            )

    def _find_player_entities(self) -> list['Entity']:
        """
        Find all player entities in the game.

        Returns:
            List of player entities.
        """
        if not self._entity_manager:
            return []

        player_entities = []
        for entity in self._entity_manager.get_all_entities():
            if self._entity_manager.has_component(
                entity, PlayerComponent
            ) and self._entity_manager.has_component(
                entity, ExperienceComponent
            ):
                player_entities.append(entity)

        return player_entities

    def _determine_enemy_type(self, enemy_entity_id: str) -> str:
        """
        Determine the type of enemy based on entity ID or other factors.

        Args:
            enemy_entity_id: The enemy entity ID.

        Returns:
            Enemy type string.
        """
        # AI-DEV : 간단한 구현 - 실제로는 EnemyComponent에서 타입 정보 가져올 수 있음
        # - 문제: 적 엔티티가 이미 제거된 경우 컴포넌트 조회 불가
        # - 해결책: 현재는 기본값 반환, 향후 이벤트에 적 정보 포함 고려
        # - 주의사항: 적 타입 결정 로직 개선 필요

        # 임시 구현: ID 패턴으로 적 타입 추정
        if 'boss' in enemy_entity_id.lower():
            return 'boss'
        elif 'mini' in enemy_entity_id.lower():
            return 'mini_boss'
        elif 'enhanced' in enemy_entity_id.lower():
            return 'enhanced'
        else:
            return 'basic'

    def _determine_enemy_level(self, enemy_entity_id: str) -> int:
        """
        Determine the level of enemy based on entity ID or other factors.

        Args:
            enemy_entity_id: The enemy entity ID.

        Returns:
            Enemy level.
        """
        # AI-DEV : 간단한 구현 - 레벨 정보는 게임 진행도에 따라 결정
        # - 문제: 현재는 고정값 반환, 실제로는 게임 시간이나 웨이브 정보 필요
        # - 해결책: 게임 상태 매니저와 연동하여 동적 레벨 계산
        # - 주의사항: 시간에 따른 적 레벨 스케일링 구현 필요

        # 임시 구현: 기본 레벨 1
        return 1

    def _award_experience_to_player(
        self,
        player_entity: 'Entity',
        base_experience: int,
        enemy_type: str,
        enemy_level: int,
    ) -> None:
        """
        Award experience to a specific player entity.

        Args:
            player_entity: The player entity to award experience to.
            base_experience: Base experience amount.
            enemy_type: Type of enemy killed.
            enemy_level: Level of enemy killed.
        """
        if not self._entity_manager:
            return

        # 플레이어의 경험치 컴포넌트 가져오기
        exp_component = self._entity_manager.get_component(
            player_entity, ExperienceComponent
        )
        if not exp_component:
            return

        # 레벨업 전 상태 저장
        previous_level = exp_component.level
        previous_total_exp = exp_component.total_exp_earned

        # 경험치 추가
        actual_exp_gained, level_up_occurred = exp_component.add_experience(
            base_experience, enemy_type, enemy_level
        )

        # 레벨업 발생 시 이벤트 생성
        if level_up_occurred and self._event_bus:
            level_up_event = LevelUpEvent.create_from_level_change(
                player_entity_id=player_entity.entity_id,
                previous_level=previous_level,
                new_level=exp_component.level,
                total_experience=exp_component.total_exp_earned,
                remaining_experience=exp_component.current_exp,
                timestamp=self._last_update_time,
            )
            self._event_bus.publish(level_up_event)

    def update(
        self, entity_manager: 'EntityManager', delta_time: float
    ) -> None:
        """
        Update the experience system.

        Args:
            entity_manager: The entity manager containing all entities.
            delta_time: Time elapsed since last update in seconds.
        """
        self._entity_manager = entity_manager
        self._last_update_time = time.time()

        # 현재 시스템은 주로 이벤트 기반으로 동작하므로
        # 정기적인 업데이트에서는 특별한 처리 없음

        # 미래 확장: 시간 기반 경험치 획득, 경험치 배율 이벤트 등
        # self._process_time_based_experience(delta_time)

    def _process_time_based_experience(self, delta_time: float) -> None:
        """
        Process time-based experience gain (for future features).

        Args:
            delta_time: Time elapsed since last update.
        """
        # AI-NOTE : 미래 확장 포인트 - 시간 기반 경험치 시스템
        # - 목적: 아이들 게임 요소, 생존 시간 보너스 등 구현
        # - 구현 예시: 특정 아이템 보유 시 시간당 경험치 획득
        # - 확장성: 경험치 배율 이벤트, 더블 경험치 시간 등

        # 현재는 미구현 - 필요시 활성화
        pass

    def get_system_name(self) -> str:
        """Get the name of this system."""
        return 'ExperienceSystem'

    def cleanup(self) -> None:
        """Clean up system resources."""
        if self._event_bus:
            self._event_bus.unsubscribe(self)
        super().cleanup()

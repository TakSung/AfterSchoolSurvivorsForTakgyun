"""
ExperienceGainEvent implementation for experience gain notifications.

This module provides the event structure for communicating experience
gain events throughout the game systems, enabling loose coupling between
combat systems and progression systems.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from .base_event import BaseEvent
from .event_types import EventType

if TYPE_CHECKING:
    pass


@dataclass
class ExperienceGainEvent(BaseEvent):
    """
    Event fired when a player gains experience points.

    This event carries information about experience gained,
    allowing other systems to react to experience changes.
    """

    # AI-NOTE : 2025-08-15 경험치 획득 이벤트 시스템 도입
    # - 이유: 적 처치 시 경험치 부여를 위한 이벤트 기반 시스템 필요
    # - 요구사항: 경험치양, 획득 소스, 적 정보 전달
    # - 히스토리: ExperienceComponent와 연동하여 느슨한 결합 구현

    player_entity_id: str  # 경험치를 받는 플레이어 엔티티 ID
    experience_amount: int  # 획득한 경험치 양
    source_type: str  # 경험치 획득 소스 (enemy_kill, quest, etc)
    source_entity_id: str  # 소스 엔티티 ID (적 ID 등)
    enemy_type: str = 'basic'  # 적 타입 (basic, enhanced, boss 등)
    enemy_level: int = 1  # 적 레벨

    def get_event_type(self) -> EventType:  # noqa: D102
        return EventType.EXPERIENCE_GAIN

    def __post_init__(self) -> None:
        """Initialize the ExperienceGainEvent with proper validation."""
        # 이벤트 타입 자동 설정
        assert self.get_event_type() is EventType.EXPERIENCE_GAIN, (
            '반드시 EXPERIENCE_GAIN 타입이여야 한다.'
        )

        # 부모 클래스의 __post_init__ 호출
        super().__post_init__()

        # 데이터 검증 수행
        if not self.validate():
            raise ValueError(
                f'Invalid ExperienceGainEvent data: '
                f"player_id='{self.player_entity_id}', "
                f'exp={self.experience_amount}, '
                f"source='{self.source_type}'"
            )

    def validate(self) -> bool:
        """
        Validate the experience gain event data.

        Returns:
            True if the event data is valid, False otherwise.
        """
        # player_entity_id 검증
        if (
            not isinstance(self.player_entity_id, str)
            or not self.player_entity_id.strip()
        ):
            return False

        # 경험치 양 검증
        if (
            not isinstance(self.experience_amount, int)
            or self.experience_amount <= 0
        ):
            return False

        # source_type 검증
        if (
            not isinstance(self.source_type, str)
            or not self.source_type.strip()
        ):
            return False

        # source_entity_id 검증
        if (
            not isinstance(self.source_entity_id, str)
            or not self.source_entity_id.strip()
        ):
            return False

        # enemy_type 검증
        if not isinstance(self.enemy_type, str) or not self.enemy_type.strip():
            return False

        # enemy_level 검증
        if not isinstance(self.enemy_level, int) or self.enemy_level <= 0:
            return False

        return True

    @classmethod
    def create_from_enemy_kill(
        cls,
        player_entity_id: str,
        enemy_entity_id: str,
        base_experience: int,
        enemy_type: str = 'basic',
        enemy_level: int = 1,
        timestamp: float | None = None,
        created_at: datetime | None = None,
    ) -> 'ExperienceGainEvent':
        """
        Create an ExperienceGainEvent from enemy kill information.

        Args:
            player_entity_id: ID of the player gaining experience
            enemy_entity_id: ID of the enemy that was killed
            base_experience: Base experience amount before modifiers
            enemy_type: Type of enemy killed
            enemy_level: Level of enemy killed
            timestamp: Optional custom timestamp
            created_at: Optional custom creation datetime

        Returns:
            A new ExperienceGainEvent instance.
        """
        return cls(
            timestamp=timestamp if timestamp is not None else 0.0,
            created_at=created_at,
            player_entity_id=player_entity_id,
            experience_amount=base_experience,
            source_type='enemy_kill',
            source_entity_id=enemy_entity_id,
            enemy_type=enemy_type,
            enemy_level=enemy_level,
        )

    @classmethod
    def create_from_quest(
        cls,
        player_entity_id: str,
        quest_id: str,
        experience_amount: int,
        timestamp: float | None = None,
        created_at: datetime | None = None,
    ) -> 'ExperienceGainEvent':
        """
        Create an ExperienceGainEvent from quest completion.

        Args:
            player_entity_id: ID of the player gaining experience
            quest_id: ID of the completed quest
            experience_amount: Experience amount from quest
            timestamp: Optional custom timestamp
            created_at: Optional custom creation datetime

        Returns:
            A new ExperienceGainEvent instance.
        """
        return cls(
            timestamp=timestamp if timestamp is not None else 0.0,
            created_at=created_at,
            player_entity_id=player_entity_id,
            experience_amount=experience_amount,
            source_type='quest_completion',
            source_entity_id=quest_id,
            enemy_type='none',
            enemy_level=1,
        )

    def get_player_id(self) -> str:
        """Get the player entity ID."""
        return self.player_entity_id

    def get_experience_amount(self) -> int:
        """Get the experience amount."""
        return self.experience_amount

    def get_source_type(self) -> str:
        """Get the experience source type."""
        return self.source_type

    def get_source_entity_id(self) -> str:
        """Get the source entity ID."""
        return self.source_entity_id

    def get_enemy_type(self) -> str:
        """Get the enemy type."""
        return self.enemy_type

    def get_enemy_level(self) -> int:
        """Get the enemy level."""
        return self.enemy_level

    def is_from_enemy_kill(self) -> bool:
        """Check if this experience was gained from killing an enemy."""
        return self.source_type == 'enemy_kill'

    def is_from_quest(self) -> bool:
        """Check if this experience was gained from quest completion."""
        return self.source_type == 'quest_completion'

    def __str__(self) -> str:
        """String representation of the experience gain event."""
        return (
            f'ExperienceGainEvent('
            f'player_id={self.player_entity_id}, '
            f'exp={self.experience_amount}, '
            f'source={self.source_type}, '
            f'enemy_type={self.enemy_type}, '
            f'enemy_level={self.enemy_level})'
        )

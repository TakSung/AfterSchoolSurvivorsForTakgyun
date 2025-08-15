"""
LevelUpEvent implementation for level up notifications.

This module provides the event structure for communicating level up
events throughout the game systems, enabling other systems to react
to player progression.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from .base_event import BaseEvent
from .event_types import EventType

if TYPE_CHECKING:
    pass


@dataclass
class LevelUpEvent(BaseEvent):
    """
    Event fired when a player levels up.

    This event carries information about the level up,
    allowing other systems to react to level changes.
    """

    # AI-NOTE : 2025-08-15 레벨업 이벤트 시스템 도입
    # - 이유: 레벨업 시 다른 시스템들이 반응할 수 있도록 알림 필요
    # - 요구사항: 플레이어 ID, 이전/현재 레벨, 총 경험치 정보 전달
    # - 히스토리: ExperienceSystem에서 발생시켜 UI, 능력치 등 업데이트

    player_entity_id: str  # 레벨업한 플레이어 엔티티 ID
    previous_level: int  # 이전 레벨
    new_level: int  # 새로운 레벨
    total_experience: int  # 총 획득 경험치
    remaining_experience: int  # 현재 레벨에서의 남은 경험치

    def get_event_type(self) -> EventType:  # noqa: D102
        return EventType.LEVEL_UP

    def __post_init__(self) -> None:
        """Initialize the LevelUpEvent with proper validation."""
        # 이벤트 타입 자동 설정
        assert self.get_event_type() is EventType.LEVEL_UP, (
            '반드시 LEVEL_UP 타입이여야 한다.'
        )

        # 부모 클래스의 __post_init__ 호출
        super().__post_init__()

        # 데이터 검증 수행
        if not self.validate():
            raise ValueError(
                f'Invalid LevelUpEvent data: '
                f"player_id='{self.player_entity_id}', "
                f'prev_level={self.previous_level}, '
                f'new_level={self.new_level}'
            )

    def validate(self) -> bool:
        """
        Validate the level up event data.

        Returns:
            True if the event data is valid, False otherwise.
        """
        # player_entity_id 검증
        if (
            not isinstance(self.player_entity_id, str)
            or not self.player_entity_id.strip()
        ):
            return False

        # 레벨 검증
        if not isinstance(self.previous_level, int) or not isinstance(
            self.new_level, int
        ):
            return False

        if self.previous_level <= 0 or self.new_level <= 0:
            return False

        # 새 레벨이 이전 레벨보다 커야 함
        if self.new_level <= self.previous_level:
            return False

        # 경험치 검증
        if not isinstance(self.total_experience, int) or not isinstance(
            self.remaining_experience, int
        ):
            return False

        if self.total_experience < 0 or self.remaining_experience < 0:
            return False

        return True

    @classmethod
    def create_from_level_change(
        cls,
        player_entity_id: str,
        previous_level: int,
        new_level: int,
        total_experience: int,
        remaining_experience: int,
        timestamp: float | None = None,
        created_at: datetime | None = None,
    ) -> 'LevelUpEvent':
        """
        Create a LevelUpEvent from level change information.

        Args:
            player_entity_id: ID of the player who leveled up
            previous_level: The player's previous level
            new_level: The player's new level
            total_experience: Total experience earned by the player
            remaining_experience: Experience remaining in the current level
            timestamp: Optional custom timestamp
            created_at: Optional custom creation datetime

        Returns:
            A new LevelUpEvent instance.
        """
        return cls(
            timestamp=timestamp if timestamp is not None else 0.0,
            created_at=created_at,
            player_entity_id=player_entity_id,
            previous_level=previous_level,
            new_level=new_level,
            total_experience=total_experience,
            remaining_experience=remaining_experience,
        )

    def get_player_id(self) -> str:
        """Get the player entity ID."""
        return self.player_entity_id

    def get_previous_level(self) -> int:
        """Get the previous level."""
        return self.previous_level

    def get_new_level(self) -> int:
        """Get the new level."""
        return self.new_level

    def get_level_difference(self) -> int:
        """Get the number of levels gained."""
        return self.new_level - self.previous_level

    def get_total_experience(self) -> int:
        """Get the total experience."""
        return self.total_experience

    def get_remaining_experience(self) -> int:
        """Get the remaining experience in current level."""
        return self.remaining_experience

    def is_multiple_level_up(self) -> bool:
        """Check if this was a multiple level up (gained more than 1 level)."""
        return self.get_level_difference() > 1

    def __str__(self) -> str:
        """String representation of the level up event."""
        levels_gained = self.get_level_difference()
        return (
            f'LevelUpEvent('
            f'player_id={self.player_entity_id}, '
            f'{self.previous_level}->{self.new_level} '
            f'(+{levels_gained} level{"s" if levels_gained > 1 else ""}), '
            f'total_exp={self.total_experience})'
        )

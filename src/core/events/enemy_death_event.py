"""
EnemyDeathEvent implementation for enemy death notifications.

This module provides the event structure for communicating enemy death
events throughout the game systems, enabling loose coupling between
combat systems and other game components.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from .base_event import BaseEvent
from .event_types import EventType

if TYPE_CHECKING:
    from ...core.entity import Entity


@dataclass
class EnemyDeathEvent(BaseEvent):
    """
    Event fired when an enemy dies in the game.
    
    This event carries the minimal necessary information about an enemy
    death, following the principle of minimal data transfer. Systems that
    need additional enemy information can query the EntityManager using
    the provided enemy_entity_id.
    """

    # AI-NOTE : 2025-08-12 적 사망 이벤트 시스템 도입
    # - 이유: ProjectileSystem과 다른 시스템 간 느슨한 결합 필요
    # - 요구사항: 최소 데이터 전달, EntityManager 연동, 검증 메커니즘
    # - 히스토리: 옵저버 패턴 리팩토링의 첫 단계 구현

    enemy_entity_id: str

    def __post_init__(self) -> None:
        """Initialize the EnemyDeathEvent with proper event type."""
        # 이벤트 타입 자동 설정
        object.__setattr__(self, 'event_type', EventType.ENEMY_DEATH)

        # 부모 클래스의 __post_init__ 호출
        super().__post_init__()

        # 데이터 검증 수행
        if not self.validate():
            raise ValueError(f"Invalid EnemyDeathEvent data: enemy_entity_id='{self.enemy_entity_id}'")

    def validate(self) -> bool:
        """
        Validate the enemy death event data.
        
        Returns:
            True if the event data is valid, False otherwise.
        """
        # enemy_entity_id가 유효한 문자열인지 검증
        if not isinstance(self.enemy_entity_id, str):
            return False

        # 빈 문자열이나 공백만 있는 문자열 검증
        if not self.enemy_entity_id or not self.enemy_entity_id.strip():
            return False

        return True

    @classmethod
    def create_from_entity(
        cls,
        enemy_entity: 'Entity',
        timestamp: float | None = None,
        created_at: datetime | None = None
    ) -> 'EnemyDeathEvent':
        """
        Create an EnemyDeathEvent from an Entity object.
        
        This convenience method extracts the entity ID and creates the event
        with proper validation.
        
        Args:
            enemy_entity: The enemy entity that died.
            timestamp: Optional custom timestamp. If None, current time is used.
            created_at: Optional custom creation datetime. If None, current time is used.
            
        Returns:
            A new EnemyDeathEvent instance.
            
        Raises:
            ValueError: If the entity is invalid or has no ID.
        """
        if enemy_entity is None:
            raise ValueError("Entity cannot be None")

        if not hasattr(enemy_entity, 'id') or not enemy_entity.id:
            raise ValueError("Entity must have a valid ID")

        return cls(
            event_type=EventType.ENEMY_DEATH,  # 명시적으로 설정하지만 __post_init__에서 덮어씀
            timestamp=timestamp if timestamp is not None else 0.0,  # 0.0이면 자동 설정
            created_at=created_at,
            enemy_entity_id=str(enemy_entity.id)
        )

    @classmethod
    def create_from_id(
        cls,
        enemy_entity_id: str,
        timestamp: float | None = None,
        created_at: datetime | None = None
    ) -> 'EnemyDeathEvent':
        """
        Create an EnemyDeathEvent from an entity ID string.
        
        Args:
            enemy_entity_id: The ID of the enemy that died.
            timestamp: Optional custom timestamp. If None, current time is used.
            created_at: Optional custom creation datetime. If None, current time is used.
            
        Returns:
            A new EnemyDeathEvent instance.
            
        Raises:
            ValueError: If the entity ID is invalid.
        """
        return cls(
            event_type=EventType.ENEMY_DEATH,  # 명시적으로 설정하지만 __post_init__에서 덮어씀
            timestamp=timestamp if timestamp is not None else 0.0,  # 0.0이면 자동 설정
            created_at=created_at,
            enemy_entity_id=enemy_entity_id
        )

    def get_enemy_id(self) -> str:
        """
        Get the enemy entity ID.
        
        Returns:
            The enemy entity ID that this event represents.
        """
        return self.enemy_entity_id

    def __str__(self) -> str:
        """String representation of the enemy death event."""
        return (
            f'EnemyDeathEvent('
            f'enemy_id={self.enemy_entity_id}, '
            f'timestamp={self.timestamp:.3f})'
        )

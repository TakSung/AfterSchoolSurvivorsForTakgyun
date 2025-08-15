"""
ProjectileCreatedEvent for projectile management system.

This event is emitted when a new projectile entity is created,
allowing the ProjectileManager to track projectiles independently
of the ECS component filtering system.
"""

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base_event import BaseEvent
from .event_types import EventType

if TYPE_CHECKING:
    from ..entity import Entity


@dataclass
class ProjectileCreatedEvent(BaseEvent):
    """
    Event emitted when a projectile is created.
    
    This event allows the ProjectileManager to register new projectiles
    without relying on component filtering, solving the issue where
    ProjectileSystem couldn't find created projectiles.
    """
    
    # AI-NOTE : 2025-08-15 투사체 생성 이벤트 시스템 도입
    # - 이유: ECS 컴포넌트 필터링 문제로 투사체를 찾지 못하는 이슈 해결
    # - 요구사항: 투사체 생성 시 즉시 ProjectileManager에 등록
    # - 히스토리: 사용자 제안으로 이벤트 기반 투사체 관리 시스템 구현
    
    projectile_entity_id: str
    owner_entity_id: str
    timestamp: float = 0.0
    created_at: None = None
    
    def get_event_type(self) -> EventType:
        """Get the event type for projectile creation."""
        return EventType.PROJECTILE_CREATED
    
    def validate(self) -> bool:
        """
        Validate event data integrity.
        
        Returns:
            True if the event data is valid, False otherwise.
        """
        # 필수 필드 검증
        if not self.projectile_entity_id or not self.owner_entity_id:
            return False
            
        # 타임스탬프 검증
        if self.timestamp < 0:
            return False
            
        return True
    
    @classmethod
    def create(
        cls,
        projectile_entity: 'Entity',
        owner_entity: 'Entity',
        timestamp: float | None = None
    ) -> 'ProjectileCreatedEvent':
        """
        Create a ProjectileCreatedEvent from entity objects.
        
        Args:
            projectile_entity: The created projectile entity
            owner_entity: The entity that created the projectile
            timestamp: Event timestamp (uses current time if None)
            
        Returns:
            New ProjectileCreatedEvent instance
        """
        if timestamp is None:
            timestamp = time.time()
            
        return cls(
            projectile_entity_id=projectile_entity.entity_id,
            owner_entity_id=owner_entity.entity_id,
            timestamp=timestamp
        )
    
    @classmethod
    def create_from_ids(
        cls,
        projectile_entity_id: str,
        owner_entity_id: str,
        timestamp: float | None = None
    ) -> 'ProjectileCreatedEvent':
        """
        Create a ProjectileCreatedEvent from entity IDs.
        
        Args:
            projectile_entity_id: ID of the created projectile entity
            owner_entity_id: ID of the entity that created the projectile
            timestamp: Event timestamp (uses current time if None)
            
        Returns:
            New ProjectileCreatedEvent instance
        """
        if timestamp is None:
            timestamp = time.time()
            
        return cls(
            projectile_entity_id=projectile_entity_id,
            owner_entity_id=owner_entity_id,
            timestamp=timestamp
        )
    
    def __str__(self) -> str:
        """String representation of the event."""
        return (
            f'ProjectileCreatedEvent('
            f'projectile={self.projectile_entity_id}, '
            f'owner={self.owner_entity_id}, '
            f'timestamp={self.timestamp:.3f})'
        )
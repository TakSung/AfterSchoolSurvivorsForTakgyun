"""
ProjectileManager for event-based projectile tracking.

This manager handles projectile registration through events,
providing an alternative to ECS component filtering for
reliable projectile management.
"""

import logging
import threading
import time
from typing import TYPE_CHECKING, Dict, List, Set

from .events.base_event import BaseEvent
from .events.event_types import EventType
from .events.projectile_created_event import ProjectileCreatedEvent

if TYPE_CHECKING:
    from .entity import Entity
    from .entity_manager import EntityManager

logger = logging.getLogger(__name__)


class ProjectileManager:
    """
    Manager for tracking projectiles through event-based registration.
    
    This class provides an alternative to ECS component filtering
    for projectile management, solving issues where ProjectileSystem
    couldn't find created projectiles.
    """
    
    def __init__(self) -> None:
        """Initialize the ProjectileManager."""
        # AI-NOTE : 2025-08-15 이벤트 기반 투사체 추적 시스템
        # - 이유: ECS 컴포넌트 필터링 문제로 투사체가 발견되지 않는 이슈 해결
        # - 요구사항: 투사체 생성 이벤트를 통한 실시간 등록 및 추적
        # - 히스토리: 사용자 제안으로 ProjectileSystem 대안 구현
        
        # 활성 투사체 추적
        self._active_projectiles: Set[str] = set()
        self._projectile_owners: Dict[str, str] = {}
        self._projectile_creation_times: Dict[str, float] = {}
        
        # 스레드 안전성을 위한 락
        self._lock = threading.RLock()
        
        # 통계
        self._total_created = 0
        self._total_removed = 0
        
        logger.info("ProjectileManager initialized")
    
    def handle_event(self, event: BaseEvent) -> None:
        """
        Handle incoming events related to projectiles.
        
        Args:
            event: Event to process
        """
        if event.get_event_type() == EventType.PROJECTILE_CREATED:
            if isinstance(event, ProjectileCreatedEvent):
                self._register_projectile(event)
    
    def _register_projectile(self, event: ProjectileCreatedEvent) -> None:
        """
        Register a new projectile from creation event.
        
        Args:
            event: ProjectileCreatedEvent containing projectile info
        """
        if not event.validate():
            logger.warning(f"Invalid ProjectileCreatedEvent: {event}")
            return
        
        with self._lock:
            projectile_id = event.projectile_entity_id
            
            # 이미 등록된 투사체인지 확인
            if projectile_id in self._active_projectiles:
                logger.warning(f"Projectile {projectile_id} already registered")
                return
            
            # 투사체 등록
            self._active_projectiles.add(projectile_id)
            self._projectile_owners[projectile_id] = event.owner_entity_id
            self._projectile_creation_times[projectile_id] = event.timestamp
            
            self._total_created += 1
            
            logger.info(
                f"Registered projectile {projectile_id} "
                f"from owner {event.owner_entity_id}"
            )
    
    def unregister_projectile(self, projectile_entity_id: str) -> bool:
        """
        Unregister a projectile (when destroyed or expired).
        
        Args:
            projectile_entity_id: ID of the projectile entity to unregister
            
        Returns:
            True if projectile was found and removed, False otherwise
        """
        with self._lock:
            if projectile_entity_id not in self._active_projectiles:
                return False
            
            # 투사체 제거
            self._active_projectiles.remove(projectile_entity_id)
            self._projectile_owners.pop(projectile_entity_id, None)
            self._projectile_creation_times.pop(projectile_entity_id, None)
            
            self._total_removed += 1
            
            logger.info(f"Unregistered projectile {projectile_entity_id}")
            return True
    
    def get_active_projectiles(self) -> List[str]:
        """
        Get list of all active projectile entity IDs.
        
        Returns:
            List of active projectile entity IDs
        """
        with self._lock:
            return list(self._active_projectiles)
    
    def get_projectile_count(self) -> int:
        """
        Get the total number of active projectiles.
        
        Returns:
            Number of active projectiles
        """
        with self._lock:
            return len(self._active_projectiles)
    
    def get_projectiles_by_owner(self, owner_entity_id: str) -> List[str]:
        """
        Get all projectiles created by a specific owner.
        
        Args:
            owner_entity_id: ID of the owner entity
            
        Returns:
            List of projectile entity IDs owned by the specified entity
        """
        with self._lock:
            return [
                projectile_id for projectile_id, owner_id 
                in self._projectile_owners.items()
                if owner_id == owner_entity_id
            ]
    
    def is_projectile_active(self, projectile_entity_id: str) -> bool:
        """
        Check if a projectile is currently active.
        
        Args:
            projectile_entity_id: ID of the projectile entity
            
        Returns:
            True if projectile is active, False otherwise
        """
        with self._lock:
            return projectile_entity_id in self._active_projectiles
    
    def get_projectile_age(self, projectile_entity_id: str) -> float | None:
        """
        Get the age of a projectile in seconds.
        
        Args:
            projectile_entity_id: ID of the projectile entity
            
        Returns:
            Age in seconds, or None if projectile not found
        """
        with self._lock:
            creation_time = self._projectile_creation_times.get(projectile_entity_id)
            if creation_time is None:
                return None
            return time.time() - creation_time
    
    def cleanup_inactive_projectiles(
        self, entity_manager: 'EntityManager'
    ) -> int:
        """
        Remove projectiles that no longer exist in the entity manager.
        
        Args:
            entity_manager: EntityManager to check entity existence
            
        Returns:
            Number of inactive projectiles removed
        """
        with self._lock:
            inactive_projectiles = []
            
            for projectile_id in self._active_projectiles:
                # 엔티티 매니저에서 엔티티가 존재하는지 확인
                entity = entity_manager.get_entity_by_id(projectile_id)
                if entity is None:
                    inactive_projectiles.append(projectile_id)
            
            # 비활성 투사체 제거
            for projectile_id in inactive_projectiles:
                self.unregister_projectile(projectile_id)
            
            if inactive_projectiles:
                logger.info(f"Cleaned up {len(inactive_projectiles)} inactive projectiles")
            
            return len(inactive_projectiles)
    
    def clear_all_projectiles(self) -> int:
        """
        Clear all registered projectiles.
        
        Returns:
            Number of projectiles that were cleared
        """
        with self._lock:
            count = len(self._active_projectiles)
            self._active_projectiles.clear()
            self._projectile_owners.clear()
            self._projectile_creation_times.clear()
            
            logger.info(f"Cleared all {count} registered projectiles")
            return count
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get projectile manager statistics.
        
        Returns:
            Dictionary containing various statistics
        """
        with self._lock:
            return {
                'active_count': len(self._active_projectiles),
                'total_created': self._total_created,
                'total_removed': self._total_removed,
                'net_created': self._total_created - self._total_removed
            }
    
    def __str__(self) -> str:
        """String representation of the manager."""
        stats = self.get_statistics()
        return (
            f'ProjectileManager('
            f'active={stats["active_count"]}, '
            f'created={stats["total_created"]}, '
            f'removed={stats["total_removed"]})'
        )
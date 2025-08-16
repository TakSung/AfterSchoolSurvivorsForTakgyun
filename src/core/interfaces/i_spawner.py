"""
ISpawner interface for spawner system abstraction.

This module defines the basic contract for all spawner implementations,
enabling polymorphism and dependency inversion in the spawning system.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...dto.spawn_result import SpawnResult


class ISpawner(ABC):
    """
    Abstract interface for spawner systems.
    
    Defines the basic contract that all spawner implementations must follow,
    enabling polymorphic spawner management and testing through dependency injection.
    """
    
    @abstractmethod
    def can_spawn(self) -> bool:
        """
        Determine if spawning is currently possible.
        
        This method should check internal conditions like timing,
        cooldowns, or resource constraints without external dependencies.
        
        Returns:
            True if spawning conditions are met, False otherwise.
        """
        pass
    
    @abstractmethod
    def spawn(self) -> 'SpawnResult | None':
        """
        Generate spawn information for entity creation.
        
        This method creates spawn data without actually creating entities,
        following the separation of concerns principle. Entity creation
        is delegated to appropriate managers.
        
        Returns:
            SpawnResult containing spawn information, or None if spawn failed.
        """
        pass
    
    @abstractmethod
    def get_spawn_info(self) -> dict[str, str]:
        """
        Get current spawner status information.
        
        Provides diagnostic information about the spawner's current state,
        useful for debugging and monitoring. All values must be strings
        for consistent serialization.
        
        Returns:
            Dictionary with spawner status where all values are strings.
        """
        pass
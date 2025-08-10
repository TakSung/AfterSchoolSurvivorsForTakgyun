"""
System base class for ECS (Entity-Component-System) architecture.

Systems contain the game logic and operate on entities that have
specific component combinations.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .entity import Entity
    from .entity_manager import EntityManager


class ISystem(ABC):
    """
    Interface for all systems in the ECS architecture.
    
    Systems are responsible for processing entities that have specific
    component combinations. They contain the game logic and behavior.
    """
    
    @abstractmethod
    def update(self, entity_manager: 'EntityManager', delta_time: float) -> None:
        """
        Update the system logic.
        
        Args:
            entity_manager: The entity manager to access entities and components.
            delta_time: Time elapsed since the last update in seconds.
        """
        pass
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the system.
        
        Called once when the system is registered with the system orchestrator.
        Use this method to set up any resources or initial state.
        """
        pass
    
    def cleanup(self) -> None:
        """
        Clean up system resources.
        
        Called when the system is being removed or the application is shutting down.
        Override this method to clean up any resources.
        """
        pass


class System(ISystem):
    """
    Base implementation of the ISystem interface.
    
    Provides common functionality that most systems will need.
    Systems should inherit from this class and implement the required methods.
    """
    
    def __init__(self, priority: int = 0, enabled: bool = True) -> None:
        """
        Initialize the system.
        
        Args:
            priority: System execution priority (lower numbers execute first).
            enabled: Whether the system is initially enabled.
        """
        self._priority = priority
        self._enabled = enabled
        self._initialized = False
    
    @property
    def priority(self) -> int:
        """Get the system's execution priority."""
        return self._priority
    
    @property
    def enabled(self) -> bool:
        """Check if the system is enabled."""
        return self._enabled
    
    @property
    def initialized(self) -> bool:
        """Check if the system has been initialized."""
        return self._initialized
    
    def enable(self) -> None:
        """Enable the system."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable the system."""
        self._enabled = False
    
    def set_priority(self, priority: int) -> None:
        """Set the system's execution priority."""
        self._priority = priority
    
    @abstractmethod
    def update(self, entity_manager: 'EntityManager', delta_time: float) -> None:
        """
        Update the system logic.
        
        Args:
            entity_manager: The entity manager to access entities and components.
            delta_time: Time elapsed since the last update in seconds.
        """
        pass
    
    def initialize(self) -> None:
        """
        Initialize the system.
        
        Override this method in subclasses to perform custom initialization.
        """
        self._initialized = True
    
    def get_required_components(self) -> list[type]:
        """
        Get the list of component types this system requires.
        
        Override this method in subclasses to specify which components
        entities must have to be processed by this system.
        
        Returns:
            List of component types required by this system.
        """
        return []
    
    def filter_entities(self, entity_manager: 'EntityManager') -> list['Entity']:
        """
        Filter entities based on required components.
        
        Args:
            entity_manager: The entity manager to query entities from.
            
        Returns:
            List of entities that have all required components.
        """
        required_components = self.get_required_components()
        if not required_components:
            return entity_manager.get_all_entities()
        
        return entity_manager.get_entities_with_components(required_components)
    
    def __str__(self) -> str:
        """String representation of the system."""
        status = "enabled" if self._enabled else "disabled"
        init_status = "initialized" if self._initialized else "uninitialized"
        return f"{self.__class__.__name__}(priority={self._priority}, {status}, {init_status})"
"""
EntityManager interface for System dependency injection.

Defines the contract for EntityManager access that Systems will use
through dependency injection, promoting architectural decoupling.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TypeVar, Any

if TYPE_CHECKING:
    from ..entity import Entity
    from ..component import Component

ComponentType = TypeVar('ComponentType', bound='Component')


class IEntityManagerForSystems(ABC):
    """
    Interface for EntityManager access by Systems.
    
    This interface defines the minimum contract that Systems need
    from EntityManager, enabling dependency injection and loose coupling.
    """

    @abstractmethod
    def get_entities_with_components(self, *component_types: type[ComponentType]) -> list['Entity']:
        """
        Get entities that have all specified component types.
        
        Args:
            *component_types: Component types that entities must have
            
        Returns:
            List of entities that have all specified components
        """
        pass

    @abstractmethod
    def get_component(self, entity: 'Entity', component_type: type[ComponentType]) -> ComponentType | None:
        """
        Get a component of specified type from an entity.
        
        Args:
            entity: Entity to get component from
            component_type: Type of component to retrieve
            
        Returns:
            Component instance or None if not found
        """
        pass

    @abstractmethod
    def add_component(self, entity: 'Entity', component: 'Component') -> None:
        """
        Add a component to an entity.
        
        Args:
            entity: Entity to add component to
            component: Component instance to add
        """
        pass

    @abstractmethod
    def remove_component(self, entity: 'Entity', component_type: type[ComponentType]) -> bool:
        """
        Remove a component from an entity.
        
        Args:
            entity: Entity to remove component from
            component_type: Type of component to remove
            
        Returns:
            True if component was removed, False if not found
        """
        pass

    @abstractmethod
    def has_component(self, entity: 'Entity', component_type: type[ComponentType]) -> bool:
        """
        Check if entity has a component of specified type.
        
        Args:
            entity: Entity to check
            component_type: Type of component to check for
            
        Returns:
            True if entity has the component, False otherwise
        """
        pass

    @abstractmethod
    def get_all_entities(self) -> list['Entity']:
        """
        Get all entities in the manager.
        
        Returns:
            List of all entities
        """
        pass
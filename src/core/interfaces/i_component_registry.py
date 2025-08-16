"""
IComponentRegistry interface for ECS component management abstraction.

This interface defines the contract for component storage, retrieval,
and management operations, enabling dependency inversion and multiple
implementations (memory-based, cached, file-based, etc.).

Supports multiple components of the same type per entity (e.g., weapons).
Provides immutable collections to prevent side effects.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator, Sequence
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from ..component import Component
    from ..entity import Entity

T = TypeVar('T', bound='Component')


class IComponentRegistry(ABC):
    """
    Abstract interface for component registry operations.

    Defines the contract for managing components in an ECS architecture,
    including adding, removing, querying, and validating components.
    This interface enables dependency inversion and supports multiple
    implementation strategies (in-memory, cached, persistent, etc.).
    """

    # Core Component Operations

    @abstractmethod
    def add_component(self, entity: 'Entity', component: 'Component') -> None:
        """
        Add a component to an entity.

        Supports multiple components of the same type per entity.
        Each component instance is stored separately.

        Args:
            entity: The entity to add the component to
            component: The component instance to add

        Raises:
            ValueError: If entity is inactive
        """
        pass

    @abstractmethod
    def remove_component(
        self, entity: 'Entity', component: 'Component'
    ) -> bool:
        """
        Remove a specific component instance from an entity.

        Args:
            entity: The entity to remove the component from
            component: The specific component instance to remove

        Returns:
            True if component was removed, False if not found
        """
        pass

    @abstractmethod
    def remove_component_by_type(
        self, entity: 'Entity', component_type: type[T], index: int = 0
    ) -> T | None:
        """
        Remove a component by type and index from an entity.

        Args:
            entity: The entity to remove the component from
            component_type: The type of component to remove
            index: Index of the component to remove (default: 0 for first)

        Returns:
            The removed component instance, or None if not found
        """
        pass

    @abstractmethod
    def remove_all_components_by_type(
        self, entity: 'Entity', component_type: type[T]
    ) -> Sequence[T]:
        """
        Remove all components of a specific type from an entity.

        Args:
            entity: The entity to remove components from
            component_type: The type of components to remove

        Returns:
            Immutable sequence of removed component instances
        """
        pass

    @abstractmethod
    def get_component(
        self, entity: 'Entity', component_type: type[T], index: int = 0
    ) -> T | None:
        """
        Get a single component by type and index from an entity.

        Args:
            entity: The entity to get the component from
            component_type: The type of component to get
            index: Index of the component to get (default: 0 for first)

        Returns:
            The component instance, or None if not found
        """
        pass

    @abstractmethod
    def get_components(
        self, entity: 'Entity', component_type: type[T]
    ) -> Sequence[T]:
        """
        Get all components of a specific type from an entity.

        Args:
            entity: The entity to get components from
            component_type: The type of components to get

        Returns:
            Immutable sequence of component instances (empty if none found)
        """
        pass

    @abstractmethod
    def has_component(
        self, entity: 'Entity', component_type: type['Component']
    ) -> bool:
        """
        Check if an entity has any components of a specific type.

        Args:
            entity: The entity to check
            component_type: The type of component to check for

        Returns:
            True if the entity has at least one component of this type
        """
        pass

    @abstractmethod
    def get_component_count_by_type(
        self, entity: 'Entity', component_type: type['Component']
    ) -> int:
        """
        Get the number of components of a specific type on an entity.

        Args:
            entity: The entity to count components for
            component_type: The type of component to count

        Returns:
            Number of components of the specified type
        """
        pass

    # Entity-Component Relationship Operations

    @abstractmethod
    def get_components_for_entity(
        self, entity: 'Entity'
    ) -> dict[type['Component'], Sequence['Component']]:
        """
        Get all components for a specific entity.

        Args:
            entity: The entity to get components for

        Returns:
            Immutable dictionary mapping types to component sequences
        """
        pass

    @abstractmethod
    def remove_entity_components(
        self, entity: 'Entity'
    ) -> dict[type['Component'], Sequence['Component']]:
        """
        Remove all components from an entity.

        Args:
            entity: The entity to remove components from

        Returns:
            Immutable dictionary of removed components by type to sequences
        """
        pass

    # Query Operations

    @abstractmethod
    def get_entities_with_component(
        self, component_type: type[T]
    ) -> Iterator[tuple['Entity', Sequence[T]]]:
        """
        Get all entities that have a specific component type.

        Args:
            component_type: The type of component to filter by

        Yields:
            Tuples of (entity, immutable_sequence_of_components)
        """
        pass

    @abstractmethod
    def get_entities_with_components(
        self, *component_types: type['Component']
    ) -> Iterator[
        tuple['Entity', dict[type['Component'], Sequence['Component']]]
    ]:
        """
        Get entities that have ALL of the specified component types.

        Args:
            *component_types: Component types that entities must have

        Yields:
            Tuples of (entity, dict_mapping_types_to_component_sequences)
        """
        pass

    @abstractmethod
    def get_entities_with_single_components(
        self, *component_types: type['Component']
    ) -> Iterator[tuple['Entity', tuple['Component', ...]]]:
        """
        Get entities with ALL specified types (single component per type).

        Assumes each entity has exactly one component of each specified type
        and returns the first component found for each type.

        Args:
            *component_types: Component types that entities must have

        Yields:
            Tuples of (entity, tuple_of_single_components)

        Note:
            Convenience method for backward compatibility and simple cases
            where each entity has only one component of each type.
        """
        pass

    # Statistics and Metadata Operations

    @abstractmethod
    def get_component_count(self, component_type: type['Component']) -> int:
        """
        Get the number of components of a specific type.

        Args:
            component_type: The component type to count

        Returns:
            Number of components of the specified type
        """
        pass

    @abstractmethod
    def get_entity_component_count(self, entity: 'Entity') -> int:
        """
        Get the number of components on a specific entity.

        Args:
            entity: The entity to count components for

        Returns:
            Number of components on the entity
        """
        pass

    @abstractmethod
    def get_all_component_types(self) -> set[type['Component']]:
        """
        Get all component types currently stored in the registry.

        Returns:
            Set of all component types in the registry
        """
        pass

    # Lifecycle Operations

    @abstractmethod
    def clear(self) -> None:
        """Clear all components and entities from the registry."""
        pass

    @abstractmethod
    def validate_registry(self) -> bool:
        """
        Validate the internal consistency of the registry.

        Returns:
            True if the registry is consistent, False otherwise
        """
        pass

    # Container Protocol Support

    @abstractmethod
    def __len__(self) -> int:
        """
        Return the total number of component instances in the registry.

        Returns:
            Total number of component instances
        """
        pass

    @abstractmethod
    def __contains__(self, entity: 'Entity') -> bool:
        """
        Check if an entity is managed by this registry.

        Args:
            entity: The entity to check

        Returns:
            True if the entity is managed by this registry
        """
        pass

"""
ComponentRegistry for ECS (Entity-Component-System) architecture.

The ComponentRegistry manages components by type, providing efficient storage,
retrieval, and management of components across all entities.
"""

from collections import defaultdict
from collections.abc import Iterator
from typing import TypeVar, cast
from weakref import WeakSet

from .component import Component
from .entity import Entity

T = TypeVar('T', bound=Component)


class ComponentRegistry:
    """
    Registry that manages components by type for efficient storage/retrieval.

    The registry uses a type-based storage system where components are
    organized by their class type, allowing for fast queries and operations
    on specific component types.
    """

    def __init__(self) -> None:
        """Initialize the component registry."""
        # Maps component type to dict of entity_id -> component instance
        self._components: dict[type[Component], dict[str, Component]] = (
            defaultdict(dict)
        )
        # Maps entity_id to set of component types for that entity
        self._entity_components: dict[str, set[type[Component]]] = defaultdict(
            set
        )
        # WeakSet to track all managed entities
        self._entities: WeakSet[Entity] = WeakSet()

    def add_component(self, entity: Entity, component: Component) -> None:
        """
        Add a component to an entity.

        Args:
            entity: The entity to add the component to
            component: The component instance to add

        Raises:
            ValueError: If the entity already has a component of this type
        """
        if not entity.active:
            raise ValueError(
                f'Cannot add component to inactive entity {entity}'
            )

        component_type = type(component)

        if self.has_component(entity, component_type):
            raise ValueError(
                f'Entity {entity} already has component of type '
                f'{component_type.__name__}'
            )

        # Validate component data before adding
        if not component.validate():
            raise ValueError(f'Component {component} failed validation')

        # Store the component
        self._components[component_type][entity.entity_id] = component
        self._entity_components[entity.entity_id].add(component_type)
        self._entities.add(entity)

    def remove_component(
        self, entity: Entity, component_type: type[T]
    ) -> T | None:
        """
        Remove a component from an entity.

        Args:
            entity: The entity to remove the component from
            component_type: The type of component to remove

        Returns:
            The removed component instance, or None if not found
        """
        if not self.has_component(entity, component_type):
            return None

        # Remove from component storage
        component = self._components[component_type].pop(
            entity.entity_id, None
        )

        # Remove from entity's component set
        self._entity_components[entity.entity_id].discard(component_type)

        # Clean up empty component type storage
        if not self._components[component_type]:
            del self._components[component_type]

        # Clean up empty entity storage
        if not self._entity_components[entity.entity_id]:
            del self._entity_components[entity.entity_id]

        return cast(T, component) if component else None

    def get_component(
        self, entity: Entity, component_type: type[T]
    ) -> T | None:
        """
        Get a component from an entity.

        Args:
            entity: The entity to get the component from
            component_type: The type of component to get

        Returns:
            The component instance, or None if not found
        """
        components_of_type = self._components.get(component_type, {})
        component = components_of_type.get(entity.entity_id)
        return cast(T, component) if component else None

    def has_component(
        self, entity: Entity, component_type: type[Component]
    ) -> bool:
        """
        Check if an entity has a specific component type.

        Args:
            entity: The entity to check
            component_type: The type of component to check for

        Returns:
            True if the entity has the component, False otherwise
        """
        return component_type in self._entity_components.get(
            entity.entity_id, set()
        )

    def get_components_for_entity(
        self, entity: Entity
    ) -> dict[type[Component], Component]:
        """
        Get all components for a specific entity.

        Args:
            entity: The entity to get components for

        Returns:
            Dictionary mapping component types to component instances
        """
        result = {}
        component_types = self._entity_components.get(entity.entity_id, set())

        for component_type in component_types:
            component = self._components[component_type].get(entity.entity_id)
            if component:
                result[component_type] = component

        return result

    def get_entities_with_component(
        self, component_type: type[T]
    ) -> Iterator[tuple[Entity, T]]:
        """
        Get all entities that have a specific component type.

        Args:
            component_type: The type of component to filter by

        Yields:
            Tuples of (entity, component) for each entity with the component
        """
        components_of_type = self._components.get(component_type, {})

        for entity in self._entities:
            if entity.entity_id in components_of_type and entity.active:
                component = components_of_type[entity.entity_id]
                yield entity, cast(T, component)

    def get_entities_with_components(
        self, *component_types: type[Component]
    ) -> Iterator[tuple[Entity, tuple[Component, ...]]]:
        """
        Get entities that have ALL of the specified component types.

        Args:
            *component_types: Component types that entities must have

        Yields:
            Tuples of (entity, tuple_of_components) for matching entities
        """
        if not component_types:
            return

        # Find entities that have all required components
        for entity in self._entities:
            if not entity.active:
                continue

            entity_component_types = self._entity_components.get(
                entity.entity_id, set()
            )

            if all(
                comp_type in entity_component_types
                for comp_type in component_types
            ):
                components = []
                for comp_type in component_types:
                    component = self._components[comp_type][entity.entity_id]
                    components.append(component)
                yield entity, tuple(components)

    def remove_entity_components(
        self, entity: Entity
    ) -> dict[type[Component], Component]:
        """
        Remove all components from an entity.

        Args:
            entity: The entity to remove components from

        Returns:
            Dictionary of removed components mapped by type
        """
        removed_components = {}
        component_types = self._entity_components.get(
            entity.entity_id, set()
        ).copy()

        for component_type in component_types:
            removed_component = self.remove_component(entity, component_type)
            if removed_component:
                removed_components[component_type] = removed_component

        return removed_components

    def get_component_count(self, component_type: type[Component]) -> int:
        """
        Get the number of components of a specific type.

        Args:
            component_type: The component type to count

        Returns:
            Number of components of the specified type
        """
        return len(self._components.get(component_type, {}))

    def get_entity_component_count(self, entity: Entity) -> int:
        """
        Get the number of components on a specific entity.

        Args:
            entity: The entity to count components for

        Returns:
            Number of components on the entity
        """
        return len(self._entity_components.get(entity.entity_id, set()))

    def get_all_component_types(self) -> set[type[Component]]:
        """
        Get all component types currently stored in the registry.

        Returns:
            Set of all component types in the registry
        """
        return set(self._components.keys())

    def clear(self) -> None:
        """Clear all components and entities from the registry."""
        self._components.clear()
        self._entity_components.clear()
        self._entities.clear()

    def validate_registry(self) -> bool:
        """
        Validate the internal consistency of the registry.

        Returns:
            True if the registry is consistent, False otherwise
        """
        # Check that all components referenced in _entity_components
        # exist in _components
        for entity_id, component_types in self._entity_components.items():
            for component_type in component_types:
                if entity_id not in self._components.get(component_type, {}):
                    return False

        # Check that all components in _components
        # are referenced in _entity_components
        for component_type, components in self._components.items():
            for entity_id in components:
                if component_type not in self._entity_components.get(
                    entity_id, set()
                ):
                    return False

        return True

    def __len__(self) -> int:
        """Return the total number of component instances in the registry."""
        return sum(len(components) for components in self._components.values())

    def __contains__(self, entity: Entity) -> bool:
        """Check if an entity is managed by this registry."""
        return entity in self._entities

    def __str__(self) -> str:
        """Return string representation of the registry."""
        total_components = len(self)
        total_types = len(self._components)
        total_entities = len(self._entities)
        return (
            f'ComponentRegistry(components={total_components}, '
            f'types={total_types}, entities={total_entities})'
        )

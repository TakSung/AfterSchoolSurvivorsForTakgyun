"""
EntityManager class for ECS (Entity-Component-System) architecture.

The EntityManager is responsible for creating, destroying, and managing entities
and their components throughout the game lifecycle.
"""

import weakref
from collections import defaultdict
from collections.abc import Iterator

from .entity import Entity
from .component import Component


class EntityManager:
    """
    Manages entities and their components in the ECS architecture.

    The EntityManager handles entity lifecycle, component assignment,
    and provides efficient querying capabilities for systems.
    """

    def __init__(self) -> None:
        """Initialize the EntityManager."""
        # Use weak references to prevent memory leaks
        self._entities: weakref.WeakValueDictionary[str, Entity] = (
            weakref.WeakValueDictionary()
        )
        # Component storage: component_type -> entity_id -> component_instance
        self._components: dict[type[Component], dict[str, Component]] = (
            defaultdict(dict)
        )
        # Entity component mapping: entity_id -> set of component types
        self._entity_components: dict[str, set[type[Component]]] = defaultdict(
            set
        )
        # Active entities set for efficient filtering
        self._active_entities: set[str] = set()

    def create_entity(self) -> Entity:
        """
        Create a new entity.

        Returns:
            The newly created entity with a unique ID.
        """
        entity = Entity.create()
        self._entities[entity.entity_id] = entity
        self._active_entities.add(entity.entity_id)
        return entity

    def destroy_entity(self, entity: Entity) -> None:
        """
        Destroy an entity and remove all its components.

        Args:
            entity: The entity to destroy.
        """
        if entity.entity_id not in self._entities:
            return

        # Remove all components associated with this entity
        component_types = self._entity_components[entity.entity_id].copy()
        for component_type in component_types:
            self.remove_component(entity, component_type)

        # Clean up entity references
        self._entity_components.pop(entity.entity_id, None)
        self._active_entities.discard(entity.entity_id)

        # Mark entity as destroyed
        entity.destroy()

        # Remove from entities dict (weak reference will be cleaned automatically)
        if entity.entity_id in self._entities:
            del self._entities[entity.entity_id]

    def get_entity(self, entity_id: str) -> Entity | None:
        """
        Get an entity by its ID.

        Args:
            entity_id: The unique identifier of the entity.

        Returns:
            The entity if found, None otherwise.
        """
        return self._entities.get(entity_id)

    def get_all_entities(self) -> list[Entity]:
        """
        Get all entities.

        Returns:
            List of all entities (including inactive ones).
        """
        return list(self._entities.values())

    def get_active_entities(self) -> list[Entity]:
        """
        Get all active entities.

        Returns:
            List of active entities only.
        """
        return [
            entity
            for entity in self._entities.values()
            if entity.entity_id in self._active_entities and entity.active
        ]

    def add_component(self, entity: Entity, component: Component) -> None:
        """
        Add a component to an entity.

        Args:
            entity: The entity to add the component to.
            component: The component to add.

        Raises:
            ValueError: If the entity doesn't exist.
        """
        if entity.entity_id not in self._entities:
            raise ValueError(f'Entity {entity.entity_id} does not exist')

        component_type = type(component)
        self._components[component_type][entity.entity_id] = component
        self._entity_components[entity.entity_id].add(component_type)

    def remove_component(
        self, entity: Entity, component_type: type[Component]
    ) -> None:
        """
        Remove a component from an entity.

        Args:
            entity: The entity to remove the component from.
            component_type: The type of component to remove.
        """
        if entity.entity_id not in self._entities:
            return

        # Remove component from storage
        if component_type in self._components:
            self._components[component_type].pop(entity.entity_id, None)

        # Update entity component mapping
        self._entity_components[entity.entity_id].discard(component_type)

    def get_component(
        self, entity: Entity, component_type: type[Component]
    ) -> Component | None:
        """
        Get a specific component from an entity.

        Args:
            entity: The entity to get the component from.
            component_type: The type of component to retrieve.

        Returns:
            The component if found, None otherwise.
        """
        if component_type not in self._components:
            return None
        return self._components[component_type].get(entity.entity_id)

    def has_component(
        self, entity: Entity, component_type: type[Component]
    ) -> bool:
        """
        Check if an entity has a specific component.

        Args:
            entity: The entity to check.
            component_type: The type of component to check for.

        Returns:
            True if the entity has the component, False otherwise.
        """
        return component_type in self._entity_components[entity.entity_id]

    def get_entities_with_component(
        self, component_type: type[Component]
    ) -> list[Entity]:
        """
        Get all entities that have a specific component.

        Args:
            component_type: The type of component to search for.

        Returns:
            List of entities that have the specified component.
        """
        if component_type not in self._components:
            return []

        entities = []
        for entity_id in self._components[component_type]:
            entity = self._entities.get(entity_id)
            if entity is not None:
                entities.append(entity)

        return entities

    def get_entities_with_components(
        self, *component_types: type[Component]
    ) -> list[Entity]:
        """
        Get all entities that have all specified components.

        Args:
            *component_types: Variable number of component types to match.

        Returns:
            List of entities that have all specified components.
        """
        if not component_types:
            return self.get_all_entities()

        # Start with entities that have the first component type
        entity_ids = set(self._components.get(component_types[0], {}).keys())

        # Intersect with entities that have each additional component type
        for component_type in component_types[1:]:
            if component_type not in self._components:
                return []
            entity_ids &= set(self._components[component_type].keys())

        # Convert entity IDs back to entities
        entities = []
        for entity_id in entity_ids:
            entity = self._entities.get(entity_id)
            if entity is not None:
                entities.append(entity)

        return entities

    def get_components_for_entity(
        self, entity: Entity
    ) -> dict[type[Component], Component]:
        """
        Get all components for a specific entity.

        Args:
            entity: The entity to get components for.

        Returns:
            Dictionary mapping component types to component instances.
        """
        components = {}
        component_types = self._entity_components.get(entity.entity_id, set())

        for component_type in component_types:
            component = self._components[component_type].get(entity.entity_id)
            if component is not None:
                components[component_type] = component

        return components

    def clear_all(self) -> None:
        """Clear all entities and components."""
        # Destroy all entities
        entities_to_destroy = list(self._entities.values())
        for entity in entities_to_destroy:
            self.destroy_entity(entity)

        # Clear all storage
        self._entities.clear()
        self._components.clear()
        self._entity_components.clear()
        self._active_entities.clear()

    def get_entity_count(self) -> int:
        """
        Get the total number of entities.

        Returns:
            Total number of entities (including inactive ones).
        """
        return len(self._entities)

    def get_active_entity_count(self) -> int:
        """
        Get the number of active entities.

        Returns:
            Number of active entities only.
        """
        return len([e for e in self._entities.values() if e.active])

    def get_component_count(self, component_type: type[Component]) -> int:
        """
        Get the number of entities with a specific component type.

        Args:
            component_type: The component type to count.

        Returns:
            Number of entities with the specified component.
        """
        return len(self._components.get(component_type, {}))

    def __len__(self) -> int:
        """Return the total number of entities."""
        return len(self._entities)

    def __iter__(self) -> Iterator[Entity]:
        """Iterate over all entities."""
        return iter(self._entities.values())

    def __contains__(self, entity: Entity) -> bool:
        """Check if an entity exists in the manager."""
        return entity.entity_id in self._entities

    def __str__(self) -> str:
        """String representation of the EntityManager."""
        active_count = self.get_active_entity_count()
        total_count = self.get_entity_count()
        return f'EntityManager({active_count}/{total_count} active entities)'

    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (
            f'EntityManager(entities={len(self._entities)}, '
            f'active={self.get_active_entity_count()}, '
            f'component_types={len(self._components)})'
        )


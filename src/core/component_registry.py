"""
ComponentRegistry for ECS (Entity-Component-System) architecture.

The ComponentRegistry manages components by type, providing efficient storage,
retrieval, and management of components across all entities.

Supports multiple components of the same type per entity and provides
immutable collections to prevent side effects.
"""

from collections import defaultdict
from collections.abc import Iterator, Sequence
from typing import TypeVar, cast
from weakref import WeakSet

from .component import Component
from .entity import Entity
from .interfaces.i_component_registry import IComponentRegistry

T = TypeVar('T', bound=Component)


class ComponentRegistry(IComponentRegistry):
    """
    Registry that manages components by type for efficient storage/retrieval.

    The registry uses a type-based storage system where components are
    organized by their class type, allowing for fast queries and operations
    on specific component types.

    Supports multiple components of the same type per entity and provides
    immutable collections to prevent side effects.
    """

    def __init__(self) -> None:
        """Initialize the component registry."""
        # Maps component type to dict of entity_id -> list of components
        self._components: dict[type[Component], dict[str, list[Component]]] = (
            defaultdict(lambda: defaultdict(list))
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

        Supports multiple components of the same type per entity.
        Each component instance is stored separately.

        Args:
            entity: The entity to add the component to
            component: The component instance to add

        Raises:
            ValueError: If entity is inactive
        """
        if not entity.active:
            raise ValueError(
                f'Cannot add component to inactive entity {entity}'
            )

        component_type = type(component)

        # Validate component data before adding
        if not component.validate():
            raise ValueError(f'Component {component} failed validation')

        # Store the component (multiple components of same type allowed)
        self._components[component_type][entity.entity_id].append(component)
        self._entity_components[entity.entity_id].add(component_type)
        self._entities.add(entity)

    def remove_component(self, entity: Entity, component: Component) -> bool:
        """
        Remove a specific component instance from an entity.

        Args:
            entity: The entity to remove the component from
            component: The specific component instance to remove

        Returns:
            True if component was removed, False if not found
        """
        component_type = type(component)
        entity_id = entity.entity_id

        if (
            component_type not in self._components
            or entity_id not in self._components[component_type]
        ):
            return False

        component_list = self._components[component_type][entity_id]

        try:
            component_list.remove(component)

            # Clean up empty lists and mappings
            if not component_list:
                del self._components[component_type][entity_id]
                self._entity_components[entity_id].discard(component_type)

                # Clean up empty component type storage
                if not self._components[component_type]:
                    del self._components[component_type]

                # Clean up empty entity storage
                if not self._entity_components[entity_id]:
                    del self._entity_components[entity_id]

            return True
        except ValueError:
            return False

    def remove_component_by_type(
        self, entity: Entity, component_type: type[T], index: int = 0
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
        entity_id = entity.entity_id

        if (
            component_type not in self._components
            or entity_id not in self._components[component_type]
        ):
            return None

        component_list = self._components[component_type][entity_id]

        if index < 0 or index >= len(component_list):
            return None

        removed_component = component_list.pop(index)

        # Clean up empty lists and mappings
        if not component_list:
            del self._components[component_type][entity_id]
            self._entity_components[entity_id].discard(component_type)

            # Clean up empty component type storage
            if not self._components[component_type]:
                del self._components[component_type]

            # Clean up empty entity storage
            if not self._entity_components[entity_id]:
                del self._entity_components[entity_id]

        return cast(T, removed_component)

    def remove_all_components_by_type(
        self, entity: Entity, component_type: type[T]
    ) -> Sequence[T]:
        """
        Remove all components of a specific type from an entity.

        Args:
            entity: The entity to remove components from
            component_type: The type of components to remove

        Returns:
            Immutable sequence of removed component instances
        """
        entity_id = entity.entity_id

        if (
            component_type not in self._components
            or entity_id not in self._components[component_type]
        ):
            return ()

        component_list = self._components[component_type][entity_id].copy()

        # Remove all components
        del self._components[component_type][entity_id]
        self._entity_components[entity_id].discard(component_type)

        # Clean up empty component type storage
        if not self._components[component_type]:
            del self._components[component_type]

        # Clean up empty entity storage
        if not self._entity_components[entity_id]:
            del self._entity_components[entity_id]

        return tuple(cast(T, comp) for comp in component_list)

    def get_component(
        self, entity: Entity, component_type: type[T], index: int = 0
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
        entity_id = entity.entity_id

        if (
            component_type not in self._components
            or entity_id not in self._components[component_type]
        ):
            return None

        component_list = self._components[component_type][entity_id]

        if index < 0 or index >= len(component_list):
            return None

        return cast(T, component_list[index])

    def get_components(
        self, entity: Entity, component_type: type[T]
    ) -> Sequence[T]:
        """
        Get all components of a specific type from an entity.

        Args:
            entity: The entity to get components from
            component_type: The type of components to get

        Returns:
            Immutable sequence of component instances (empty if none found)
        """
        entity_id = entity.entity_id

        if (
            component_type not in self._components
            or entity_id not in self._components[component_type]
        ):
            return ()

        component_list = self._components[component_type][entity_id]
        return tuple(cast(T, comp) for comp in component_list)

    def has_component(
        self, entity: Entity, component_type: type[Component]
    ) -> bool:
        """
        Check if an entity has any components of a specific type.

        Args:
            entity: The entity to check
            component_type: The type of component to check for

        Returns:
            True if the entity has at least one component of this type
        """
        entity_id = entity.entity_id
        return (
            component_type in self._components
            and entity_id in self._components[component_type]
            and len(self._components[component_type][entity_id]) > 0
        )

    def get_component_count_by_type(
        self, entity: Entity, component_type: type[Component]
    ) -> int:
        """
        Get the number of components of a specific type on an entity.

        Args:
            entity: The entity to count components for
            component_type: The type of component to count

        Returns:
            Number of components of the specified type
        """
        entity_id = entity.entity_id

        if (
            component_type not in self._components
            or entity_id not in self._components[component_type]
        ):
            return 0

        return len(self._components[component_type][entity_id])

    def get_components_for_entity(
        self, entity: Entity
    ) -> dict[type[Component], Sequence[Component]]:
        """
        Get all components for a specific entity.

        Args:
            entity: The entity to get components for

        Returns:
            Immutable dictionary mapping types to component sequences
        """
        result = {}
        entity_id = entity.entity_id
        component_types = self._entity_components.get(entity_id, set())

        for component_type in component_types:
            if entity_id in self._components[component_type]:
                component_list = self._components[component_type][entity_id]
                result[component_type] = tuple(component_list)

        return result

    def get_entities_with_component(
        self, component_type: type[T]
    ) -> Iterator[tuple[Entity, Sequence[T]]]:
        """
        Get all entities that have a specific component type.

        Args:
            component_type: The type of component to filter by

        Yields:
            Tuples of (entity, immutable_sequence_of_components)
        """
        if component_type not in self._components:
            return

        for entity in self._entities:
            if (
                entity.active
                and entity.entity_id in self._components[component_type]
            ):
                component_list = self._components[component_type][
                    entity.entity_id
                ]
                if component_list:  # Only yield if there are components
                    yield (
                        entity,
                        tuple(cast(T, comp) for comp in component_list),
                    )

    def get_entities_with_components(
        self, *component_types: type[Component]
    ) -> Iterator[tuple[Entity, dict[type[Component], Sequence[Component]]]]:
        """
        Get entities that have ALL of the specified component types.

        Args:
            *component_types: Component types that entities must have

        Yields:
            Tuples of (entity, dict_mapping_types_to_component_sequences)
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
                component_dict = {}
                for comp_type in component_types:
                    if entity.entity_id in self._components[comp_type]:
                        component_list = self._components[comp_type][
                            entity.entity_id
                        ]
                        component_dict[comp_type] = tuple(component_list)

                if len(component_dict) == len(component_types):
                    yield entity, component_dict

    def get_entities_with_single_components(
        self, *component_types: type[Component]
    ) -> Iterator[tuple[Entity, tuple[Component, ...]]]:
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
        if not component_types:
            return

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
                    if entity.entity_id in self._components[comp_type]:
                        component_list = self._components[comp_type][
                            entity.entity_id
                        ]
                        if component_list:  # Take first component
                            components.append(component_list[0])
                        else:
                            break  # Skip if any component list is empty
                else:
                    if len(components) == len(component_types):
                        yield entity, tuple(components)

    def remove_entity_components(
        self, entity: Entity
    ) -> dict[type[Component], Sequence[Component]]:
        """
        Remove all components from an entity.

        Args:
            entity: The entity to remove components from

        Returns:
            Immutable dictionary of removed components by type to sequences
        """
        removed_components = {}
        entity_id = entity.entity_id
        component_types = self._entity_components.get(entity_id, set()).copy()

        for component_type in component_types:
            removed_sequence = self.remove_all_components_by_type(
                entity, component_type
            )
            if removed_sequence:
                removed_components[component_type] = removed_sequence

        return removed_components

    def get_component_count(self, component_type: type[Component]) -> int:
        """
        Get the number of components of a specific type.

        Args:
            component_type: The component type to count

        Returns:
            Number of components of the specified type
        """
        if component_type not in self._components:
            return 0

        total_count = 0
        for component_list in self._components[component_type].values():
            total_count += len(component_list)
        return total_count

    def get_entity_component_count(self, entity: Entity) -> int:
        """
        Get the number of components on a specific entity.

        Args:
            entity: The entity to count components for

        Returns:
            Number of components on the entity
        """
        entity_id = entity.entity_id
        total_count = 0

        for component_type in self._entity_components.get(entity_id, set()):
            if entity_id in self._components[component_type]:
                total_count += len(self._components[component_type][entity_id])

        return total_count

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
                if (
                    component_type not in self._components
                    or entity_id not in self._components[component_type]
                    or not self._components[component_type][entity_id]
                ):
                    return False

        # Check that all components in _components
        # are referenced in _entity_components
        for component_type, entity_components in self._components.items():
            for entity_id, component_list in entity_components.items():
                if (
                    entity_id not in self._entity_components
                    or component_type not in self._entity_components[entity_id]
                    or not component_list
                ):
                    return False

        return True

    def __len__(self) -> int:
        """Return the total number of component instances in the registry."""
        total_count = 0
        for entity_components in self._components.values():
            for component_list in entity_components.values():
                total_count += len(component_list)
        return total_count

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

"""
EntityManager class for ECS (Entity-Component-System) architecture.

The EntityManager is responsible for creating, destroying, and managing entities
and their components throughout the game lifecycle.
"""

import weakref
from collections.abc import Iterator
from typing import TYPE_CHECKING, TypeVar

from .component import Component
from .component_registry import ComponentRegistry
from .entity import Entity
from .interfaces.i_component_registry import IComponentRegistry

if TYPE_CHECKING:
    from ..dto.spawn_result import SpawnResult
    from ..managers.enemy_manager import EnemyManager
    from .coordinate_manager import CoordinateManager
    from .difficulty_manager import DifficultyManager

T = TypeVar('T', bound=Component)


class EntityManager:
    """
    Manages entities and their components in the ECS architecture.

    The EntityManager handles entity lifecycle, component assignment,
    and provides efficient querying capabilities for systems.

    Uses dependency injection for component registry to support
    interface abstraction and testing.
    """

    def __init__(
        self,
        component_registry: IComponentRegistry | None = None,
        coordinate_manager: 'CoordinateManager | None' = None,
        difficulty_manager: 'DifficultyManager | None' = None,
    ) -> None:
        """Initialize the EntityManager with optional dependencies injection.

        Args:
            component_registry: Optional component registry implementation.
                               If None, uses default ComponentRegistry.
            coordinate_manager: Optional coordinate manager.
                               If None, uses singleton instance.
            difficulty_manager: Optional difficulty manager.
                               If None, uses singleton instance.
        """
        # Use weak references to prevent memory leaks
        self._entities: weakref.WeakValueDictionary[str, Entity] = (
            weakref.WeakValueDictionary()
        )
        # Active entities set for efficient filtering
        self._active_entities: set[str] = set()

        # Dependency injection for component registry
        self._component_registry: IComponentRegistry = (
            component_registry
            if component_registry is not None
            else ComponentRegistry()
        )

        # AI-NOTE : 2025-01-16 세부 매니저들에 대한 의존성 주입 지원
        # - 이유: EntityManager가 세부 매니저들을 관리하고 위임할 수 있도록 함
        # - 요구사항: 테스트 시 Mock 매니저 주입, 운영 시 실제 매니저 사용
        # - 비즈니스 가치: 시스템들이 EntityManager만 알면 되는 단순한 구조

        # Store injected dependencies
        self._coordinate_manager = coordinate_manager
        self._difficulty_manager = difficulty_manager

        # Specialized managers (lazy initialization)
        self._enemy_manager: EnemyManager | None = None

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

        # 투사체 엔티티 삭제 디버깅
        from ..components.projectile_component import ProjectileComponent

        if self.has_component(entity, ProjectileComponent):
            import logging
            import traceback

            logging.error(
                f'🚨 DESTROYING PROJECTILE ENTITY: {entity.entity_id}'
            )
            logging.error('   Stack trace:')
            for line in traceback.format_stack():
                logging.error(f'     {line.strip()}')

        # Remove all components through the registry
        self._component_registry.remove_entity_components(entity)

        # Clean up entity references
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

        self._component_registry.add_component(entity, component)

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

        # Remove first component of the specified type
        self._component_registry.remove_component_by_type(
            entity, component_type
        )

    def get_component(
        self, entity: Entity, component_type: type[T]
    ) -> T | None:
        """
        Get a specific component from an entity.

        Args:
            entity: The entity to get the component from.
            component_type: The type of component to retrieve.

        Returns:
            The component if found, None otherwise.
        """
        return self._component_registry.get_component(entity, component_type)

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
        return self._component_registry.has_component(entity, component_type)

    def get_entities_with_component(
        self, component_type: type[T]
    ) -> list[tuple[Entity, T]]:
        """
        Get all active entities that have a specific component.

        Args:
            component_type: The type of component to search for.

        Returns:
            List of (Entity, Component) tuples for active entities that have the component.
        """
        entities_with_component = []
        for (
            entity,
            components,
        ) in self._component_registry.get_entities_with_component(
            component_type
        ):
            # Take first component for backward compatibility
            if components and entity.active:
                entities_with_component.append((entity, components[0]))

        return entities_with_component

    def get_entities_with_components(
        self, *component_types: type[Component]
    ) -> list[Entity]:
        """
        Get all active entities that have all specified components.

        Args:
            *component_types: Variable number of component types to match.

        Returns:
            List of active entities that have all specified components.
        """
        if not component_types:
            return self.get_active_entities()

        active_entities = []
        for entity, _ in self._component_registry.get_entities_with_components(
            *component_types
        ):
            if entity.active:
                active_entities.append(entity)

        return active_entities

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
        multi_components = self._component_registry.get_components_for_entity(
            entity
        )

        # Convert to single component format for backward compatibility
        single_components = {}
        for component_type, component_sequence in multi_components.items():
            if component_sequence:
                single_components[component_type] = component_sequence[0]

        return single_components

    def clear_all(self) -> None:
        """Clear all entities and components."""
        # Destroy all entities
        entities_to_destroy = list(self._entities.values())
        for entity in entities_to_destroy:
            self.destroy_entity(entity)

        # Clear all storage
        self._entities.clear()
        self._component_registry.clear()
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
        return self._component_registry.get_component_count(component_type)

    def _ensure_managers_initialized(self) -> None:
        """Ensure all specialized managers are initialized (lazy initialization)."""
        # AI-DEV : 지연 초기화를 통한 순환 의존성 방지
        # - 문제: 매니저 간 순환 참조로 인한 초기화 순서 이슈
        # - 해결책: 실제 사용 시점에 매니저 초기화
        # - 주의사항: 싱글톤 매니저들의 초기화 시점 관리

        if self._coordinate_manager is None:
            from .coordinate_manager import CoordinateManager

            self._coordinate_manager = CoordinateManager.get_instance()

        if self._difficulty_manager is None:
            from .difficulty_manager import DifficultyManager

            self._difficulty_manager = DifficultyManager.get_instance()

        if self._enemy_manager is None:
            from ..managers.enemy_manager import EnemyManager

            self._enemy_manager = EnemyManager(
                component_registry=self._component_registry,
                coordinate_manager=self._coordinate_manager,
                difficulty_manager=self._difficulty_manager,
            )

    def create_enemy_entity(self, spawn_result: 'SpawnResult') -> Entity:
        """
        Create an enemy entity with components based on spawn result.

        Delegates enemy-specific component assembly to EnemyManager
        while handling basic entity creation.

        Args:
            spawn_result: Spawn configuration data

        Returns:
            Created enemy entity with all components
        """
        self._ensure_managers_initialized()

        # 1. Create basic entity
        entity = self.create_entity()

        # 2. Delegate enemy component assembly to EnemyManager
        if self._enemy_manager:
            self._enemy_manager.create_enemy_from_spawn_result(
                entity, spawn_result
            )

        return entity

    def get_enemy_count(self) -> int:
        """
        Get current number of enemy entities.

        Delegates to EnemyManager for specialized enemy counting.

        Returns:
            Number of active enemy entities
        """
        self._ensure_managers_initialized()
        return (
            self._enemy_manager.get_enemy_count() if self._enemy_manager else 0
        )

    @property
    def component_registry(self) -> IComponentRegistry:
        """Get the component registry instance for advanced operations."""
        return self._component_registry

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
        """Return string representation of the EntityManager."""
        active_count = self.get_active_entity_count()
        total_count = self.get_entity_count()
        return f'EntityManager({active_count}/{total_count} active entities)'

    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (
            f'EntityManager(entities={len(self._entities)}, '
            f'active={self.get_active_entity_count()}, '
            f'component_types={len(self._component_registry.get_all_component_types())})'
        )

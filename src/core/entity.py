"""
Entity class for ECS (Entity-Component-System) architecture.

The Entity class represents a unique game object that can have components
attached to it.
"""

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class Entity:
    """
    Entity represents a unique game object in the ECS architecture.

    Entities are lightweight containers that provide a unique identifier
    for game objects. Components are managed through EntityManager, not
    directly on the Entity instance.

    Attributes:
        entity_id: Unique identifier for this entity
        _active: Whether this entity is currently active in the game
    """

    entity_id: str
    _active: bool = True

    def __post_init__(self) -> None:
        """Initialize entity after creation."""
        if not self.entity_id:
            self.entity_id = str(uuid.uuid4())

    @classmethod
    def create(cls) -> "Entity":
        """
        Create a new entity with a unique ID.

        Returns:
            A new Entity instance with a generated UUID
        """
        return cls(entity_id=str(uuid.uuid4()))

    @property
    def id(self) -> str:
        """
        Get entity ID (alias for entity_id for backward compatibility).

        Returns:
            The entity's unique identifier string
        """
        return self.entity_id

    @property
    def active(self) -> bool:
        """
        Check if the entity is active.

        Returns:
            True if entity is active, False otherwise
        """
        return self._active

    def activate(self) -> None:
        """
        Activate the entity.

        Sets the entity's active state to True, making it available
        for processing by systems.
        """
        self._active = True

    def deactivate(self) -> None:
        """
        Deactivate the entity.

        Sets the entity's active state to False, excluding it from
        system processing without destroying it.
        """
        self._active = False

    def destroy(self) -> None:
        """
        Mark entity for destruction.

        Deactivates the entity, making it eligible for cleanup.
        The actual removal is handled by EntityManager.
        """
        self._active = False

    def __hash__(self) -> int:
        """
        Make entity hashable for use in sets and as dict keys.

        Returns:
            Hash value based on entity_id
        """
        return hash(self.entity_id)

    def __eq__(self, other: object) -> bool:
        """
        Compare entities by their ID.

        Args:
            other: Object to compare against

        Returns:
            True if both are Entity instances with same entity_id
        """
        if not isinstance(other, Entity):
            return False
        return self.entity_id == other.entity_id

    def __str__(self) -> str:
        """
        Return string representation of entity.

        Returns:
            Human-readable string showing truncated ID and status
        """
        status = "active" if self._active else "inactive"
        return f"Entity({self.entity_id[:8]}...)[{status}]"

    def __repr__(self) -> str:
        """
        Detailed string representation for debugging.

        Returns:
            Complete entity information for debugging
        """
        return f"Entity(entity_id='{self.entity_id}', active={self._active})"

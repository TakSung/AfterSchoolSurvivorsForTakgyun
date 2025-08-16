"""
Entity class for ECS (Entity-Component-System) architecture.

The Entity class represents a unique game object that can have components attached to it.
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

    Entities are lightweight containers that hold components and provide
    a unique identifier for game objects.
    """

    entity_id: str
    _active: bool = True

    def __post_init__(self) -> None:
        """Initialize entity after creation."""
        if not self.entity_id:
            self.entity_id = str(uuid.uuid4())

    @classmethod
    def create(cls) -> 'Entity':
        """Create a new entity with a unique ID."""
        return cls(entity_id=str(uuid.uuid4()))

    @property
    def id(self) -> str:
        """Get entity ID (alias for entity_id for backward compatibility)."""
        return self.entity_id

    @property
    def active(self) -> bool:
        """Check if the entity is active."""
        return self._active

    def activate(self) -> None:
        """Activate the entity."""
        self._active = True

    def deactivate(self) -> None:
        """Deactivate the entity."""
        self._active = False

    def destroy(self) -> None:
        """Mark entity for destruction."""
        self._active = False

    def __hash__(self) -> int:
        """Make entity hashable for use in sets and as dict keys."""
        return hash(self.entity_id)

    def __eq__(self, other: object) -> bool:
        """Compare entities by their ID."""
        if not isinstance(other, Entity):
            return False
        return self.entity_id == other.entity_id

    def __str__(self) -> str:
        """String representation of entity."""
        status = 'active' if self._active else 'inactive'
        return f'Entity({self.entity_id[:8]}...)[{status}]'

    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return f"Entity(entity_id='{self.entity_id}', active={self._active})"

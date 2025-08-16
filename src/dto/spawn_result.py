"""
SpawnResult DTO for spawner system communication.

This module contains the SpawnResult data transfer object used
to communicate spawn information between spawners and entity managers.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SpawnResult:
    """
    Data transfer object for spawn operation results.

    Contains all necessary information for entity creation,
    separated from the actual entity creation logic.
    """

    spawn_position: tuple[float, float]
    """World coordinates where the entity should be spawned (x, y)"""

    entity_type: str
    """Type of entity to spawn (e.g., 'enemy', 'item', 'boss')"""

    difficulty_scale: float
    """Difficulty scaling factor for entity attributes"""

    additional_data: dict[str, Any] = field(default_factory=dict)
    """Extended data for entity customization"""

    def __post_init__(self) -> None:
        """Validate spawn result data after initialization."""
        if (
            not isinstance(self.spawn_position, tuple)
            or len(self.spawn_position) != 2
        ):
            raise ValueError(
                'spawn_position must be a tuple of (x, y) coordinates'
            )

        if (
            not isinstance(self.entity_type, str)
            or not self.entity_type.strip()
        ):
            raise ValueError('entity_type must be a non-empty string')

        if (
            not isinstance(self.difficulty_scale, (int, float))
            or self.difficulty_scale <= 0
        ):
            raise ValueError('difficulty_scale must be a positive number')

    @property
    def x(self) -> float:
        """Get x coordinate of spawn position."""
        return self.spawn_position[0]

    @property
    def y(self) -> float:
        """Get y coordinate of spawn position."""
        return self.spawn_position[1]

    def get_additional_data(self, key: str, default: Any = None) -> Any:
        """
        Get additional data value by key.

        Args:
            key: Data key to retrieve
            default: Default value if key not found

        Returns:
            Value for the key or default
        """
        return self.additional_data.get(key, default)

    def set_additional_data(self, key: str, value: Any) -> None:
        """
        Set additional data value.

        Args:
            key: Data key to set
            value: Value to set
        """
        self.additional_data[key] = value

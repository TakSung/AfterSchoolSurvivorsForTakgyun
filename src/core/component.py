"""
Component base class for ECS (Entity-Component-System) architecture.

Components are pure data containers that define the properties and attributes
of entities without any behavior or logic.
"""

from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


@dataclass
class Component(ABC):
    """
    Abstract base class for all components in the ECS architecture.

    Components are data containers that hold attributes for entities.
    They should not contain any game logic - that belongs in Systems.

    All component classes should inherit from this class and use the
    @dataclass decorator for automatic __init__ generation.
    """

    def __post_init__(self) -> None:
        """
        Called after component initialization.

        Override this method in subclasses to perform custom initialization
        logic after the dataclass __init__ is called.
        """
        pass

    def copy(self) -> 'Component':
        """
        Create a shallow copy of this component.

        Returns:
            A new instance of the same component type with copied values.
        """
        return type(self)(
            **{
                field.name: getattr(self, field.name)
                for field in self.__dataclass_fields__.values()
            }
        )

    def validate(self) -> bool:
        """
        Validate component data integrity.

        Override this method in subclasses to implement custom validation logic.

        Returns:
            True if the component data is valid, False otherwise.
        """
        return True

    def serialize(self) -> dict[str, Any]:
        """
        Serialize component data to a dictionary.

        Returns:
            Dictionary representation of the component data.
        """
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> 'Component':
        """
        Create a component instance from serialized data.

        Args:
            data: Dictionary containing component data.

        Returns:
            New component instance with the provided data.
        """
        return cls(**data)

    def __str__(self) -> str:
        """String representation of the component."""
        class_name = self.__class__.__name__
        field_strs = []
        for field in self.__dataclass_fields__.values():
            value = getattr(self, field.name)
            field_strs.append(f'{field.name}={value}')
        return f'{class_name}({", ".join(field_strs)})'

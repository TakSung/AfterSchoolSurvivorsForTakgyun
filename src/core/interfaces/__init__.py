"""
Core interfaces for the ECS architecture.

This module contains abstract interfaces that define contracts
for core ECS components, enabling dependency inversion and
better testability.
"""

from .i_component_registry import IComponentRegistry
from .i_spawner import ISpawner
from .entity_manager_interface import IEntityManagerForSystems
from .coordinate_manager_interface import ICoordinateManagerForSystems

__all__ = [
    'IComponentRegistry', 
    'ISpawner',
    'IEntityManagerForSystems',
    'ICoordinateManagerForSystems'
]

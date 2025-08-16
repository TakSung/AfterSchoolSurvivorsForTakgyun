"""
CoordinateManager interface for System dependency injection.

Defines the contract for coordinate transformation access that Systems will use
through dependency injection, promoting architectural decoupling.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..coordinate_transformer import ICoordinateTransformer
    from ...utils.vector2 import Vector2


class ICoordinateManagerForSystems(ABC):
    """
    Interface for CoordinateManager access by Systems.
    
    This interface defines the minimum contract that Systems need
    from CoordinateManager, enabling dependency injection and loose coupling.
    """

    @abstractmethod
    def world_to_screen(self, world_pos: 'Vector2') -> 'Vector2':
        """
        Transform world coordinates to screen coordinates.
        
        Args:
            world_pos: Position in world coordinates
            
        Returns:
            Position in screen coordinates
        """
        pass

    @abstractmethod
    def screen_to_world(self, screen_pos: 'Vector2') -> 'Vector2':
        """
        Transform screen coordinates to world coordinates.
        
        Args:
            screen_pos: Position in screen coordinates
            
        Returns:
            Position in world coordinates
        """
        pass

    @abstractmethod
    def set_world_offset(self, offset: 'Vector2') -> None:
        """
        Set the world offset for coordinate transformation.
        
        Args:
            offset: New world offset
        """
        pass

    @abstractmethod
    def get_world_offset(self) -> 'Vector2':
        """
        Get the current world offset.
        
        Returns:
            Current world offset
        """
        pass

    @abstractmethod
    def set_transformer(self, transformer: 'ICoordinateTransformer') -> None:
        """
        Set the coordinate transformer.
        
        Args:
            transformer: New coordinate transformer
        """
        pass

    @abstractmethod
    def get_transformer(self) -> 'ICoordinateTransformer':
        """
        Get the current coordinate transformer.
        
        Returns:
            Current coordinate transformer
        """
        pass

    @abstractmethod
    def invalidate_cache(self) -> None:
        """
        Invalidate the coordinate transformation cache.
        
        Forces recalculation of cached transformations.
        """
        pass
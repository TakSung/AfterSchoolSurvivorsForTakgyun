from abc import ABC, abstractmethod
from enum import IntEnum

from ..utils.vector2 import Vector2


class CoordinateSpace(IntEnum):
    WORLD = 0
    SCREEN = 1

    @property
    def display_name(self) -> str:
        display_names = {
            CoordinateSpace.WORLD: '월드 좌표',
            CoordinateSpace.SCREEN: '스크린 좌표',
        }
        return display_names[self]


class ICoordinateTransformer(ABC):
    @abstractmethod
    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        pass

    @abstractmethod
    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        pass

    @abstractmethod
    def get_camera_offset(self) -> Vector2:
        pass

    @abstractmethod
    def set_camera_offset(self, offset: Vector2) -> None:
        pass

    @abstractmethod
    def invalidate_cache(self) -> None:
        pass

    @property
    @abstractmethod
    def zoom_level(self) -> float:
        pass

    @zoom_level.setter
    @abstractmethod
    def zoom_level(self, value: float) -> None:
        pass

    @property
    @abstractmethod
    def screen_size(self) -> Vector2:
        pass

    @screen_size.setter
    @abstractmethod
    def screen_size(self, size: Vector2) -> None:
        pass

    def transform(
        self,
        position: Vector2,
        from_space: CoordinateSpace,
        to_space: CoordinateSpace,
    ) -> Vector2:
        if from_space == to_space:
            return position.copy()

        if (
            from_space == CoordinateSpace.WORLD
            and to_space == CoordinateSpace.SCREEN
        ):
            return self.world_to_screen(position)
        elif (
            from_space == CoordinateSpace.SCREEN
            and to_space == CoordinateSpace.WORLD
        ):
            return self.screen_to_world(position)
        else:
            raise ValueError(
                f'Unsupported transformation: {from_space.display_name} to {to_space.display_name}'
            )

    def is_point_visible(
        self, world_pos: Vector2, margin: float = 0.0
    ) -> bool:
        screen_pos = self.world_to_screen(world_pos)
        screen_size = self.screen_size

        return (
            -margin <= screen_pos.x <= screen_size.x + margin
            and -margin <= screen_pos.y <= screen_size.y + margin
        )

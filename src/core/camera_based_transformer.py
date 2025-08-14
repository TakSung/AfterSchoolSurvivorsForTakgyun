from typing import Any

from ..utils.vector2 import Vector2
from .coordinate_transformer import ICoordinateTransformer


class CameraBasedTransformer(ICoordinateTransformer):
    __slots__ = (
        '_cache_dirty',
        '_camera_offset',
        '_inverse_matrix_cache',
        '_screen_size',
        '_transformation_matrix_cache',
        '_zoom_level',
    )

    def __init__(
        self,
        screen_size: Vector2,
        camera_offset: Vector2 | None = None,
        zoom_level: float = 1.0,
    ) -> None:
        self._screen_size = screen_size.copy()
        self._camera_offset = (
            camera_offset.copy() if camera_offset else Vector2.zero()
        )
        self._zoom_level = max(0.1, zoom_level)
        self._cache_dirty = True
        self._transformation_matrix_cache: (
            tuple[float, float, float, float, float, float] | None
        ) = None
        self._inverse_matrix_cache: (
            tuple[float, float, float, float, float, float] | None
        ) = None

    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        relative_pos = world_pos + self._camera_offset  # 오프셋 부호 수정
        scaled_pos = relative_pos * self._zoom_level
        screen_center = self._screen_size / 2
        return scaled_pos + screen_center

    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        screen_center = self._screen_size / 2
        relative_pos = screen_pos - screen_center
        scaled_pos = relative_pos / self._zoom_level
        return scaled_pos - self._camera_offset  # 오프셋 부호 수정

    def get_camera_offset(self) -> Vector2:
        return self._camera_offset.copy()

    def set_camera_offset(self, offset: Vector2) -> None:
        if self._camera_offset != offset:
            self._camera_offset = offset.copy()
            self.invalidate_cache()

    def invalidate_cache(self) -> None:
        self._cache_dirty = True
        self._transformation_matrix_cache = None
        self._inverse_matrix_cache = None

    @property
    def zoom_level(self) -> float:
        return self._zoom_level

    @zoom_level.setter
    def zoom_level(self, value: float) -> None:
        new_zoom = max(0.1, min(10.0, value))
        if self._zoom_level != new_zoom:
            self._zoom_level = new_zoom
            self.invalidate_cache()

    @property
    def screen_size(self) -> Vector2:
        return self._screen_size.copy()

    @screen_size.setter
    def screen_size(self, size: Vector2) -> None:
        if self._screen_size != size:
            self._screen_size = size.copy()
            self.invalidate_cache()

    def get_screen_center(self) -> Vector2:
        return self._screen_size / 2

    def get_visible_world_bounds(self) -> tuple[Vector2, Vector2]:
        top_left_screen = Vector2.zero()
        bottom_right_screen = self._screen_size.copy()

        top_left_world = self.screen_to_world(top_left_screen)
        bottom_right_world = self.screen_to_world(bottom_right_screen)

        return top_left_world, bottom_right_world

    def get_transformation_matrix(
        self,
    ) -> tuple[float, float, float, float, float, float]:
        if self._cache_dirty or self._transformation_matrix_cache is None:
            screen_center = self.get_screen_center()

            # 2D 변환 매트릭스 (아핀 변환): [sx, 0, tx, 0, sy, ty]
            # sx, sy: scale, tx, ty: translation
            sx = self._zoom_level
            sy = self._zoom_level
            tx = screen_center.x + self._camera_offset.x * self._zoom_level
            ty = screen_center.y + self._camera_offset.y * self._zoom_level

            self._transformation_matrix_cache = (sx, 0.0, tx, 0.0, sy, ty)

        return self._transformation_matrix_cache

    def get_inverse_transformation_matrix(
        self,
    ) -> tuple[float, float, float, float, float, float]:
        if self._cache_dirty or self._inverse_matrix_cache is None:
            screen_center = self.get_screen_center()

            # 역변환 매트릭스
            inv_scale = 1.0 / self._zoom_level
            inv_tx = (
                -self._camera_offset.x - screen_center.x / self._zoom_level
            )
            inv_ty = (
                -self._camera_offset.y - screen_center.y / self._zoom_level
            )

            self._inverse_matrix_cache = (
                inv_scale,
                0.0,
                inv_tx,
                0.0,
                inv_scale,
                inv_ty,
            )

        return self._inverse_matrix_cache

    def transform_multiple_points(
        self, world_positions: list[Vector2]
    ) -> list[Vector2]:
        if not world_positions:
            return []

        matrix = self.get_transformation_matrix()
        sx, _, tx, _, sy, ty = matrix

        screen_positions = []
        for world_pos in world_positions:
            screen_x = world_pos.x * sx + tx
            screen_y = world_pos.y * sy + ty
            screen_positions.append(Vector2(screen_x, screen_y))

        return screen_positions

    def is_world_rect_visible(
        self, world_center: Vector2, world_size: Vector2, margin: float = 0.0
    ) -> bool:
        half_size = world_size / 2
        rect_corners = [
            world_center + Vector2(-half_size.x, -half_size.y),  # top-left
            world_center + Vector2(half_size.x, -half_size.y),  # top-right
            world_center + Vector2(half_size.x, half_size.y),  # bottom-right
            world_center + Vector2(-half_size.x, half_size.y),  # bottom-left
        ]

        # 최소한 한 모서리가 화면에 보이거나, 사각형이 화면을 완전히 덮는 경우
        screen_corners = self.transform_multiple_points(rect_corners)
        screen_bounds = self._screen_size

        for screen_pos in screen_corners:
            if (
                -margin <= screen_pos.x <= screen_bounds.x + margin
                and -margin <= screen_pos.y <= screen_bounds.y + margin
            ):
                return True

        # 사각형이 화면을 완전히 덮는 경우 체크
        min_x = min(pos.x for pos in screen_corners)
        max_x = max(pos.x for pos in screen_corners)
        min_y = min(pos.y for pos in screen_corners)
        max_y = max(pos.y for pos in screen_corners)

        return (
            min_x <= -margin
            and max_x >= screen_bounds.x + margin
            and min_y <= -margin
            and max_y >= screen_bounds.y + margin
        )

    def get_cache_stats(self) -> dict[str, Any]:
        return {
            'cache_dirty': self._cache_dirty,
            'has_transform_matrix': self._transformation_matrix_cache
            is not None,
            'has_inverse_matrix': self._inverse_matrix_cache is not None,
            'zoom_level': self._zoom_level,
            'camera_offset': self._camera_offset.to_tuple(),
            'screen_size': self._screen_size.to_tuple(),
        }

"""
MapComponent for managing map tile data and visual properties.

This component stores map-specific data including tile size, map boundaries,
and visual properties for rendering the background tile system.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..core.component import Component

if TYPE_CHECKING:
    pass


@dataclass
class MapComponent(Component):
    """
    Component that stores map configuration and tile system properties.

    The MapComponent manages the map's visual and logical properties including
    tile size, world boundaries, and rendering configuration.
    """

    # AI-NOTE : 2025-08-13 타일 기반 맵 시스템 설정
    # - 이유: 카메라 이동을 시각적으로 확인할 수 있는 격자 패턴 필요
    # - 요구사항: 64x64 픽셀 크기의 타일 기반 배경 시스템 (Task 17 요구사항)
    # - 히스토리: 50px에서 64px로 표준화, 무한 스크롤 최적화
    tile_size: int = 64  # 픽셀 단위 타일 크기

    # AI-DEV : 타일 계산 성능 최적화를 위한 월드 경계 설정
    # - 문제: 무한 타일 계산 시 성능 저하 발생 가능
    # - 해결책: 맵 경계를 설정하여 렌더링 범위 제한
    # - 주의사항: 카메라 이동 범위와 연동하여 설정 필요
    world_width: float = 2000.0  # 월드 전체 너비 (픽셀)
    world_height: float = 2000.0  # 월드 전체 높이 (픽셀)

    # AI-NOTE : 2025-08-13 맵 시각적 속성 설정 (Task 17 체스판 패턴)
    # - 이유: 타일 구분을 위한 시각적 피드백 제공
    # - 요구사항: 밝은 회색(240,240,240)과 어두운 회색(220,220,220) 체스판
    # - 히스토리: 단조로운 배경에서 체스판 패턴으로 시각적 개선
    light_tile_color: tuple[int, int, int] = (240, 240, 240)  # 밝은 타일
    dark_tile_color: tuple[int, int, int] = (220, 220, 220)  # 어두운 타일
    grid_color: tuple[int, int, int] = (0, 0, 0)  # 1픽셀 검은색 경계선

    # AI-DEV : 무한 스크롤링을 위한 타일 패턴 설정
    # - 문제: 맵 경계를 벗어날 때 빈 공간 표시 문제
    # - 해결책: 타일 패턴 반복을 통한 무한 스크롤링 구현
    # - 주의사항: 패턴 인덱스 계산 시 모듈로 연산 사용
    enable_infinite_scroll: bool = True
    tile_pattern_size: int = 4  # 반복 패턴 크기 (4x4 타일)

    def validate(self) -> bool:
        """
        Validate map component data integrity.

        Returns:
            True if all map data is valid, False otherwise.
        """
        # 타일 크기 유효성 검사
        if not isinstance(self.tile_size, int) or self.tile_size <= 0:
            return False

        # 월드 크기 유효성 검사
        if (
            not isinstance(self.world_width, int | float)
            or self.world_width <= 0
        ):
            return False

        if (
            not isinstance(self.world_height, int | float)
            or self.world_height <= 0
        ):
            return False

        # 색상 유효성 검사
        if not self._validate_color(self.light_tile_color):
            return False

        if not self._validate_color(self.dark_tile_color):
            return False

        if not self._validate_color(self.grid_color):
            return False

        # 무한 스크롤 설정 유효성 검사
        if not isinstance(self.enable_infinite_scroll, bool):
            return False

        if (
            not isinstance(self.tile_pattern_size, int)
            or self.tile_pattern_size <= 0
        ):
            return False

        return True

    def _validate_color(self, color: tuple[int, int, int]) -> bool:
        """
        Validate RGB color tuple.

        Args:
            color: RGB color tuple to validate

        Returns:
            True if valid RGB color, False otherwise
        """
        return (
            isinstance(color, tuple)
            and len(color) == 3
            and all(
                isinstance(component, int) and 0 <= component <= 255
                for component in color
            )
        )

    def get_tile_at_position(
        self, world_x: float, world_y: float
    ) -> tuple[int, int]:
        """
        Get the tile coordinates at a given world position.

        Args:
            world_x: World X coordinate
            world_y: World Y coordinate

        Returns:
            Tile coordinates as (tile_x, tile_y)
        """
        # AI-DEV : 타일 좌표 계산을 위한 간단한 나눗셈 연산
        # - 문제: 부동소수점 좌표를 정수 타일 인덱스로 변환 필요
        # - 해결책: 타일 크기로 나눈 후 정수 변환
        # - 주의사항: 음수 좌표에서도 올바른 타일 인덱스 계산
        tile_x = int(world_x // self.tile_size)
        tile_y = int(world_y // self.tile_size)

        return (tile_x, tile_y)

    def get_tile_world_position(
        self, tile_x: int, tile_y: int
    ) -> tuple[float, float]:
        """
        Get the world position of a tile's top-left corner.

        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate

        Returns:
            World position as (world_x, world_y)
        """
        world_x = float(tile_x * self.tile_size)
        world_y = float(tile_y * self.tile_size)

        return (world_x, world_y)

    def get_visible_tile_range(
        self,
        camera_offset: tuple[float, float],
        screen_width: int,
        screen_height: int,
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        """
        Calculate the range of tiles visible on screen.

        Args:
            camera_offset: Current camera offset (world coordinates)
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels

        Returns:
            ((min_tile_x, min_tile_y), (max_tile_x, max_tile_y))
        """
        # AI-NOTE : 2025-08-11 화면에 보이는 타일 범위 계산 최적화
        # - 이유: 모든 타일을 렌더링하지 않고 보이는 영역만 계산
        # - 요구사항: 카메라 오프셋과 화면 크기를 기반으로 한 컬링
        # - 히스토리: 전체 맵 렌더링에서 뷰포트 컬링으로 성능 개선

        # 카메라 오프셋을 고려한 월드 좌표 계산
        # 화면 좌상단의 월드 좌표
        top_left_world_x = -camera_offset[0]
        top_left_world_y = -camera_offset[1]

        # 화면 우하단의 월드 좌표
        bottom_right_world_x = top_left_world_x + screen_width
        bottom_right_world_y = top_left_world_y + screen_height

        # 타일 범위 계산 (여유분 1타일 추가)
        min_tile_x = int(top_left_world_x // self.tile_size) - 1
        min_tile_y = int(top_left_world_y // self.tile_size) - 1
        max_tile_x = int(bottom_right_world_x // self.tile_size) + 1
        max_tile_y = int(bottom_right_world_y // self.tile_size) + 1

        return ((min_tile_x, min_tile_y), (max_tile_x, max_tile_y))

    def get_tile_pattern_type(self, tile_x: int, tile_y: int) -> int:
        """
        Get the tile pattern type for visual variety.

        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate

        Returns:
            Pattern type (0 or 1 for checkerboard pattern)
        """
        # AI-DEV : 체스보드 패턴을 위한 간단한 모듈로 연산
        # - 문제: 단조로운 격자 패턴으로 인한 시각적 지루함
        # - 해결책: 타일 좌표 기반 체스보드 패턴 생성으로 시각적 개선
        # - 주의사항: (x+y) % 2 연산으로 체스보드 패턴 생성
        return (tile_x + tile_y) % 2

    def get_tile_color(self, tile_x: int, tile_y: int) -> tuple[int, int, int]:
        """
        Get the tile color based on checkerboard pattern.

        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate

        Returns:
            RGB color tuple for the tile
        """
        pattern_type = self.get_tile_pattern_type(tile_x, tile_y)
        return (
            self.light_tile_color
            if pattern_type == 0
            else self.dark_tile_color
        )

    def is_within_world_bounds(self, world_x: float, world_y: float) -> bool:
        """
        Check if a world coordinate is within map boundaries.

        Args:
            world_x: World X coordinate
            world_y: World Y coordinate

        Returns:
            True if within bounds, False otherwise
        """
        return (
            0 <= world_x <= self.world_width
            and 0 <= world_y <= self.world_height
        )

    def clamp_to_world_bounds(
        self, world_x: float, world_y: float
    ) -> tuple[float, float]:
        """
        Clamp world coordinates to map boundaries.

        Args:
            world_x: World X coordinate
            world_y: World Y coordinate

        Returns:
            Clamped coordinates as (x, y)
        """
        clamped_x = max(0.0, min(world_x, self.world_width))
        clamped_y = max(0.0, min(world_y, self.world_height))

        return (clamped_x, clamped_y)

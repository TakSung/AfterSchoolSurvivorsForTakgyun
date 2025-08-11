"""
PositionComponent for storing entity position in world coordinates.

This component represents the position of an entity in the game world,
used by various systems including rendering, movement, and collision detection.
"""

from dataclasses import dataclass

from ..core.component import Component


@dataclass
class PositionComponent(Component):
    """
    Component that stores position data for entities in world coordinates.

    The PositionComponent tracks the entity's position in the world coordinate system,
    which is separate from screen coordinates used for rendering.
    """

    # AI-NOTE : 2025-08-11 월드 좌표계 기반 위치 저장
    # - 이유: 화면 독립적인 게임 로직을 위한 월드 좌표 사용
    # - 요구사항: 모든 엔티티는 월드 상의 실제 위치를 가져야 함
    # - 히스토리: 스크린 좌표에서 월드 좌표 시스템으로 분리
    x: float = 0.0
    y: float = 0.0

    def validate(self) -> bool:
        """
        Validate position component data.

        Returns:
            True if position data is valid, False otherwise.
        """
        return isinstance(self.x, (int, float)) and isinstance(
            self.y, (int, float)
        )

    def get_position(self) -> tuple[float, float]:
        """
        Get position as a tuple.

        Returns:
            Position as (x, y) tuple.
        """
        return (self.x, self.y)

    def set_position(self, x: float, y: float) -> None:
        """
        Set position coordinates.

        Args:
            x: New X coordinate
            y: New Y coordinate
        """
        self.x = x
        self.y = y

    def distance_to(self, other: 'PositionComponent') -> float:
        """
        Calculate distance to another position component.

        Args:
            other: Other position component

        Returns:
            Distance between the two positions.
        """
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx * dx + dy * dy) ** 0.5

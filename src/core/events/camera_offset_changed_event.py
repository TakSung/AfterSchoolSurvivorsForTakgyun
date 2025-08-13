"""
CameraOffsetChangedEvent for notifying camera offset changes.

This event is published when the camera's world offset changes, allowing
other systems to react to camera movement without tight coupling.
"""

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base_event import BaseEvent
from .event_types import EventType

if TYPE_CHECKING:
    pass


@dataclass
class CameraOffsetChangedEvent(BaseEvent):
    """
    Event published when camera offset changes in the coordinate system.

    This event allows systems like MapRenderSystem and other rendering
    systems to efficiently cache camera offset information without
    needing to directly query camera entities every frame.
    """

    # AI-NOTE : 2025-08-13 카메라 오프셋 변경 이벤트 시스템 구현
    # - 이유: CameraSystem과 CoordinateManager 간의 느슨한 결합 구현
    # - 요구사항: 카메라 오프셋 변경 시 관련 시스템들에게 자동 알림
    # - 히스토리: MapRenderSystem의 직접 엔티티 순회에서 이벤트 기반으로 변경

    world_offset: tuple[float, float]
    """The new world offset coordinates (x, y)"""

    screen_center: tuple[int, int]
    """Screen center coordinates for reference"""

    camera_entity_id: str
    """ID of the camera entity that changed"""

    previous_offset: tuple[float, float] | None = None
    """Previous offset for delta calculations (optional)"""

    def __post_init__(self) -> None:
        """Initialize the event with camera-specific data."""
        # AI-DEV : screen_center float 값 자동 정수 변환 처리
        # - 문제: 사용자가 float 좌표를 전달할 수 있음
        # - 해결책: __post_init__에서 자동으로 int로 변환
        # - 주의사항: 원본 튜플 불변성 유지하면서 새 튜플 생성
        if (
            hasattr(self, 'screen_center')
            and isinstance(self.screen_center, tuple)
            and len(self.screen_center) == 2
        ):
            converted_center = (
                (
                    int(self.screen_center[0])
                    if isinstance(self.screen_center[0], int | float)
                    else self.screen_center[0]
                ),
                (
                    int(self.screen_center[1])
                    if isinstance(self.screen_center[1], int | float)
                    else self.screen_center[1]
                ),
            )
            object.__setattr__(self, 'screen_center', converted_center)

        # Set event type before calling parent's __post_init__
        object.__setattr__(self, 'event_type', EventType.CAMERA_OFFSET_CHANGED)

        # Set timestamp if not provided
        if not hasattr(self, 'timestamp') or self.timestamp == 0.0:
            object.__setattr__(self, 'timestamp', time.time())

        if not hasattr(self, 'created_at') or self.created_at is None:
            from datetime import datetime

            object.__setattr__(self, 'created_at', datetime.now())

        # Call parent's validation through super().__post_init__()
        # would cause issues with dataclass inheritance, handle it manually
        if not hasattr(self, '_initialized'):
            object.__setattr__(self, '_initialized', True)

    def validate(self) -> bool:
        """
        Validate camera offset event data.

        Returns:
            True if event data is valid, False otherwise.
        """
        # 월드 오프셋 유효성 검사
        if (
            not isinstance(self.world_offset, tuple)
            or len(self.world_offset) != 2
        ):
            return False

        if not all(
            isinstance(coord, int | float) for coord in self.world_offset
        ):
            return False

        # 화면 중앙 좌표 유효성 검사
        if (
            not isinstance(self.screen_center, tuple)
            or len(self.screen_center) != 2
        ):
            return False

        if not all(isinstance(coord, int) for coord in self.screen_center):
            return False

        # 카메라 엔티티 ID 유효성 검사 (UUID : str)
        if not isinstance(self.camera_entity_id, str):
            return False

        # 이전 오프셋이 제공된 경우 유효성 검사
        if self.previous_offset is not None:
            if (
                not isinstance(self.previous_offset, tuple)
                or len(self.previous_offset) != 2
            ):
                return False

            if not all(
                isinstance(coord, int | float)
                for coord in self.previous_offset
            ):
                return False

        # 기본 이벤트 검증
        if (
            not hasattr(self, 'event_type')
            or self.event_type != EventType.CAMERA_OFFSET_CHANGED
        ):
            return False

        return isinstance(self.timestamp, int | float) and self.timestamp > 0

    def get_offset_delta(self) -> tuple[float, float] | None:
        """
        Calculate the offset delta if previous offset is available.

        Returns:
            Tuple of (delta_x, delta_y) or None if previous offset unavailable.
        """
        if self.previous_offset is None:
            return None

        delta_x = self.world_offset[0] - self.previous_offset[0]
        delta_y = self.world_offset[1] - self.previous_offset[1]
        return (delta_x, delta_y)

    def has_significant_change(self, threshold: float = 1.0) -> bool:
        """
        Check if offset change is significant enough to warrant processing.

        Args:
            threshold: Minimum change threshold in pixels.

        Returns:
            True if change is above threshold, False otherwise.
        """
        if self.previous_offset is None:
            return True  # First time is always significant

        delta = self.get_offset_delta()
        if delta is None:
            return True

        delta_magnitude = (delta[0] ** 2 + delta[1] ** 2) ** 0.5
        return delta_magnitude >= threshold

    def __str__(self) -> str:
        """Return string representation of the camera offset changed event."""
        return (
            f'CameraOffsetChangedEvent('
            f'entity={self.camera_entity_id}, '
            f'offset={self.world_offset}, '
            f'timestamp={self.timestamp:.3f})'
        )

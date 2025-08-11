"""
CameraComponent for managing camera position and behavior in the game.

This component stores camera-related data including world offset, screen center,
world boundaries, and follow target for the camera system.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from ..core.component import Component

if TYPE_CHECKING:
    from ..core.entity import Entity


@dataclass
class CameraComponent(Component):
    """
    Component that stores camera data for rendering and viewport management.

    The CameraComponent manages the camera's world offset to keep the player
    centered on screen, handles world boundaries, and tracks the target entity.
    """

    # AI-NOTE : 2025-08-11 카메라 월드 오프셋 시스템 도입
    # - 이유: 플레이어를 화면 중앙에 고정하기 위한 월드 좌표 변환 필요
    # - 요구사항: 플레이어 이동 시 카메라가 역방향으로 이동하여 중앙 고정
    # - 히스토리: 기본 렌더링에서 카메라 시스템으로 확장
    world_offset: tuple[float, float] = (0.0, 0.0)

    # AI-DEV : 화면 중앙 좌표 사전 계산으로 성능 최적화
    # - 문제: 매 프레임마다 화면 중앙 계산 시 불필요한 연산
    # - 해결책: 컴포넌트 초기화 시 고정값으로 설정
    # - 주의사항: 화면 해상도 변경 시 재계산 필요
    screen_center: tuple[int, int] = (
        400,
        300,
    )  # SCREEN_WIDTH//2, SCREEN_HEIGHT//2

    # AI-NOTE : 2025-08-11 월드 경계 제한 시스템
    # - 이유: 카메라가 무한히 이동하여 빈 공간을 보여주는 것 방지
    # - 요구사항: 게임 월드의 경계를 넘어서지 않도록 카메라 제한
    # - 히스토리: 초기에는 무제한 이동에서 경계 제한으로 변경
    world_bounds: dict[str, float] = field(
        default_factory=lambda: {
            'min_x': -1000.0,
            'max_x': 1000.0,
            'min_y': -1000.0,
            'max_y': 1000.0,
        }
    )

    # AI-DEV : Optional[Entity] 타입으로 추적 대상 유연성 확보
    # - 문제: 카메라가 항상 플레이어만 추적해야 하는 제약
    # - 해결책: None 허용으로 추적 대상 변경 가능
    # - 주의사항: None일 경우 카메라 이동 로직 분기 처리 필요
    follow_target: Optional['Entity'] = None

    # AI-NOTE : 2025-08-11 마우스 추적 데드존 시스템
    # - 이유: 미세한 마우스 움직임으로 인한 카메라 떨림 방지
    # - 요구사항: 10픽셀 이내의 마우스 이동은 무시
    # - 히스토리: 즉시 추적에서 데드존 적용으로 개선
    dead_zone_radius: float = 10.0

    def validate(self) -> bool:
        """
        Validate camera component data integrity.

        Returns:
            True if all camera data is valid, False otherwise.
        """
        # 월드 오프셋 값 유효성 검사
        if (
            not isinstance(self.world_offset, tuple)
            or len(self.world_offset) != 2
        ):
            return False

        if not all(
            isinstance(coord, (int, float)) for coord in self.world_offset
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

        # 월드 경계 유효성 검사
        required_bounds = {'min_x', 'max_x', 'min_y', 'max_y'}
        if not isinstance(
            self.world_bounds, dict
        ) or not required_bounds.issubset(self.world_bounds.keys()):
            return False

        # 경계값의 논리적 일관성 검사
        if (
            self.world_bounds['min_x'] >= self.world_bounds['max_x']
            or self.world_bounds['min_y'] >= self.world_bounds['max_y']
        ):
            return False

        # 데드존 반지름 유효성 검사
        if (
            not isinstance(self.dead_zone_radius, (int, float))
            or self.dead_zone_radius < 0
        ):
            return False

        return True

    def set_world_bounds(
        self, min_x: float, max_x: float, min_y: float, max_y: float
    ) -> None:
        """
        Set the world boundaries for camera movement.

        Args:
            min_x: Minimum X coordinate the camera can see
            max_x: Maximum X coordinate the camera can see
            min_y: Minimum Y coordinate the camera can see
            max_y: Maximum Y coordinate the camera can see
        """
        self.world_bounds = {
            'min_x': min_x,
            'max_x': max_x,
            'min_y': min_y,
            'max_y': max_y,
        }

    def update_world_offset(self, new_offset: tuple[float, float]) -> bool:
        """
        Update the world offset with boundary checking.

        Args:
            new_offset: New world offset coordinates

        Returns:
            True if the offset was updated, False if constrained by boundaries
        """
        # 경계 제한 적용
        constrained_x = max(
            self.world_bounds['min_x'],
            min(self.world_bounds['max_x'], new_offset[0]),
        )
        constrained_y = max(
            self.world_bounds['min_y'],
            min(self.world_bounds['max_y'], new_offset[1]),
        )

        constrained_offset = (constrained_x, constrained_y)

        # 실제 변경이 있는 경우에만 업데이트
        if constrained_offset != self.world_offset:
            self.world_offset = constrained_offset
            return True

        return False

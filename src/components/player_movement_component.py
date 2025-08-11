"""
PlayerMovementComponent for managing player position and movement state.

This component stores player-specific movement data including world position,
direction, speed, rotation angle, and angular velocity limits for smooth movement.
"""

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..core.component import Component

if TYPE_CHECKING:
    pass


@dataclass
class PlayerMovementComponent(Component):
    """
    Component that stores player movement data and physics properties.

    The PlayerMovementComponent manages the player's world position, movement
    direction, speed, and rotation properties for mouse-based movement control.
    """

    # AI-NOTE : 2025-08-11 플레이어 월드 위치 추적 시스템
    # - 이유: 카메라 중앙 고정 방식에서도 실제 월드 내 플레이어 위치 필요
    # - 요구사항: 월드 좌표계에서의 정확한 위치 추적
    # - 히스토리: 스크린 좌표에서 월드 좌표 기반으로 변경
    world_position: tuple[float, float] = (0.0, 0.0)

    # AI-DEV : 정규화된 방향 벡터로 성능 최적화
    # - 문제: 매번 방향 벡터 정규화 연산 시 성능 저하
    # - 해결책: 미리 정규화된 방향 벡터를 컴포넌트에 저장
    # - 주의사항: 방향 변경 시 정규화 상태 유지 필요
    direction: tuple[float, float] = (
        1.0,
        0.0,
    )  # 정규화된 방향 벡터 (기본: 우측)

    # AI-NOTE : 2025-08-11 플레이어 이동 속도 시스템
    # - 이유: 게임플레이 밸런스를 위한 이동 속도 조절
    # - 요구사항: pixels per second 단위의 이동 속도
    # - 히스토리: 고정 속도에서 조절 가능한 속도로 확장
    speed: float = 200.0  # pixels per second

    # AI-DEV : 회전각 추적을 통한 부드러운 회전 구현
    # - 문제: 급작스러운 방향 전환으로 인한 부자연스러운 움직임
    # - 해결책: 현재 회전각을 추적하여 보간된 회전 적용
    # - 주의사항: 라디안 단위 사용, -π ~ π 범위 유지
    rotation_angle: float = 0.0  # 현재 회전각 (라디안)

    # AI-NOTE : 2025-08-11 부드러운 회전을 위한 각속도 제한
    # - 이유: 마우스 위치 급변 시 자연스러운 회전 제공
    # - 요구사항: 라디안/초 단위의 최대 각속도 제한
    # - 히스토리: 즉시 회전에서 제한된 각속도로 개선
    angular_velocity_limit: float = math.pi * 2.0  # 라디안/초 (360도/초)

    # AI-DEV : 이전 위치 추적을 통한 이동 벡터 계산
    # - 문제: 충돌 처리나 보간 계산 시 이전 위치 정보 필요
    # - 해결책: 컴포넌트에 이전 프레임의 위치 저장
    # - 주의사항: 매 프레임 업데이트 시 갱신 필요
    previous_position: tuple[float, float] = (0.0, 0.0)

    # AI-NOTE : 2025-08-11 마우스 데드존 시스템
    # - 이유: 미세한 마우스 움직임으로 인한 떨림 현상 방지
    # - 요구사항: 화면 중앙에서 10픽셀 이내는 정지 상태 유지
    # - 히스토리: 카메라 시스템과 동일한 데드존 값 사용
    dead_zone_radius: float = 10.0  # 픽셀 단위

    def validate(self) -> bool:
        """
        Validate player movement component data integrity.

        Returns:
            True if all movement data is valid, False otherwise.
        """
        # 월드 위치 유효성 검사
        if (
            not isinstance(self.world_position, tuple)
            or len(self.world_position) != 2
        ):
            return False

        if not all(
            isinstance(coord, (int, float)) for coord in self.world_position
        ):
            return False

        # 방향 벡터 유효성 검사
        if not isinstance(self.direction, tuple) or len(self.direction) != 2:
            return False

        if not all(
            isinstance(coord, (int, float)) for coord in self.direction
        ):
            return False

        # 방향 벡터 정규화 상태 확인 (허용 오차 0.01)
        direction_magnitude = math.sqrt(
            self.direction[0] ** 2 + self.direction[1] ** 2
        )
        if abs(direction_magnitude - 1.0) > 0.01:
            return False

        # 속도 유효성 검사
        if not isinstance(self.speed, (int, float)) or self.speed < 0:
            return False

        # 회전각 유효성 검사 (-π ~ π 범위)
        if not isinstance(self.rotation_angle, (int, float)):
            return False

        if abs(self.rotation_angle) > math.pi + 0.01:  # 허용 오차 포함
            return False

        # 각속도 제한 유효성 검사
        if (
            not isinstance(self.angular_velocity_limit, (int, float))
            or self.angular_velocity_limit <= 0
        ):
            return False

        # 이전 위치 유효성 검사
        if (
            not isinstance(self.previous_position, tuple)
            or len(self.previous_position) != 2
        ):
            return False

        if not all(
            isinstance(coord, (int, float)) for coord in self.previous_position
        ):
            return False

        # 데드존 반지름 유효성 검사
        if (
            not isinstance(self.dead_zone_radius, (int, float))
            or self.dead_zone_radius < 0
        ):
            return False

        return True

    def normalize_direction(self) -> None:
        """
        Normalize the direction vector to unit length.

        Ensures the direction vector has magnitude 1 for consistent movement.
        """
        dx, dy = self.direction
        magnitude = math.sqrt(dx * dx + dy * dy)

        if magnitude > 0.0001:  # 너무 작은 값은 0으로 처리
            self.direction = (dx / magnitude, dy / magnitude)
        else:
            self.direction = (1.0, 0.0)  # 기본 방향 (우측)

    def set_direction_from_angle(self, angle: float) -> None:
        """
        Set direction vector from rotation angle.

        Args:
            angle: Rotation angle in radians
        """
        self.rotation_angle = self._normalize_angle(angle)
        self.direction = (math.cos(angle), math.sin(angle))

    def get_movement_vector(self, delta_time: float) -> tuple[float, float]:
        """
        Calculate movement vector for this frame.

        Args:
            delta_time: Time elapsed since last frame in seconds

        Returns:
            Movement vector as (dx, dy) in pixels
        """
        distance = self.speed * delta_time
        return (self.direction[0] * distance, self.direction[1] * distance)

    def update_position(self, new_position: tuple[float, float]) -> None:
        """
        Update world position and track previous position.

        Args:
            new_position: New world position coordinates
        """
        self.previous_position = self.world_position
        self.world_position = new_position

    def get_velocity(self) -> tuple[float, float]:
        """
        Get current velocity vector.

        Returns:
            Velocity vector as (vx, vy) in pixels per second
        """
        return (self.direction[0] * self.speed, self.direction[1] * self.speed)

    def _normalize_angle(self, angle: float) -> float:
        """
        Normalize angle to -π ~ π range.

        Args:
            angle: Angle in radians

        Returns:
            Normalized angle in -π ~ π range
        """
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def calculate_angular_difference(self, target_angle: float) -> float:
        """
        Calculate the shortest angular difference to target angle.

        Args:
            target_angle: Target angle in radians

        Returns:
            Angular difference in radians (-π ~ π)
        """
        diff = target_angle - self.rotation_angle
        return self._normalize_angle(diff)

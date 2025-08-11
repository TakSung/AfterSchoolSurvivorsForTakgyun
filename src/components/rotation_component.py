"""
RotationComponent for storing entity rotation information.

This component manages the rotation angle and related properties for entities
that need to be rotated during rendering.
"""

import math
from dataclasses import dataclass

from ..core.component import Component


@dataclass
class RotationComponent(Component):
    """
    Component that stores rotation data for entities.

    The RotationComponent tracks the entity's rotation angle and provides
    methods for rotation calculations and angle normalization.
    """

    # AI-NOTE : 2025-08-11 회전 각도 관리 시스템
    # - 이유: 플레이어가 마우스 방향을 바라보기 위한 회전 처리
    # - 요구사항: 도 단위 각도로 0-360 범위 관리
    # - 히스토리: 기본 렌더링에서 회전 가능한 렌더링으로 확장
    angle: float = 0.0  # 각도 (도 단위, 0-360)

    # AI-DEV : 회전 속도 제한을 위한 최대 각속도 설정
    # - 문제: 무제한 회전으로 인한 시각적 어색함
    # - 해결책: 최대 각속도로 부드러운 회전 구현
    # - 주의사항: None이면 즉시 회전, 값이 있으면 제한된 속도로 회전
    max_angular_velocity: float | None = None

    def validate(self) -> bool:
        """
        Validate rotation component data.

        Returns:
            True if rotation data is valid, False otherwise.
        """
        if not isinstance(self.angle, (int, float)):
            return False

        if self.max_angular_velocity is not None:
            if not isinstance(self.max_angular_velocity, (int, float)):
                return False
            if self.max_angular_velocity < 0:
                return False

        return True

    def normalize_angle(self) -> None:
        """Normalize angle to 0-360 range."""
        self.angle = self.angle % 360.0

    def get_angle_radians(self) -> float:
        """
        Get angle in radians.

        Returns:
            Angle in radians.
        """
        return math.radians(self.angle)

    def set_angle_radians(self, radians: float) -> None:
        """
        Set angle from radians.

        Args:
            radians: Angle in radians
        """
        self.angle = math.degrees(radians)
        self.normalize_angle()

    def set_angle(self, angle: float) -> None:
        """
        Set angle and normalize.

        Args:
            angle: Angle in degrees
        """
        self.angle = angle
        self.normalize_angle()

    def rotate_by(self, delta_angle: float) -> None:
        """
        Rotate by the specified angle.

        Args:
            delta_angle: Angle to rotate by (in degrees)
        """
        self.angle += delta_angle
        self.normalize_angle()

    def get_direction_vector(self) -> tuple[float, float]:
        """
        Get direction vector from current angle.

        Returns:
            Direction vector as (x, y) tuple (normalized).
        """
        radians = self.get_angle_radians()
        return (math.cos(radians), math.sin(radians))

    def look_at(
        self,
        target_x: float,
        target_y: float,
        origin_x: float,
        origin_y: float,
    ) -> None:
        """
        Set angle to look at target position.

        Args:
            target_x: Target X coordinate
            target_y: Target Y coordinate
            origin_x: Origin X coordinate
            origin_y: Origin Y coordinate
        """
        dx = target_x - origin_x
        dy = target_y - origin_y

        if dx == 0 and dy == 0:
            return

        angle_radians = math.atan2(dy, dx)
        self.set_angle_radians(angle_radians)

    def smooth_rotate_towards(
        self, target_angle: float, delta_time: float
    ) -> bool:
        """
        Smoothly rotate towards target angle with angular velocity limit.

        Args:
            target_angle: Target angle in degrees
            delta_time: Time elapsed since last update

        Returns:
            True if rotation is complete, False if still rotating.
        """
        if self.max_angular_velocity is None:
            self.set_angle(target_angle)
            return True

        # 최단 회전 경로 계산
        angle_diff = target_angle - self.angle

        # -180 ~ 180 범위로 정규화
        while angle_diff > 180:
            angle_diff -= 360
        while angle_diff < -180:
            angle_diff += 360

        # 최대 회전량 계산
        max_rotation = self.max_angular_velocity * delta_time

        if abs(angle_diff) <= max_rotation:
            # 목표에 도달
            self.set_angle(target_angle)
            return True
        else:
            # 최대 속도로 회전
            rotation_direction = 1 if angle_diff > 0 else -1
            self.rotate_by(max_rotation * rotation_direction)
            return False

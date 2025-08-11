"""
Velocity component for ECS architecture.

Defines velocity properties for entities including velocity vector,
friction, and gravity application settings.
"""

from dataclasses import dataclass


@dataclass
class VelocityComponent:
    """
    Component that defines velocity and movement properties for an entity.
    
    Contains velocity vector and physics properties like friction and gravity.
    """
    
    vx: float = 0.0
    vy: float = 0.0
    max_speed: float = 1000.0
    friction: float = 0.0
    apply_gravity: bool = False

    def __post_init__(self) -> None:
        """
        Initialize velocity component after creation.
        
        Validates input parameters and ensures reasonable values.
        """
        # AI-NOTE : 2025-01-11 속도 컴포넌트 유효성 검증 및 제한
        # - 이유: 물리 시뮬레이션 안정성을 위한 속도 제한 필요
        # - 요구사항: 최대 속도, 마찰 계수 범위 제한
        # - 히스토리: 기본 속도 속성 정의 및 검증 로직 구현
        
        if self.max_speed <= 0:
            raise ValueError(f"Max speed must be positive: {self.max_speed}")
        
        if not 0.0 <= self.friction <= 1.0:
            raise ValueError(f"Friction must be between 0.0 and 1.0: {self.friction}")
        
        # 초기 속도가 최대 속도를 넘지 않도록 제한
        self._clamp_velocity()

    def _clamp_velocity(self) -> None:
        """Clamp velocity to maximum speed limit."""
        current_speed = self.get_speed()
        if current_speed > self.max_speed:
            scale = self.max_speed / current_speed
            self.vx *= scale
            self.vy *= scale

    def set_velocity(self, vx: float, vy: float) -> None:
        """
        Set velocity components.
        
        Args:
            vx: X component of velocity.
            vy: Y component of velocity.
        """
        self.vx = vx
        self.vy = vy
        self._clamp_velocity()

    def add_velocity(self, dvx: float, dvy: float) -> None:
        """
        Add velocity components to current velocity.
        
        Args:
            dvx: X component to add to velocity.
            dvy: Y component to add to velocity.
        """
        self.vx += dvx
        self.vy += dvy
        self._clamp_velocity()

    def get_velocity(self) -> tuple[float, float]:
        """
        Get velocity as a tuple.
        
        Returns:
            Velocity as (vx, vy) tuple.
        """
        return (self.vx, self.vy)

    def get_speed(self) -> float:
        """
        Get speed (magnitude of velocity).
        
        Returns:
            Speed as a scalar value.
        """
        return (self.vx ** 2 + self.vy ** 2) ** 0.5

    def normalize_velocity(self, target_speed: float) -> None:
        """
        Normalize velocity to a target speed.
        
        Args:
            target_speed: Desired speed magnitude.
        """
        current_speed = self.get_speed()
        if current_speed > 0:
            scale = min(target_speed, self.max_speed) / current_speed
            self.vx *= scale
            self.vy *= scale

    def stop(self) -> None:
        """Stop the entity by setting velocity to zero."""
        self.vx = 0.0
        self.vy = 0.0

    def is_moving(self, threshold: float = 1e-6) -> bool:
        """
        Check if the entity is moving.
        
        Args:
            threshold: Minimum speed to consider as moving.
            
        Returns:
            True if speed is above threshold, False otherwise.
        """
        return self.get_speed() > threshold

    def apply_friction_step(self, delta_time: float) -> None:
        """
        Apply one step of friction directly to velocity.
        
        Args:
            delta_time: Time step for friction application.
        """
        if self.friction > 0 and self.is_moving():
            current_speed = self.get_speed()
            # 마찰력으로 인한 속도 감소
            friction_deceleration = self.friction * current_speed
            speed_reduction = friction_deceleration * delta_time
            
            if speed_reduction >= current_speed:
                # 마찰이 현재 속도보다 크면 정지
                self.stop()
            else:
                # 속도 방향 유지하면서 크기만 감소
                scale = (current_speed - speed_reduction) / current_speed
                self.vx *= scale
                self.vy *= scale

    def __str__(self) -> str:
        """String representation of the velocity component."""
        speed = self.get_speed()
        moving = "moving" if self.is_moving() else "stationary"
        friction_text = f", friction={self.friction}" if self.friction > 0 else ""
        gravity_text = ", with gravity" if self.apply_gravity else ""
        
        return (
            f"VelocityComponent(({self.vx:.2f}, {self.vy:.2f}), "
            f"speed={speed:.2f}/{self.max_speed}, {moving}{friction_text}{gravity_text})"
        )
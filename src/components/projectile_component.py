"""
ProjectileComponent for managing projectile properties and state.

This component represents projectile properties including direction, velocity,
lifetime, damage, and physics state for entities that are projectiles.
"""

from dataclasses import dataclass

from ..core.component import Component
from ..utils.vector2 import Vector2


@dataclass
class ProjectileComponent(Component):
    """
    Component that stores projectile data for entities that move and damage.

    The ProjectileComponent tracks projectile properties including direction,
    velocity, lifetime management, and damage for physics-based systems.
    """

    # AI-NOTE : 2025-08-12 투사체 컴포넌트 구현 - 물리 기반 투사체 시스템
    # - 이유: 자동 공격 시스템에서 생성되는 투사체 데이터 관리 필요
    # - 요구사항: 방향, 속도, 수명, 데미지 관리로 투사체 물리 처리 지원
    # - 히스토리: Vector2를 활용한 벡터 기반 방향 및 속도 계산
    direction: Vector2 = None  # 정규화된 방향 벡터
    velocity: float = 300.0  # 초당 이동 속도 (픽셀)
    lifetime: float = 3.0  # 투사체 수명 (초)
    max_lifetime: float = 3.0  # 최대 수명 (초)
    damage: int = 10  # 투사체 데미지
    owner_id: str | None = None  # 투사체를 생성한 엔티티 ID
    piercing: bool = False  # 관통 여부 (True면 적을 관통해서 지나감)
    hit_targets: list[str] = None  # 이미 충돌한 타겟들 (관통 투사체용)

    def __post_init__(self) -> None:
        """Initialize default values after dataclass creation."""
        if self.hit_targets is None:
            self.hit_targets = []
        if self.direction is None:
            self.direction = Vector2.zero()

    def validate(self) -> bool:
        """
        Validate projectile component data.

        Returns:
            True if projectile data is valid, False otherwise.
        """
        return (
            self.velocity > 0
            and self.lifetime >= 0
            and self.max_lifetime > 0
            and self.damage >= 0
            and self.lifetime <= self.max_lifetime
        )

    def get_velocity_vector(self) -> Vector2:
        """
        Get the velocity vector for physics calculations.

        Returns:
            Velocity vector combining direction and speed.
        """
        return self.direction * self.velocity

    def is_expired(self) -> bool:
        """
        Check if the projectile has expired.

        Returns:
            True if projectile lifetime has ended, False otherwise.
        """
        return self.lifetime <= 0

    def update_lifetime(self, delta_time: float) -> None:
        """
        Update projectile lifetime.

        Args:
            delta_time: Time elapsed since last update in seconds.
        """
        self.lifetime -= delta_time

    def get_lifetime_ratio(self) -> float:
        """
        Get the remaining lifetime as a ratio (0.0 to 1.0).

        Returns:
            Ratio of remaining lifetime (1.0 = full, 0.0 = expired).
        """
        if self.max_lifetime <= 0:
            return 0.0
        return max(0.0, self.lifetime / self.max_lifetime)

    def has_hit_target(self, target_id: str) -> bool:
        """
        Check if this projectile has already hit the specified target.

        Args:
            target_id: ID of the target entity.

        Returns:
            True if target has been hit before, False otherwise.
        """
        return target_id in self.hit_targets

    def add_hit_target(self, target_id: str) -> None:
        """
        Add a target to the list of hit targets.

        Args:
            target_id: ID of the target entity that was hit.
        """
        if target_id not in self.hit_targets:
            self.hit_targets.append(target_id)

    @classmethod
    def create_towards_target(
        cls,
        start_pos: tuple[float, float],
        target_pos: tuple[float, float],
        velocity: float = 300.0,
        damage: int = 10,
        lifetime: float = 3.0,
        owner_id: str | None = None,
    ) -> 'ProjectileComponent':
        """
        Create a projectile component aimed towards a target position.

        Args:
            start_pos: Starting position (x, y)
            target_pos: Target position (x, y)
            velocity: Projectile speed in pixels per second
            damage: Damage dealt by projectile
            lifetime: How long projectile lasts in seconds
            owner_id: ID of entity that created this projectile

        Returns:
            ProjectileComponent configured to move towards target.
        """
        start_vector = Vector2.from_tuple(start_pos)
        target_vector = Vector2.from_tuple(target_pos)
        direction = (target_vector - start_vector).normalize()

        return cls(
            direction=direction,
            velocity=velocity,
            lifetime=lifetime,
            max_lifetime=lifetime,
            damage=damage,
            owner_id=owner_id,
        )

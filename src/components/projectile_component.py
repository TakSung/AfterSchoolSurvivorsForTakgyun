"""
ProjectileComponent for managing projectile properties and state.

This component represents projectile properties including direction, velocity,
lifetime, damage, and physics state for entities that are projectiles.
"""

from dataclasses import dataclass, field

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
    direction: Vector2 = field(default_factory=Vector2.zero)  # 정규화된 방향 벡터
    velocity: float = 300.0  # 초당 이동 속도 (픽셀)
    lifetime: float = 3.0  # 투사체 수명 (초)
    max_lifetime: float = 3.0  # 최대 수명 (초)
    damage: int = 10  # 투사체 데미지
    owner_id: str | None = None  # 투사체를 생성한 엔티티 ID
    piercing: bool = False  # 관통 여부 (True면 적을 관통해서 지나감)
    hit_targets: list[str] = field(
        default_factory=list
    )  # 이미 충돌한 타겟들 (관통 투사체용)
    max_velocity: float = 1000.0  # 최대 허용 속도

    def __post_init__(self) -> None:
        """
        Initialize default values after dataclass creation."""
        # AI-DEV : 개발자 가정 - assert 검증으로 잘못된 타입 방지
        assert isinstance(self.velocity, (int, float)), (
            'velocity must be numeric'
        )
        assert self.velocity is not None, 'velocity cannot be None'
        assert self.velocity >= 0, 'velocity cannot be negative'
        assert isinstance(self.lifetime, (int, float)), (
            'lifetime must be numeric'
        )
        assert self.lifetime >= 0, 'lifetime cannot be negative'

        # AI-DEV : 최대값 제한 적용
        if self.velocity > self.max_velocity:
            self.velocity = self.max_velocity
        if self.lifetime > self.max_lifetime:
            self.lifetime = self.max_lifetime

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
        assert delta_time is not None, 'delta_time cannot be None'
        assert delta_time >= 0, 'delta_time cannot be negative'
        assert isinstance(delta_time, (int, float)), (
            'delta_time must be numeric'
        )

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
        # AI-DEV : 개발자 가정 - 입력 파라미터 검증
        assert start_pos is not None, 'start_pos cannot be None'
        assert target_pos is not None, 'target_pos cannot be None'
        assert isinstance(start_pos, tuple) and len(start_pos) == 2, (
            'start_pos must be tuple of length 2'
        )
        assert isinstance(target_pos, tuple) and len(target_pos) == 2, (
            'target_pos must be tuple of length 2'
        )
        assert velocity is not None, 'velocity cannot be None'
        assert velocity >= 0, 'velocity cannot be negative'
        assert lifetime >= 0, 'lifetime cannot be negative'

        start_vector = Vector2.from_tuple(start_pos)
        target_vector = Vector2.from_tuple(target_pos)

        # AI-NOTE : 2025-01-12 영벡터 정규화 문제 해결 - 게임 개발 트렌드 기반
        # - 이유: start_pos와 target_pos가 동일할 때 normalize() 실패 방지
        # - 해결책: 거리 검사 후 기본 방향 벡터(우측) 제공
        # - 트렌드: 에러 전파보다 기본값 제공이 게임플레이 안정성에 유리
        direction_vector = target_vector - start_vector
        if (
            direction_vector.magnitude < 1e-6
        ):  # 부동소수점 오차 고려한 영벡터 검사
            direction = Vector2(1.0, 0.0)  # 기본 방향: 우측
        else:
            direction = direction_vector.normalize()

        return cls(
            direction=direction,
            velocity=velocity,
            lifetime=lifetime,
            max_lifetime=lifetime,
            damage=damage,
            owner_id=owner_id,
        )

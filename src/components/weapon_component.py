"""
WeaponComponent for storing weapon properties and state.

This component represents weapon properties including attack speed, range,
damage, and projectile type for entities that can attack.
"""

from dataclasses import dataclass
from enum import IntEnum

from ..core.component import Component


class WeaponType(IntEnum):
    """Types of weapons available in the game."""

    SOCCER_BALL = 0
    BASKETBALL = 1
    BASEBALL_BAT = 2

    @property
    def display_name(self) -> str:
        """Get the Korean display name for the weapon type."""
        display_names = {
            WeaponType.SOCCER_BALL: '축구공',
            WeaponType.BASKETBALL: '농구공',
            WeaponType.BASEBALL_BAT: '야구 배트',
        }
        return display_names[self]

    @property
    def damage_multiplier(self) -> float:
        """Get the damage multiplier for this weapon type."""
        damage_multipliers = [1.2, 1.0, 1.5]  # Index-based fast lookup
        return damage_multipliers[self.value]


class ProjectileType(IntEnum):
    """Types of projectiles for weapons."""

    BASIC = 0

    @property
    def display_name(self) -> str:
        """Get the Korean display name for the projectile type."""
        display_names = {ProjectileType.BASIC: '기본'}
        return display_names[self]


@dataclass
class WeaponComponent(Component):
    """
    Component that stores weapon data for entities that can attack.

    The WeaponComponent tracks weapon properties including attack speed,
    range, damage, and cooldown state for automatic targeting systems.
    """

    # AI-NOTE : 2025-08-11 무기 컴포넌트 구현 - 자동 공격 시스템
    # - 이유: 플레이어 자동 공격을 위한 무기 데이터 관리 필요
    # - 요구사항: 공격속도, 사거리, 데미지, 쿨다운 시스템 지원
    # - 히스토리: 초기 구현에서는 기본 무기 타입만 지원
    weapon_type: WeaponType = WeaponType.SOCCER_BALL
    projectile_type: ProjectileType = ProjectileType.BASIC
    attack_speed: float = 1.0  # 초당 공격 횟수
    range: float = 200.0  # 사거리 (픽셀)
    damage: int = 10  # 기본 데미지
    last_attack_time: float = 0.0  # 마지막 공격 시간
    current_target_id: str | None = None  # 현재 타겟 엔티티 ID

    def validate(self) -> bool:
        """
        Validate weapon component data.

        Returns:
            True if weapon data is valid, False otherwise.
        """
        return (
            self.attack_speed > 0
            and self.range > 0
            and self.damage > 0
            and self.last_attack_time >= 0
        )

    def get_cooldown_duration(self) -> float:
        """
        Get the cooldown duration between attacks.

        Returns:
            Cooldown duration in seconds.
        """
        return 1.0 / self.attack_speed

    def can_attack(self, current_time: float) -> bool:
        """
        Check if the weapon can attack at the current time.

        Args:
            current_time: Current game time in seconds.

        Returns:
            True if weapon is ready to attack, False otherwise.
        """
        return (
            current_time - self.last_attack_time
            >= self.get_cooldown_duration()
        )

    def set_last_attack_time(self, current_time: float) -> None:
        """
        Update the last attack time to the current time.

        Args:
            current_time: Current game time in seconds.
        """
        self.last_attack_time = current_time

    def get_effective_damage(self) -> int:
        """
        Calculate effective damage with weapon type multiplier.

        Returns:
            Effective damage considering weapon type multiplier.
        """
        return int(self.damage * self.weapon_type.damage_multiplier)

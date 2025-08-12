"""
HealthComponent for managing entity health and damage.

This component tracks current health, maximum health, and provides
methods for taking damage and healing.
"""

from dataclasses import dataclass

from ..core.component import Component


@dataclass
class HealthComponent(Component):
    """
    Component that manages entity health and damage.

    The HealthComponent tracks current and maximum health,
    handles damage application, and determines when entities die.
    """

    # AI-NOTE : 2025-08-12 체력 관리 컴포넌트 구현 - 투사체 데미지 시스템
    # - 이유: 투사체 충돌 시 데미지 적용 및 적 체력 관리 필요
    # - 요구사항: 현재/최대 체력 관리, 데미지 적용, 죽음 판정
    # - 히스토리: 적 엔티티와 플레이어 모두 사용할 수 있는 범용 설계
    current_health: int = 100
    max_health: int = 100
    damage_immunity_time: float = 0.0  # 데미지 무적 시간 (초)
    last_damage_time: float = 0.0  # 마지막 데미지 받은 시간
    is_invulnerable: bool = False  # 무적 상태 여부
    regeneration_rate: float = 0.0  # 초당 체력 회복량

    def __post_init__(self) -> None:
        """Initialize health component after creation."""
        # 현재 체력이 최대 체력을 초과하지 않도록 조정
        if self.current_health > self.max_health:
            self.current_health = self.max_health

    def validate(self) -> bool:
        """
        Validate health component data.

        Returns:
            True if health data is valid, False otherwise.
        """
        return (
            self.max_health > 0
            and 0 <= self.current_health <= self.max_health
            and self.damage_immunity_time >= 0
            and self.last_damage_time >= 0
            and self.regeneration_rate >= 0
        )

    def is_alive(self) -> bool:
        """
        Check if the entity is alive.

        Returns:
            True if current health is greater than 0, False otherwise.
        """
        return self.current_health > 0

    def is_dead(self) -> bool:
        """
        Check if the entity is dead.

        Returns:
            True if current health is 0 or less, False otherwise.
        """
        return self.current_health <= 0

    def take_damage(self, damage: int, current_time: float) -> int:
        """
        Apply damage to the entity.

        Args:
            damage: Amount of damage to apply
            current_time: Current game time in seconds

        Returns:
            Actual damage dealt (may be 0 if invulnerable or immune)
        """
        assert damage is not None, "damage cannot be None"
        assert damage >= 0, "damage cannot be negative"
        assert current_time is not None, "current_time cannot be None"
        assert current_time >= 0, "current_time cannot be negative"
        assert isinstance(current_time, (int, float)), "current_time must be numeric"
        
        # 무적 상태이거나 데미지 면역 시간 내에 있으면 데미지 무시
        if self.is_invulnerable:
            return 0

        if (
            self.damage_immunity_time > 0
            and current_time - self.last_damage_time
            < self.damage_immunity_time
        ):
            return 0

        # 데미지 적용
        actual_damage = min(int(damage), self.current_health)
        self.current_health -= actual_damage
        self.last_damage_time = current_time

        return actual_damage

    def heal(self, amount: int) -> int:
        """
        Heal the entity.

        Args:
            amount: Amount of health to restore

        Returns:
            Actual amount healed (limited by max health)
        """
        assert amount is not None, "amount cannot be None"
        assert amount >= 0, "amount cannot be negative"
        
        if amount <= 0:
            return 0

        old_health = self.current_health
        self.current_health = min(
            self.current_health + int(amount), self.max_health
        )
        return self.current_health - old_health

    def set_max_health(self, new_max_health: int) -> None:
        """
        Set new maximum health.

        Args:
            new_max_health: New maximum health value
        """
        assert new_max_health is not None, "new_max_health cannot be None"
        assert new_max_health > 0, "new_max_health must be positive"
        
        self.max_health = int(new_max_health)
        # 현재 체력이 새로운 최대 체력을 초과하면 조정
        if self.current_health > self.max_health:
            self.current_health = self.max_health

    def get_health_ratio(self) -> float:
        """
        Get the current health as a ratio of max health.

        Returns:
            Health ratio between 0.0 and 1.0
        """
        if self.max_health <= 0:
            return 0.0
        return self.current_health / self.max_health

    def is_critically_wounded(self, threshold: float = 0.25) -> bool:
        """
        Check if the entity is critically wounded.

        Args:
            threshold: Health ratio threshold for critical wounds
                (default: 25%)

        Returns:
            True if health ratio is below threshold, False otherwise.
        """
        assert threshold is not None, "threshold cannot be None"
        assert threshold >= 0, "threshold cannot be negative"
        assert isinstance(threshold, (int, float)), "threshold must be numeric"
        
        return self.get_health_ratio() <= threshold

    def update_regeneration(self, delta_time: float) -> int:
        """
        Update health regeneration.

        Args:
            delta_time: Time elapsed since last update in seconds

        Returns:
            Amount of health regenerated
        """
        assert delta_time is not None, "delta_time cannot be None"
        assert delta_time >= 0, "delta_time cannot be negative"
        assert isinstance(delta_time, (int, float)), "delta_time must be numeric"
        
        if self.regeneration_rate <= 0 or self.is_dead():
            return 0

        regen_amount = int(self.regeneration_rate * delta_time)
        return self.heal(regen_amount)

    def set_invulnerable(self, invulnerable: bool) -> None:
        """
        Set invulnerability status.

        Args:
            invulnerable: New invulnerability status
        """
        self.is_invulnerable = invulnerable

    def full_heal(self) -> None:
        """Restore health to maximum."""
        self.current_health = self.max_health

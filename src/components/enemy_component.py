"""
EnemyComponent for identifying enemy entities.

This component marks entities as enemies and stores enemy-specific properties
like AI behavior type and difficulty level.
"""

from dataclasses import dataclass
from enum import IntEnum

from ..core.component import Component


class EnemyType(IntEnum):
    """Types of enemies in the game based on game design document."""

    KOREAN = 0  # 국어 선생님
    MATH = 1  # 수학 선생님
    PRINCIPAL = 2  # 교장 선생님

    @property
    def display_name(self) -> str:
        """Get the Korean display name for the enemy type."""
        display_names = {
            EnemyType.KOREAN: '국어 선생님',
            EnemyType.MATH: '수학 선생님',
            EnemyType.PRINCIPAL: '교장 선생님',
        }
        return display_names[self]

    @property
    def base_health(self) -> int:
        """Get the base health for this enemy type."""
        base_healths = [50, 30, 200]  # Index-based fast lookup
        return base_healths[self.value]

    @property
    def base_speed(self) -> float:
        """Get the base move speed for this enemy type."""
        base_speeds = [30.0, 80.0, 50.0]  # Index-based fast lookup
        return base_speeds[self.value]

    @property
    def base_attack_power(self) -> int:
        """Get the base attack power for this enemy type."""
        base_attack_powers = [25, 15, 50]  # Index-based fast lookup
        return base_attack_powers[self.value]


@dataclass
class EnemyComponent(Component):
    """
    Component that marks entities as enemies and stores enemy properties.

    The EnemyComponent identifies entities as targets for player attacks
    and stores enemy-specific properties like type and AI behavior.
    """

    # AI-NOTE : 2025-08-12 적 식별 컴포넌트 구현 - 투사체 충돌 시스템
    # - 이유: 투사체가 공격할 적 엔티티 식별을 위해 필요
    # - 요구사항: 적 타입별 기본 속성 관리, 충돌 감지에서 사용
    # - 히스토리: 자동 공격 시스템과 연동하여 타겟팅에 활용
    enemy_type: EnemyType = EnemyType.KOREAN
    difficulty_level: int = 1  # 난이도 레벨 (1-10)
    experience_reward: int = 10  # 처치 시 주는 경험치
    is_boss: bool = False  # 보스 여부

    def validate(self) -> bool:
        """
        Validate enemy component data.

        Returns:
            True if enemy data is valid, False otherwise.
        """
        assert isinstance(self.enemy_type, EnemyType), (
            'enemy_type must be EnemyType'
        )
        assert isinstance(self.difficulty_level, int), (
            'difficulty_level must be int'
        )
        assert isinstance(self.experience_reward, int), (
            'experience_reward must be int'
        )
        assert isinstance(self.is_boss, bool), 'is_boss must be bool'

        return 1 <= self.difficulty_level <= 10 and self.experience_reward >= 0

    def get_scaled_health(self) -> int:
        """
        Get health scaled by difficulty level.

        Returns:
            Base health multiplied by difficulty scaling.
        """
        base_health = self.enemy_type.base_health
        difficulty_multiplier = 1.0 + (self.difficulty_level - 1) * 0.2
        return int(base_health * difficulty_multiplier)

    def get_scaled_speed(self) -> float:
        """
        Get movement speed scaled by difficulty level.

        Only MATH and PRINCIPAL teachers get speed scaling per game design.

        Returns:
            Base speed with difficulty scaling applied.
        """
        base_speed = self.enemy_type.base_speed

        # 기획서에 따른 난이도별 스케일링
        if self.enemy_type in (EnemyType.MATH, EnemyType.PRINCIPAL):
            difficulty_multiplier = 1.0 + (self.difficulty_level - 1) * 0.1
            return base_speed * difficulty_multiplier
        else:
            return base_speed

    def get_scaled_attack_power(self) -> int:
        """
        Get attack power scaled by difficulty level.

        Only KOREAN and PRINCIPAL teachers get attack power scaling per game design.

        Returns:
            Base attack power with difficulty scaling applied.
        """
        base_attack = self.enemy_type.base_attack_power

        # 기획서에 따른 난이도별 스케일링
        if self.enemy_type in (EnemyType.KOREAN, EnemyType.PRINCIPAL):
            difficulty_multiplier = 1.0 + (self.difficulty_level - 1) * 0.2
            return int(base_attack * difficulty_multiplier)
        else:
            return base_attack

    def get_experience_reward(self) -> int:
        """
        Get experience reward with difficulty scaling.

        Returns:
            Experience points awarded for defeating this enemy.
        """
        difficulty_multiplier = 1.0 + (self.difficulty_level - 1) * 0.5
        return int(self.experience_reward * difficulty_multiplier)

    def is_valid_target(self) -> bool:
        """
        Check if this enemy is a valid target for attacks.

        Returns:
            True if enemy can be targeted, False otherwise.
        """
        # 현재는 모든 적이 유효한 타겟이지만, 향후 무적 상태 등 추가 가능
        return True

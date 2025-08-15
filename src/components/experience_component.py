"""
ExperienceComponent for managing player experience and leveling.

This component tracks current experience, level, and provides
experience calculation strategies through the Strategy pattern.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import IntEnum
from typing import TYPE_CHECKING

from ..core.component import Component

if TYPE_CHECKING:
    pass


class ExperienceType(IntEnum):
    """Types of experience calculation strategies."""

    DEFAULT = 0
    LINEAR = 1
    EXPONENTIAL = 2

    @property
    def display_name(self) -> str:
        """Get display name for experience type."""
        _display_names = {
            ExperienceType.DEFAULT: '기본 경험치',
            ExperienceType.LINEAR: '선형 경험치',
            ExperienceType.EXPONENTIAL: '지수 경험치',
        }
        return _display_names[self]


class ExperienceCalculationStrategy(ABC):
    """
    Abstract base class for experience calculation strategies.

    This class defines the interface for different experience
    calculation methods using the Strategy pattern.
    """

    @abstractmethod
    def calculate_exp_to_next_level(self, current_level: int) -> int:
        """
        Calculate experience needed for next level.

        Args:
            current_level: Current player level

        Returns:
            Experience points needed to reach next level
        """
        pass

    @abstractmethod
    def calculate_total_exp_for_level(self, level: int) -> int:
        """
        Calculate total experience needed to reach a specific level.

        Args:
            level: Target level

        Returns:
            Total experience points needed to reach the level
        """
        pass


class DefaultExperienceStrategy(ExperienceCalculationStrategy):
    """Default experience calculation strategy with moderate scaling."""

    def __init__(self, base_exp: int = 100, multiplier: float = 1.5):
        """
        Initialize default strategy.

        Args:
            base_exp: Base experience for level 2
            multiplier: Scaling multiplier per level
        """
        self.base_exp = base_exp
        self.multiplier = multiplier

    def calculate_exp_to_next_level(self, current_level: int) -> int:
        """Calculate experience needed for next level using moderate scaling."""
        if current_level <= 0:
            return self.base_exp
        return int(self.base_exp * (self.multiplier ** (current_level - 1)))

    def calculate_total_exp_for_level(self, level: int) -> int:
        """Calculate total experience needed to reach a specific level."""
        if level <= 1:
            return 0

        total = 0
        for i in range(1, level):
            total += self.calculate_exp_to_next_level(i)
        return total


class LinearExperienceStrategy(ExperienceCalculationStrategy):
    """Linear experience calculation strategy."""

    def __init__(self, base_exp: int = 100, increment: int = 50):
        """
        Initialize linear strategy.

        Args:
            base_exp: Base experience for level 2
            increment: Experience increment per level
        """
        self.base_exp = base_exp
        self.increment = increment

    def calculate_exp_to_next_level(self, current_level: int) -> int:
        """Calculate experience needed for next level using linear scaling."""
        if current_level <= 0:
            return self.base_exp
        return self.base_exp + (current_level - 1) * self.increment

    def calculate_total_exp_for_level(self, level: int) -> int:
        """Calculate total experience needed to reach a specific level."""
        if level <= 1:
            return 0

        total = 0
        for i in range(1, level):
            total += self.calculate_exp_to_next_level(i)
        return total


class ExponentialExperienceStrategy(ExperienceCalculationStrategy):
    """Exponential experience calculation strategy for challenging progression."""

    def __init__(self, base_exp: int = 100, exponent: float = 2.0):
        """
        Initialize exponential strategy.

        Args:
            base_exp: Base experience for level 2
            exponent: Exponential scaling factor
        """
        self.base_exp = base_exp
        self.exponent = exponent

    def calculate_exp_to_next_level(self, current_level: int) -> int:
        """Calculate experience needed for next level using exponential scaling."""
        if current_level <= 0:
            return self.base_exp
        return int(self.base_exp * (current_level**self.exponent))

    def calculate_total_exp_for_level(self, level: int) -> int:
        """Calculate total experience needed to reach a specific level."""
        if level <= 1:
            return 0

        total = 0
        for i in range(1, level):
            total += self.calculate_exp_to_next_level(i)
        return total


class IExperiencePolicy(ABC):
    """
    Interface for experience-related policies.

    This interface defines policies for leveling conditions,
    experience multipliers, and reward distribution.
    """

    @abstractmethod
    def get_enemy_exp_reward(self, enemy_type: str, enemy_level: int) -> int:
        """
        Get experience reward for defeating an enemy.

        Args:
            enemy_type: Type of enemy defeated
            enemy_level: Level of enemy defeated

        Returns:
            Experience points awarded
        """
        pass

    @abstractmethod
    def get_exp_multiplier(self, player_level: int) -> float:
        """
        Get experience multiplier based on player level.

        Args:
            player_level: Current player level

        Returns:
            Experience multiplier factor
        """
        pass

    @abstractmethod
    def should_level_up(self, current_exp: int, exp_to_next: int) -> bool:
        """
        Check if player should level up.

        Args:
            current_exp: Current experience points
            exp_to_next: Experience needed for next level

        Returns:
            True if player should level up
        """
        pass


class DefaultExperiencePolicy(IExperiencePolicy):
    """Default implementation of experience policy."""

    def __init__(self):
        """Initialize default experience policy."""
        # AI-NOTE : 2025-08-15 적 타입별 경험치 보상 테이블 설정
        # - 이유: 적 종류별로 차별화된 경험치 제공 필요
        # - 요구사항: 기본 적(10), 강화 적(25), 보스(100) 경험치 차등
        # - 히스토리: 게임 밸런스를 위한 초기 설정값
        self._enemy_exp_table = {
            'basic': 10,
            'enhanced': 25,
            'boss': 100,
            'mini_boss': 50,
        }

    def get_enemy_exp_reward(self, enemy_type: str, enemy_level: int) -> int:
        """Get experience reward for defeating an enemy."""
        base_exp = self._enemy_exp_table.get(enemy_type, 10)
        # 적 레벨에 따른 보너스 (레벨당 20% 증가)
        level_multiplier = 1.0 + (enemy_level - 1) * 0.2
        return int(base_exp * level_multiplier)

    def get_exp_multiplier(self, player_level: int) -> float:
        """Get experience multiplier based on player level."""
        # 레벨이 높을수록 경험치 획득량 약간 감소 (난이도 조절)
        if player_level <= 10:
            return 1.0
        elif player_level <= 20:
            return 0.9
        else:
            return 0.8

    def should_level_up(self, current_exp: int, exp_to_next: int) -> bool:
        """Check if player should level up."""
        return current_exp >= exp_to_next


@dataclass
class ExperienceComponent(Component):
    """
    Component that manages player experience and leveling.

    The ExperienceComponent tracks current experience, level,
    and provides configurable experience calculation strategies.
    """

    # AI-NOTE : 2025-08-15 경험치 컴포넌트 설계 - Strategy 패턴 적용
    # - 이유: 다양한 경험치 계산 방식을 런타임에 변경 가능하도록 설계
    # - 요구사항: 현재 경험치, 레벨, 전략 패턴을 통한 유연한 계산 로직
    # - 히스토리: 단순 헬퍼 메서드에서 Strategy 패턴으로 확장 설계
    current_exp: int = 0
    level: int = 1
    total_exp_earned: int = 0  # 총 획득 경험치 (통계용)
    strategy: ExperienceCalculationStrategy = field(
        default_factory=DefaultExperienceStrategy
    )
    policy: IExperiencePolicy = field(default_factory=DefaultExperiencePolicy)

    def __post_init__(self) -> None:
        """Initialize experience component after creation."""
        # 레벨이 1보다 작으면 1로 조정
        if self.level < 1:
            self.level = 1

        # 현재 경험치가 음수면 0으로 조정
        if self.current_exp < 0:
            self.current_exp = 0

        # 총 경험치가 음수면 0으로 조정
        if self.total_exp_earned < 0:
            self.total_exp_earned = 0

        # 총 경험치가 현재 경험치보다 작으면 현재 경험치로 조정
        if self.total_exp_earned < self.current_exp:
            self.total_exp_earned = self.current_exp

    def validate(self) -> bool:
        """
        Validate experience component data.

        Returns:
            True if experience data is valid, False otherwise.
        """
        return (
            self.level >= 1
            and self.current_exp >= 0
            and self.total_exp_earned >= 0
            and self.total_exp_earned >= self.current_exp
            and self.strategy is not None
            and self.policy is not None
        )

    def get_exp_to_next_level(self) -> int:
        """
        Get experience points needed for next level.

        Returns:
            Experience points needed to level up.
        """
        return self.strategy.calculate_exp_to_next_level(self.level)

    def get_exp_progress_ratio(self) -> float:
        """
        Get current experience progress as a ratio.

        Returns:
            Progress ratio between 0.0 and 1.0 towards next level.
        """
        exp_to_next = self.get_exp_to_next_level()
        if exp_to_next <= 0:
            return 0.0
        return min(1.0, self.current_exp / exp_to_next)

    def add_experience(
        self, amount: int, enemy_type: str = 'basic', enemy_level: int = 1
    ) -> tuple[int, bool]:
        """
        Add experience points.

        Args:
            amount: Base experience amount to add
            enemy_type: Type of enemy that provided experience
            enemy_level: Level of enemy that provided experience

        Returns:
            Tuple of (actual_exp_gained, level_up_occurred)
        """
        if amount <= 0:
            return 0, False

        # 정책에 따른 경험치 계산
        policy_exp = self.policy.get_enemy_exp_reward(enemy_type, enemy_level)
        exp_multiplier = self.policy.get_exp_multiplier(self.level)
        actual_exp = int((amount + policy_exp) * exp_multiplier)

        # 경험치 추가
        self.current_exp += actual_exp
        self.total_exp_earned += actual_exp

        # 레벨업 확인
        level_up_occurred = False
        while self.policy.should_level_up(
            self.current_exp, self.get_exp_to_next_level()
        ):
            level_up_occurred = True
            exp_to_next = self.get_exp_to_next_level()
            self.current_exp -= exp_to_next
            self.level += 1

        return actual_exp, level_up_occurred

    def set_strategy(self, strategy: ExperienceCalculationStrategy) -> None:
        """
        Change experience calculation strategy.

        Args:
            strategy: New experience calculation strategy.
        """
        if strategy is not None:
            self.strategy = strategy

    def set_policy(self, policy: IExperiencePolicy) -> None:
        """
        Change experience policy.

        Args:
            policy: New experience policy.
        """
        if policy is not None:
            self.policy = policy

    def get_level_info(self) -> dict[str, int | float]:
        """
        Get comprehensive level information.

        Returns:
            Dictionary containing level, current exp, exp to next, and progress.
        """
        exp_to_next = self.get_exp_to_next_level()
        progress = self.get_exp_progress_ratio()

        return {
            'level': self.level,
            'current_exp': self.current_exp,
            'exp_to_next': exp_to_next,
            'total_exp_earned': self.total_exp_earned,
            'progress_ratio': progress,
        }

    def force_level_up(self, levels: int = 1) -> None:
        """
        Force level up by specified number of levels.

        Args:
            levels: Number of levels to advance (default: 1)
        """
        if levels > 0:
            self.level += levels
            self.current_exp = 0

    def reset_experience(self) -> None:
        """Reset experience to starting values."""
        self.current_exp = 0
        self.level = 1
        self.total_exp_earned = 0

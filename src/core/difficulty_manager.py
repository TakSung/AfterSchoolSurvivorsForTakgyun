"""
DifficultyManager for game difficulty scaling over time.

Manages game difficulty progression by tracking elapsed time and providing
scaling multipliers for enemy stats and spawn mechanics.
"""

from dataclasses import dataclass
from enum import IntEnum


class DifficultyLevel(IntEnum):
    """Difficulty levels for game progression."""

    EASY = 0  # 0-60초
    NORMAL = 1  # 60-180초
    HARD = 2  # 180-360초
    EXTREME = 3  # 360초+

    @property
    def display_name(self) -> str:
        """Get display name for the difficulty level."""
        display_names = {
            DifficultyLevel.EASY: '쉬움',
            DifficultyLevel.NORMAL: '보통',
            DifficultyLevel.HARD: '어려움',
            DifficultyLevel.EXTREME: '극한',
        }
        return display_names[self]

    @property
    def base_multiplier(self) -> float:
        """Get base multiplier for this difficulty level."""
        multipliers = [1.0, 1.2, 1.5, 2.0]  # Index-based fast lookup
        return multipliers[self.value]


@dataclass
class DifficultySettings:
    """Configuration for difficulty scaling parameters."""

    # AI-NOTE : 2025-08-15 난이도 조정 설정 구조 설계
    # - 이유: 게임 진행에 따른 점진적 난이도 증가로 흥미 유지
    # - 요구사항: 시간 기반 난이도 단계, 각 단계별 배율 설정
    # - 히스토리: 고정 난이도에서 동적 난이도 조정 시스템으로 확장

    # 시간 기반 난이도 단계 (초)
    easy_duration: float = 60.0  # 쉬움 단계 지속 시간
    normal_duration: float = 120.0  # 보통 단계 지속 시간
    hard_duration: float = 180.0  # 어려움 단계 지속 시간
    # extreme은 hard_duration 이후 무한정

    # 능력치 스케일링 설정
    health_scale_rate: float = 0.02  # 초당 체력 증가율 (2%)
    speed_scale_rate: float = 0.015  # 초당 속도 증가율 (1.5%)
    spawn_scale_rate: float = 0.05  # 초당 스폰 간격 감소율 (5%)

    # 최대/최소 제한
    max_health_multiplier: float = 3.0  # 최대 체력 배수
    max_speed_multiplier: float = 2.5  # 최대 속도 배수
    min_spawn_multiplier: float = 0.25  # 최소 스폰 간격 배수

    def validate(self) -> bool:
        """Validate difficulty settings."""
        return (
            self.easy_duration > 0
            and self.normal_duration > 0
            and self.hard_duration > 0
            and self.health_scale_rate >= 0
            and self.speed_scale_rate >= 0
            and self.spawn_scale_rate >= 0
            and self.max_health_multiplier >= 1.0
            and self.max_speed_multiplier >= 1.0
            and 0 < self.min_spawn_multiplier <= 1.0
        )


class DifficultyManager:
    """
    Singleton manager for game difficulty progression.

    Tracks game time and calculates difficulty multipliers for various
    game mechanics including enemy stats and spawn rates.
    """

    _instance: 'DifficultyManager | None' = None

    def __init__(self, settings: DifficultySettings | None = None) -> None:
        """
        Initialize the difficulty manager.

        Args:
            settings: Custom difficulty settings, defaults used if None
        """
        if DifficultyManager._instance is not None:
            raise RuntimeError('DifficultyManager is a singleton')

        self._settings = settings or DifficultySettings()
        self._game_time: float = 0.0
        self._current_level: DifficultyLevel = DifficultyLevel.EASY

        # AI-DEV : 설정 유효성 검증으로 런타임 오류 방지
        # - 문제: 잘못된 설정값으로 인한 예상치 못한 게임 동작
        # - 해결책: 초기화 시 설정 검증 및 기본값 사용
        # - 주의사항: 검증 실패 시 안전한 기본값으로 복구
        if not self._settings.validate():
            self._settings = DifficultySettings()

        DifficultyManager._instance = self

    @classmethod
    def get_instance(cls) -> 'DifficultyManager':
        """Get the singleton instance of DifficultyManager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (mainly for testing)."""
        cls._instance = None

    def update(self, delta_time: float) -> None:
        """
        Update game time and difficulty level.

        Args:
            delta_time: Time elapsed since last update in seconds
        """
        self._game_time += delta_time
        self._update_difficulty_level()

    def _update_difficulty_level(self) -> None:
        """Update current difficulty level based on elapsed time."""
        if self._game_time < self._settings.easy_duration:
            self._current_level = DifficultyLevel.EASY
        elif self._game_time < (
            self._settings.easy_duration + self._settings.normal_duration
        ):
            self._current_level = DifficultyLevel.NORMAL
        elif self._game_time < (
            self._settings.easy_duration
            + self._settings.normal_duration
            + self._settings.hard_duration
        ):
            self._current_level = DifficultyLevel.HARD
        else:
            self._current_level = DifficultyLevel.EXTREME

    def get_health_multiplier(self) -> float:
        """
        Get current health multiplier for new enemies.

        Returns:
            Multiplier for enemy health based on game time and difficulty
        """
        # AI-NOTE : 2025-08-15 시간 기반 체력 배율 계산
        # - 이유: 게임 진행에 따른 점진적 적 강화로 도전감 증대
        # - 요구사항: 초당 2% 증가, 최대 300%까지 제한
        # - 히스토리: 고정 체력에서 동적 체력 스케일링으로 변경

        base_multiplier = self._current_level.base_multiplier
        time_multiplier = 1.0 + (
            self._game_time * self._settings.health_scale_rate
        )

        total_multiplier = base_multiplier * time_multiplier
        return min(total_multiplier, self._settings.max_health_multiplier)

    def get_speed_multiplier(self) -> float:
        """
        Get current speed multiplier for new enemies.

        Returns:
            Multiplier for enemy movement speed based on game time and difficulty
        """
        base_multiplier = self._current_level.base_multiplier
        time_multiplier = 1.0 + (
            self._game_time * self._settings.speed_scale_rate
        )

        total_multiplier = base_multiplier * time_multiplier
        return min(total_multiplier, self._settings.max_speed_multiplier)

    def get_spawn_interval_multiplier(self) -> float:
        """
        Get current spawn interval multiplier (lower = faster spawning).

        Returns:
            Multiplier for spawn intervals, decreases over time
        """
        # AI-DEV : 스폰 간격 감소 계산 (빠른 스폰을 위한 역배율)
        # - 문제: 시간이 지날수록 더 빠른 스폰이 필요하지만 배율은 증가 개념
        # - 해결책: 역배율 사용으로 시간 증가 시 간격 감소 효과
        # - 주의사항: 최소값 제한으로 너무 빠른 스폰 방지

        base_divisor = self._current_level.base_multiplier
        time_reduction = self._game_time * self._settings.spawn_scale_rate

        # 스폰 간격은 감소해야 하므로 역수 계산
        multiplier = 1.0 / (base_divisor + time_reduction)
        return max(multiplier, self._settings.min_spawn_multiplier)

    def get_current_level(self) -> DifficultyLevel:
        """Get current difficulty level."""
        return self._current_level

    def get_game_time(self) -> float:
        """Get current game time in seconds."""
        return self._game_time

    def get_difficulty_info(self) -> dict[str, float | str]:
        """
        Get comprehensive difficulty information.

        Returns:
            Dictionary with current difficulty stats
        """
        return {
            'game_time': self._game_time,
            'difficulty_level': self._current_level.display_name,
            'health_multiplier': self.get_health_multiplier(),
            'speed_multiplier': self.get_speed_multiplier(),
            'spawn_interval_multiplier': self.get_spawn_interval_multiplier(),
        }

    def reset(self) -> None:
        """Reset difficulty manager to initial state."""
        self._game_time = 0.0
        self._current_level = DifficultyLevel.EASY

    def set_game_time(self, time: float) -> None:
        """
        Set game time directly (mainly for testing).

        Args:
            time: New game time in seconds
        """
        self._game_time = max(0.0, time)
        self._update_difficulty_level()

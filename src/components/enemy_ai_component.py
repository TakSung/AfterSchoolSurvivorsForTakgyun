"""
EnemyAIComponent for managing enemy AI behavior and state.

This component stores AI-specific properties like behavior type, ranges,
movement speed, and current AI state for enemy entities.
"""

from dataclasses import dataclass
from enum import IntEnum

from ..core.component import Component


class AIState(IntEnum):
    """AI behavior states for enemies."""

    IDLE = 0  # 대기 상태 (순찰 또는 정지)
    CHASE = 1  # 추적 상태 (플레이어 추격)
    ATTACK = 2  # 공격 상태 (공격 범위 내)

    @property
    def display_name(self) -> str:
        """Get the Korean display name for the AI state."""
        display_names = {
            AIState.IDLE: '대기',
            AIState.CHASE: '추적',
            AIState.ATTACK: '공격',
        }
        return display_names[self]


class AIType(IntEnum):
    """Types of AI behavior patterns."""

    AGGRESSIVE = 0  # 공격적 (빠른 추격, 짧은 공격 거리)
    DEFENSIVE = 1  # 방어적 (느린 추격, 긴 공격 거리)
    PATROL = 2  # 순찰형 (정해진 경로 이동)

    @property
    def display_name(self) -> str:
        """Get the Korean display name for the AI type."""
        display_names = {
            AIType.AGGRESSIVE: '공격형',
            AIType.DEFENSIVE: '방어형',
            AIType.PATROL: '순찰형',
        }
        return display_names[self]

    @property
    def chase_range_multiplier(self) -> float:
        """Get the chase range multiplier for this AI type."""
        multipliers = [1.2, 0.8, 1.0]  # Index-based fast lookup
        return multipliers[self.value]

    @property
    def attack_range_multiplier(self) -> float:
        """Get the attack range multiplier for this AI type."""
        multipliers = [0.8, 1.2, 1.0]  # Index-based fast lookup
        return multipliers[self.value]


@dataclass
class EnemyAIComponent(Component):
    """
    Component that stores enemy AI behavior data.

    The EnemyAIComponent manages AI state, ranges, and movement properties
    for enemies that need intelligent behavior in the world coordinate system.
    """

    # AI-NOTE : 2025-08-13 적 AI 컴포넌트 구현 - 월드 좌표 기반 AI 시스템
    # - 이유: 좌표계 확장에 따른 정확한 거리 기반 AI 동작 제공
    # - 요구사항: 상태 기반 AI, 월드 좌표 거리 계산, 유연한 AI 타입 지원
    # - 히스토리: 화면 좌표에서 월드 좌표 기반 AI로 확장

    ai_type: AIType = AIType.AGGRESSIVE
    current_state: AIState = AIState.IDLE
    chase_range: float = 150.0  # 추적 시작 거리 (월드 좌표)
    attack_range: float = 50.0  # 공격 시작 거리 (월드 좌표)
    movement_speed: float = 80.0  # 이동 속도 (픽셀/초)
    state_change_cooldown: float = (
        0.0  # 상태 변경 쿨다운 (프레임 간 떨림 방지)
    )
    last_player_position: tuple[float, float] | None = (
        None  # 마지막 플레이어 위치
    )

    def validate(self) -> bool:
        """
        Validate enemy AI component data.

        Returns:
            True if AI data is valid, False otherwise.
        """
        return (
            isinstance(self.ai_type, AIType)
            and isinstance(self.current_state, AIState)
            and self.chase_range > 0
            and self.attack_range > 0
            and self.movement_speed > 0
            and self.attack_range
            <= self.chase_range  # 공격 범위는 추적 범위보다 작아야 함
            and self.state_change_cooldown >= 0
        )

    def get_effective_chase_range(self) -> float:
        """
        Get the effective chase range with AI type modifier.

        Returns:
            Chase range multiplied by AI type modifier.
        """
        return self.chase_range * self.ai_type.chase_range_multiplier

    def get_effective_attack_range(self) -> float:
        """
        Get the effective attack range with AI type modifier.

        Returns:
            Attack range multiplied by AI type modifier.
        """
        return self.attack_range * self.ai_type.attack_range_multiplier

    def can_change_state(self) -> bool:
        """
        Check if AI state can be changed (cooldown expired).

        Returns:
            True if state can be changed, False if in cooldown.
        """
        return self.state_change_cooldown <= 0.0

    def set_state(
        self, new_state: AIState, cooldown_duration: float = 0.1
    ) -> None:
        """
        Set new AI state with cooldown to prevent rapid switching.

        Args:
            new_state: New AI state to set
            cooldown_duration: Cooldown duration in seconds
        """
        if self.current_state != new_state:
            self.current_state = new_state
            self.state_change_cooldown = cooldown_duration

    def update_cooldown(self, delta_time: float) -> None:
        """
        Update state change cooldown.

        Args:
            delta_time: Time elapsed since last update in seconds.
        """
        if self.state_change_cooldown > 0:
            self.state_change_cooldown = max(
                0.0, self.state_change_cooldown - delta_time
            )

    def update_last_player_position(
        self, position: tuple[float, float]
    ) -> None:
        """
        Update the last known player position.

        Args:
            position: Player's world coordinates (x, y).
        """
        self.last_player_position = position

    def get_distance_to_player(
        self, enemy_pos: tuple[float, float], player_pos: tuple[float, float]
    ) -> float:
        """
        Calculate distance to player in world coordinates.

        Args:
            enemy_pos: Enemy's world position (x, y)
            player_pos: Player's world position (x, y)

        Returns:
            Distance to player in world coordinate units.
        """
        # AI-DEV : 성능 최적화를 위한 Vector2 import 지연
        # - 문제: 모든 컴포넌트 생성 시 Vector2 import 비용 발생
        # - 해결책: 실제 사용 시점에 import하여 초기화 비용 절약
        # - 주의사항: 빈번한 호출 시 import 비용 고려 필요
        from ..utils.vector2 import Vector2

        enemy_vec = Vector2(enemy_pos[0], enemy_pos[1])
        player_vec = Vector2(player_pos[0], player_pos[1])
        return (enemy_vec - player_vec).magnitude

    def should_chase(self, distance_to_player: float) -> bool:
        """
        Determine if enemy should chase the player.

        Args:
            distance_to_player: Current distance to player

        Returns:
            True if enemy should chase, False otherwise.
        """
        effective_chase_range = self.get_effective_chase_range()
        return distance_to_player <= effective_chase_range

    def should_attack(self, distance_to_player: float) -> bool:
        """
        Determine if enemy should attack the player.

        Args:
            distance_to_player: Current distance to player

        Returns:
            True if enemy should attack, False otherwise.
        """
        effective_attack_range = self.get_effective_attack_range()
        return distance_to_player <= effective_attack_range

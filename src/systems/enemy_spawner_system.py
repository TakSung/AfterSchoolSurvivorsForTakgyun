"""
EnemySpawnerSystem for managing enemy spawn mechanics.

This system handles time-based enemy spawning at screen edges with
configurable spawn rates, maximum enemy limits, and difficulty scaling.

리팩토링: 새로운 IEnemyManager 인터페이스를 사용하여 적 생성을 위임합니다.
"""

import random

from ..core.interfaces.i_spawner import ISpawner
from ..core.system import System
from ..dto.spawn_result import SpawnResult
from ..interfaces import ICoordinateManager, IDifficultyManager, IEnemyManager
from ..utils.vector2 import Vector2

# TYPE_CHECKING 블록 정리됨 - 더 이상 EntityManager import 불필요

# AI-NOTE : 컴포넌트 import 제거 - IEnemyManager가 처리


class EnemySpawnerSystem(System, ISpawner):
    """
    System that spawns enemies at screen edges with configurable rates.

    Implements ISpawner interface for polymorphic spawner management.
    Focuses on spawn timing and position calculation, delegating
    entity creation to EntityManager.

    The EnemySpawnerSystem manages:
    - Time-based enemy spawning with configurable intervals
    - Spawn position calculation at screen edges
    - Spawn condition evaluation (timing, limits)
    """

    def __init__(
        self,
        priority: int = 5,
        enemy_manager: IEnemyManager | None = None,
        coordinate_manager: ICoordinateManager | None = None,
        difficulty_manager: IDifficultyManager | None = None,
    ) -> None:
        """
        Initialize the EnemySpawnerSystem.

        Args:
            priority: System execution priority (5 = early in frame)
            enemy_manager: Enemy management interface (의존성 주입)
            coordinate_manager: Coordinate transformation interface (의존성 주입)
            difficulty_manager: Difficulty scaling interface (의존성 주입)
        """
        super().__init__(priority=priority)

        # AI-NOTE : 2025-08-17 의존성 주입을 통한 새로운 Manager 패턴 적용
        # - 이유: IEnemyManager 인터페이스를 통해 적 생성 로직 분리
        # - 요구사항: 테스트 용이성과 확장성을 위한 인터페이스 기반 설계
        # - 히스토리: 기존 EntityManager 직접 사용에서 인터페이스 패턴으로 변경

        # 스폰 관련 설정
        self._base_spawn_interval: float = 2.0  # 기본 스폰 간격 (초)
        self._current_spawn_timer: float = 0.0  # 현재 스폰 타이머
        self._max_enemies: int = 20  # 최대 적 수
        self._spawn_distance_from_edge: float = (
            50.0  # 화면 가장자리로부터 스폰 거리
        )

        # 난이도 조정 관련
        self._game_time: float = 0.0  # 게임 경과 시간
        self._difficulty_scale_interval: float = (
            30.0  # 난이도 증가 간격 (30초)
        )

        # 매니저 인터페이스들 (의존성 주입)
        self._enemy_manager = enemy_manager
        self._coordinate_manager = coordinate_manager
        self._difficulty_manager = difficulty_manager

    def initialize(self) -> None:
        """Initialize the enemy spawner system."""
        super().initialize()

        # AI-DEV : 매니저 인터페이스 지연 초기화 (백워드 호환성)
        # - 이유: 의존성 주입이 없는 경우 기본 구현체 사용
        # - 해결책: 주입된 매니저가 없으면 기본 싱글톤 인스턴스 사용
        # - 주의사항: 새로운 코드에서는 생성자 주입을 권장

        if self._coordinate_manager is None:
            # 기존 호환성을 위한 지연 초기화
            from ..core.coordinate_manager import CoordinateManager

            self._coordinate_manager = CoordinateManager.get_instance()

        if self._difficulty_manager is None:
            # 기존 호환성을 위한 지연 초기화
            from ..core.difficulty_manager import DifficultyManager

            self._difficulty_manager = DifficultyManager.get_instance()

        if self._enemy_manager is None:
            # 기존 호환성을 위해 기본 구현체 생성 (EntityManager 필요)
            from ..managers import create_enemy_manager, create_entity_manager

            entity_manager = create_entity_manager()
            self._enemy_manager = create_enemy_manager(
                entity_manager,
                self._coordinate_manager,
                self._difficulty_manager,
            )

    def get_required_components(self) -> list[type]:
        """
        Get required component types (spawner doesn't require entities).

        Returns:
            Empty list as spawner creates its own entities.
        """
        return []

    def update(self, delta_time: float) -> None:
        """
        Update enemy spawner system logic.

        Args:
            delta_time: Time elapsed since last update in seconds
        """
        if not self.enabled:
            return

        # 게임 경과 시간 업데이트
        self._game_time += delta_time

        # 난이도 관리자 업데이트
        if self._difficulty_manager:
            self._difficulty_manager.update(delta_time)

        # 스폰 타이머 업데이트
        self._current_spawn_timer += delta_time

        # 스폰 실행 - IEnemyManager를 통해 위임
        if self.can_spawn():
            # 적 수 체크를 IEnemyManager에 위임
            if self._enemy_manager:
                current_enemy_count = self._enemy_manager.get_enemy_count()
                if current_enemy_count < self._max_enemies:
                    spawn_result = self.spawn()
                    if spawn_result:
                        # 엔티티 생성을 IEnemyManager에 위임
                        self._enemy_manager.create_enemy_entity(spawn_result)
                        self._reset_spawn_timer()

    # ISpawner interface implementation
    def can_spawn(self) -> bool:
        """
        Determine if spawning is currently possible.

        Checks only timing conditions, enemy count is checked in update().

        Returns:
            True if spawn timing conditions are met, False otherwise.
        """
        return self._is_spawn_time_ready()

    def spawn(self) -> SpawnResult | None:
        """
        Generate spawn information for enemy creation.

        Creates spawn data without actually creating entities,
        delegating entity creation to EntityManager.

        Returns:
            SpawnResult containing spawn information, or None if spawn failed.
        """
        # AI-NOTE : 2025-01-16 SpawnResult DTO를 통한 스폰 정보 생성
        # - 이유: 스폰 로직과 엔티티 생성 로직의 책임 분리
        # - 요구사항: 위치 계산과 난이도 정보를 DTO로 전달
        # - 비즈니스 가치: 스포너의 단일 책임 원칙 준수

        # 1. 스폰 위치 계산
        spawn_pos = self._calculate_spawn_position()
        if not spawn_pos:
            return None

        # 2. 현재 스폰 간격 계산 (난이도 반영)
        current_interval = self._get_current_spawn_interval()
        difficulty_scale = self._base_spawn_interval / max(
            current_interval, 0.1
        )

        # 3. SpawnResult DTO 생성
        return SpawnResult(
            spawn_position=spawn_pos,
            entity_type='enemy',
            difficulty_scale=difficulty_scale,
            additional_data={
                'ai_type_options': ['AGGRESSIVE', 'DEFENSIVE', 'PATROL'],
                'base_health': 100,
                'base_speed': 80.0,
                'spawn_time': self._game_time,
            },
        )

    def get_spawn_info(self) -> dict[str, str]:
        """
        Get current spawner status information.

        Returns:
            Dictionary with spawner status where all values are strings.
        """
        current_interval = self._get_current_spawn_interval()
        return {
            'base_spawn_interval': str(self._base_spawn_interval),
            'current_spawn_interval': str(round(current_interval, 2)),
            'current_spawn_timer': str(round(self._current_spawn_timer, 2)),
            'max_enemies': str(self._max_enemies),
            'game_time': str(round(self._game_time, 1)),
            'spawn_distance': str(self._spawn_distance_from_edge),
            'spawner_type': 'enemy',
        }

    def _is_spawn_time_ready(self) -> bool:
        """
        Check if enough time has passed for spawning.

        Returns:
            True if spawn timer has exceeded current spawn interval.
        """
        current_spawn_interval = self._get_current_spawn_interval()
        return self._current_spawn_timer >= current_spawn_interval

    def _get_current_spawn_interval(self) -> float:
        """
        Calculate current spawn interval based on difficulty scaling.

        Returns:
            Current spawn interval in seconds.
        """
        # AI-NOTE : 2025-08-15 난이도 관리자 기반 스폰 간격 계산
        # - 이유: 중앙집중식 난이도 관리로 일관된 게임 밸런스 제공
        # - 요구사항: DifficultyManager에서 제공하는 스폰 간격 배율 사용
        # - 히스토리: 로컬 난이도 계산에서 중앙 관리 방식으로 변경

        if self._difficulty_manager:
            multiplier = self._difficulty_manager.get_spawn_rate_multiplier()
            return self._base_spawn_interval * multiplier
        else:
            # 난이도 관리자가 없을 때 기본 로직 (fallback)
            difficulty_level = (
                self._game_time / self._difficulty_scale_interval
            )
            difficulty_multiplier = max(0.25, 1.0 - (difficulty_level * 0.05))
            return max(0.5, self._base_spawn_interval * difficulty_multiplier)

    def _reset_spawn_timer(self) -> None:
        """Reset the spawn timer to zero."""
        self._current_spawn_timer = 0.0

    # AI-NOTE : 2025-08-17 레거시 메서드 제거 완료
    # - 이유: IEnemyManager 인터페이스를 통해 적 생성 로직 완전 분리
    # - 결과: 더 깔끔하고 테스트 가능한 코드 구조

    def _calculate_spawn_position(self) -> tuple[float, float] | None:
        """
        Calculate a random spawn position at screen edges.

        Returns:
            World coordinates (x, y) for spawn position, or None if failed.
        """
        if not self._coordinate_manager:
            return None

        # AI-DEV : 화면 가장자리 스폰 위치 계산
        # - 문제: 좌표 변환 시스템을 활용한 정확한 화면 경계 계산 필요
        # - 해결책: 화면 경계를 월드 좌표로 변환하여 스폰 위치 결정
        # - 주의사항: 카메라 위치 변화에 따른 동적 스폰 위치 계산

        # 화면 크기 가정 (실제로는 설정에서 가져와야 함)
        screen_width, screen_height = 1024, 768

        # 화면 경계의 월드 좌표 계산
        screen_corners = [
            (0, 0),  # 좌상단
            (screen_width, 0),  # 우상단
            (screen_width, screen_height),  # 우하단
            (0, screen_height),  # 좌하단
        ]

        world_corners = []
        for screen_pos in screen_corners:
            world_pos = self._coordinate_manager.screen_to_world(
                Vector2(screen_pos[0], screen_pos[1])
            )
            world_corners.append((world_pos.x, world_pos.y))

        # 화면 경계 영역 계산
        min_x = min(corner[0] for corner in world_corners)
        max_x = max(corner[0] for corner in world_corners)
        min_y = min(corner[1] for corner in world_corners)
        max_y = max(corner[1] for corner in world_corners)

        # 스폰 거리만큼 확장
        spawn_min_x = min_x - self._spawn_distance_from_edge
        spawn_max_x = max_x + self._spawn_distance_from_edge
        spawn_min_y = min_y - self._spawn_distance_from_edge
        spawn_max_y = max_y + self._spawn_distance_from_edge

        # 4개 가장자리 중 하나를 랜덤 선택
        edge = random.randint(0, 3)

        if edge == 0:  # 위쪽 가장자리
            x = random.uniform(spawn_min_x, spawn_max_x)
            y = spawn_min_y
        elif edge == 1:  # 오른쪽 가장자리
            x = spawn_max_x
            y = random.uniform(spawn_min_y, spawn_max_y)
        elif edge == 2:  # 아래쪽 가장자리
            x = random.uniform(spawn_min_x, spawn_max_x)
            y = spawn_max_y
        else:  # 왼쪽 가장자리
            x = spawn_min_x
            y = random.uniform(spawn_min_y, spawn_max_y)

        return (x, y)

    # Legacy component addition methods - now handled by EnemyManager
    # These methods have been moved to EnemyManager for better separation of concerns
    # They remain here temporarily for backward compatibility

    def set_spawn_interval(self, interval: float) -> None:
        """
        Set the base spawn interval.

        Args:
            interval: New base spawn interval in seconds
        """
        if interval > 0:
            self._base_spawn_interval = interval

    def set_max_enemies(self, max_count: int) -> None:
        """
        Set the maximum number of enemies.

        Args:
            max_count: New maximum enemy count
        """
        if max_count > 0:
            self._max_enemies = max_count

    # Legacy method - use ISpawner.get_spawn_info() instead
    def get_spawn_system_info(self) -> dict[str, float | int]:
        """
        Legacy method - use get_spawn_info() for ISpawner interface compatibility.

        Returns:
            Dictionary with spawn system stats (numeric values).
        """
        return {
            'base_spawn_interval': self._base_spawn_interval,
            'current_spawn_interval': self._get_current_spawn_interval(),
            'spawn_timer': self._current_spawn_timer,
            'max_enemies': self._max_enemies,
            'game_time': self._game_time,
        }

    def get_difficulty_info(self) -> dict[str, float | str]:
        """
        Get current difficulty information.

        Returns:
            Dictionary with current difficulty stats, empty if manager unavailable
        """
        if self._difficulty_manager:
            return self._difficulty_manager.get_difficulty_info()
        else:
            return {}

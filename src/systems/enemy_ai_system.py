"""
EnemyAISystem for managing enemy AI behavior using world coordinates.

This system processes enemy entities with AI components to handle state-based
behavior including idle, chase, and attack states based on world coordinates.
"""

from typing import TYPE_CHECKING, Optional

from ..components.enemy_ai_component import AIState, EnemyAIComponent
from ..components.enemy_component import EnemyComponent
from ..components.player_component import PlayerComponent
from ..components.position_component import PositionComponent
from ..core.coordinate_manager import CoordinateManager
from ..core.system import System

if TYPE_CHECKING:
    from ..core.entity import Entity
    from ..core.entity_manager import EntityManager


class EnemyAISystem(System):
    """
    System that manages enemy AI behavior using world coordinates.

    The EnemyAISystem processes entities with EnemyAIComponent to:
    - Calculate distances in world coordinate space
    - Manage AI state transitions (IDLE -> CHASE -> ATTACK)
    - Handle enemy movement towards player
    - Update AI behavior based on world coordinate ranges
    """

    def __init__(self, priority: int = 12) -> None:
        """
        Initialize the EnemyAISystem.

        Args:
            priority: System execution priority (12 = after player)
        """
        super().__init__(priority=priority)

        # AI-NOTE : 2025-08-13 월드 좌표 기반 적 AI 시스템
        # - 이유: 좌표계 확장에 따른 정확한 거리 기반 AI 동작 제공
        # - 요구사항: 월드 좌표 거리 계산, 상태 기반 AI, FPS 독립적 동작
        # - 히스토리: AutoAttackSystem 패턴을 따라 일관된 아키텍처 구현

        self._coordinate_manager: CoordinateManager | None = None

    def initialize(self) -> None:
        """Initialize the enemy AI system."""
        super().initialize()

        # AI-DEV : 좌표 관리자 지연 초기화
        # - 문제: 싱글톤 초기화 순서 이슈 방지
        # - 해결책: 시스템 초기화 시점에 좌표 관리자 설정
        # - 주의사항: AutoAttackSystem과 동일한 패턴 사용
        self._coordinate_manager = CoordinateManager.get_instance()

    def get_required_components(self) -> list[type]:
        """
        Get required component types for enemy AI entities.

        Returns:
            List of required component types.
        """
        return [EnemyAIComponent, EnemyComponent, PositionComponent]

    def update(
        self, delta_time: float
    ) -> None:
        """
        Update enemy AI system logic.

        Args:
            delta_time: Time elapsed since last update in seconds
        """
        if not self.enabled:
            return

        # 플레이어 엔티티 찾기
        player_entity = self._find_player()
        if not player_entity:
            return  # 플레이어가 없으면 AI 동작 없음

        player_pos = self._entity_manager.get_component(
            player_entity, PositionComponent
        )
        if not player_pos:
            return

        player_world_pos = (player_pos.x, player_pos.y)

        # 모든 적 AI 엔티티 처리
        enemy_entities = self.filter_required_entities()
        for enemy in enemy_entities:
            self._process_enemy_ai(
                enemy, player_world_pos, delta_time
            )

    def _find_player(self) -> Optional['Entity']:
        """
        Find the player entity in the game world.

        Returns:
            Player entity if found, None otherwise.
        """
        # AI-DEV : 플레이어 엔티티 탐색 최적화
        # - 문제: 매 프레임 플레이어 엔티티 탐색으로 인한 성능 비용
        # - 해결책: PlayerComponent를 가진 엔티티 직접 필터링
        # - 주의사항: 플레이어가 여러 명일 경우 첫 번째만 반환

        player_entities = self._entity_manager.get_entities_with_components(
            PlayerComponent, PositionComponent
        )
        return player_entities[0] if player_entities else None

    def _process_enemy_ai(
        self,
        enemy_entity: 'Entity',
        player_world_pos: tuple[float, float],
        delta_time: float,
    ) -> None:
        """
        Process AI behavior for a single enemy entity.

        Args:
            enemy_entity: Enemy entity to process
            player_world_pos: Player's world position (x, y)
            delta_time: Time elapsed since last update in seconds
        """
        ai_component = self._entity_manager.get_component(
            enemy_entity, EnemyAIComponent
        )
        enemy_pos = self._entity_manager.get_component(
            enemy_entity, PositionComponent
        )

        if not ai_component or not enemy_pos:
            return

        # AI-NOTE : 2025-08-13 월드 좌표 기반 거리 계산 및 상태 전환
        # - 이유: 좌표계 확장에 따른 정확한 AI 동작 보장
        # - 요구사항: chase_range, attack_range 기반 상태 전환
        # - 히스토리: AutoAttackSystem의 거리 계산 패턴 활용

        # 쿨다운 업데이트
        ai_component.update_cooldown(delta_time)

        # 월드 좌표에서 플레이어와의 거리 계산
        enemy_world_pos = (enemy_pos.x, enemy_pos.y)
        distance_to_player = ai_component.get_distance_to_player(
            enemy_world_pos, player_world_pos
        )

        # 플레이어 위치 업데이트
        ai_component.update_last_player_position(player_world_pos)

        # AI 상태 전환 로직
        if ai_component.can_change_state():
            self._update_ai_state(ai_component, distance_to_player)

        # 현재 상태에 따른 동작 처리
        if ai_component.current_state == AIState.CHASE:
            self._handle_chase_behavior(
                enemy_entity, player_world_pos, delta_time
            )
        elif ai_component.current_state == AIState.ATTACK:
            self._handle_attack_behavior(
                enemy_entity, player_world_pos, delta_time
            )
        # IDLE 상태는 특별한 동작 없음 (순찰 로직은 향후 추가 가능)

    def _update_ai_state(
        self, ai_component: EnemyAIComponent, distance_to_player: float
    ) -> None:
        """
        Update AI state based on distance to player.

        Args:
            ai_component: Enemy AI component to update
            distance_to_player: Current distance to player
        """
        # AI-DEV : 상태 전환 우선순위 로직
        # - 문제: 여러 조건이 동시에 만족될 때 우선순위 필요
        # - 해결책: 공격 -> 추적 -> 대기 순으로 우선순위 설정
        # - 주의사항: 상태 변경 쿨다운으로 떨림 현상 방지

        if ai_component.should_attack(distance_to_player):
            ai_component.set_state(AIState.ATTACK)
        elif ai_component.should_chase(distance_to_player):
            ai_component.set_state(AIState.CHASE)
        else:
            ai_component.set_state(AIState.IDLE)

    def _handle_chase_behavior(
        self,
        enemy_entity: 'Entity',
        player_world_pos: tuple[float, float],
        delta_time: float,
    ) -> None:
        """
        Handle chase behavior - move enemy towards player.

        Args:
            enemy_entity: Enemy entity to move
            player_world_pos: Player's world position (x, y)
            delta_time: Time elapsed since last update
        """
        # AI-NOTE : 2025-08-14 월드 좌표 기반 적 추적 이동 구현
        # - 이유: 플레이어 추적 상태에서 적이 플레이어 방향으로 이동 구현
        # - 요구사항: 월드 좌표 방향 벡터 계산, Vector2 정규화, FPS 독립적 이동
        # - 히스토리: TODO에서 실제 추적 로직으로 구현

        ai_component = self._entity_manager.get_component(
            enemy_entity, EnemyAIComponent
        )
        enemy_pos = self._entity_manager.get_component(
            enemy_entity, PositionComponent
        )

        if not ai_component or not enemy_pos:
            return

        # AI-DEV : Vector2를 사용한 월드 좌표 방향 벡터 계산
        # - 문제: tuple 좌표에서 벡터 연산을 위한 변환 필요
        # - 해결책: Vector2 클래스 활용하여 정확한 방향 계산과 정규화
        # - 주의사항: import 지연으로 초기화 비용 절약
        from ..utils.vector2 import Vector2

        # 현재 적 위치와 플레이어 위치를 Vector2로 변환
        enemy_world_pos = Vector2(enemy_pos.x, enemy_pos.y)
        player_vec = Vector2(player_world_pos[0], player_world_pos[1])

        # 플레이어 방향 벡터 계산
        direction_vector = player_vec - enemy_world_pos

        # AI-DEV : 제로 벡터 예외 처리
        # - 문제: 플레이어와 적이 정확히 같은 위치에 있을 때 normalize() 실패
        # - 해결책: magnitude가 0인 경우 이동하지 않고 early return
        # - 주의사항: 부동소수점 오차 고려하여 임계값 사용
        if direction_vector.magnitude < 1e-6:
            return  # 플레이어와 너무 가까우면 이동하지 않음

        # 방향 벡터를 단위 벡터로 정규화
        normalized_direction = direction_vector.normalize()

        # AI 컴포넌트의 이동 속도와 delta_time을 곱하여 이동 거리 계산
        movement_distance = ai_component.movement_speed * delta_time

        # 이동 벡터 계산 (정규화된 방향 * 이동 거리)
        movement_vector = normalized_direction * movement_distance

        # 적의 위치 업데이트 (월드 좌표에서 직접 수정)
        enemy_pos.x += movement_vector.x
        enemy_pos.y += movement_vector.y

    def _handle_attack_behavior(
        self,
        enemy_entity: 'Entity',
        player_world_pos: tuple[float, float],
        delta_time: float,
    ) -> None:
        """
        Handle attack behavior - enemy attacks player.

        Args:
            enemy_entity: Enemy entity attacking
            player_world_pos: Player's world position (x, y)
            delta_time: Time elapsed since last update
        """
        # TODO: 향후 공격 시스템과 연동
        # 1. 공격 쿨다운 관리
        # 2. 공격 애니메이션 트리거
        # 3. 플레이어에게 데미지 적용
        pass

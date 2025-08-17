"""
Test module for EnemyAISystem chase behavior implementation.

Tests world coordinate-based direction vector calculation, normalization,
and chase movement behavior for enemy AI entities.
"""

from unittest.mock import MagicMock

import pytest

from src.components.enemy_ai_component import AIState, AIType, EnemyAIComponent
from src.components.position_component import PositionComponent
from src.core.component import Component
from src.core.coordinate_manager import CoordinateManager
from src.core.entity import Entity
from src.core.entity_manager import EntityManager
from src.systems.enemy_ai_system import EnemyAISystem
from src.utils.vector2 import Vector2


class TestEnemyAIChaseBehavior:
    """Test cases for EnemyAISystem chase behavior."""

    @pytest.fixture
    def mock_entity_manager(self) -> EntityManager:
        """Create a mock entity manager for testing."""
        return MagicMock(spec=EntityManager)

    @pytest.fixture
    def mock_coordinate_manager(self) -> CoordinateManager:
        """Create a mock coordinate manager for testing."""
        return MagicMock(spec=CoordinateManager)

    @pytest.fixture
    def enemy_ai_system(
        self, mock_coordinate_manager: CoordinateManager
    ) -> EnemyAISystem:
        """Create an EnemyAISystem instance for testing."""
        # 싱글톤 인스턴스를 테스트용 mock으로 교체
        CoordinateManager.set_instance(mock_coordinate_manager)

        system = EnemyAISystem(priority=12)
        system.initialize()
        return system

    @pytest.fixture
    def chase_enemy_setup(
        self, mock_entity_manager: EntityManager
    ) -> tuple[Entity, EnemyAIComponent, PositionComponent]:
        """Create a chase-ready enemy entity setup."""
        # 적 엔티티 생성
        enemy_entity = MagicMock(spec=Entity)
        enemy_entity.entity_id = 'enemy_chase_1'

        # 추적 상태의 AI 컴포넌트 생성
        ai_component = EnemyAIComponent(
            ai_type=AIType.AGGRESSIVE,
            current_state=AIState.CHASE,
            movement_speed=100.0,  # 100 픽셀/초
            chase_range=150.0,
            attack_range=30.0,
        )

        # 적 위치 컴포넌트 생성
        enemy_pos = PositionComponent(x=200.0, y=200.0)

        # Mock 엔티티 매니저 설정
        def mock_get_component(
            entity: Entity, component_type: type
        ) -> Component | None:
            if component_type == EnemyAIComponent:
                return ai_component
            elif component_type == PositionComponent:
                return enemy_pos
            return None

        mock_entity_manager.get_component.side_effect = mock_get_component

        return enemy_entity, ai_component, enemy_pos

    def test_월드_좌표_방향_벡터_계산_정확성_검증_성공_시나리오(
        self,
        enemy_ai_system: EnemyAISystem,
        chase_enemy_setup: tuple[Entity, EnemyAIComponent, PositionComponent],
        mock_entity_manager: EntityManager,
    ) -> None:
        """1. 월드 좌표 방향 벡터 계산 정확성 검증 (성공 시나리오)

        목적: 적과 플레이어 사이의 방향 벡터 계산 정확성 검증
        테스트할 범위: _handle_chase_behavior의 방향 벡터 계산
        커버하는 함수 및 데이터: Vector2 변환, 방향 벡터 계산
        기대되는 안정성: 정확한 월드 좌표 기반 방향 계산
        """
        # Given - 적이 (200, 200) 위치에 있고 플레이어가 (300, 250)에 있음
        enemy_entity, ai_component, enemy_pos = chase_enemy_setup
        player_world_pos = (300.0, 250.0)  # 플레이어 위치
        delta_time = 1.0  # 1초 (계산 편의)

        # When - 추적 행동 처리
        enemy_ai_system.set_entity_manager(mock_entity_manager)
        enemy_ai_system._handle_chase_behavior(
            enemy_entity, player_world_pos, delta_time
        )

        # Then - 예상 방향 벡터 계산
        expected_direction = Vector2(300.0 - 200.0, 250.0 - 200.0)  # (100, 50)
        # √(100² + 50²) ≈ 111.8 (distance unused in test)
        expected_normalized = expected_direction.normalize()

        # 이동 거리 계산: movement_speed(100) * delta_time(1) = 100
        expected_movement = expected_normalized * 100.0

        # 예상 최종 위치
        expected_final_x = 200.0 + expected_movement.x
        expected_final_y = 200.0 + expected_movement.y

        # 실제 위치와 비교 (부동소수점 오차 고려)
        assert abs(enemy_pos.x - expected_final_x) < 0.001, (
            f'X 위치 오류: 예상 {expected_final_x}, 실제 {enemy_pos.x}'
        )
        assert abs(enemy_pos.y - expected_final_y) < 0.001, (
            f'Y 위치 오류: 예상 {expected_final_y}, 실제 {enemy_pos.y}'
        )

        # 방향성 검증 - 플레이어 쪽으로 이동했는지 확인
        movement_x = enemy_pos.x - 200.0
        movement_y = enemy_pos.y - 200.0
        assert movement_x > 0, (
            '플레이어가 오른쪽에 있으므로 X 방향으로 이동해야 함'
        )
        assert movement_y > 0, (
            '플레이어가 아래쪽에 있으므로 Y 방향으로 이동해야 함'
        )

    def test_Vector2_정규화_단위_벡터_생성_검증_성공_시나리오(
        self,
        enemy_ai_system: EnemyAISystem,
        chase_enemy_setup: tuple[Entity, EnemyAIComponent, PositionComponent],
        mock_entity_manager: EntityManager,
    ) -> None:
        """2. Vector2 정규화 단위 벡터 생성 검증 (성공 시나리오)

        목적: Vector2.normalize() 메서드의 정확한 단위 벡터 생성 검증
        테스트할 범위: 정규화된 방향 벡터의 크기가 1.0인지 확인
        커버하는 함수 및 데이터: Vector2.normalize(), magnitude 계산
        기대되는 안정성: 일관된 단위 벡터 생성
        """
        # Given - 다양한 방향에서의 플레이어 위치 테스트
        enemy_entity, ai_component, enemy_pos = chase_enemy_setup
        delta_time = 0.1  # 작은 시간 간격으로 테스트

        test_cases = [
            (300.0, 200.0),  # 오른쪽
            (200.0, 100.0),  # 위쪽
            (100.0, 200.0),  # 왼쪽
            (200.0, 300.0),  # 아래쪽
            (350.0, 350.0),  # 대각선 (오른쪽 아래)
            (50.0, 50.0),  # 대각선 (왼쪽 위)
        ]

        for player_x, player_y in test_cases:
            # 적 위치 초기화
            enemy_pos.x = 200.0
            enemy_pos.y = 200.0
            initial_pos = (enemy_pos.x, enemy_pos.y)

            # When - 추적 행동 처리
            enemy_ai_system.set_entity_manager(mock_entity_manager)
            enemy_ai_system._handle_chase_behavior(
                enemy_entity,
                (player_x, player_y),
                delta_time,
            )

            # Then - 이동 벡터 계산
            movement_x = enemy_pos.x - initial_pos[0]
            movement_y = enemy_pos.y - initial_pos[1]
            movement_magnitude = (movement_x**2 + movement_y**2) ** 0.5

            # 예상 이동 거리: movement_speed * delta_time = 100 * 0.1 = 10
            expected_movement_distance = (
                ai_component.movement_speed * delta_time
            )

            # 이동 거리가 예상과 일치하는지 확인 (정규화된 벡터 사용으로 인해)
            assert (
                abs(movement_magnitude - expected_movement_distance) < 0.001
            ), (
                f'플레이어 위치 ({player_x}, {player_y})에서 '
                f'이동 거리 오류: 예상 {expected_movement_distance}, '
                f'실제 {movement_magnitude}'
            )

    def test_FPS_독립적_이동_처리_검증_성공_시나리오(
        self,
        enemy_ai_system: EnemyAISystem,
        chase_enemy_setup: tuple[Entity, EnemyAIComponent, PositionComponent],
        mock_entity_manager: EntityManager,
    ) -> None:
        """3. FPS 독립적 이동 처리 검증 (성공 시나리오)

        목적: delta_time 기반 이동 계산의 FPS 독립성 검증
        테스트할 범위: 서로 다른 delta_time에서 일관된 속도 유지
        커버하는 함수 및 데이터: movement_speed * delta_time 계산
        기대되는 안정성: 프레임률과 무관한 일정한 이동 속도
        """
        # Given - 동일한 시나리오에서 서로 다른 delta_time 테스트
        enemy_entity, ai_component, enemy_pos = chase_enemy_setup
        player_world_pos = (300.0, 200.0)  # 오른쪽으로 100픽셀 떨어진 위치

        # 다양한 프레임률 시뮬레이션 (60fps, 30fps, 120fps)
        delta_time_cases = [
            1.0 / 60.0,  # 60 FPS: ~0.0167초
            1.0 / 30.0,  # 30 FPS: ~0.0333초
            1.0 / 120.0,  # 120 FPS: ~0.0083초
        ]

        for delta_time in delta_time_cases:
            # 적 위치 초기화
            enemy_pos.x = 200.0
            enemy_pos.y = 200.0
            initial_x = enemy_pos.x

            # When - 추적 행동 처리
            enemy_ai_system.set_entity_manager(mock_entity_manager)
            enemy_ai_system._handle_chase_behavior(
                enemy_entity, player_world_pos, delta_time
            )

            # Then - 이동 거리가 delta_time에 비례하는지 확인
            actual_movement_x = enemy_pos.x - initial_x
            expected_movement_x = ai_component.movement_speed * delta_time

            # 방향이 정규화되었으므로 X 방향 이동도 정확히 계산됨
            # 플레이어가 오른쪽에 있으므로 X 방향으로만 이동
            assert abs(actual_movement_x - expected_movement_x) < 0.001, (
                f'Delta time {delta_time}에서 X 이동 오류: '
                f'예상 {expected_movement_x}, 실제 {actual_movement_x}'
            )

            # Y 방향은 이동하지 않아야 함 (같은 Y 좌표)
            assert abs(enemy_pos.y - 200.0) < 0.001, (
                f'Y 방향 이동 오류: 같은 Y 좌표에서 Y 이동 발생 {enemy_pos.y}'
            )

    def test_제로_벡터_예외_처리_안정성_검증_성공_시나리오(
        self,
        enemy_ai_system: EnemyAISystem,
        chase_enemy_setup: tuple[Entity, EnemyAIComponent, PositionComponent],
        mock_entity_manager: EntityManager,
    ) -> None:
        """4. 제로 벡터 예외 처리 안정성 검증 (성공 시나리오)

        목적: 플레이어와 적이 같은 위치에 있을 때 안전한 처리 검증
        테스트할 범위: magnitude < 1e-6 조건에서 early return
        커버하는 함수 및 데이터: 제로 벡터 감지, normalize() 예외 방지
        기대되는 안정성: 크래시 없는 안전한 예외 처리
        """
        # Given - 적과 플레이어가 같은 위치에 있는 상황
        enemy_entity, ai_component, enemy_pos = chase_enemy_setup
        enemy_pos.x = 250.0
        enemy_pos.y = 150.0

        # 플레이어도 같은 위치
        player_world_pos = (250.0, 150.0)
        delta_time = 0.1

        initial_pos = (enemy_pos.x, enemy_pos.y)

        # When - 추적 행동 처리
        enemy_ai_system.set_entity_manager(mock_entity_manager)
        enemy_ai_system._handle_chase_behavior(
            enemy_entity, player_world_pos, delta_time
        )

        # Then - 위치가 변경되지 않아야 함
        assert enemy_pos.x == initial_pos[0], (
            f'제로 벡터에서 X 이동 발생: {initial_pos[0]} -> {enemy_pos.x}'
        )
        assert enemy_pos.y == initial_pos[1], (
            f'제로 벡터에서 Y 이동 발생: {initial_pos[1]} -> {enemy_pos.y}'
        )

        # 매우 가까운 거리에서도 테스트 (부동소수점 오차 범위)
        player_world_pos = (250.0000001, 150.0000001)  # 극미한 차이

        # When - 다시 추적 행동 처리
        enemy_ai_system.set_entity_manager(mock_entity_manager)
        enemy_ai_system._handle_chase_behavior(
            enemy_entity, player_world_pos, delta_time
        )

        # Then - 여전히 이동하지 않아야 함 (1e-6 임계값보다 작음)
        assert enemy_pos.x == initial_pos[0], (
            '극미한 거리에서 예상치 못한 X 이동 발생'
        )
        assert enemy_pos.y == initial_pos[1], (
            '극미한 거리에서 예상치 못한 Y 이동 발생'
        )

    def test_AI_타입별_이동_속도_적용_검증_성공_시나리오(
        self,
        enemy_ai_system: EnemyAISystem,
        mock_entity_manager: EntityManager,
    ) -> None:
        """5. AI 타입별 이동 속도 적용 검증 (성공 시나리오)

        목적: 서로 다른 AI 타입에서 개별 이동 속도 적용 검증
        테스트할 범위: 각 AI 타입별 movement_speed 적용
        커버하는 함수 및 데이터: AIType에 따른 이동 속도 차이
        기대되는 안정성: AI 타입별 고유한 이동 특성 적용
        """
        # Given - 서로 다른 AI 타입의 적들 설정
        ai_types_and_speeds = [
            (AIType.AGGRESSIVE, 120.0),  # 공격적: 빠른 이동
            (AIType.DEFENSIVE, 60.0),  # 방어적: 느린 이동
            (AIType.PATROL, 80.0),  # 순찰형: 중간 이동
        ]

        player_world_pos = (300.0, 200.0)
        delta_time = 1.0  # 1초 (계산 편의)

        for ai_type, movement_speed in ai_types_and_speeds:
            # 각 AI 타입별 엔티티 생성
            enemy_entity = MagicMock(spec=Entity)
            enemy_entity.entity_id = f'enemy_{ai_type.display_name}'

            ai_component = EnemyAIComponent(
                ai_type=ai_type,
                current_state=AIState.CHASE,
                movement_speed=movement_speed,
            )

            enemy_pos = PositionComponent(x=200.0, y=200.0)

            # Mock 설정 - 클로저 변수 바인딩 해결
            def create_mock_closure(
                ai_comp: EnemyAIComponent, pos_comp: PositionComponent
            ) -> callable:
                def mock_get_component(
                    entity: Entity, component_type: type
                ) -> Component | None:
                    if component_type == EnemyAIComponent:
                        return ai_comp
                    elif component_type == PositionComponent:
                        return pos_comp
                    return None
                return mock_get_component

            mock_entity_manager.get_component.side_effect = (
                create_mock_closure(ai_component, enemy_pos)
            )

            initial_x = enemy_pos.x

            # When - 추적 행동 처리
            enemy_ai_system.set_entity_manager(mock_entity_manager)
            enemy_ai_system._handle_chase_behavior(
                enemy_entity, player_world_pos, delta_time
            )

            # Then - 각 AI 타입의 속도에 맞는 이동 거리 확인
            actual_movement_x = enemy_pos.x - initial_x
            expected_movement_x = (
                movement_speed  # 오른쪽으로만 이동 (정규화된 벡터)
            )

            assert abs(actual_movement_x - expected_movement_x) < 0.001, (
                f'{ai_type.display_name} AI 타입의 이동 거리 오류: '
                f'예상 {expected_movement_x}, 실제 {actual_movement_x}'
            )

    def teardown_method(self) -> None:
        """각 테스트 후 싱글톤 상태 정리."""
        CoordinateManager.set_instance(None)


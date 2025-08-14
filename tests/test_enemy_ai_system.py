"""
Test module for EnemyAISystem and EnemyAIComponent.

Tests enemy AI functionality including state transitions, world coordinate
distance calculations, and AI behavior management.
"""

from unittest.mock import MagicMock

import pytest

from src.components.enemy_ai_component import (
    AIState,
    AIType,
    EnemyAIComponent,
)
from src.components.enemy_component import EnemyComponent
from src.components.player_component import PlayerComponent
from src.components.position_component import PositionComponent
from src.core.coordinate_manager import CoordinateManager
from src.core.entity import Entity
from src.core.entity_manager import EntityManager
from src.systems.enemy_ai_system import EnemyAISystem


class TestEnemyAIComponent:
    """Test cases for EnemyAIComponent."""

    def test_AI_상태_및_타입_enum_정확성_검증_성공_시나리오(self) -> None:
        """1. AI 상태 및 타입 enum 정확성 검증 (성공 시나리오)

        목적: AIState와 AIType enum의 정의와 속성 검증
        테스트할 범위: enum 값, display_name, multiplier 속성
        커버하는 함수 및 데이터: AIState, AIType의 모든 속성
        기대되는 안정성: 일관된 enum 값과 속성 반환
        """
        # Given & When & Then - AIState enum 검증
        assert AIState.IDLE == 0
        assert AIState.CHASE == 1
        assert AIState.ATTACK == 2
        assert AIState.IDLE.display_name == '대기'
        assert AIState.CHASE.display_name == '추적'
        assert AIState.ATTACK.display_name == '공격'

        # AIType enum 검증
        assert AIType.AGGRESSIVE == 0
        assert AIType.DEFENSIVE == 1
        assert AIType.PATROL == 2
        assert AIType.AGGRESSIVE.display_name == '공격형'
        assert AIType.DEFENSIVE.display_name == '방어형'
        assert AIType.PATROL.display_name == '순찰형'

        # AI 타입별 배율 검증
        assert AIType.AGGRESSIVE.chase_range_multiplier == 1.2
        assert AIType.DEFENSIVE.chase_range_multiplier == 0.8
        assert AIType.PATROL.chase_range_multiplier == 1.0

        assert AIType.AGGRESSIVE.attack_range_multiplier == 0.8
        assert AIType.DEFENSIVE.attack_range_multiplier == 1.2
        assert AIType.PATROL.attack_range_multiplier == 1.0

    def test_적_AI_컴포넌트_초기화_및_검증_성공_시나리오(self) -> None:
        """2. 적 AI 컴포넌트 초기화 및 검증 (성공 시나리오)

        목적: EnemyAIComponent의 초기화와 유효성 검증 확인
        테스트할 범위: 초기값, validate 메서드, 범위 관계
        커버하는 함수 및 데이터: 기본값, attack_range <= chase_range 검증
        기대되는 안정성: 올바른 초기값과 논리적 범위 관계
        """
        # Given & When - 기본값으로 컴포넌트 생성
        ai_component = EnemyAIComponent()

        # Then - 기본값 확인
        assert ai_component.ai_type == AIType.AGGRESSIVE
        assert ai_component.current_state == AIState.IDLE
        assert ai_component.chase_range == 150.0
        assert ai_component.attack_range == 50.0
        assert ai_component.movement_speed == 80.0
        assert ai_component.state_change_cooldown == 0.0
        assert ai_component.last_player_position is None

        # 유효성 검증
        assert ai_component.validate() is True

        # 논리적 관계 검증
        assert ai_component.attack_range <= ai_component.chase_range

    def test_AI_타입별_효과적_범위_계산_정확성_검증_성공_시나리오(
        self,
    ) -> None:
        """3. AI 타입별 효과적 범위 계산 정확성 검증 (성공 시나리오)

        목적: AI 타입에 따른 범위 배율 적용 정확성 검증
        테스트할 범위: get_effective_chase_range, get_effective_attack_range
        커버하는 함수 및 데이터: 각 AI 타입별 배율 계산
        기대되는 안정성: 정확한 배율 적용과 계산 결과
        """
        # Given - 각 AI 타입별 컴포넌트 생성
        test_cases = [
            (AIType.AGGRESSIVE, 150.0, 50.0, 180.0, 40.0),  # 1.2배, 0.8배
            (AIType.DEFENSIVE, 150.0, 50.0, 120.0, 60.0),  # 0.8배, 1.2배
            (AIType.PATROL, 150.0, 50.0, 150.0, 50.0),  # 1.0배, 1.0배
        ]

        for (
            ai_type,
            chase_range,
            attack_range,
            expected_chase,
            expected_attack,
        ) in test_cases:
            # When - 각 타입의 컴포넌트 생성
            ai_component = EnemyAIComponent(
                ai_type=ai_type,
                chase_range=chase_range,
                attack_range=attack_range,
            )

            # Then - 효과적 범위 계산 검증
            actual_chase = ai_component.get_effective_chase_range()
            actual_attack = ai_component.get_effective_attack_range()

            assert abs(actual_chase - expected_chase) < 0.001, (
                f'{ai_type.display_name} 추적 범위: 예상 {expected_chase}, '
                f'실제 {actual_chase}'
            )
            assert abs(actual_attack - expected_attack) < 0.001, (
                f'{ai_type.display_name} 공격 범위: 예상 {expected_attack}, '
                f'실제 {actual_attack}'
            )

    def test_상태_변경_쿨다운_관리_정확성_검증_성공_시나리오(self) -> None:
        """4. 상태 변경 쿨다운 관리 정확성 검증 (성공 시나리오)

        목적: AI 상태 변경 쿨다운 시스템의 정확성 검증
        테스트할 범위: set_state, can_change_state, update_cooldown
        커버하는 함수 및 데이터: 쿨다운 시간 관리, 상태 변경 제한
        기대되는 안정성: 떨림 방지를 위한 정확한 쿨다운 동작
        """
        # Given - AI 컴포넌트 생성
        ai_component = EnemyAIComponent()

        # When & Then - 초기 상태에서는 변경 가능
        assert ai_component.can_change_state() is True
        assert ai_component.current_state == AIState.IDLE

        # 상태 변경 (쿨다운 설정)
        ai_component.set_state(AIState.CHASE, cooldown_duration=0.2)
        assert ai_component.current_state == AIState.CHASE
        assert ai_component.can_change_state() is False

        # 쿨다운 부분 업데이트
        ai_component.update_cooldown(0.1)
        assert ai_component.can_change_state() is False

        # 쿨다운 완료
        ai_component.update_cooldown(0.1)
        assert ai_component.can_change_state() is True

    def test_플레이어_거리_계산_및_상태_판단_정확성_검증_성공_시나리오(
        self,
    ) -> None:
        """5. 플레이어 거리 계산 및 상태 판단 정확성 검증 (성공 시나리오)

        목적: 월드 좌표 기반 거리 계산과 AI 상태 판단 로직 검증
        테스트할 범위: get_distance_to_player, should_chase, should_attack
        커버하는 함수 및 데이터: Vector2 거리 계산, 범위 비교 로직
        기대되는 안정성: 정확한 거리 계산과 상태 판단
        """
        # Given - AI 컴포넌트와 위치 설정 (AGGRESSIVE: chase*1.2, attack*0.8)
        ai_component = EnemyAIComponent(
            ai_type=AIType.AGGRESSIVE,  # chase: 100*1.2=120, attack: 30*0.8=24
            chase_range=100.0,
            attack_range=30.0,
        )
        enemy_pos = (200.0, 200.0)

        # When & Then - 다양한 거리에서 테스트 (효과적 범위 고려)
        test_cases = [
            (
                (200.0, 210.0),
                10.0,
                True,
                True,
            ),  # 공격 범위 내 (24 > 10, 120 > 10)
            (
                (200.0, 230.0),
                30.0,
                True,
                False,
            ),  # 추적 범위 내 (24 < 30 < 120)
            ((200.0, 350.0), 150.0, False, False),  # 범위 밖 (120 < 150)
        ]

        for (
            player_pos,
            expected_distance,
            expected_chase,
            expected_attack,
        ) in test_cases:
            # 거리 계산 검증
            actual_distance = ai_component.get_distance_to_player(
                enemy_pos, player_pos
            )
            assert abs(actual_distance - expected_distance) < 0.001, (
                f'거리 계산 오류: 예상 {expected_distance}, 실제 {actual_distance}'
            )

            # 상태 판단 검증 (효과적 범위 사용)
            assert (
                ai_component.should_chase(actual_distance) == expected_chase
            ), (
                f'Chase 판단 오류: 거리 {actual_distance}, '
                f'효과적 chase 범위 {ai_component.get_effective_chase_range()}, '
                f'예상 {expected_chase}'
            )
            assert (
                ai_component.should_attack(actual_distance) == expected_attack
            ), (
                f'Attack 판단 오류: 거리 {actual_distance}, '
                f'효과적 attack 범위 {ai_component.get_effective_attack_range()}, '
                f'예상 {expected_attack}'
            )

            # 플레이어 위치 업데이트
            ai_component.update_last_player_position(player_pos)
            assert ai_component.last_player_position == player_pos


class TestEnemyAISystem:
    """Test cases for EnemyAISystem."""

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

    def test_시스템_초기화_및_의존성_설정_검증_성공_시나리오(
        self,
        enemy_ai_system: EnemyAISystem,
        mock_coordinate_manager: CoordinateManager,
    ) -> None:
        """6. 시스템 초기화 및 의존성 설정 검증 (성공 시나리오)

        목적: EnemyAISystem의 초기화와 의존성 주입 검증
        테스트할 범위: __init__, initialize 메서드
        커버하는 함수 및 데이터: 우선순위 설정, CoordinateManager 의존성
        기대되는 안정성: 올바른 초기화와 의존성 설정
        """
        # Then - 시스템 속성이 올바르게 설정되어야 함
        assert enemy_ai_system.priority == 12
        assert enemy_ai_system.enabled
        assert enemy_ai_system.initialized
        assert enemy_ai_system._coordinate_manager == mock_coordinate_manager

        # 필수 컴포넌트 확인
        required_components = enemy_ai_system.get_required_components()
        assert EnemyAIComponent in required_components
        assert EnemyComponent in required_components
        assert PositionComponent in required_components

    def test_플레이어_엔티티_탐색_정확성_검증_성공_시나리오(
        self,
        enemy_ai_system: EnemyAISystem,
        mock_entity_manager: EntityManager,
    ) -> None:
        """7. 플레이어 엔티티 탐색 정확성 검증 (성공 시나리오)

        목적: 플레이어 엔티티 탐색 로직의 정확성 검증
        테스트할 범위: _find_player 메서드
        커버하는 함수 및 데이터: PlayerComponent 필터링, 엔티티 반환
        기대되는 안정성: 정확한 플레이어 엔티티 탐색과 None 처리
        """
        # Given - 플레이어 엔티티 설정
        player_entity = MagicMock(spec=Entity)
        player_entity.entity_id = 'player_1'

        # When & Then - 플레이어가 존재하는 경우
        mock_entity_manager.get_entities_with_components.return_value = [
            player_entity
        ]
        found_player = enemy_ai_system._find_player(mock_entity_manager)
        assert found_player == player_entity

        # PlayerComponent와 PositionComponent로 필터링 확인
        mock_entity_manager.get_entities_with_components.assert_called_with(
            PlayerComponent, PositionComponent
        )

        # When & Then - 플레이어가 없는 경우
        mock_entity_manager.get_entities_with_components.return_value = []
        found_player = enemy_ai_system._find_player(mock_entity_manager)
        assert found_player is None

    def test_AI_상태_전환_로직_정확성_검증_성공_시나리오(
        self,
        enemy_ai_system: EnemyAISystem,
    ) -> None:
        """8. AI 상태 전환 로직 정확성 검증 (성공 시나리오)

        목적: 거리에 따른 AI 상태 전환 로직의 정확성 검증
        테스트할 범위: _update_ai_state 메서드
        커버하는 함수 및 데이터: 거리 기반 상태 전환, 우선순위 처리
        기대되는 안정성: 정확한 상태 전환과 우선순위 적용
        """
        # Given - AI 컴포넌트 설정
        ai_component = EnemyAIComponent(
            chase_range=100.0,
            attack_range=30.0,
        )

        # When & Then - 공격 범위 내 (우선순위 최고)
        enemy_ai_system._update_ai_state(ai_component, 20.0)
        assert ai_component.current_state == AIState.ATTACK

        # 상태 리셋 (쿨다운 무시하고 테스트)
        ai_component.current_state = AIState.IDLE
        ai_component.state_change_cooldown = 0.0

        # 추적 범위 내
        enemy_ai_system._update_ai_state(ai_component, 50.0)
        assert ai_component.current_state == AIState.CHASE

        # 상태 리셋
        ai_component.current_state = AIState.IDLE
        ai_component.state_change_cooldown = 0.0

        # 범위 밖
        enemy_ai_system._update_ai_state(ai_component, 150.0)
        assert ai_component.current_state == AIState.IDLE

    def teardown_method(self) -> None:
        """각 테스트 후 싱글톤 상태 정리."""
        CoordinateManager.set_instance(None)

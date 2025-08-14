"""
Test module for AutoAttackSystem.

Tests automatic attack system functionality including cooldown management,
enemy targeting, and world coordinate based calculations.
"""

from unittest.mock import MagicMock

import pytest

from src.components.enemy_component import EnemyComponent
from src.components.position_component import PositionComponent
from src.components.weapon_component import WeaponComponent, WeaponType
from src.core.coordinate_manager import CoordinateManager
from src.core.entity import Entity
from src.core.entity_manager import EntityManager
from src.systems.auto_attack_system import AutoAttackSystem


class TestAutoAttackSystem:
    """Test cases for AutoAttackSystem."""

    @pytest.fixture
    def mock_entity_manager(self) -> EntityManager:
        """Create a mock entity manager for testing."""
        return MagicMock(spec=EntityManager)

    @pytest.fixture
    def mock_coordinate_manager(self) -> CoordinateManager:
        """Create a mock coordinate manager for testing."""
        mock_manager = MagicMock(spec=CoordinateManager)
        return mock_manager

    @pytest.fixture
    def auto_attack_system(
        self, mock_coordinate_manager: CoordinateManager
    ) -> AutoAttackSystem:
        """Create an AutoAttackSystem instance for testing."""
        # 싱글톤 인스턴스를 테스트용 mock으로 교체
        CoordinateManager.set_instance(mock_coordinate_manager)

        system = AutoAttackSystem(priority=15)
        system.initialize()
        return system

    @pytest.fixture
    def weapon_entity(self) -> Entity:
        """Create a mock weapon entity for testing."""
        entity = MagicMock(spec=Entity)
        entity.entity_id = 'weapon_entity_1'
        return entity

    @pytest.fixture
    def enemy_entity(self) -> Entity:
        """Create a mock enemy entity for testing."""
        entity = MagicMock(spec=Entity)
        entity.entity_id = 'enemy_entity_1'
        return entity

    def test_시간_기반_공격_쿨다운_관리_정확성_검증_성공_시나리오(
        self,
        auto_attack_system: AutoAttackSystem,
        mock_entity_manager: EntityManager,
    ) -> None:
        """1. 시간 기반 공격 쿨다운 관리 정확성 검증 (성공 시나리오)

        목적: FPS 독립적인 delta_time 기반 쿨다운 시스템 동작 검증
        테스트할 범위: _update_attack_cooldown, _can_attack, _reset_attack_cooldown
        커버하는 함수 및 데이터: WeaponComponent.attack_speed, last_attack_time 관리
        기대되는 안정성: 프레임률과 무관한 일정한 공격 주기 보장
        """
        # Given - 공격속도 2.0 (초당 2회 공격, 쿨다운 0.5초)인 무기 설정
        weapon = WeaponComponent(
            weapon_type=WeaponType.SOCCER_BALL,
            attack_speed=2.0,  # 초당 2회 공격
            range=100.0,
            damage=10,
            last_attack_time=0.0,
        )

        # When - 쿨다운 기간보다 적은 시간 경과 (0.3초)
        auto_attack_system._update_attack_cooldown(weapon, 0.3)

        # Then - 아직 공격 불가능 상태여야 함
        assert not auto_attack_system._can_attack(weapon), (
            '쿨다운 중에는 공격이 불가능해야 함'
        )
        assert weapon.last_attack_time == 0.3, (
            'delta_time이 정확히 누적되어야 함'
        )

        # When - 쿨다운 기간을 초과하는 시간 경과 (추가 0.3초, 총 0.6초)
        auto_attack_system._update_attack_cooldown(weapon, 0.3)

        # Then - 공격 가능 상태가 되어야 함
        assert auto_attack_system._can_attack(weapon), (
            '쿨다운 완료 후 공격이 가능해야 함'
        )
        assert weapon.last_attack_time == 0.6, (
            'delta_time이 계속 누적되어야 함'
        )

        # When - 공격 실행 후 쿨다운 리셋
        auto_attack_system._reset_attack_cooldown(weapon)

        # Then - 초과 시간이 다음 쿨다운에 반영되어야 함
        expected_remaining = 0.6 - 0.5  # 초과된 0.1초가 다음 쿨다운에 반영
        assert weapon.last_attack_time == expected_remaining, (
            '초과 시간이 다음 쿨다운에 보존되어야 함'
        )

    def test_무기_컴포넌트_쿨다운_계산_정확성_검증_성공_시나리오(
        self,
        auto_attack_system: AutoAttackSystem,
    ) -> None:
        """2. 무기 컴포넌트 쿨다운 계산 정확성 검증 (성공 시나리오)

        목적: WeaponComponent의 쿨다운 관련 메서드 동작 검증
        테스트할 범위: get_cooldown_duration, can_attack 메서드
        커버하는 함수 및 데이터: attack_speed와 쿨다운 시간의 역수 관계
        기대되는 안정성: 다양한 공격속도에서 정확한 쿨다운 계산
        """
        # Given - 다양한 공격속도를 가진 무기들
        test_cases = [
            (1.0, 1.0),  # 초당 1회 공격 = 1초 쿨다운
            (2.0, 0.5),  # 초당 2회 공격 = 0.5초 쿨다운
            (0.5, 2.0),  # 초당 0.5회 공격 = 2초 쿨다운
            (4.0, 0.25),  # 초당 4회 공격 = 0.25초 쿨다운
        ]

        for attack_speed, expected_cooldown in test_cases:
            # When - 각 공격속도에 대한 무기 생성
            weapon = WeaponComponent(
                attack_speed=attack_speed, last_attack_time=0.0
            )

            # Then - 쿨다운 계산이 정확해야 함
            actual_cooldown = weapon.get_cooldown_duration()
            assert abs(actual_cooldown - expected_cooldown) < 0.001, (
                f'공격속도 {attack_speed}에서 쿨다운 {expected_cooldown}초 예상, '
                f'실제 {actual_cooldown}초'
            )

    def test_월드_좌표_기반_적_탐색_범위_계산_검증_성공_시나리오(
        self,
        auto_attack_system: AutoAttackSystem,
        mock_entity_manager: EntityManager,
        weapon_entity: Entity,
        enemy_entity: Entity,
    ) -> None:
        """3. 월드 좌표 기반 적 탐색 범위 계산 검증 (성공 시나리오)

        목적: 월드 좌표를 기준으로 한 적 탐색 알고리즘 정확성 검증
        테스트할 범위: _find_nearest_enemy_in_world 메서드
        커버하는 함수 및 데이터: Vector2 거리 계산, EnemyComponent 필터링
        기대되는 안정성: 정확한 거리 기반 타겟 선택과 범위 제한
        """
        # Given - 무기 위치 (100, 100), 사거리 150
        weapon_pos = PositionComponent(x=100.0, y=100.0)
        weapon_range = 150.0

        # 적 엔티티들 설정 (거리별로 배치)
        enemy1_entity = MagicMock(spec=Entity)
        enemy1_entity.entity_id = 'enemy1'
        enemy1_pos = PositionComponent(
            x=180.0, y=160.0
        )  # 거리: sqrt(80²+60²) = 100

        enemy2_entity = MagicMock(spec=Entity)
        enemy2_entity.entity_id = 'enemy2'
        enemy2_pos = PositionComponent(
            x=200.0, y=200.0
        )  # 거리: sqrt(100²+100²) ≈ 141.4

        enemy3_entity = MagicMock(spec=Entity)
        enemy3_entity.entity_id = 'enemy3'
        enemy3_pos = PositionComponent(
            x=300.0, y=300.0
        )  # 거리: sqrt(200²+200²) ≈ 282.8 (범위 밖)

        # Mock 설정
        mock_entity_manager.get_entities_with_components.return_value = [
            enemy1_entity,
            enemy2_entity,
            enemy3_entity,
        ]

        def mock_get_component(entity: Entity, component_type: type) -> object:
            if entity == enemy1_entity and component_type == PositionComponent:
                return enemy1_pos
            elif (
                entity == enemy2_entity and component_type == PositionComponent
            ):
                return enemy2_pos
            elif (
                entity == enemy3_entity and component_type == PositionComponent
            ):
                return enemy3_pos
            return None

        mock_entity_manager.get_component.side_effect = mock_get_component

        # When - 가장 가까운 적 탐색
        closest_enemy = auto_attack_system._find_nearest_enemy_in_world(
            weapon_pos, weapon_range, mock_entity_manager
        )

        # Then - 범위 내에서 가장 가까운 적이 선택되어야 함
        assert closest_enemy == enemy1_entity, (
            '범위 내에서 가장 가까운 적이 선택되어야 함'
        )

        # 올바른 컴포넌트로 엔티티 필터링 확인
        mock_entity_manager.get_entities_with_components.assert_called_once_with(
            EnemyComponent, PositionComponent
        )

    def test_적이_없을_때_타겟_탐색_예외_처리_검증_성공_시나리오(
        self,
        auto_attack_system: AutoAttackSystem,
        mock_entity_manager: EntityManager,
    ) -> None:
        """4. 적이 없을 때 타겟 탐색 예외 처리 검증 (성공 시나리오)

        목적: 적이 없거나 범위 밖에 있을 때의 안전한 처리 검증
        테스트할 범위: _find_nearest_enemy_in_world의 예외 상황 처리
        커버하는 함수 및 데이터: 빈 엔티티 리스트, 범위 밖 적들
        기대되는 안정성: 예외 발생 없이 None 반환
        """
        # Given - 무기 위치와 사거리 설정
        weapon_pos = PositionComponent(x=100.0, y=100.0)
        weapon_range = 50.0

        # When & Then - 적이 전혀 없는 경우
        mock_entity_manager.get_entities_with_components.return_value = []

        closest_enemy = auto_attack_system._find_nearest_enemy_in_world(
            weapon_pos, weapon_range, mock_entity_manager
        )

        assert closest_enemy is None, '적이 없을 때 None을 반환해야 함'

        # When & Then - 적이 모두 범위 밖에 있는 경우
        far_enemy = MagicMock(spec=Entity)
        far_enemy_pos = PositionComponent(
            x=200.0, y=200.0
        )  # 거리 약 141.4 (범위 50 밖)

        mock_entity_manager.get_entities_with_components.return_value = [
            far_enemy
        ]
        mock_entity_manager.get_component.return_value = far_enemy_pos

        closest_enemy = auto_attack_system._find_nearest_enemy_in_world(
            weapon_pos, weapon_range, mock_entity_manager
        )

        assert closest_enemy is None, '범위 밖 적만 있을 때 None을 반환해야 함'

    def test_시스템_초기화_및_의존성_설정_검증_성공_시나리오(
        self,
        mock_coordinate_manager: CoordinateManager,
    ) -> None:
        """5. 시스템 초기화 및 의존성 설정 검증 (성공 시나리오)

        목적: AutoAttackSystem의 초기화와 의존성 주입 검증
        테스트할 범위: __init__, initialize 메서드
        커버하는 함수 및 데이터: 우선순위 설정, CoordinateManager 의존성
        기대되는 안정성: 올바른 초기화와 의존성 설정
        """
        # Given & When - AutoAttackSystem 생성 및 초기화
        CoordinateManager.set_instance(mock_coordinate_manager)

        system = AutoAttackSystem(priority=20)
        system.initialize()

        # Then - 시스템 속성이 올바르게 설정되어야 함
        assert system.priority == 20, '우선순위가 올바르게 설정되어야 함'
        assert system.enabled, '시스템이 기본적으로 활성화되어야 함'
        assert system.initialized, '초기화가 완료되어야 함'
        assert system._coordinate_manager == mock_coordinate_manager, (
            '좌표 관리자가 설정되어야 함'
        )

        # 필수 컴포넌트 확인
        required_components = system.get_required_components()
        assert WeaponComponent in required_components, (
            'WeaponComponent가 필수여야 함'
        )
        assert PositionComponent in required_components, (
            'PositionComponent가 필수여야 함'
        )

    def test_월드_좌표_기반_투사체_생성_및_방향_계산_검증_성공_시나리오(
        self,
        auto_attack_system: AutoAttackSystem,
        mock_entity_manager: EntityManager,
    ) -> None:
        """6. 월드 좌표 기반 투사체 생성 및 방향 계산 검증 (성공 시나리오)

        목적: 월드 좌표 기반 투사체 생성과 정확한 방향 계산 검증
        테스트할 범위: _execute_world_attack 메서드
        커버하는 함수 및 데이터: ProjectileComponent 생성, 컴포넌트 추가
        기대되는 안정성: 정확한 방향과 속성을 가진 투사체 생성
        """
        # Given - 무기와 위치 설정
        weapon = WeaponComponent(
            weapon_type=WeaponType.SOCCER_BALL,
            attack_speed=1.0,
            range=200.0,
            damage=20,
        )
        start_pos = PositionComponent(x=100.0, y=100.0)
        target_pos = PositionComponent(x=200.0, y=150.0)

        # Mock 엔티티 생성
        mock_projectile_entity = MagicMock()
        mock_projectile_entity.entity_id = 'projectile_1'
        mock_entity_manager.create_entity.return_value = mock_projectile_entity

        # When - 투사체 생성 실행
        auto_attack_system._execute_world_attack(
            weapon, start_pos, target_pos, mock_entity_manager
        )

        # Then - 투사체 엔티티가 생성되어야 함
        mock_entity_manager.create_entity.assert_called_once()

        # 컴포넌트 추가 호출 확인 (5번: Projectile, Position, Render, Collision)
        assert mock_entity_manager.add_component.call_count == 4

        # 각 컴포넌트가 올바르게 추가되었는지 확인
        add_component_calls = mock_entity_manager.add_component.call_args_list

        # ProjectileComponent 확인
        projectile_call = add_component_calls[0]
        assert projectile_call[0][0] == mock_projectile_entity
        projectile_comp = projectile_call[0][1]
        assert hasattr(projectile_comp, 'direction')
        assert hasattr(projectile_comp, 'velocity')
        assert projectile_comp.damage == weapon.get_effective_damage()

        # PositionComponent 확인
        position_call = add_component_calls[1]
        position_comp = position_call[0][1]
        assert position_comp.x == start_pos.x
        assert position_comp.y == start_pos.y

    def test_투사체_생성_예외_처리_안정성_검증_성공_시나리오(
        self,
        auto_attack_system: AutoAttackSystem,
        mock_entity_manager: EntityManager,
    ) -> None:
        """7. 투사체 생성 예외 처리 안정성 검증 (성공 시나리오)

        목적: 투사체 생성 중 예외 발생 시 안전한 처리 검증
        테스트할 범위: _execute_world_attack의 예외 처리
        커버하는 함수 및 데이터: Exception 처리, 시스템 안정성
        기대되는 안정성: 예외 발생 시에도 시스템 계속 동작
        """
        # Given - 무기와 위치 설정
        weapon = WeaponComponent()
        start_pos = PositionComponent(x=100.0, y=100.0)
        target_pos = PositionComponent(x=200.0, y=150.0)

        # Mock 설정 - create_entity에서 예외 발생
        mock_entity_manager.create_entity.side_effect = Exception(
            'Entity creation failed'
        )

        # When & Then - 예외 발생해도 메서드가 정상 완료되어야 함
        try:
            auto_attack_system._execute_world_attack(
                weapon, start_pos, target_pos, mock_entity_manager
            )
            # 예외가 전파되지 않고 메서드가 정상 완료되어야 함
        except Exception as e:
            pytest.fail(f'예외가 전파되지 않아야 함: {e}')

        # 엔티티 생성 시도는 했어야 함
        mock_entity_manager.create_entity.assert_called_once()

    def teardown_method(self) -> None:
        """각 테스트 후 싱글톤 상태 정리."""
        CoordinateManager.set_instance(None)

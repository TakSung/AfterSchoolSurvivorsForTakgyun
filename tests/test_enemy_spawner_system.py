"""
적 스포너 시스템 테스트 모듈

EnemySpawnerSystem의 시간 기반 적 생성, 최대 적 수 제한,
난이도 조정 메커니즘을 검증합니다.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.interfaces import (
    ICoordinateManager,
    IDifficultyManager,
    IEnemyManager,
)
from src.systems.enemy_spawner_system import EnemySpawnerSystem
from src.utils.vector2 import Vector2


class TestEnemySpawnerSystem:
    """EnemySpawnerSystem 테스트 클래스"""

    def setup_method(self) -> None:
        """각 테스트 메서드 전에 실행되는 설정"""
        # Mock 매니저들 생성
        self.mock_coordinate_manager = MagicMock(spec=ICoordinateManager)
        self.mock_difficulty_manager = MagicMock(spec=IDifficultyManager)
        self.mock_enemy_manager = MagicMock(spec=IEnemyManager)

        # Mock 매니저 설정
        self.mock_difficulty_manager.get_spawn_rate_multiplier.return_value = (
            1.0
        )
        self.mock_difficulty_manager.get_speed_multiplier.return_value = 1.0
        self.mock_difficulty_manager.get_health_multiplier.return_value = 1.0
        self.mock_difficulty_manager.update.return_value = None

        self.mock_coordinate_manager.screen_to_world.return_value = Vector2(
            100, 100
        )

        # EnemyManager Mock 설정
        self.mock_enemy_manager.get_enemy_count.return_value = (
            0  # 기본값으로 0 설정
        )
        self.mock_enemy_manager.create_enemy_entity.return_value = None

        # 새로운 패턴으로 EnemySpawnerSystem 생성 (의존성 주입)
        self.spawner_system = EnemySpawnerSystem(
            priority=5,
            enemy_manager=self.mock_enemy_manager,
            coordinate_manager=self.mock_coordinate_manager,
            difficulty_manager=self.mock_difficulty_manager,
        )

        # 의존성 주입으로 인해 패치가 더 이상 필요하지 않음
        # 시스템 초기화
        self.spawner_system.initialize()

    def teardown_method(self) -> None:
        """각 테스트 메서드 후에 실행되는 정리"""
        # 더 이상 패치할 것이 없으므로 정리 코드도 간소화
        pass

    def test_시스템_초기화_및_기본_설정_검증_성공_시나리오(self) -> None:
        """1. 시스템 초기화 및 기본 설정 검증 (성공 시나리오)"""
        spawn_info = self.spawner_system.get_spawn_info()
        assert spawn_info['base_spawn_interval'] == '2.0'
        assert spawn_info['max_enemies'] == '20'
        assert spawn_info['current_spawn_interval'] == '2.0'

    def test_스폰_시간_조건_확인_정확성_검증_성공_시나리오(self) -> None:
        """2. 스폰 시간 조건 확인 정확성 검증 (성공 시나리오)"""
        self.spawner_system._current_spawn_timer = 1.5
        assert self.spawner_system._is_spawn_time_ready() is False
        self.spawner_system._current_spawn_timer = 2.1
        assert self.spawner_system._is_spawn_time_ready() is True

    def test_최대_적_수_제한_동작_검증_성공_시나리오(self) -> None:
        """3. 최대 적 수 제한 동작 검증 (성공 시나리오) - REFACTORED"""
        # Given - 최대 적 수를 5로 설정
        self.spawner_system.set_max_enemies(5)

        # Given - 4개의 적이 있는 상황을 Mock으로 시뮬레이션
        self.mock_enemy_manager.get_enemy_count.return_value = 4

        # When - 적 개수가 제한 이하인지 확인 (4마리 < 5마리 제한)
        # EnemySpawnerSystem이 IEnemyManager를 통해 적 수를 확인하는지 테스트
        self.spawner_system._current_spawn_timer = 2.5  # 스폰 시간 조건 만족

        # 스폰 조건 확인 - 적 수가 제한 이하이므로 스폰 가능해야 함
        can_spawn_with_4_enemies = self.spawner_system.can_spawn()
        assert can_spawn_with_4_enemies is True, (
            '4마리일 때는 스폰 시간 조건만 확인'
        )

        # Given - 5개의 적이 있는 상황 (최대 제한 도달)
        self.mock_enemy_manager.get_enemy_count.return_value = 5

        # When - update() 메서드 호출 시 스폰이 실행되지 않아야 함
        initial_call_count = (
            self.mock_enemy_manager.create_enemy_entity.call_count
        )
        self.spawner_system.update(0.1)
        final_call_count = (
            self.mock_enemy_manager.create_enemy_entity.call_count
        )

        # Then - 최대 적 수에 도달했으므로 엔티티 생성이 호출되지 않아야 함
        assert final_call_count == initial_call_count, (
            '최대 적 수 도달 시 스폰 불가능해야 함'
        )

    def test_전체_스폰_조건_통합_검증_성공_시나리오(self) -> None:
        """4. 전체 스폰 조건 통합 검증 (성공 시나리오) - REFACTORED"""
        self.spawner_system.set_max_enemies(3)

        # Given - 스폰 시간이 아직 부족한 상황 (1.0초 < 2.0초 간격)
        self.spawner_system._current_spawn_timer = 1.0
        self.mock_enemy_manager.get_enemy_count.return_value = 0

        # When - update() 호출
        initial_call_count = (
            self.mock_enemy_manager.create_enemy_entity.call_count
        )
        self.spawner_system.update(0.1)

        # Then - 시간 조건 미달로 스폰되지 않아야 함
        assert (
            self.mock_enemy_manager.create_enemy_entity.call_count
            == initial_call_count
        )

        # Given - 적이 최대치에 도달한 상황 (3마리)
        self.mock_enemy_manager.get_enemy_count.return_value = 3
        self.spawner_system._current_spawn_timer = 3.0  # 충분한 시간 경과

        # When - update() 호출
        initial_call_count = (
            self.mock_enemy_manager.create_enemy_entity.call_count
        )
        self.spawner_system.update(0.1)

        # Then - 적 수 제한으로 스폰되지 않아야 함
        assert (
            self.mock_enemy_manager.create_enemy_entity.call_count
            == initial_call_count
        )

        # Given - 적 수가 줄어든 상황 (2마리)
        self.mock_enemy_manager.get_enemy_count.return_value = 2
        self.spawner_system._current_spawn_timer = 3.0  # 충분한 시간 경과

        # When - update() 호출
        initial_call_count = (
            self.mock_enemy_manager.create_enemy_entity.call_count
        )
        self.spawner_system.update(0.1)

        # Then - 조건을 만족하므로 스폰되어야 함
        assert (
            self.mock_enemy_manager.create_enemy_entity.call_count
            == initial_call_count + 1
        )

    def test_난이도_기반_스폰_간격_조정_검증_성공_시나리오(self) -> None:
        """5. 난이도 기반 스폰 간격 조정 검증 (성공 시나리오) - FIXED METHOD NAME"""
        base_interval = self.spawner_system._base_spawn_interval

        # 올바른 메서드 이름 사용: get_spawn_rate_multiplier
        self.mock_difficulty_manager.get_spawn_rate_multiplier.return_value = (
            1.0
        )
        assert (
            self.spawner_system._get_current_spawn_interval() == base_interval
        )

        self.mock_difficulty_manager.get_spawn_rate_multiplier.return_value = (
            0.8
        )
        assert (
            self.spawner_system._get_current_spawn_interval()
            == pytest.approx(base_interval * 0.8)
        )

        self.mock_difficulty_manager.get_spawn_rate_multiplier.return_value = (
            0.5
        )
        assert (
            self.spawner_system._get_current_spawn_interval()
            == pytest.approx(base_interval * 0.5)
        )

    @patch('src.systems.enemy_spawner_system.random.randint', return_value=0)
    @patch(
        'src.systems.enemy_spawner_system.random.uniform', return_value=50.0
    )
    def test_적_생성_및_컴포넌트_구성_검증_성공_시나리오(
        self, mock_uniform, mock_randint
    ) -> None:
        """6. 적 엔티티 생성 및 컴포넌트 구성 검증 (성공 시나리오)"""
        # 스폰 조건 설정 - 타이머를 충분히 높게 설정
        self.spawner_system._current_spawn_timer = 2.5  # 스폰 간격(2.0초) 초과

        # 스폰 실행
        self.spawner_system.update(0.1)

        # Mock EnemyManager가 호출되었는지 확인
        self.mock_enemy_manager.get_enemy_count.assert_called_once()
        self.mock_enemy_manager.create_enemy_entity.assert_called_once()

        # 호출된 spawn_result 검증
        call_args = self.mock_enemy_manager.create_enemy_entity.call_args
        spawn_result = call_args[0][0]  # 첫 번째 인자

        # SpawnResult 검증
        assert spawn_result.entity_type == 'enemy'
        assert spawn_result.x == 50.0
        assert (
            spawn_result.difficulty_scale == 1.0
        )  # base_interval / current_interval

        # 추가 데이터 검증
        additional_data = spawn_result.additional_data
        assert additional_data['base_health'] == 100
        assert additional_data['base_speed'] == 80.0
        assert 'AGGRESSIVE' in additional_data['ai_type_options']
        assert 'DEFENSIVE' in additional_data['ai_type_options']
        assert 'PATROL' in additional_data['ai_type_options']

    def test_시스템_업데이트_전체_플로우_검증_성공_시나리오(self) -> None:
        """7. 시스템 업데이트 전체 플로우 검증 (성공 시나리오)"""
        # 초기 상태 확인
        assert self.spawner_system._current_spawn_timer == 0.0

        # 첫 번째 업데이트 - 스폰 시간 미달
        self.spawner_system.update(0.5)
        assert self.spawner_system._current_spawn_timer == 0.5
        # 아직 스폰되지 않아야 함
        self.mock_enemy_manager.create_enemy_entity.assert_not_called()

        # 두 번째 업데이트 - 스폰 시간 초과 (총 2.3초)
        self.spawner_system.update(1.8)

        # 스폰이 발생해야 함
        self.mock_enemy_manager.get_enemy_count.assert_called()
        self.mock_enemy_manager.create_enemy_entity.assert_called_once()

        # 스폰 후 타이머가 리셋되었는지 확인
        assert self.spawner_system._current_spawn_timer == 0.0

    def test_설정_변경_메서드_동작_검증_성공_시나리오(self) -> None:
        """8. 설정 변경 메서드 동작 검증 (성공 시나리오)"""
        # 직접 설정 변경 (설정 메서드들이 존재한다면)
        if hasattr(self.spawner_system, 'set_spawn_interval'):
            self.spawner_system.set_spawn_interval(1.5)
        if hasattr(self.spawner_system, 'set_max_enemies'):
            self.spawner_system.set_max_enemies(15)

        # 또는 직접 속성 변경
        self.spawner_system._base_spawn_interval = 1.5
        self.spawner_system._max_enemies = 15

        spawn_info = self.spawner_system.get_spawn_info()
        assert spawn_info['base_spawn_interval'] == '1.5'
        assert spawn_info['max_enemies'] == '15'

        # 잘못된 값 설정 시 검증
        if hasattr(self.spawner_system, 'set_spawn_interval'):
            self.spawner_system.set_spawn_interval(-1.0)
        if hasattr(self.spawner_system, 'set_max_enemies'):
            self.spawner_system.set_max_enemies(0)
        final_spawn_info = self.spawner_system.get_spawn_info()
        # 잘못된 값은 설정되지 않아야 함 (검증 로직에 따라)
        assert final_spawn_info['base_spawn_interval'] == '1.5'
        assert final_spawn_info['max_enemies'] == '15'

    def test_좌표_관리자_없을_때_안전_처리_검증_성공_시나리오(self) -> None:
        """9. 좌표 관리자 없을 때 안전 처리 검증 (성공 시나리오) - REFACTORED"""
        # Given - 좌표 관리자가 없는 상황
        self.spawner_system._coordinate_manager = None

        # When - 스폰 위치 계산 시도
        spawn_position = self.spawner_system._calculate_spawn_position()

        # Then - None을 반환해야 함
        assert spawn_position is None

        # Given - 스폰 조건을 만족하는 상황이지만 좌표 관리자가 없음
        self.spawner_system._current_spawn_timer = 2.5  # 충분한 시간
        self.mock_enemy_manager.get_enemy_count.return_value = (
            0  # 적 수 제한 없음
        )

        # When - spawn() 메서드 호출
        spawn_result = self.spawner_system.spawn()

        # Then - 좌표 계산 실패로 None을 반환해야 함
        assert spawn_result is None

        # When - update() 메서드 호출
        initial_call_count = (
            self.mock_enemy_manager.create_enemy_entity.call_count
        )
        self.spawner_system.update(0.1)

        # Then - 스폰 실패로 적 생성이 호출되지 않아야 함
        assert (
            self.mock_enemy_manager.create_enemy_entity.call_count
            == initial_call_count
        )

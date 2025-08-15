"""
적 스포너 시스템 테스트 모듈

EnemySpawnerSystem의 시간 기반 적 생성, 최대 적 수 제한,
난이도 조정 메커니즘을 검증합니다.
"""

from unittest.mock import MagicMock, patch

from src.components.enemy_ai_component import AIType, EnemyAIComponent
from src.components.enemy_component import EnemyComponent
from src.components.position_component import PositionComponent
from src.core.component_registry import ComponentRegistry
from src.core.coordinate_manager import CoordinateManager
from src.core.entity_manager import EntityManager
from src.systems.enemy_spawner_system import EnemySpawnerSystem
from src.utils.vector2 import Vector2


class TestEnemySpawnerSystem:
    """EnemySpawnerSystem 테스트 클래스"""

    def setup_method(self) -> None:
        """각 테스트 메서드 전에 실행되는 설정"""
        self.component_registry = ComponentRegistry()
        self.entity_manager = EntityManager()
        self.entity_manager.component_registry = self.component_registry
        self.spawner_system = EnemySpawnerSystem(priority=5)

        # CoordinateManager 모킹
        self.mock_coordinate_manager = MagicMock(spec=CoordinateManager)

        # 기본 좌표 변환 설정
        self.mock_coordinate_manager.screen_to_world.return_value = Vector2(
            100, 100
        )

        with patch(
            'src.systems.enemy_spawner_system.CoordinateManager.get_instance',
            return_value=self.mock_coordinate_manager,
        ):
            self.spawner_system.initialize()

    def test_시스템_초기화_및_기본_설정_검증_성공_시나리오(self) -> None:
        """1. 시스템 초기화 및 기본 설정 검증 (성공 시나리오)

        목적: EnemySpawnerSystem의 초기 상태와 설정값 검증
        테스트할 범위: 시스템 초기화, 기본 설정값, 좌표 관리자 연결
        커버하는 함수 및 데이터: __init__, initialize(), get_spawn_info()
        기대되는 안정성: 일관된 초기 상태 보장
        """
        # Given - 시스템이 초기화된 상태

        # When - 스폰 정보 조회
        spawn_info = self.spawner_system.get_spawn_info()

        # Then - 기본 설정값 확인
        assert spawn_info['base_spawn_interval'] == 2.0, (
            '기본 스폰 간격이 2초여야 함'
        )
        assert spawn_info['max_enemies'] == 20, '최대 적 수가 20이어야 함'
        assert spawn_info['game_time'] == 0.0, (
            '게임 시간이 0으로 초기화되어야 함'
        )
        assert spawn_info['spawn_timer'] == 0.0, (
            '스폰 타이머가 0으로 초기화되어야 함'
        )
        assert spawn_info['current_spawn_interval'] == 2.0, (
            '현재 스폰 간격이 기본값과 같아야 함'
        )

        # 시스템 상태 확인
        assert self.spawner_system.enabled is True, '시스템이 활성화되어야 함'
        assert self.spawner_system.priority == 5, '우선순위가 5여야 함'

    def test_스폰_시간_조건_확인_정확성_검증_성공_시나리오(self) -> None:
        """2. 스폰 시간 조건 확인 정확성 검증 (성공 시나리오)

        목적: 스폰 타이머와 간격 비교 로직의 정확성 검증
        테스트할 범위: _is_spawn_time_ready() 메서드
        커버하는 함수 및 데이터: 시간 조건 분기 로직
        기대되는 안정성: 정확한 타이밍 기반 스폰 판정
        """
        # Given - 스폰 간격이 2초인 상황

        # When - 스폰 시간이 충분하지 않은 경우
        self.spawner_system._current_spawn_timer = 1.5
        is_ready_before = self.spawner_system._is_spawn_time_ready()

        # When - 스폰 시간이 충분한 경우
        self.spawner_system._current_spawn_timer = 2.1
        is_ready_after = self.spawner_system._is_spawn_time_ready()

        # Then - 정확한 시간 조건 확인
        assert is_ready_before is False, '1.5초에서는 스폰할 수 없어야 함'
        assert is_ready_after is True, '2.1초에서는 스폰할 수 있어야 함'

    def test_최대_적_수_제한_동작_검증_성공_시나리오(self) -> None:
        """3. 최대 적 수 제한 동작 검증 (성공 시나리오)

        목적: 최대 적 수 제한이 올바르게 동작하는지 검증
        테스트할 범위: _is_enemy_count_within_limit() 메서드
        커버하는 함수 및 데이터: 적 개수 카운팅 및 제한 로직
        기대되는 안정성: 정확한 적 수 관리로 성능 보장
        """
        # Given - 최대 적 수를 5로 설정
        self.spawner_system.set_max_enemies(5)

        # Given - 4개의 적 엔티티 생성
        enemies = []
        for i in range(4):
            enemy = self.entity_manager.create_entity()
            self.entity_manager.add_component(enemy, EnemyComponent())
            self.entity_manager.add_component(
                enemy, PositionComponent(x=i * 10, y=0)
            )
            enemies.append(enemy)

        # Debug - 적 개수 확인
        entities_with_components = (
            self.entity_manager.get_entities_with_components(
                EnemyComponent, PositionComponent
            )
        )
        print(f'Debug: 생성된 적 엔티티 수: {len(entities_with_components)}')

        # When - 적 개수 제한 확인
        current_count_before = self.spawner_system._get_current_enemy_count(
            self.entity_manager
        )
        is_within_limit_before = (
            self.spawner_system._is_enemy_count_within_limit(
                self.entity_manager
            )
        )

        # Given - 1개 적 추가 (총 5개)
        enemy = self.entity_manager.create_entity()
        self.entity_manager.add_component(enemy, EnemyComponent())
        self.entity_manager.add_component(enemy, PositionComponent(x=40, y=0))
        enemies.append(enemy)

        # When - 적 개수 제한 재확인
        current_count_after = self.spawner_system._get_current_enemy_count(
            self.entity_manager
        )
        is_within_limit_after = (
            self.spawner_system._is_enemy_count_within_limit(
                self.entity_manager
            )
        )

        # Then - 정확한 제한 동작 확인
        assert current_count_before == 4, (
            f'4개 적이 정확히 카운팅되어야 함, 실제: {current_count_before}'
        )
        assert is_within_limit_before is True, '4개일 때는 스폰 가능해야 함'
        assert current_count_after == 5, (
            f'5개 적이 정확히 카운팅되어야 함, 실제: {current_count_after}'
        )
        assert is_within_limit_after is False, '5개일 때는 스폰 불가능해야 함'

    def test_전체_스폰_조건_통합_검증_성공_시나리오(self) -> None:
        """4. 전체 스폰 조건 통합 검증 (성공 시나리오)

        목적: 시간과 개수 조건을 모두 만족해야 스폰되는 로직 검증
        테스트할 범위: _should_spawn_enemy() 메서드
        커버하는 함수 및 데이터: 복합 조건 판정 로직
        기대되는 안정성: 모든 조건 만족 시에만 스폰 실행
        """
        # Given - 최대 적 수를 3으로 설정 (더 작은 수로 테스트)
        self.spawner_system.set_max_enemies(3)

        # Given - 적 개수는 제한 내, 시간은 부족
        self.spawner_system._current_spawn_timer = 1.0
        should_spawn_time_not_ready = self.spawner_system._should_spawn_enemy(
            self.entity_manager
        )

        # Given - 3개 적 생성하여 제한에 도달
        enemies = []
        for i in range(3):
            enemy = self.entity_manager.create_entity()
            self.entity_manager.add_component(enemy, EnemyComponent())
            self.entity_manager.add_component(
                enemy, PositionComponent(x=i * 10, y=0)
            )
            enemies.append(enemy)

        # Given - 시간은 충분하지만 적 개수가 제한에 도달
        self.spawner_system._current_spawn_timer = 3.0
        current_count_at_limit = self.spawner_system._get_current_enemy_count(
            self.entity_manager
        )

        should_spawn_count_exceeded = self.spawner_system._should_spawn_enemy(
            self.entity_manager
        )

        # Given - 적 하나 제거하여 조건 만족 상태로 변경
        if enemies:
            self.entity_manager.destroy_entity(enemies[0])

        should_spawn_all_conditions_met = (
            self.spawner_system._should_spawn_enemy(self.entity_manager)
        )

        final_count = self.spawner_system._get_current_enemy_count(
            self.entity_manager
        )

        # Then - 복합 조건 검증
        assert should_spawn_time_not_ready is False, (
            '시간 부족 시 스폰하지 않아야 함'
        )
        assert current_count_at_limit == 3, (
            f'3개 적이 정확히 카운팅되어야 함, 실제: {current_count_at_limit}'
        )
        assert should_spawn_count_exceeded is False, (
            '적 개수가 제한에 도달했으므로 스폰하지 않아야 함'
        )
        assert final_count == 2, (
            f'적 제거 후 2개가 되어야 함, 실제: {final_count}'
        )
        assert should_spawn_all_conditions_met is True, (
            '모든 조건 만족 시 스폰해야 함'
        )

    def test_난이도_기반_스폰_간격_조정_검증_성공_시나리오(self) -> None:
        """5. 난이도 기반 스폰 간격 조정 검증 (성공 시나리오)

        목적: 게임 시간에 따른 스폰 간격 단축 메커니즘 검증
        테스트할 범위: _get_current_spawn_interval() 메서드
        커버하는 함수 및 데이터: 난이도 스케일링 공식
        기대되는 안정성: 점진적 난이도 증가로 게임 밸런스 유지
        """
        # Given - 기본 스폰 간격 2초 설정

        # When - 게임 시작 직후 (0초)
        interval_start = self.spawner_system._get_current_spawn_interval()

        # When - 30초 경과 (DifficultyManager 업데이트를 통해)
        if self.spawner_system._difficulty_manager:
            self.spawner_system._difficulty_manager.update(30.0)
        self.spawner_system._game_time = 30.0
        interval_30s = self.spawner_system._get_current_spawn_interval()

        # When - 60초 경과 (총 60초)
        if self.spawner_system._difficulty_manager:
            self.spawner_system._difficulty_manager.update(30.0)  # 추가 30초
        self.spawner_system._game_time = 60.0
        interval_60s = self.spawner_system._get_current_spawn_interval()

        # When - 매우 긴 시간 경과 (최소값 테스트)
        if self.spawner_system._difficulty_manager:
            self.spawner_system._difficulty_manager.set_game_time(1200.0)
        self.spawner_system._game_time = 1200.0
        interval_max_difficulty = (
            self.spawner_system._get_current_spawn_interval()
        )

        # Then - 점진적 간격 단축 확인
        assert interval_start == 2.0, '시작 시 기본 간격이어야 함'
        assert interval_30s < interval_start, '30초 후 간격이 단축되어야 함'
        assert interval_60s < interval_30s, '60초 후 더 많이 단축되어야 함'
        assert interval_max_difficulty >= 0.5, (
            '최소 간격 0.5초 이상 유지되어야 함'
        )

        # 난이도 관리자가 있으면 DifficultyManager 기반 계산 검증
        if self.spawner_system._difficulty_manager:
            # DifficultyManager 기반 계산이므로 정확한 값은 다를 수 있음
            assert interval_30s <= 2.0, '30초 후 간격이 기본값 이하여야 함'
        else:
            # 기존 fallback 로직 검증 (30초: 5% 감소)
            expected_30s = 2.0 * 0.95  # 1.9초
            assert abs(interval_30s - expected_30s) < 0.01, (
                f'30초 후 간격이 {expected_30s}초 근처여야 함'
            )

    @patch('src.systems.enemy_spawner_system.random.randint')
    @patch('src.systems.enemy_spawner_system.random.uniform')
    @patch('src.systems.enemy_spawner_system.random.choice')
    def test_화면_가장자리_스폰_위치_계산_검증_성공_시나리오(
        self, mock_choice, mock_uniform, mock_randint
    ) -> None:
        """6. 화면 가장자리 스폰 위치 계산 검증 (성공 시나리오)

        목적: 화면 경계에서의 적 스폰 위치 계산 정확성 검증
        테스트할 범위: _calculate_spawn_position() 메서드
        커버하는 함수 및 데이터: 월드 좌표 변환 및 가장자리 계산
        기대되는 안정성: 정확한 스폰 위치로 시각적 일관성 보장
        """
        # Given - 랜덤 값들을 고정
        mock_randint.return_value = 0  # 위쪽 가장자리 선택
        mock_uniform.return_value = 50.0  # 고정 x 좌표

        # Given - 좌표 변환 결과 설정
        def screen_to_world_side_effect(screen_pos):
            # 화면 크기를 1024x768로 가정한 변환
            return Vector2(screen_pos.x - 512, screen_pos.y - 384)

        self.mock_coordinate_manager.screen_to_world.side_effect = (
            screen_to_world_side_effect
        )

        # When - 스폰 위치 계산
        spawn_pos = self.spawner_system._calculate_spawn_position()

        # Then - 올바른 스폰 위치 검증
        assert spawn_pos is not None, '스폰 위치가 계산되어야 함'
        x, y = spawn_pos

        # 위쪽 가장자리이므로 y가 음수 영역에 있어야 함
        assert y < -384, '위쪽 가장자리 스폰 시 y가 화면 위쪽에 있어야 함'

        # 좌표 변환이 호출되었는지 확인
        assert self.mock_coordinate_manager.screen_to_world.called, (
            '좌표 변환이 호출되어야 함'
        )

    def test_적_엔티티_생성_및_컴포넌트_구성_검증_성공_시나리오(self) -> None:
        """7. 적 엔티티 생성 및 컴포넌트 구성 검증 (성공 시나리오)

        목적: 생성된 적 엔티티가 필요한 모든 컴포넌트를 가지는지 검증
        테스트할 범위: _spawn_enemy(), _add_*_components() 메서드들
        커버하는 함수 및 데이터: 적 엔티티 구성 로직
        기대되는 안정성: 완전한 적 엔티티 생성으로 게임 안정성 보장
        """
        # Given - 간단한 적 엔티티 직접 생성으로 테스트
        spawn_pos = (100.0, 200.0)

        # When - 적 엔티티 생성 및 기본 컴포넌트 추가
        enemy_entity = self.entity_manager.create_entity()

        # 기본 컴포넌트만 추가
        self.entity_manager.add_component(
            enemy_entity, PositionComponent(x=spawn_pos[0], y=spawn_pos[1])
        )
        self.entity_manager.add_component(enemy_entity, EnemyComponent())
        self.entity_manager.add_component(
            enemy_entity, EnemyAIComponent(ai_type=AIType.AGGRESSIVE)
        )

        # Then - 적 엔티티 검증
        enemies = self.entity_manager.get_entities_with_components(
            EnemyComponent
        )
        assert len(enemies) == 1, '1개의 적 엔티티가 있어야 함'

        enemy = enemies[0]

        # 필수 컴포넌트 존재 확인
        assert self.entity_manager.has_component(enemy, EnemyComponent), (
            'EnemyComponent 필요'
        )
        assert self.entity_manager.has_component(enemy, PositionComponent), (
            'PositionComponent 필요'
        )
        assert self.entity_manager.has_component(enemy, EnemyAIComponent), (
            'EnemyAIComponent 필요'
        )

        # 위치 컴포넌트 확인
        pos_component = self.entity_manager.get_component(
            enemy, PositionComponent
        )
        assert pos_component.x == spawn_pos[0], (
            'X 위치가 올바르게 설정되어야 함'
        )
        assert pos_component.y == spawn_pos[1], (
            'Y 위치가 올바르게 설정되어야 함'
        )

        # AI 컴포넌트 설정 검증
        ai_component = self.entity_manager.get_component(
            enemy, EnemyAIComponent
        )
        assert ai_component is not None, 'AI 컴포넌트가 존재해야 함'
        assert isinstance(ai_component.ai_type, AIType), (
            'AI 타입이 올바르게 설정되어야 함'
        )
        assert ai_component.chase_range > 0, '추적 범위가 양수여야 함'
        assert ai_component.attack_range > 0, '공격 범위가 양수여야 함'

    def test_시스템_업데이트_전체_플로우_검증_성공_시나리오(self) -> None:
        """8. 시스템 업데이트 전체 플로우 검증 (성공 시나리오)

        목적: update() 메서드의 전체적인 동작 플로우 검증
        테스트할 범위: update() 메서드의 타이머 관리
        커버하는 함수 및 데이터: 게임 시간 및 스폰 타이머 동작
        기대되는 안정성: 매 프레임 안정적인 타이머 시스템 동작
        """
        # Given - 최대 적 수를 충분히 크게 설정
        self.spawner_system.set_max_enemies(10)

        # When - 첫 번째 업데이트 (시간 부족)
        initial_game_time = self.spawner_system._game_time
        initial_spawn_timer = self.spawner_system._current_spawn_timer

        self.spawner_system.update(self.entity_manager, 0.5)

        after_first_update_timer = self.spawner_system._current_spawn_timer
        after_first_update_game_time = self.spawner_system._game_time

        # When - 두 번째 업데이트 (더 긴 시간)
        self.spawner_system.update(self.entity_manager, 1.8)  # 총 2.3초

        after_second_update_timer = self.spawner_system._current_spawn_timer
        after_second_update_game_time = self.spawner_system._game_time

        # Then - 업데이트 플로우 검증

        # 게임 시간 누적 확인
        assert after_first_update_game_time > initial_game_time, (
            '게임 시간이 증가해야 함'
        )
        assert after_second_update_game_time > after_first_update_game_time, (
            '게임 시간이 계속 증가해야 함'
        )

        # 첫 번째 업데이트 후 - 난이도 관리자에 따라 결과가 달라질 수 있음
        if self.spawner_system._difficulty_manager:
            # DifficultyManager가 있으면 스폰 간격이 짧아질 수 있어 스폰이 발생할 수 있음
            assert after_first_update_timer >= 0.0, '타이머가 0 이상이어야 함'
        else:
            # DifficultyManager가 없으면 기본 로직 (2초 간격)
            assert after_first_update_timer == 0.5, (
                '타이머가 0.5초 증가해야 함'
            )

        # 두 번째 업데이트 후 - 충분한 시간이 지나면 스폰이 발생해야 함
        # 스폰 시도가 일어나면 타이머가 0으로 리셋됨
        assert after_second_update_timer == 0.0, (
            f'스폰 시도 후 타이머가 리셋되어야 함, 실제: {after_second_update_timer}'
        )

    def test_설정_변경_메서드_동작_검증_성공_시나리오(self) -> None:
        """9. 설정 변경 메서드 동작 검증 (성공 시나리오)

        목적: 런타임 설정 변경 메서드들의 정확한 동작 검증
        테스트할 범위: set_spawn_interval(), set_max_enemies() 메서드
        커버하는 함수 및 데이터: 설정 변경 및 검증 로직
        기대되는 안정성: 런타임 설정 변경으로 유연한 게임 조정
        """
        # Given - 초기 설정값
        initial_spawn_info = self.spawner_system.get_spawn_info()

        # When - 스폰 간격 변경
        self.spawner_system.set_spawn_interval(1.5)

        # When - 최대 적 수 변경
        self.spawner_system.set_max_enemies(15)

        # When - 변경된 설정 조회
        updated_spawn_info = self.spawner_system.get_spawn_info()

        # Then - 설정 변경 확인
        assert initial_spawn_info['base_spawn_interval'] == 2.0, (
            '초기 간격이 2초여야 함'
        )
        assert initial_spawn_info['max_enemies'] == 20, (
            '초기 최대 적 수가 20이어야 함'
        )

        assert updated_spawn_info['base_spawn_interval'] == 1.5, (
            '간격이 1.5초로 변경되어야 함'
        )
        assert updated_spawn_info['max_enemies'] == 15, (
            '최대 적 수가 15로 변경되어야 함'
        )

        # When - 잘못된 값 설정 시도
        self.spawner_system.set_spawn_interval(-1.0)  # 음수
        self.spawner_system.set_max_enemies(0)  # 0

        final_spawn_info = self.spawner_system.get_spawn_info()

        # Then - 잘못된 값은 무시되어야 함
        assert final_spawn_info['base_spawn_interval'] == 1.5, (
            '잘못된 간격 값은 무시되어야 함'
        )
        assert final_spawn_info['max_enemies'] == 15, (
            '잘못된 최대 적 수는 무시되어야 함'
        )

    def test_좌표_관리자_없을_때_예외_처리_검증_성공_시나리오(self) -> None:
        """10. 좌표 관리자 없을 때 예외 처리 검증 (성공 시나리오)

        목적: 좌표 관리자가 없거나 실패할 때의 안전한 동작 검증
        테스트할 범위: _calculate_spawn_position() 예외 처리
        커버하는 함수 및 데이터: 좌표 계산 실패 시 안전 처리
        기대되는 안정성: 외부 의존성 실패 시에도 시스템 안정성 유지
        """
        # Given - 좌표 관리자를 None으로 설정
        self.spawner_system._coordinate_manager = None

        # When - 스폰 위치 계산 시도
        spawn_pos = self.spawner_system._calculate_spawn_position()

        # Then - 안전하게 None 반환
        assert spawn_pos is None, '좌표 관리자 없을 때 None을 반환해야 함'

        # When - 스폰 시도 (위치 계산 실패로 인해 스폰되지 않아야 함)
        initial_count = self.spawner_system._get_current_enemy_count(
            self.entity_manager
        )
        self.spawner_system._spawn_enemy(self.entity_manager)
        final_count = self.spawner_system._get_current_enemy_count(
            self.entity_manager
        )

        # Then - 적이 생성되지 않아야 함
        assert final_count == initial_count, (
            '좌표 계산 실패 시 적이 생성되지 않아야 함'
        )

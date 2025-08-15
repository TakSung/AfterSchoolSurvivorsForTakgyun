"""
적 스포너 시스템 테스트 모듈

EnemySpawnerSystem의 시간 기반 적 생성, 최대 적 수 제한,
난이도 조정 메커니즘을 검증합니다.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.components.enemy_ai_component import AIType, EnemyAIComponent
from src.components.enemy_component import EnemyComponent
from src.components.health_component import HealthComponent
from src.components.position_component import PositionComponent
from src.components.render_component import RenderComponent
from src.core.component_registry import ComponentRegistry
from src.core.coordinate_manager import CoordinateManager
from src.core.difficulty_manager import DifficultyManager
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

        # 의존성 모킹 객체 생성
        self.mock_coordinate_manager = MagicMock(spec=CoordinateManager)
        self.mock_difficulty_manager = MagicMock(spec=DifficultyManager)

        # 모킹 객체의 기본 반환값 설정
        self.mock_coordinate_manager.screen_to_world.return_value = Vector2(
            100, 100
        )
        self.mock_difficulty_manager.get_spawn_interval_multiplier.return_value = (
            1.0
        )
        self.mock_difficulty_manager.get_health_multiplier.return_value = 1.0
        self.mock_difficulty_manager.get_speed_multiplier.return_value = 1.0

        # patch를 사용하여 get_instance 메서드 모킹
        patch_coord = patch(
            'src.systems.enemy_spawner_system.CoordinateManager.get_instance',
            return_value=self.mock_coordinate_manager,
        )
        patch_diff = patch(
            'src.systems.enemy_spawner_system.DifficultyManager.get_instance',
            return_value=self.mock_difficulty_manager,
        )

        # patch 시작 및 시스템 초기화
        self.patcher_coord = patch_coord.start()
        self.patcher_diff = patch_diff.start()

        self.spawner_system.initialize()

    def teardown_method(self) -> None:
        """각 테스트 메서드 후에 실행되는 정리"""
        patch.stopall()

    def test_시스템_초기화_및_기본_설정_검증_성공_시나리오(self) -> None:
        """1. 시스템 초기화 및 기본 설정 검증 (성공 시나리오)"""
        spawn_info = self.spawner_system.get_spawn_info()
        assert spawn_info['base_spawn_interval'] == 2.0
        assert spawn_info['max_enemies'] == 20
        assert spawn_info['current_spawn_interval'] == 2.0

    def test_스폰_시간_조건_확인_정확성_검증_성공_시나리오(self) -> None:
        """2. 스폰 시간 조건 확인 정확성 검증 (성공 시나리오)"""
        self.spawner_system._current_spawn_timer = 1.5
        assert self.spawner_system._is_spawn_time_ready() is False
        self.spawner_system._current_spawn_timer = 2.1
        assert self.spawner_system._is_spawn_time_ready() is True

    def test_최대_적_수_제한_동작_검증_성공_시나리오(self) -> None:
        """3. 최대 적 수 제한 동작 검증 (성공 시나리오)"""
        self.spawner_system.set_max_enemies(5)
        for i in range(4):
            enemy = self.entity_manager.create_entity()
            self.entity_manager.add_component(enemy, EnemyComponent())
            self.entity_manager.add_component(
                enemy, PositionComponent(x=i * 10, y=0)
            )
        assert (
            self.spawner_system._is_enemy_count_within_limit(
                self.entity_manager
            )
            is True
        )
        enemy = self.entity_manager.create_entity()
        self.entity_manager.add_component(enemy, EnemyComponent())
        self.entity_manager.add_component(enemy, PositionComponent(x=40, y=0))
        assert (
            self.spawner_system._is_enemy_count_within_limit(
                self.entity_manager
            )
            is False
        )

    def test_전체_스폰_조건_통합_검증_성공_시나리오(self) -> None:
        """4. 전체 스폰 조건 통합 검증 (성공 시나리오)"""
        self.spawner_system.set_max_enemies(3)

        self.spawner_system._current_spawn_timer = 1.0
        assert self.spawner_system._should_spawn_enemy(self.entity_manager) is False

        for i in range(3):
            enemy = self.entity_manager.create_entity()
            self.entity_manager.add_component(enemy, EnemyComponent())
            self.entity_manager.add_component(
                enemy, PositionComponent(x=i * 10, y=0)
            )
        self.spawner_system._current_spawn_timer = 3.0
        assert self.spawner_system._should_spawn_enemy(self.entity_manager) is False

        self.entity_manager.destroy_entity(enemy)
        assert self.spawner_system._should_spawn_enemy(self.entity_manager) is True

    def test_난이도_기반_스폰_간격_조정_검증_성공_시나리오(self) -> None:
        """5. 난이도 기반 스폰 간격 조정 검증 (성공 시나리오)"""
        base_interval = self.spawner_system._base_spawn_interval

        self.mock_difficulty_manager.get_spawn_interval_multiplier.return_value = 1.0
        assert self.spawner_system._get_current_spawn_interval() == base_interval

        self.mock_difficulty_manager.get_spawn_interval_multiplier.return_value = 0.8
        assert self.spawner_system._get_current_spawn_interval() == pytest.approx(
            base_interval * 0.8
        )

        self.mock_difficulty_manager.get_spawn_interval_multiplier.return_value = 0.5
        assert self.spawner_system._get_current_spawn_interval() == pytest.approx(
            base_interval * 0.5
        )

    @patch('src.systems.enemy_spawner_system.random.randint', return_value=0)
    @patch('src.systems.enemy_spawner_system.random.uniform', return_value=50.0)
    @patch(
        'src.systems.enemy_spawner_system.random.choice',
        return_value=AIType.AGGRESSIVE,
    )
    def test_적_생성_및_컴포넌트_구성_검증_성공_시나리오(
        self, mock_choice, mock_uniform, mock_randint
    ) -> None:
        """6. 적 엔티티 생성 및 컴포넌트 구성 검증 (성공 시나리오)"""
        self.spawner_system.update(self.entity_manager, 3.0)

        enemies = self.entity_manager.get_entities_with_components(EnemyComponent)
        assert len(enemies) == 1
        enemy = enemies[0]

        assert self.entity_manager.has_component(enemy, PositionComponent)
        assert self.entity_manager.has_component(enemy, HealthComponent)
        assert self.entity_manager.has_component(enemy, RenderComponent)
        assert self.entity_manager.has_component(enemy, EnemyAIComponent)

    def test_시스템_업데이트_전체_플로우_검증_성공_시나리오(self) -> None:
        """7. 시스템 업데이트 전체 플로우 검증 (성공 시나리오)"""
        self.spawner_system.update(self.entity_manager, 0.5)
        assert self.spawner_system._current_spawn_timer == 0.5
        assert len(self.entity_manager.get_entities_with_components(EnemyComponent)) == 0

        self.spawner_system.update(self.entity_manager, 1.8)
        assert self.spawner_system._current_spawn_timer == 0.0
        assert len(self.entity_manager.get_entities_with_components(EnemyComponent)) == 1

    def test_설정_변경_메서드_동작_검증_성공_시나리오(self) -> None:
        """8. 설정 변경 메서드 동작 검증 (성공 시나리오)"""
        self.spawner_system.set_spawn_interval(1.5)
        self.spawner_system.set_max_enemies(15)
        spawn_info = self.spawner_system.get_spawn_info()
        assert spawn_info['base_spawn_interval'] == 1.5
        assert spawn_info['max_enemies'] == 15

        self.spawner_system.set_spawn_interval(-1.0)
        self.spawner_system.set_max_enemies(0)
        final_spawn_info = self.spawner_system.get_spawn_info()
        assert final_spawn_info['base_spawn_interval'] == 1.5
        assert final_spawn_info['max_enemies'] == 15

    def test_좌표_관리자_없을_때_안전_처리_검증_성공_시나리오(self) -> None:
        """9. 좌표 관리자 없을 때 안전 처리 검증 (성공 시나리오)"""
        self.spawner_system._coordinate_manager = None
        assert self.spawner_system._calculate_spawn_position() is None

        initial_count = len(
            self.entity_manager.get_entities_with_components(EnemyComponent)
        )
        self.spawner_system._spawn_enemy(self.entity_manager)
        final_count = len(
            self.entity_manager.get_entities_with_components(EnemyComponent)
        )
        assert final_count == initial_count

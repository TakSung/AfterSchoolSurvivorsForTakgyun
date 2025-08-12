"""
Tests for WeaponSystem class.

무기 시스템의 자동 타겟팅, 쿨다운 관리, 투사체 생성,
거리 계산 등 핵심 기능을 검증하는 테스트 모음입니다.
"""

from unittest.mock import Mock, patch

from src.components.position_component import PositionComponent
from src.components.weapon_component import ProjectileType, WeaponComponent
from src.core.entity import Entity
from src.core.entity_manager import EntityManager
from src.systems.weapon_system import (
    BasicProjectileHandler,
    IProjectileHandler,
    WeaponSystem,
)


class MockEntity(Entity):
    """테스트용 Mock Entity 클래스"""

    def __init__(self, entity_id: str = '') -> None:
        super().__init__(entity_id=entity_id or f'test-entity-{id(self)}')


class MockEntityManager(EntityManager):
    """테스트용 Mock EntityManager 클래스"""

    def __init__(self) -> None:
        super().__init__()

    def create_entity(self) -> MockEntity:
        entity = MockEntity()
        self._entities[entity.entity_id] = entity
        self._active_entities.add(entity.entity_id)
        return entity


class TestWeaponSystem:
    """WeaponSystem에 대한 테스트 클래스"""

    def test_무기_시스템_초기화_검증_성공_시나리오(self) -> None:
        """1. 무기 시스템 초기화 검증 (성공 시나리오)

        목적: WeaponSystem이 올바르게 초기화되는지 확인
        테스트할 범위: 시스템 초기화, 기본 설정값, 핸들러 등록
        커버하는 함수 및 데이터: __init__, initialize()
        기대되는 안정성: 정상적인 시스템 초기화
        """
        # Given & When - 무기 시스템 생성
        weapon_system = WeaponSystem(priority=15)

        # Then - 초기화 상태 확인
        assert weapon_system.priority == 15, '설정한 우선순위가 반영되어야 함'
        assert weapon_system.enabled is True, '기본적으로 활성화되어야 함'
        assert weapon_system.initialized is False, '초기화 전에는 False여야 함'

        # 초기화 수행 및 확인
        weapon_system.initialize()
        assert weapon_system.initialized is True, '초기화 후에는 True여야 함'

        # 투사체 핸들러 등록 확인
        assert ProjectileType.BASIC in weapon_system._projectile_handlers, (
            'BASIC 투사체 핸들러가 등록되어야 함'
        )
        assert isinstance(
            weapon_system._projectile_handlers[ProjectileType.BASIC],
            BasicProjectileHandler,
        ), 'BASIC 타입에 대한 핸들러가 올바른 타입이어야 함'

    def test_필수_컴포넌트_타입_확인_검증_성공_시나리오(self) -> None:
        """2. 필수 컴포넌트 타입 확인 검증 (성공 시나리오)

        목적: WeaponSystem이 올바른 컴포넌트 타입을 요구하는지 확인
        테스트할 범위: get_required_components() 메서드
        커버하는 함수 및 데이터: get_required_components()
        기대되는 안정성: 정확한 필수 컴포넌트 타입 반환
        """
        # Given - 무기 시스템 생성
        weapon_system = WeaponSystem()

        # When - 필수 컴포넌트 타입 조회
        required_components = weapon_system.get_required_components()

        # Then - 필수 컴포넌트 확인
        assert len(required_components) == 2, '2개의 필수 컴포넌트가 있어야 함'
        assert WeaponComponent in required_components, (
            'WeaponComponent가 필수 컴포넌트여야 함'
        )
        assert PositionComponent in required_components, (
            'PositionComponent가 필수 컴포넌트여야 함'
        )

    def test_가장_가까운_적_찾기_정확성_검증_성공_시나리오(self) -> None:
        """3. 가장 가까운 적 찾기 정확성 검증 (성공 시나리오)

        목적: 거리 계산을 통한 가장 가까운 적 선택이 정확한지 확인
        테스트할 범위: _find_closest_enemy() 메서드
        커버하는 함수 및 데이터: _find_closest_enemy()
        기대되는 안정성: 정확한 거리 기반 타겟 선택
        """
        # Given - 무기 시스템과 Mock 엔티티 매니저
        weapon_system = WeaponSystem()
        entity_manager = MockEntityManager()

        # 무기 위치 설정 (0, 0)
        weapon_pos = PositionComponent(x=0.0, y=0.0)
        weapon_range = 300.0

        # 적 엔티티들 생성 및 위치 설정
        enemy1 = entity_manager.create_entity()
        enemy1_pos = PositionComponent(x=100.0, y=0.0)  # 거리: 100
        entity_manager.add_component(enemy1, enemy1_pos)

        enemy2 = entity_manager.create_entity()
        enemy2_pos = PositionComponent(x=0.0, y=50.0)  # 거리: 50 (가장 가까움)
        entity_manager.add_component(enemy2, enemy2_pos)

        enemy3 = entity_manager.create_entity()
        enemy3_pos = PositionComponent(x=200.0, y=200.0)  # 거리: ~283
        entity_manager.add_component(enemy3, enemy3_pos)

        enemy_entities = [enemy1, enemy2, enemy3]

        # When - 가장 가까운 적 찾기
        closest_enemy = weapon_system._find_closest_enemy(
            weapon_pos, weapon_range, enemy_entities, entity_manager
        )

        # Then - 가장 가까운 적 확인
        assert closest_enemy == enemy2, (
            '거리 50인 enemy2가 가장 가까운 적이어야 함'
        )

    def test_사거리_밖_적_제외_검증_성공_시나리오(self) -> None:
        """4. 사거리 밖 적 제외 검증 (성공 시나리오)

        목적: 무기 사거리를 벗어난 적이 타겟에서 제외되는지 확인
        테스트할 범위: _find_closest_enemy()의 사거리 필터링
        커버하는 함수 및 데이터: _find_closest_enemy() range checking
        기대되는 안정성: 사거리 기반 정확한 타겟 필터링
        """
        # Given - 무기 시스템과 Mock 엔티티 매니저
        weapon_system = WeaponSystem()
        entity_manager = MockEntityManager()

        # 무기 위치와 짧은 사거리 설정
        weapon_pos = PositionComponent(x=0.0, y=0.0)
        weapon_range = 100.0  # 짧은 사거리

        # 사거리 밖의 적들만 생성
        enemy1 = entity_manager.create_entity()
        enemy1_pos = PositionComponent(x=150.0, y=0.0)  # 거리: 150 (사거리 밖)
        entity_manager.add_component(enemy1, enemy1_pos)

        enemy2 = entity_manager.create_entity()
        enemy2_pos = PositionComponent(x=0.0, y=120.0)  # 거리: 120 (사거리 밖)
        entity_manager.add_component(enemy2, enemy2_pos)

        enemy_entities = [enemy1, enemy2]

        # When - 가장 가까운 적 찾기
        closest_enemy = weapon_system._find_closest_enemy(
            weapon_pos, weapon_range, enemy_entities, entity_manager
        )

        # Then - 타겟이 없어야 함
        assert closest_enemy is None, (
            '사거리 밖의 적들만 있으면 타겟이 없어야 함'
        )

    def test_사거리_내_가장_가까운_적_선택_검증_성공_시나리오(self) -> None:
        """5. 사거리 내 가장 가까운 적 선택 검증 (성공 시나리오)

        목적: 사거리 내에 여러 적이 있을 때 가장 가까운 적을 선택하는지 확인
        테스트할 범위: _find_closest_enemy()의 거리 비교 로직
        커버하는 함수 및 데이터: _find_closest_enemy() distance comparison
        기대되는 안정성: 사거리 내 최단 거리 적 선택
        """
        # Given - 무기 시스템과 Mock 엔티티 매니저
        weapon_system = WeaponSystem()
        entity_manager = MockEntityManager()

        # 무기 위치와 사거리 설정
        weapon_pos = PositionComponent(x=0.0, y=0.0)
        weapon_range = 200.0

        # 사거리 내 적들 생성 (일부는 사거리 밖)
        enemy_in_range1 = entity_manager.create_entity()
        enemy_in_range1_pos = PositionComponent(x=80.0, y=0.0)  # 거리: 80
        entity_manager.add_component(enemy_in_range1, enemy_in_range1_pos)

        enemy_in_range2 = entity_manager.create_entity()
        enemy_in_range2_pos = PositionComponent(
            x=0.0, y=60.0
        )  # 거리: 60 (최단)
        entity_manager.add_component(enemy_in_range2, enemy_in_range2_pos)

        enemy_out_range = entity_manager.create_entity()
        enemy_out_range_pos = PositionComponent(
            x=250.0, y=0.0
        )  # 거리: 250 (사거리 밖)
        entity_manager.add_component(enemy_out_range, enemy_out_range_pos)

        enemy_entities = [enemy_in_range1, enemy_in_range2, enemy_out_range]

        # When - 가장 가까운 적 찾기
        closest_enemy = weapon_system._find_closest_enemy(
            weapon_pos, weapon_range, enemy_entities, entity_manager
        )

        # Then - 사거리 내 가장 가까운 적 확인
        assert closest_enemy == enemy_in_range2, (
            '사거리 내에서 거리 60인 적이 선택되어야 함'
        )

    @patch('time.time')
    def test_쿨다운_완료_시_공격_처리_검증_성공_시나리오(
        self, mock_time: Mock
    ) -> None:
        """6. 쿨다운 완료 시 공격 처리 검증 (성공 시나리오)

        목적: 무기 쿨다운이 완료되었을 때 공격이 정상적으로 처리되는지 확인
        테스트할 범위: _process_weapon_attack() 메서드의 쿨다운 검사
        커버하는 함수 및 데이터: _process_weapon_attack(), can_attack()
        기대되는 안정성: 쿨다운 완료 시 정상 공격 처리
        """
        # Given - 현재 시간 Mock 설정
        current_time = 10.0
        mock_time.return_value = current_time

        # 무기 시스템과 Mock 엔티티 매니저
        weapon_system = WeaponSystem()
        entity_manager = MockEntityManager()

        # 무기 엔티티와 컴포넌트 생성
        weapon_entity = entity_manager.create_entity()
        weapon_comp = WeaponComponent(
            attack_speed=2.0,  # 0.5초 쿨다운
            last_attack_time=9.0,  # 1초 전 마지막 공격 (쿨다운 완료)
            current_target_id='target-42',
        )
        weapon_pos = PositionComponent(x=100.0, y=100.0)

        entity_manager.add_component(weapon_entity, weapon_comp)
        entity_manager.add_component(weapon_entity, weapon_pos)

        # 타겟 엔티티 생성
        target_entity = MockEntity('target-42')
        entity_manager._entities[target_entity.entity_id] = target_entity
        target_pos = PositionComponent(x=150.0, y=100.0)
        entity_manager.add_component(target_entity, target_pos)

        # Mock handler로 투사체 생성 확인
        mock_handler = Mock(spec=IProjectileHandler)
        mock_projectile = Mock()
        mock_handler.create_projectile.return_value = mock_projectile
        weapon_system._projectile_handlers[ProjectileType.BASIC] = mock_handler

        # When - 공격 처리
        weapon_system._process_weapon_attack(
            weapon_entity, entity_manager, current_time
        )

        # Then - 공격 실행 확인
        mock_handler.create_projectile.assert_called_once()
        assert weapon_comp.last_attack_time == current_time, (
            '마지막 공격 시간이 현재 시간으로 업데이트되어야 함'
        )

    @patch('time.time')
    def test_쿨다운_미완료_시_공격_대기_검증_성공_시나리오(
        self, mock_time: Mock
    ) -> None:
        """7. 쿨다운 미완료 시 공격 대기 검증 (성공 시나리오)

        목적: 무기 쿨다운이 완료되지 않았을 때 공격하지 않는지 확인
        테스트할 범위: _process_weapon_attack() 메서드의 쿨다운 검사
        커버하는 함수 및 데이터: _process_weapon_attack(), can_attack()
        기대되는 안정성: 쿨다운 미완료 시 공격 대기
        """
        # Given - 현재 시간 Mock 설정
        current_time = 10.0
        mock_time.return_value = current_time

        # 무기 시스템과 Mock 엔티티 매니저
        weapon_system = WeaponSystem()
        entity_manager = MockEntityManager()

        # 무기 엔티티와 컴포넌트 생성 (쿨다운 미완료)
        weapon_entity = entity_manager.create_entity()
        weapon_comp = WeaponComponent(
            attack_speed=2.0,  # 0.5초 쿨다운
            last_attack_time=9.8,  # 0.2초 전 마지막 공격 (쿨다운 미완료)
            current_target_id='target-42',
        )
        weapon_pos = PositionComponent(x=100.0, y=100.0)

        entity_manager.add_component(weapon_entity, weapon_comp)
        entity_manager.add_component(weapon_entity, weapon_pos)

        # Mock handler로 투사체 생성 확인
        mock_handler = Mock(spec=IProjectileHandler)
        weapon_system._projectile_handlers[ProjectileType.BASIC] = mock_handler

        initial_attack_time = weapon_comp.last_attack_time

        # When - 공격 처리
        weapon_system._process_weapon_attack(
            weapon_entity, entity_manager, current_time
        )

        # Then - 공격하지 않았는지 확인
        mock_handler.create_projectile.assert_not_called()
        assert weapon_comp.last_attack_time == initial_attack_time, (
            '쿨다운 미완료 시 마지막 공격 시간이 변경되지 않아야 함'
        )

    def test_타겟_없을_시_공격_대기_검증_성공_시나리오(self) -> None:
        """8. 타겟이 없을 시 공격 대기 검증 (성공 시나리오)

        목적: 현재 타겟이 없을 때 공격하지 않는지 확인
        테스트할 범위: _process_weapon_attack() 메서드의 타겟 검사
        커버하는 함수 및 데이터: _process_weapon_attack() target validation
        기대되는 안정성: 타겟 없을 시 공격 대기
        """
        # Given - 무기 시스템과 Mock 엔티티 매니저
        weapon_system = WeaponSystem()
        entity_manager = MockEntityManager()
        current_time = 10.0

        # 무기 엔티티와 컴포넌트 생성 (타겟 없음)
        weapon_entity = entity_manager.create_entity()
        weapon_comp = WeaponComponent(
            attack_speed=2.0,
            last_attack_time=0.0,  # 충분히 오래 전 (쿨다운 완료)
            current_target_id=None,  # 타겟 없음
        )
        weapon_pos = PositionComponent(x=100.0, y=100.0)

        entity_manager.add_component(weapon_entity, weapon_comp)
        entity_manager.add_component(weapon_entity, weapon_pos)

        # Mock handler로 투사체 생성 확인
        mock_handler = Mock(spec=IProjectileHandler)
        weapon_system._projectile_handlers[ProjectileType.BASIC] = mock_handler

        # When - 공격 처리
        weapon_system._process_weapon_attack(
            weapon_entity, entity_manager, current_time
        )

        # Then - 공격하지 않았는지 확인
        mock_handler.create_projectile.assert_not_called()


class TestBasicProjectileHandler:
    """BasicProjectileHandler에 대한 테스트 클래스"""

    def test_기본_투사체_핸들러_생성_검증_성공_시나리오(self) -> None:
        """9. 기본 투사체 핸들러 생성 검증 (성공 시나리오)

        목적: BasicProjectileHandler가 정상적으로 생성되는지 확인
        테스트할 범위: BasicProjectileHandler 초기화
        커버하는 함수 및 데이터: __init__
        기대되는 안정성: 정상적인 핸들러 객체 생성
        """
        # Given & When - 기본 투사체 핸들러 생성
        handler = BasicProjectileHandler()

        # Then - 핸들러 객체 확인
        assert isinstance(handler, IProjectileHandler), (
            'IProjectileHandler 인터페이스를 구현해야 함'
        )
        assert isinstance(handler, BasicProjectileHandler), (
            'BasicProjectileHandler 타입이어야 함'
        )

    def test_기본_투사체_생성_호출_검증_성공_시나리오(self) -> None:
        """10. 기본 투사체 생성 호출 검증 (성공 시나리오)

        목적: create_projectile 메서드가 호출 가능한지 확인
        테스트할 범위: create_projectile() 메서드 호출
        커버하는 함수 및 데이터: create_projectile()
        기대되는 안정성: 메서드 호출 시 예외 발생하지 않음
        """
        # Given - 기본 투사체 핸들러와 테스트 데이터
        handler = BasicProjectileHandler()
        weapon = WeaponComponent()
        start_pos = (100.0, 100.0)
        target_pos = (200.0, 200.0)
        entity_manager = MockEntityManager()

        # When - 투사체 생성 호출
        result = handler.create_projectile(
            weapon, start_pos, target_pos, entity_manager
        )

        # Then - 현재 구현에서는 None 반환 확인
        assert result is None, '현재 기본 구현에서는 None을 반환해야 함'

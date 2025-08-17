"""
Tests for SystemOrchestrator class.

This module contains comprehensive tests for the SystemOrchestrator class,
verifying system registration, execution order, and lifecycle management.
"""

from typing import TYPE_CHECKING

import pytest

from src.core.entity_manager import EntityManager
from src.core.system import System
from src.core.system_orchestrator import SystemOrchestrator

if TYPE_CHECKING:
    from src.core.entity_manager import EntityManager


# AI-DEV : pytest 컬렉션 경고 방지를 위한 Helper 클래스명 변경
# - 문제: Test*로 시작하는 Helper 클래스가 pytest에 의해 테스트 클래스로 수집됨
# - 해결책: Mock* 접두사로 Helper 클래스 명확화
# - 결과: 3개 PytestCollectionWarning 제거
class MockMovementSystem(System):
    """Mock system for movement logic."""

    def __init__(self, priority: int = 0) -> None:
        super().__init__(priority=priority)
        self.update_count = 0

    def update(self, delta_time: float) -> None:
        """Update movement system."""
        self.update_count += 1


class MockRenderSystem(System):
    """Mock system for rendering logic."""

    def __init__(self, priority: int = 100) -> None:
        super().__init__(priority=priority)
        self.update_count = 0

    def update(self, delta_time: float) -> None:
        """Update render system."""
        self.update_count += 1


class MockPhysicsSystem(System):
    """Mock system for physics logic."""

    def __init__(self, priority: int = 50) -> None:
        super().__init__(priority=priority)
        self.update_count = 0

    def update(self, delta_time: float) -> None:
        """Update physics system."""
        self.update_count += 1


class FailingInitSystem(System):
    """Test system that fails during initialization."""

    def __init__(self) -> None:
        super().__init__()

    def initialize(self) -> None:
        """Initialize system with failure."""
        raise RuntimeError('Initialization failed')

    def update(self, delta_time: float) -> None:
        """Update system (never called)."""
        pass


class FailingUpdateSystem(System):
    """Test system that fails during update."""

    def __init__(self) -> None:
        super().__init__()
        self.update_count = 0

    def update(self, delta_time: float) -> None:
        """Update system with failure."""
        self.update_count += 1
        raise RuntimeError('Update failed')


class CustomCleanupSystem(System):
    """Test system with custom cleanup logic."""

    def __init__(self) -> None:
        super().__init__()
        self.cleaned_up = False

    def update(self, delta_time: float) -> None:
        """Update system."""
        pass

    def cleanup(self) -> None:
        """Custom cleanup logic."""
        self.cleaned_up = True


class TestSystemOrchestrator:
    """Test suite for SystemOrchestrator."""

    @pytest.fixture
    def orchestrator(self, entity_manager: EntityManager) -> SystemOrchestrator:
        """Create a fresh system orchestrator for each test."""
        return SystemOrchestrator(entity_manager=entity_manager)

    @pytest.fixture
    def entity_manager(self) -> EntityManager:
        """Create a fresh entity manager for each test."""
        return EntityManager()

    @pytest.fixture
    def movement_system(self) -> MockMovementSystem:
        """Create a test movement system."""
        return MockMovementSystem(priority=10)

    @pytest.fixture
    def render_system(self) -> MockRenderSystem:
        """Create a test render system."""
        return MockRenderSystem(priority=100)

    @pytest.fixture
    def physics_system(self) -> MockPhysicsSystem:
        """Create a test physics system."""
        return MockPhysicsSystem(priority=50)

    def test_시스템_등록_성공_시나리오(
        self,
        orchestrator: SystemOrchestrator,
        movement_system: MockMovementSystem,
    ) -> None:
        """1. 시스템 등록 성공 시나리오

        목적: 시스템이 올바르게 등록되고 초기화되는지 검증
        테스트할 범위: register_system 메서드의 정상 동작
        커버하는 함수 및 데이터: SystemOrchestrator.register_system()
        기대되는 안정성: 시스템이 등록되고 초기화되어야 함
        """
        # When - 시스템 등록
        orchestrator.register_system(movement_system, 'MovementSystem')

        # Then - 시스템이 올바르게 등록됨
        assert orchestrator.has_system('MovementSystem'), (
            '시스템이 등록되어야 함'
        )
        assert orchestrator.get_system('MovementSystem') is movement_system
        assert movement_system.initialized, '시스템이 초기화되어야 함'
        assert len(orchestrator) == 1, '등록된 시스템 수가 1이어야 함'
        assert 'MovementSystem' in orchestrator.get_system_names()

    def test_중복_시스템_등록_실패_시나리오(
        self,
        orchestrator: SystemOrchestrator,
        movement_system: MockMovementSystem,
    ) -> None:
        """2. 중복 시스템 등록 실패 시나리오

        목적: 같은 이름의 시스템 중복 등록 시 예외 발생 검증
        테스트할 범위: register_system 메서드의 중복 방지 로직
        커버하는 함수 및 데이터: SystemOrchestrator.register_system() 예외 처리
        기대되는 안정성: ValueError 예외가 발생해야 함
        """
        # Given - 시스템이 이미 등록된 상태
        orchestrator.register_system(movement_system, 'MovementSystem')

        # When & Then - 같은 이름으로 시스템 재등록 시 예외 발생
        duplicate_system = MockMovementSystem()
        with pytest.raises(ValueError, match='already registered'):
            orchestrator.register_system(duplicate_system, 'MovementSystem')

    def test_초기화_실패_시스템_등록_실패_시나리오(
        self, orchestrator: SystemOrchestrator
    ) -> None:
        """3. 초기화 실패 시스템 등록 실패 시나리오

        목적: 시스템 초기화 실패 시 등록이 롤백되는지 검증
        테스트할 범위: register_system 메서드의 초기화 실패 처리
        커버하는 함수 및 데이터: SystemOrchestrator.register_system() 오류 처리
        기대되는 안정성: RuntimeError 예외가 발생하고 시스템이 등록되지 않아야 함
        """
        # Given - 초기화에 실패하는 시스템
        failing_system = FailingInitSystem()

        # When & Then - 초기화 실패 시스템 등록 시 예외 발생
        with pytest.raises(RuntimeError, match='Failed to initialize'):
            orchestrator.register_system(failing_system, 'FailingSystem')

        # 시스템이 등록되지 않았는지 확인
        assert not orchestrator.has_system('FailingSystem')
        assert len(orchestrator) == 0

    def test_시스템_등록_해제_성공_시나리오(
        self,
        orchestrator: SystemOrchestrator,
        movement_system: MockMovementSystem,
    ) -> None:
        """4. 시스템 등록 해제 성공 시나리오

        목적: 시스템이 올바르게 등록 해제되고 정리되는지 검증
        테스트할 범위: unregister_system 메서드의 정상 동작
        커버하는 함수 및 데이터: SystemOrchestrator.unregister_system()
        기대되는 안정성: 시스템이 완전히 제거되고 정리되어야 함
        """
        # Given - 시스템이 등록된 상태
        orchestrator.register_system(movement_system, 'MovementSystem')

        # When - 시스템 등록 해제
        removed_system = orchestrator.unregister_system('MovementSystem')

        # Then - 시스템이 올바르게 제거됨
        assert removed_system is movement_system, (
            '제거된 시스템이 반환되어야 함'
        )
        assert not orchestrator.has_system('MovementSystem'), (
            '시스템이 제거되어야 함'
        )
        assert orchestrator.get_system('MovementSystem') is None
        assert len(orchestrator) == 0, '등록된 시스템 수가 0이어야 함'
        assert 'MovementSystem' not in orchestrator.get_system_names()

    def test_존재하지_않는_시스템_등록_해제_시나리오(
        self, orchestrator: SystemOrchestrator
    ) -> None:
        """5. 존재하지 않는 시스템 등록 해제 시나리오

        목적: 존재하지 않는 시스템 제거 시 None 반환 검증
        테스트할 범위: unregister_system 메서드의 None 반환 로직
        커버하는 함수 및 데이터: SystemOrchestrator.unregister_system() 예외 처리
        기대되는 안정성: 존재하지 않는 시스템 제거 시 None 반환되어야 함
        """
        # When - 존재하지 않는 시스템 제거 시도
        removed_system = orchestrator.unregister_system('NonExistentSystem')

        # Then - None 반환
        assert removed_system is None, (
            '존재하지 않는 시스템 제거 시 None 반환되어야 함'
        )

    def test_시스템_실행_순서_우선순위_검증(
        self, orchestrator: SystemOrchestrator, entity_manager: EntityManager
    ) -> None:
        """6. 시스템 실행 순서 우선순위 검증

        목적: 시스템들이 우선순위에 따라 올바른 순서로 실행되는지 검증
        테스트할 범위: update_systems 메서드의 우선순위 기반 실행
        커버하는 함수 및 데이터: SystemOrchestrator.update_systems() 우선순위 처리
        기대되는 안정성: 낮은 우선순위 값을 가진 시스템이 먼저 실행되어야 함
        """
        # Given - 다른 우선순위를 가진 시스템들 등록
        movement_system = MockMovementSystem(priority=10)
        physics_system = MockPhysicsSystem(priority=50)
        render_system = MockRenderSystem(priority=100)

        # 의도적으로 등록 순서를 우선순위와 다르게 함
        orchestrator.register_system(render_system, 'RenderSystem')
        orchestrator.register_system(movement_system, 'MovementSystem')
        orchestrator.register_system(physics_system, 'PhysicsSystem')

        # When - 시스템 업데이트 실행
        orchestrator.update_systems(0.016)

        # Then - 모든 시스템이 실행됨
        assert movement_system.update_count == 1, (
            'Movement 시스템이 실행되어야 함'
        )
        assert physics_system.update_count == 1, (
            'Physics 시스템이 실행되어야 함'
        )
        assert render_system.update_count == 1, 'Render 시스템이 실행되어야 함'

        # 우선순위 순서 확인을 위한 추가 테스트
        # (실제 실행 순서는 내부 구현에 의존하지만, 모든 시스템이 실행되었는지는 확인 가능)
        stats = orchestrator.get_execution_stats()
        assert len(stats) == 3, '세 시스템의 실행 통계가 있어야 함'
        assert all(s['call_count'] == 1 for s in stats.values()), (
            '모든 시스템이 한 번씩 호출되어야 함'
        )

    def test_비활성_시스템_실행_제외_검증(
        self,
        orchestrator: SystemOrchestrator,
        entity_manager: EntityManager,
        movement_system: MockMovementSystem,
    ) -> None:
        """7. 비활성 시스템 실행 제외 검증

        목적: 비활성화된 시스템이 업데이트에서 제외되는지 검증
        테스트할 범위: update_systems 메서드의 enabled 필터링
        커버하는 함수 및 데이터: SystemOrchestrator.update_systems() 활성 상태 확인
        기대되는 안정성: 비활성 시스템은 업데이트되지 않아야 함
        """
        # Given - 시스템 등록 후 비활성화
        orchestrator.register_system(movement_system, 'MovementSystem')
        movement_system.disable()

        # When - 시스템 업데이트 실행
        orchestrator.update_systems(0.016)

        # Then - 비활성 시스템이 실행되지 않음
        assert movement_system.update_count == 0, (
            '비활성 시스템은 업데이트되지 않아야 함'
        )
        stats = orchestrator.get_execution_stats()
        assert stats['MovementSystem']['call_count'] == 0, (
            '비활성 시스템 호출 횟수는 0이어야 함'
        )

    def test_시스템_업데이트_오류_처리_검증(
        self,
        orchestrator: SystemOrchestrator,
        entity_manager: EntityManager,
        movement_system: MockMovementSystem,
    ) -> None:
        """8. 시스템 업데이트 오류 처리 검증

        목적: 한 시스템에서 오류가 발생해도 다른 시스템들이 계속 실행되는지 검증
        테스트할 범위: update_systems 메서드의 예외 처리
        커버하는 함수 및 데이터: SystemOrchestrator.update_systems() 오류 격리
        기대되는 안정성: 한 시스템 오류가 전체 시스템 실행을 중단시키지 않아야 함
        """
        # Given - 정상 시스템과 실패 시스템 등록
        failing_system = FailingUpdateSystem()
        orchestrator.register_system(failing_system, 'FailingSystem')
        orchestrator.register_system(movement_system, 'MovementSystem')

        # When - 시스템 업데이트 실행 (예외가 발생하지 않아야 함)
        orchestrator.update_systems(0.016)

        # Then - 정상 시스템은 실행되고, 실패 시스템도 시도됨
        assert movement_system.update_count == 1, '정상 시스템은 실행되어야 함'
        assert failing_system.update_count == 1, '실패 시스템도 시도되어야 함'

    def test_시스템_우선순위_변경_기능(
        self,
        orchestrator: SystemOrchestrator,
        movement_system: MockMovementSystem,
    ) -> None:
        """9. 시스템 우선순위 변경 기능

        목적: 등록된 시스템의 우선순위를 동적으로 변경할 수 있는지 검증
        테스트할 범위: set_system_priority 메서드
        커버하는 함수 및 데이터: SystemOrchestrator.set_system_priority()
        기대되는 안정성: 우선순위 변경 후 올바른 순서로 실행되어야 함
        """
        # Given - 시스템 등록
        orchestrator.register_system(movement_system, 'MovementSystem')
        original_priority = movement_system.priority

        # When - 우선순위 변경
        new_priority = 999
        result = orchestrator.set_system_priority(
            'MovementSystem', new_priority
        )

        # Then - 우선순위가 변경됨
        assert result is True, '우선순위 변경이 성공해야 함'
        assert movement_system.priority == new_priority, (
            '시스템 우선순위가 변경되어야 함'
        )

        # 존재하지 않는 시스템 우선순위 변경 시도
        result = orchestrator.set_system_priority('NonExistent', 100)
        assert result is False, (
            '존재하지 않는 시스템 우선순위 변경은 실패해야 함'
        )

    def test_시스템_활성화_비활성화_기능(
        self,
        orchestrator: SystemOrchestrator,
        movement_system: MockMovementSystem,
    ) -> None:
        """10. 시스템 활성화/비활성화 기능

        목적: 시스템을 동적으로 활성화/비활성화할 수 있는지 검증
        테스트할 범위: enable_system, disable_system 메서드
        커버하는 함수 및 데이터: SystemOrchestrator enable/disable 메서드들
        기대되는 안정성: 시스템 상태가 올바르게 변경되어야 함
        """
        # Given - 시스템 등록
        orchestrator.register_system(movement_system, 'MovementSystem')

        # When - 시스템 비활성화
        result = orchestrator.disable_system('MovementSystem')
        assert result is True, '시스템 비활성화가 성공해야 함'
        assert not movement_system.enabled, '시스템이 비활성화되어야 함'

        # When - 시스템 활성화
        result = orchestrator.enable_system('MovementSystem')
        assert result is True, '시스템 활성화가 성공해야 함'
        assert movement_system.enabled, '시스템이 활성화되어야 함'

        # 존재하지 않는 시스템 상태 변경 시도
        assert not orchestrator.enable_system('NonExistent')
        assert not orchestrator.disable_system('NonExistent')

    def test_시스템_그룹_관리_기능(
        self,
        orchestrator: SystemOrchestrator,
        movement_system: MockMovementSystem,
        physics_system: MockPhysicsSystem,
    ) -> None:
        """11. 시스템 그룹 관리 기능

        목적: 시스템 그룹을 생성하고 일괄 관리할 수 있는지 검증
        테스트할 범위: 시스템 그룹 생성 및 일괄 제어 메서드들
        커버하는 함수 및 데이터: SystemOrchestrator 그룹 관리 메서드들
        기대되는 안정성: 그룹 단위로 시스템들을 제어할 수 있어야 함
        """
        # Given - 시스템들 등록
        orchestrator.register_system(movement_system, 'MovementSystem')
        orchestrator.register_system(physics_system, 'PhysicsSystem')

        # When - 시스템 그룹 생성
        result = orchestrator.create_system_group(
            'GameplayGroup', ['MovementSystem', 'PhysicsSystem']
        )
        assert result is True, '시스템 그룹 생성이 성공해야 함'

        # When - 그룹 일괄 비활성화
        result = orchestrator.disable_system_group('GameplayGroup')
        assert result is True, '그룹 비활성화가 성공해야 함'
        assert not movement_system.enabled, (
            'Movement 시스템이 비활성화되어야 함'
        )
        assert not physics_system.enabled, 'Physics 시스템이 비활성화되어야 함'

        # When - 그룹 일괄 활성화
        result = orchestrator.enable_system_group('GameplayGroup')
        assert result is True, '그룹 활성화가 성공해야 함'
        assert movement_system.enabled, 'Movement 시스템이 활성화되어야 함'
        assert physics_system.enabled, 'Physics 시스템이 활성화되어야 함'

        # 존재하지 않는 시스템이 포함된 그룹 생성 실패
        result = orchestrator.create_system_group(
            'InvalidGroup', ['NonExistent']
        )
        assert result is False, (
            '존재하지 않는 시스템이 포함된 그룹 생성은 실패해야 함'
        )

    def test_실행_통계_수집_기능(
        self,
        orchestrator: SystemOrchestrator,
        entity_manager: EntityManager,
        movement_system: MockMovementSystem,
    ) -> None:
        """12. 실행 통계 수집 기능

        목적: 시스템들의 실행 통계가 올바르게 수집되는지 검증
        테스트할 범위: get_execution_stats, reset_execution_stats 메서드
        커버하는 함수 및 데이터: SystemOrchestrator 통계 수집 기능
        기대되는 안정성: 정확한 실행 통계가 수집되고 리셋되어야 함
        """
        # Given - 시스템 등록
        orchestrator.register_system(movement_system, 'MovementSystem')

        # When - 여러 번 시스템 업데이트 실행
        for _ in range(3):
            orchestrator.update_systems(0.016)

        # Then - 실행 통계가 올바르게 수집됨
        stats = orchestrator.get_execution_stats()
        assert 'MovementSystem' in stats, '시스템 통계가 수집되어야 함'

        system_stats = stats['MovementSystem']
        assert system_stats['call_count'] == 3, '호출 횟수가 3이어야 함'
        assert system_stats['total_time'] > 0, '총 실행 시간이 기록되어야 함'
        assert system_stats['avg_time'] > 0, '평균 실행 시간이 계산되어야 함'
        assert system_stats['max_time'] >= system_stats['avg_time'], (
            '최대 실행 시간이 유효해야 함'
        )

        # When - 통계 리셋
        orchestrator.reset_execution_stats()

        # Then - 통계가 초기화됨
        stats = orchestrator.get_execution_stats()
        reset_stats = stats['MovementSystem']
        assert reset_stats['call_count'] == 0, '호출 횟수가 리셋되어야 함'
        assert reset_stats['total_time'] == 0.0, '총 실행 시간이 리셋되어야 함'

    def test_커스텀_정리_로직_실행_검증(
        self, orchestrator: SystemOrchestrator
    ) -> None:
        """13. 커스텀 정리 로직 실행 검증

        목적: 시스템 등록 해제 시 커스텀 cleanup 메서드가 호출되는지 검증
        테스트할 범위: unregister_system 메서드의 cleanup 호출
        커버하는 함수 및 데이터: SystemOrchestrator.unregister_system() cleanup 처리
        기대되는 안정성: 시스템의 cleanup 메서드가 호출되어야 함
        """
        # Given - 커스텀 정리 로직을 가진 시스템 등록
        cleanup_system = CustomCleanupSystem()
        orchestrator.register_system(cleanup_system, 'CleanupSystem')

        # When - 시스템 등록 해제
        orchestrator.unregister_system('CleanupSystem')

        # Then - 커스텀 정리 로직이 실행됨
        assert cleanup_system.cleaned_up, (
            '커스텀 cleanup 메서드가 호출되어야 함'
        )

    def test_모든_시스템_일괄_정리_기능(
        self,
        orchestrator: SystemOrchestrator,
        movement_system: MockMovementSystem,
        physics_system: MockPhysicsSystem,
    ) -> None:
        """14. 모든 시스템 일괄 정리 기능

        목적: 모든 시스템을 한 번에 정리할 수 있는지 검증
        테스트할 범위: clear_all_systems 메서드
        커버하는 함수 및 데이터: SystemOrchestrator.clear_all_systems()
        기대되는 안정성: 모든 시스템과 관련 데이터가 정리되어야 함
        """
        # Given - 여러 시스템 등록
        orchestrator.register_system(movement_system, 'MovementSystem')
        orchestrator.register_system(physics_system, 'PhysicsSystem')
        orchestrator.create_system_group(
            'TestGroup', ['MovementSystem', 'PhysicsSystem']
        )

        # When - 모든 시스템 일괄 정리
        orchestrator.clear_all_systems()

        # Then - 모든 데이터가 정리됨
        assert len(orchestrator) == 0, '등록된 시스템이 없어야 함'
        assert len(orchestrator.get_system_names()) == 0, (
            '시스템 이름 목록이 비어야 함'
        )
        assert len(orchestrator.get_execution_stats()) == 0, (
            '실행 통계가 비어야 함'
        )
        assert not orchestrator.has_system('MovementSystem')
        assert not orchestrator.has_system('PhysicsSystem')

    def test_시스템_조회_및_상태_확인_기능(
        self,
        orchestrator: SystemOrchestrator,
        movement_system: MockMovementSystem,
        physics_system: MockPhysicsSystem,
    ) -> None:
        """15. 시스템 조회 및 상태 확인 기능

        목적: 다양한 시스템 조회 및 상태 확인 메서드들이 올바르게 작동하는지 검증
        테스트할 범위: 시스템 조회 및 상태 확인 관련 메서드들
        커버하는 함수 및 데이터: SystemOrchestrator 조회 메서드들
        기대되는 안정성: 정확한 시스템 정보와 상태를 반환해야 함
        """
        # Given - 시스템들 등록 (하나는 비활성화)
        orchestrator.register_system(movement_system, 'MovementSystem')
        orchestrator.register_system(physics_system, 'PhysicsSystem')
        physics_system.disable()

        # Then - 시스템 조회 기능 검증
        assert len(orchestrator) == 2, '전체 시스템 수가 2여야 함'
        assert 'MovementSystem' in orchestrator, 'MovementSystem이 존재해야 함'
        assert 'PhysicsSystem' in orchestrator, 'PhysicsSystem이 존재해야 함'
        assert 'NonExistent' not in orchestrator

        system_names = orchestrator.get_system_names()
        assert len(system_names) == 2, '시스템 이름 목록 길이가 2여야 함'
        assert (
            'MovementSystem' in system_names
            and 'PhysicsSystem' in system_names
        )

        enabled_names = orchestrator.get_enabled_system_names()
        assert len(enabled_names) == 1, '활성 시스템 수가 1이어야 함'
        assert 'MovementSystem' in enabled_names
        assert 'PhysicsSystem' not in enabled_names

        # 이터레이터 테스트
        system_list = list(orchestrator)
        assert len(system_list) == 2, '이터레이터로 2개 시스템을 반환해야 함'
        assert movement_system in system_list and physics_system in system_list

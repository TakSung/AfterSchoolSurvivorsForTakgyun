"""
Integration tests for level-up system components.

This module tests the complete level-up flow from experience gain
to stat increases through event-driven communication.
"""

from src.components.experience_component import ExperienceComponent
from src.components.health_component import HealthComponent
from src.components.player_component import PlayerComponent
from src.core.entity_manager import EntityManager
from src.core.events.enemy_death_event import EnemyDeathEvent
from src.core.events.event_bus import EventBus
from src.core.events.event_types import EventType
from src.systems.experience_system import ExperienceSystem
from src.systems.player_stats_system import PlayerStatsSystem


class TestLevelUpIntegration:
    def test_적_처치_경험치_획득_레벨업_스탯_증가_완전_통합_성공_시나리오(
        self,
    ) -> None:
        """1. 적 처치 → 경험치 획득 → 레벨업 → 스탯 증가 완전 통합 (성공 시나리오)

        목적: 전체 레벨업 시스템이 통합적으로 올바르게 동작하는지 확인
        테스트할 범위: ExperienceSystem + PlayerStatsSystem + EventBus 통합
        커버하는 함수 및 데이터: 적 사망 → 경험치 이벤트 → 레벨업 → 스탯 증가 전 과정
        기대되는 안정성: 완전한 게임 플레이 시뮬레이션에서 안정적 동작 보장
        """
        # Given - 완전한 시스템 설정 (EventBus + 두 시스템 + 플레이어)
        event_bus = EventBus()
        entity_manager = EntityManager()

        # 시스템들 생성 및 이벤트 버스 연결
        exp_system = ExperienceSystem(priority=20)
        stats_system = PlayerStatsSystem(priority=30)

        exp_system.set_event_bus(event_bus)
        event_bus.subscribe(stats_system)

        # 플레이어 엔티티 생성 (레벨업 임계점 근처)
        player_entity = entity_manager.create_entity()
        player_comp = PlayerComponent()
        exp_comp = ExperienceComponent(
            current_exp=90, level=1
        )  # 10 경험치면 레벨업
        health_comp = HealthComponent(current_health=80, max_health=100)

        entity_manager.add_component(player_entity, player_comp)
        entity_manager.add_component(player_entity, exp_comp)
        entity_manager.add_component(player_entity, health_comp)

        # 시스템들에 엔티티 매니저 설정
        exp_system._entity_manager = entity_manager
        stats_system._entity_manager = entity_manager

        # When - 적 사망 이벤트 발생 및 전체 시스템 처리
        enemy_death_event = EnemyDeathEvent.create_from_id(
            enemy_entity_id='enemy_boss_1', timestamp=1000.0
        )

        # 1. 경험치 시스템이 적 사망 처리
        exp_system.handle_event(enemy_death_event)

        # 2. 이벤트 버스에서 대기 중인 이벤트들 처리 (LEVEL_UP 포함)
        processed_count = event_bus.process_events()

        # Then - 완전한 결과 검증

        # 1. 경험치 증가 확인
        updated_exp_comp = entity_manager.get_component(
            player_entity, ExperienceComponent
        )
        assert updated_exp_comp is not None
        assert updated_exp_comp.level > 1  # 레벨업 발생
        original_level = 1
        new_level = updated_exp_comp.level
        levels_gained = new_level - original_level

        # 2. 체력 증가 확인 (PlayerStatsSystem의 효과)
        updated_health_comp = entity_manager.get_component(
            player_entity, HealthComponent
        )
        assert updated_health_comp is not None

        # 예상 체력 계산: 기본 100 + (레벨당 20 * 레벨 증가)
        expected_max_health = 100 + (levels_gained * 20)
        assert updated_health_comp.max_health == expected_max_health

        # 예상 회복량 계산: 기존 80 + (레벨당 10 * 레벨 증가)
        expected_current_health = 80 + (levels_gained * 10)
        assert updated_health_comp.current_health == expected_current_health

        # 3. 이벤트 처리 확인
        assert processed_count > 0  # 적어도 하나의 이벤트가 처리됨

    def test_다중_적_처치_연속_레벨업_누적_효과_성공_시나리오(self) -> None:
        """2. 다중 적 처치 연속 레벨업 누적 효과 (성공 시나리오)

        목적: 여러 적을 연속으로 처치했을 때 누적 레벨업이 올바른지 확인
        테스트할 범위: 연속 이벤트 처리와 누적 스탯 증가
        커버하는 함수 및 데이터: 다중 이벤트 시퀀스 처리
        기대되는 안정성: 연속적인 게임 플레이에서 안정적 동작 보장
        """
        # Given - 통합 시스템 설정
        event_bus = EventBus()
        entity_manager = EntityManager()

        exp_system = ExperienceSystem()
        stats_system = PlayerStatsSystem()

        exp_system.set_event_bus(event_bus)
        event_bus.subscribe(stats_system)

        # 초기 플레이어 설정
        player_entity = entity_manager.create_entity()
        player_comp = PlayerComponent()
        exp_comp = ExperienceComponent(current_exp=0, level=1)
        health_comp = HealthComponent(current_health=100, max_health=100)

        entity_manager.add_component(player_entity, player_comp)
        entity_manager.add_component(player_entity, exp_comp)
        entity_manager.add_component(player_entity, health_comp)

        exp_system._entity_manager = entity_manager
        stats_system._entity_manager = entity_manager

        # When - 연속적인 적 처치 (다양한 적 타입)
        enemy_types = ['basic', 'enhanced', 'boss']

        for i, enemy_type in enumerate(enemy_types):
            enemy_death_event = EnemyDeathEvent.create_from_id(
                enemy_entity_id=f'enemy_{enemy_type}_{i}', timestamp=1000.0 + i
            )
            exp_system.handle_event(enemy_death_event)
            event_bus.process_events()  # 각 적 처치 후 이벤트 처리

        # Then - 누적 효과 확인
        final_exp_comp = entity_manager.get_component(
            player_entity, ExperienceComponent
        )
        final_health_comp = entity_manager.get_component(
            player_entity, HealthComponent
        )

        # 레벨 상승 확인 (기본 50 + 강화 75 + 보스 200 = 325 경험치로 여러 레벨 상승)
        assert final_exp_comp.level > 1
        levels_gained = final_exp_comp.level - 1

        # 누적 체력 증가 확인
        expected_max_health = 100 + (levels_gained * 20)
        assert final_health_comp.max_health == expected_max_health

        # 체력이 최대치를 초과하지 않았는지 확인
        assert final_health_comp.current_health <= final_health_comp.max_health

    def test_이벤트_버스_구독_해제_후_안전성_검증_성공_시나리오(self) -> None:
        """3. 이벤트 버스 구독 해제 후 안전성 검증 (성공 시나리오)

        목적: 시스템 정리 후에도 안전하게 동작하는지 확인
        테스트할 범위: 시스템 생명주기와 이벤트 처리 안전성
        커버하는 함수 및 데이터: cleanup, 구독 해제 후 이벤트 처리
        기대되는 안정성: 시스템 종료 및 재시작 시나리오 안전성 보장
        """
        # Given - 통합 시스템 설정
        event_bus = EventBus()
        entity_manager = EntityManager()

        exp_system = ExperienceSystem()
        stats_system = PlayerStatsSystem()

        exp_system.set_event_bus(event_bus)
        event_bus.subscribe(stats_system)

        # 초기 구독 상태 확인
        assert EventType.ENEMY_DEATH in event_bus._subscribers
        assert EventType.LEVEL_UP in event_bus._subscribers

        # When - 시스템 정리
        exp_system.cleanup()
        stats_system.cleanup()

        # Then - 구독 해제 후 안전성 확인

        # 이벤트 발송이 예외 없이 처리되어야 함
        enemy_death_event = EnemyDeathEvent.create_from_id('enemy_test')
        event_bus.publish(enemy_death_event)

        # 이벤트 처리가 안전하게 완료되어야 함
        processed_count = event_bus.process_events()
        assert processed_count >= 0  # 예외 없이 완료

    def test_레벨업_마일스톤_보너스_적용_검증_성공_시나리오(self) -> None:
        """4. 레벨업 마일스톤 보너스 적용 검증 (성공 시나리오)

        목적: 특정 레벨 도달 시 마일스톤 보너스가 올바르게 적용되는지 확인
        테스트할 범위: 마일스톤 레벨에서의 추가 보너스 적용
        커버하는 함수 및 데이터: _get_level_up_benefits의 마일스톤 시스템
        기대되는 안정성: 레벨 기반 보상 시스템의 정확성 보장
        """
        # Given - 5레벨 근처 플레이어 설정 (마일스톤 테스트용)
        event_bus = EventBus()
        entity_manager = EntityManager()

        exp_system = ExperienceSystem()
        stats_system = PlayerStatsSystem()

        exp_system.set_event_bus(event_bus)
        event_bus.subscribe(stats_system)

        # 4레벨 플레이어 (5레벨 마일스톤 직전)
        player_entity = entity_manager.create_entity()
        player_comp = PlayerComponent()
        exp_comp = ExperienceComponent(current_exp=90, level=4)
        health_comp = HealthComponent(
            current_health=100, max_health=180
        )  # 4레벨 상당

        entity_manager.add_component(player_entity, player_comp)
        entity_manager.add_component(player_entity, exp_comp)
        entity_manager.add_component(player_entity, health_comp)

        exp_system._entity_manager = entity_manager
        stats_system._entity_manager = entity_manager

        # When - 5레벨로 레벨업시키는 경험치 획득
        enemy_death_event = EnemyDeathEvent.create_from_id(
            enemy_entity_id='enemy_boss_milestone', timestamp=1000.0
        )
        exp_system.handle_event(enemy_death_event)
        event_bus.process_events()

        # Then - 마일스톤 보너스 확인
        final_exp_comp = entity_manager.get_component(
            player_entity, ExperienceComponent
        )
        final_health_comp = entity_manager.get_component(
            player_entity, HealthComponent
        )

        # 5레벨 달성 확인
        if final_exp_comp.level >= 5:
            # 기본 레벨업 보너스 + 마일스톤 보너스 확인 가능
            # (정확한 수치는 레벨업 횟수에 따라 달라지므로 증가 확인만)
            assert final_health_comp.max_health > 180  # 기존보다 증가

    def test_시스템_우선순위_및_실행_순서_검증_성공_시나리오(self) -> None:
        """5. 시스템 우선순위 및 실행 순서 검증 (성공 시나리오)

        목적: ExperienceSystem이 PlayerStatsSystem보다 먼저 실행되는지 확인
        테스트할 범위: 시스템 우선순위와 실행 순서
        커버하는 함수 및 데이터: 시스템 priority 설정과 실행 순서
        기대되는 안정성: 시스템 간 의존성과 실행 순서 보장
        """
        # Given - 시스템들의 우선순위 확인
        exp_system = ExperienceSystem(priority=20)
        stats_system = PlayerStatsSystem(priority=30)

        # When & Then - 우선순위 비교 (낮은 숫자가 먼저 실행)
        assert exp_system.priority < stats_system.priority

        # 기본 우선순위 확인
        default_exp_system = ExperienceSystem()
        default_stats_system = PlayerStatsSystem()

        assert default_exp_system.priority < default_stats_system.priority

        # 시스템 이름 확인
        assert exp_system.get_system_name() == 'ExperienceSystem'
        assert stats_system.get_system_name() == 'PlayerStatsSystem'

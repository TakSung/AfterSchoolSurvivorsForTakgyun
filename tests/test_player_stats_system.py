"""
Tests for PlayerStatsSystem and level-up benefit mechanics.

This module tests level-up stat increases, health scaling,
and milestone bonus systems.
"""

from src.components.experience_component import ExperienceComponent
from src.components.health_component import HealthComponent
from src.components.player_component import PlayerComponent
from src.core.entity_manager import EntityManager
from src.core.events.event_types import EventType
from src.core.events.level_up_event import LevelUpEvent
from src.systems.player_stats_system import PlayerStatsSystem


class TestPlayerStatsSystem:
    def test_플레이어_스탯_시스템_초기화_및_설정_검증_성공_시나리오(
        self,
    ) -> None:
        """1. 플레이어 스탯 시스템 초기화 및 설정 검증 (성공 시나리오)

        목적: PlayerStatsSystem의 초기화와 기본 설정이 올바른지 확인
        테스트할 범위: 시스템 초기화, 이벤트 구독 설정
        커버하는 함수 및 데이터: __init__, initialize, get_subscribed_events
        기대되는 안정성: 시스템 생성과 설정의 안정성 보장
        """
        # Given & When - 플레이어 스탯 시스템 생성
        stats_system = PlayerStatsSystem(priority=25)
        stats_system.initialize()

        # Then - 초기화 상태 확인
        assert stats_system.enabled is True
        assert stats_system.priority == 25
        assert stats_system.get_system_name() == 'PlayerStatsSystem'
        assert stats_system.get_subscriber_name() == 'PlayerStatsSystem'

        # 이벤트 구독 확인
        subscribed_events = stats_system.get_subscribed_events()
        assert EventType.LEVEL_UP in subscribed_events
        assert len(subscribed_events) == 1

    def test_레벨업_이벤트_처리_체력_증가_적용_성공_시나리오(self) -> None:
        """2. 레벨업 이벤트 처리 및 체력 증가 적용 (성공 시나리오)

        목적: 레벨업 시 플레이어 체력이 올바르게 증가하는지 확인
        테스트할 범위: 레벨업 이벤트 처리, 체력 스탯 증가
        커버하는 함수 및 데이터: handle_event, _handle_level_up, _apply_health_increase
        기대되는 안정성: 레벨업 시 정확한 스탯 증가 적용 보장
        """
        # Given - 시스템, 엔티티 매니저, 플레이어 설정
        stats_system = PlayerStatsSystem()
        entity_manager = EntityManager()

        # 기본 체력을 가진 플레이어 엔티티 생성
        player_entity = entity_manager.create_entity()
        player_comp = PlayerComponent()
        exp_comp = ExperienceComponent(current_exp=50, level=2)
        health_comp = HealthComponent(current_health=80, max_health=100)

        entity_manager.add_component(player_entity, player_comp)
        entity_manager.add_component(player_entity, exp_comp)
        entity_manager.add_component(player_entity, health_comp)

        stats_system._entity_manager = entity_manager

        # When - 단일 레벨업 이벤트 처리 (2→3레벨)
        level_up_event = LevelUpEvent.create_from_level_change(
            player_entity_id=player_entity.entity_id,
            previous_level=2,
            new_level=3,
            total_experience=300,
            remaining_experience=50,
        )
        stats_system.handle_event(level_up_event)

        # Then - 체력 증가 확인
        updated_health_comp = entity_manager.get_component(
            player_entity, HealthComponent
        )
        assert updated_health_comp is not None
        # 1레벨 증가 = +20 최대 체력, +10 회복 (50% 회복율)
        assert updated_health_comp.max_health == 120  # 100 + 20
        assert updated_health_comp.current_health == 90  # 80 + 10 (회복)

    def test_다중_레벨업_이벤트_처리_누적_증가_성공_시나리오(self) -> None:
        """3. 다중 레벨업 이벤트 처리 및 누적 증가 (성공 시나리오)

        목적: 한 번에 여러 레벨이 오를 때 스탯이 누적 적용되는지 확인
        테스트할 범위: 다중 레벨업 처리, 누적 스탯 계산
        커버하는 함수 및 데이터: _handle_level_up의 레벨 차이 처리
        기대되는 안정성: 대량 경험치 획득 시 정확한 스탯 증가 보장
        """
        # Given - 플레이어와 스탯 시스템 설정
        stats_system = PlayerStatsSystem()
        entity_manager = EntityManager()

        player_entity = entity_manager.create_entity()
        player_comp = PlayerComponent()
        exp_comp = ExperienceComponent(current_exp=50, level=1)
        health_comp = HealthComponent(current_health=90, max_health=100)

        entity_manager.add_component(player_entity, player_comp)
        entity_manager.add_component(player_entity, exp_comp)
        entity_manager.add_component(player_entity, health_comp)

        stats_system._entity_manager = entity_manager

        # When - 3레벨 점프 이벤트 처리 (1→4레벨)
        level_up_event = LevelUpEvent.create_from_level_change(
            player_entity_id=player_entity.entity_id,
            previous_level=1,
            new_level=4,  # 3레벨 증가
            total_experience=1000,
            remaining_experience=100,
        )
        stats_system.handle_event(level_up_event)

        # Then - 누적 체력 증가 확인
        updated_health_comp = entity_manager.get_component(
            player_entity, HealthComponent
        )
        assert updated_health_comp is not None
        # 3레벨 증가 = +60 최대 체력, +30 회복
        assert updated_health_comp.max_health == 160  # 100 + (3 * 20)
        assert updated_health_comp.current_health == 120  # 90 + (3 * 10)

    def test_체력_컴포넌트_없는_플레이어_자동_생성_성공_시나리오(self) -> None:
        """4. 체력 컴포넌트 없는 플레이어 자동 생성 (성공 시나리오)

        목적: 체력 컴포넌트가 없는 플레이어에게 기본 체력이 생성되는지 확인
        테스트할 범위: 체력 컴포넌트 자동 생성 로직
        커버하는 함수 및 데이터: _apply_health_increase의 컴포넌트 생성
        기대되는 안정성: 다양한 플레이어 상태에서도 안정적 동작 보장
        """
        # Given - 체력 컴포넌트 없는 플레이어
        stats_system = PlayerStatsSystem()
        entity_manager = EntityManager()

        player_entity = entity_manager.create_entity()
        player_comp = PlayerComponent()
        exp_comp = ExperienceComponent(current_exp=50, level=2)

        entity_manager.add_component(player_entity, player_comp)
        entity_manager.add_component(player_entity, exp_comp)
        # 의도적으로 HealthComponent 추가하지 않음

        stats_system._entity_manager = entity_manager

        # When - 레벨업 이벤트 처리
        level_up_event = LevelUpEvent.create_from_level_change(
            player_entity_id=player_entity.entity_id,
            previous_level=2,
            new_level=3,
            total_experience=300,
            remaining_experience=50,
        )
        stats_system.handle_event(level_up_event)

        # Then - 체력 컴포넌트 자동 생성 및 증가 적용 확인
        health_comp = entity_manager.get_component(
            player_entity, HealthComponent
        )
        assert health_comp is not None  # 자동 생성됨
        assert health_comp.max_health == 120  # 기본 100 + 20
        assert health_comp.current_health == 110  # 기본 100 + 10 회복

    def test_존재하지_않는_플레이어_ID_안전_처리_성공_시나리오(self) -> None:
        """5. 존재하지 않는 플레이어 ID 안전 처리 (성공 시나리오)

        목적: 잘못된 플레이어 ID로 이벤트가 와도 안전하게 처리되는지 확인
        테스트할 범위: 예외 상황 처리와 안전성
        커버하는 함수 및 데이터: _find_player_by_id, 빈 검색 결과 처리
        기대되는 안정성: 예상치 못한 상황에서도 안정적 동작 보장
        """
        # Given - 플레이어가 없는 환경
        stats_system = PlayerStatsSystem()
        entity_manager = EntityManager()
        stats_system._entity_manager = entity_manager

        # When - 존재하지 않는 플레이어 ID로 레벨업 이벤트 처리
        level_up_event = LevelUpEvent.create_from_level_change(
            player_entity_id='non_existent_player',
            previous_level=1,
            new_level=2,
            total_experience=200,
            remaining_experience=50,
        )

        # Then - 예외 발생 없이 안전하게 처리되어야 함
        stats_system.handle_event(level_up_event)  # 예외 없음

    def test_레벨업_혜택_계산_공식_검증_성공_시나리오(self) -> None:
        """6. 레벨업 혜택 계산 공식 검증 (성공 시나리오)

        목적: 레벨별 혜택 계산이 올바른 공식에 따라 동작하는지 확인
        테스트할 범위: 레벨업 혜택 계산 로직과 마일스톤 보너스
        커버하는 함수 및 데이터: _get_level_up_benefits, 스탯 증가 공식
        기대되는 안정성: 일관된 성장 공식과 밸런스 보장
        """
        # Given - 플레이어 스탯 시스템
        stats_system = PlayerStatsSystem()

        # When & Then - 기본 레벨 혜택 확인
        level_3_benefits = stats_system._get_level_up_benefits(3)
        assert level_3_benefits['health'] == 20  # 기본 체력 증가
        assert level_3_benefits['health_heal'] == 10  # 50% 회복

        # 5레벨 마일스톤 보너스 확인
        level_5_benefits = stats_system._get_level_up_benefits(5)
        assert level_5_benefits['health'] == 20
        assert level_5_benefits['bonus_health'] == 10  # 마일스톤 보너스

        # 10레벨 마일스톤 보너스 확인
        level_10_benefits = stats_system._get_level_up_benefits(10)
        assert level_10_benefits['health'] == 20
        assert level_10_benefits['bonus_health'] == 10  # 5레벨 보너스
        assert level_10_benefits['regeneration_boost'] == 1.0  # 10레벨 보너스

        # 보스 레벨 (15레벨) 특별 보너스 확인
        level_15_benefits = stats_system._get_level_up_benefits(15)
        assert (
            level_15_benefits['major_health_boost'] == 50
        )  # 보스 레벨 보너스

    def test_스탯_증가_공식_설정_접근_검증_성공_시나리오(self) -> None:
        """7. 스탯 증가 공식 설정 접근 검증 (성공 시나리오)

        목적: 스탯 증가 공식이 올바르게 설정되고 접근 가능한지 확인
        테스트할 범위: _stat_growth 설정값과 접근 방법
        커버하는 함수 및 데이터: __init__의 스탯 성장 설정
        기대되는 안정성: 밸런싱을 위한 설정값 접근성 보장
        """
        # Given & When - 플레이어 스탯 시스템 생성
        stats_system = PlayerStatsSystem()

        # Then - 스탯 증가 공식 확인
        assert stats_system._stat_growth['health_per_level'] == 20
        assert stats_system._stat_growth['health_heal_ratio'] == 0.5

        # 공식 일관성 확인
        health_increase = stats_system._stat_growth['health_per_level']
        heal_ratio = stats_system._stat_growth['health_heal_ratio']
        expected_heal = int(health_increase * heal_ratio)
        assert expected_heal == 10  # 20 * 0.5

    def test_플레이어_ID_검색_정확성_검증_성공_시나리오(self) -> None:
        """8. 플레이어 ID 검색 정확성 검증 (성공 시나리오)

        목적: 특정 플레이어 ID로 엔티티를 정확히 찾을 수 있는지 확인
        테스트할 범위: _find_player_by_id의 검색 로직
        커버하는 함수 및 데이터: 엔티티 ID 매칭과 컴포넌트 확인
        기대되는 안정성: 정확한 플레이어 식별과 타겟팅 보장
        """
        # Given - 여러 엔티티가 있는 환경
        stats_system = PlayerStatsSystem()
        entity_manager = EntityManager()

        # 플레이어 엔티티 생성
        player_entity = entity_manager.create_entity()
        player_comp = PlayerComponent()
        exp_comp = ExperienceComponent()

        entity_manager.add_component(player_entity, player_comp)
        entity_manager.add_component(player_entity, exp_comp)

        # 일반 엔티티 생성 (플레이어가 아님)
        non_player_entity = entity_manager.create_entity()

        stats_system._entity_manager = entity_manager

        # When - 플레이어 ID로 검색
        found_player = stats_system._find_player_by_id(player_entity.entity_id)
        not_found = stats_system._find_player_by_id(
            non_player_entity.entity_id
        )
        missing = stats_system._find_player_by_id('unknown_id')

        # Then - 검색 결과 확인
        assert found_player is player_entity  # 정확한 플레이어 찾음
        assert not_found is None  # 플레이어 컴포넌트 없어서 못 찾음
        assert missing is None  # 존재하지 않는 ID

    def test_시스템_업데이트_및_정리_동작_검증_성공_시나리오(self) -> None:
        """9. 시스템 업데이트 및 정리 동작 검증 (성공 시나리오)

        목적: 시스템의 업데이트와 정리 메서드가 안전하게 동작하는지 확인
        테스트할 범위: update, cleanup 메서드 동작
        커버하는 함수 및 데이터: 시스템 생명주기 관리
        기대되는 안정성: 시스템 실행과 종료의 안정성 보장
        """
        # Given - 플레이어 스탯 시스템과 엔티티 매니저
        stats_system = PlayerStatsSystem()
        entity_manager = EntityManager()

        # When - 시스템 업데이트
        stats_system.update(entity_manager, 0.016)  # 60 FPS

        # Then - 엔티티 매니저 설정 확인
        assert stats_system._entity_manager is entity_manager

        # When - 시스템 정리
        stats_system.cleanup()

        # Then - 예외 없이 정리 완료 (정리 후 상태는 구현에 따라 다름)
        assert True  # 예외 없이 완료됨을 확인

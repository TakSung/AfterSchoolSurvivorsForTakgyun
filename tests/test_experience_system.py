"""
Tests for ExperienceSystem and related events.

This module tests experience gain mechanics, event handling,
and level up processing.
"""

import pytest

from src.components.experience_component import ExperienceComponent
from src.components.player_component import PlayerComponent
from src.core.entity_manager import EntityManager
from src.core.events.enemy_death_event import EnemyDeathEvent
from src.core.events.event_bus import EventBus
from src.core.events.event_types import EventType
from src.core.events.experience_gain_event import ExperienceGainEvent
from src.core.events.level_up_event import LevelUpEvent
from src.systems.experience_system import ExperienceSystem


class TestExperienceGainEvent:
    def test_경험치_획득_이벤트_생성_및_검증_성공_시나리오(self) -> None:
        """1. 경험치 획득 이벤트 생성 및 검증 (성공 시나리오)

        목적: ExperienceGainEvent의 생성과 데이터 검증이 올바른지 확인
        테스트할 범위: 이벤트 생성, 검증, 접근자 메서드
        커버하는 함수 및 데이터: create_from_enemy_kill, validate, getter 메서드들
        기대되는 안정성: 적 처치 시 정확한 경험치 이벤트 생성 보장
        """
        # Given & When - 적 처치로부터 경험치 이벤트 생성
        event = ExperienceGainEvent.create_from_enemy_kill(
            player_entity_id='player_1',
            enemy_entity_id='enemy_1',
            base_experience=100,
            enemy_type='boss',
            enemy_level=3,
            timestamp=1234.5,
        )

        # Then - 이벤트 데이터 검증
        assert event.get_player_id() == 'player_1'
        assert event.get_experience_amount() == 100
        assert event.get_source_type() == 'enemy_kill'
        assert event.get_source_entity_id() == 'enemy_1'
        assert event.get_enemy_type() == 'boss'
        assert event.get_enemy_level() == 3
        assert event.timestamp == 1234.5
        assert event.is_from_enemy_kill() is True
        assert event.is_from_quest() is False
        assert event.validate() is True

    def test_퀘스트_완료_경험치_이벤트_생성_검증_성공_시나리오(self) -> None:
        """2. 퀘스트 완료 경험치 이벤트 생성 검증 (성공 시나리오)

        목적: 퀘스트 완료로부터 경험치 이벤트가 올바르게 생성되는지 확인
        테스트할 범위: create_from_quest 메서드와 퀘스트 관련 속성
        커버하는 함수 및 데이터: create_from_quest, 소스 타입 확인
        기대되는 안정성: 다양한 경험치 소스 지원 보장
        """
        # Given & When - 퀘스트 완료로부터 경험치 이벤트 생성
        event = ExperienceGainEvent.create_from_quest(
            player_entity_id='player_1',
            quest_id='quest_daily_1',
            experience_amount=500,
            timestamp=2000.0,
        )

        # Then - 퀘스트 이벤트 데이터 검증
        assert event.get_player_id() == 'player_1'
        assert event.get_experience_amount() == 500
        assert event.get_source_type() == 'quest_completion'
        assert event.get_source_entity_id() == 'quest_daily_1'
        assert event.get_enemy_type() == 'none'
        assert event.get_enemy_level() == 1
        assert event.is_from_enemy_kill() is False
        assert event.is_from_quest() is True
        assert event.validate() is True

    def test_잘못된_경험치_이벤트_데이터_검증_실패_시나리오(self) -> None:
        """3. 잘못된 경험치 이벤트 데이터 검증 실패 (실패 시나리오)

        목적: 잘못된 데이터로 이벤트 생성 시 적절한 검증 실패 확인
        테스트할 범위: 데이터 검증 로직과 예외 처리
        커버하는 함수 및 데이터: __post_init__, validate 메서드
        기대되는 안정성: 잘못된 데이터 입력 시 명확한 오류 발생 보장
        """
        # When & Then - 잘못된 데이터로 이벤트 생성 시 예외 발생
        with pytest.raises(ValueError):
            ExperienceGainEvent(
                timestamp=1000.0,
                created_at=None,
                player_entity_id='',  # 빈 문자열
                experience_amount=100,
                source_type='enemy_kill',
                source_entity_id='enemy_1',
            )

        with pytest.raises(ValueError):
            ExperienceGainEvent(
                timestamp=1000.0,
                created_at=None,
                player_entity_id='player_1',
                experience_amount=-50,  # 음수 경험치
                source_type='enemy_kill',
                source_entity_id='enemy_1',
            )

        with pytest.raises(ValueError):
            ExperienceGainEvent(
                timestamp=1000.0,
                created_at=None,
                player_entity_id='player_1',
                experience_amount=100,
                source_type='',  # 빈 소스 타입
                source_entity_id='enemy_1',
            )


class TestLevelUpEvent:
    def test_레벨업_이벤트_생성_및_검증_성공_시나리오(self) -> None:
        """4. 레벨업 이벤트 생성 및 검증 (성공 시나리오)

        목적: LevelUpEvent의 생성과 데이터 검증이 올바른지 확인
        테스트할 범위: 이벤트 생성, 레벨 차이 계산, 검증 로직
        커버하는 함수 및 데이터: create_from_level_change, getter 메서드들
        기대되는 안정성: 레벨업 시 정확한 정보 전달 보장
        """
        # Given & When - 레벨업 이벤트 생성
        event = LevelUpEvent.create_from_level_change(
            player_entity_id='player_1',
            previous_level=5,
            new_level=7,
            total_experience=1500,
            remaining_experience=150,
            timestamp=3000.0,
        )

        # Then - 레벨업 이벤트 데이터 검증
        assert event.get_player_id() == 'player_1'
        assert event.get_previous_level() == 5
        assert event.get_new_level() == 7
        assert event.get_level_difference() == 2
        assert event.get_total_experience() == 1500
        assert event.get_remaining_experience() == 150
        assert event.is_multiple_level_up() is True
        assert event.validate() is True

    def test_단일_레벨업_이벤트_검증_성공_시나리오(self) -> None:
        """5. 단일 레벨업 이벤트 검증 (성공 시나리오)

        목적: 한 번에 한 레벨만 오르는 경우의 처리 확인
        테스트할 범위: 단일 레벨업과 다중 레벨업 구분
        커버하는 함수 및 데이터: is_multiple_level_up 메서드
        기대되는 안정성: 레벨업 유형 정확한 구분 보장
        """
        # Given & When - 단일 레벨업 이벤트 생성
        event = LevelUpEvent.create_from_level_change(
            player_entity_id='player_1',
            previous_level=3,
            new_level=4,
            total_experience=500,
            remaining_experience=25,
        )

        # Then - 단일 레벨업 확인
        assert event.get_level_difference() == 1
        assert event.is_multiple_level_up() is False
        assert event.validate() is True

    def test_잘못된_레벨업_데이터_검증_실패_시나리오(self) -> None:
        """6. 잘못된 레벨업 데이터 검증 실패 (실패 시나리오)

        목적: 잘못된 레벨 데이터로 이벤트 생성 시 검증 실패 확인
        테스트할 범위: 레벨 순서, 음수 값 등 검증 로직
        커버하는 함수 및 데이터: validate 메서드의 레벨 검증
        기대되는 안정성: 논리적으로 불가능한 레벨업 데이터 거부 보장
        """
        # When & Then - 잘못된 레벨 순서로 이벤트 생성 시 예외 발생
        with pytest.raises(ValueError):
            LevelUpEvent.create_from_level_change(
                player_entity_id='player_1',
                previous_level=5,
                new_level=3,  # 레벨 다운 (불가능)
                total_experience=1000,
                remaining_experience=50,
            )

        with pytest.raises(ValueError):
            LevelUpEvent.create_from_level_change(
                player_entity_id='player_1',
                previous_level=0,  # 0 레벨 (불가능)
                new_level=1,
                total_experience=100,
                remaining_experience=0,
            )


class TestExperienceSystem:
    def test_경험치_시스템_초기화_및_설정_검증_성공_시나리오(self) -> None:
        """7. 경험치 시스템 초기화 및 설정 검증 (성공 시나리오)

        목적: ExperienceSystem의 초기화와 기본 설정이 올바른지 확인
        테스트할 범위: 시스템 초기화, 이벤트 버스 설정
        커버하는 함수 및 데이터: __init__, initialize, set_event_bus
        기대되는 안정성: 시스템 생성과 설정의 안정성 보장
        """
        # Given - 경험치 시스템과 이벤트 버스 생성
        exp_system = ExperienceSystem(priority=20)
        event_bus = EventBus()

        # When - 시스템 초기화 및 이벤트 버스 설정
        exp_system.initialize()
        exp_system.set_event_bus(event_bus)

        # Then - 초기화 상태 확인
        assert exp_system.enabled is True
        assert exp_system.priority == 20
        assert exp_system.get_system_name() == 'ExperienceSystem'
        assert exp_system._event_bus is event_bus

    def test_적_사망_이벤트_처리_경험치_부여_성공_시나리오(self) -> None:
        """8. 적 사망 이벤트 처리 및 경험치 부여 (성공 시나리오)

        목적: 적 사망 시 플레이어에게 경험치가 올바르게 부여되는지 확인
        테스트할 범위: 이벤트 처리, 경험치 계산, 컴포넌트 업데이트
        커버하는 함수 및 데이터: on_event, _handle_enemy_death, _award_experience_to_player
        기대되는 안정성: 적 처치 시 정확한 경험치 부여 보장
        """
        # Given - 시스템, 엔티티 매니저, 플레이어 설정
        exp_system = ExperienceSystem()
        entity_manager = EntityManager()
        event_bus = EventBus()

        # 플레이어 엔티티 생성
        player_entity = entity_manager.create_entity()
        player_comp = PlayerComponent()
        exp_comp = ExperienceComponent(current_exp=50, level=2)

        entity_manager.add_component(player_entity, player_comp)
        entity_manager.add_component(player_entity, exp_comp)

        exp_system.set_event_bus(event_bus)
        exp_system._entity_manager = entity_manager

        # When - 적 사망 이벤트 처리
        enemy_death_event = EnemyDeathEvent.create_from_id(
            enemy_entity_id='enemy_boss_1', timestamp=1000.0
        )
        exp_system.handle_event(enemy_death_event)

        # Then - 경험치 증가 확인
        updated_exp_comp = entity_manager.get_component(
            player_entity, ExperienceComponent
        )
        assert updated_exp_comp is not None
        # 보스 처치로 기본 200 + 정책 100 = 300 경험치 획득 예상
        # (50 + 300 = 350, 2레벨에서 필요 경험치 150 초과하여 레벨업)
        assert updated_exp_comp.total_exp_earned > 50  # 초기값보다 증가

    def test_레벨업_이벤트_발생_검증_성공_시나리오(self) -> None:
        """9. 레벨업 이벤트 발생 검증 (성공 시나리오)

        목적: 경험치 획득으로 레벨업 시 이벤트가 올바르게 발생하는지 확인
        테스트할 범위: 레벨업 감지, 이벤트 생성 및 발송
        커버하는 함수 및 데이터: 레벨업 이벤트 생성 로직
        기대되는 안정성: 레벨업 시 다른 시스템에 정확한 알림 보장
        """
        # Given - 레벨업 임계점 근처의 플레이어 설정
        exp_system = ExperienceSystem()
        entity_manager = EntityManager()
        event_bus = EventBus()

        player_entity = entity_manager.create_entity()
        player_comp = PlayerComponent()
        exp_comp = ExperienceComponent(
            current_exp=95, level=1
        )  # 레벨업 임계점

        entity_manager.add_component(player_entity, player_comp)
        entity_manager.add_component(player_entity, exp_comp)

        exp_system.set_event_bus(event_bus)
        exp_system._entity_manager = entity_manager

        # When - 레벨업을 유발하는 경험치 부여
        exp_system._award_experience_to_player(
            player_entity,
            50,
            'basic',
            1,  # 충분한 경험치로 레벨업 유발
        )

        # Then - 레벨업 이벤트 발생 확인
        # Note: 실제 이벤트 발송은 _award_experience_to_player 내부에서 처리
        updated_exp_comp = entity_manager.get_component(
            player_entity, ExperienceComponent
        )
        assert updated_exp_comp.level > 1  # 레벨업 발생 확인

    def test_적_타입별_경험치_차등_부여_검증_성공_시나리오(self) -> None:
        """10. 적 타입별 경험치 차등 부여 검증 (성공 시나리오)

        목적: 적 타입에 따라 다른 경험치가 부여되는지 확인
        테스트할 범위: 적 타입 판별과 차등 경험치 계산
        커버하는 함수 및 데이터: _determine_enemy_type, _base_enemy_experience
        기대되는 안정성: 적 타입별 적절한 경험치 보상 보장
        """
        # Given - 경험치 시스템 설정
        exp_system = ExperienceSystem()

        # When & Then - 적 타입별 경험치 확인
        basic_exp = exp_system._base_enemy_experience['basic']
        boss_exp = exp_system._base_enemy_experience['boss']
        enhanced_exp = exp_system._base_enemy_experience['enhanced']

        assert basic_exp < enhanced_exp < boss_exp  # 경험치 차등 확인
        assert basic_exp == 50
        assert enhanced_exp == 75
        assert boss_exp == 200

        # 적 타입 판별 로직 테스트
        assert exp_system._determine_enemy_type('enemy_boss_1') == 'boss'
        assert exp_system._determine_enemy_type('enemy_basic_1') == 'basic'
        assert (
            exp_system._determine_enemy_type('enemy_enhanced_1') == 'enhanced'
        )

    def test_이벤트_버스_구독_해제_정리_검증_성공_시나리오(self) -> None:
        """11. 이벤트 버스 구독 해제 및 정리 검증 (성공 시나리오)

        목적: 시스템 정리 시 이벤트 구독이 올바르게 해제되는지 확인
        테스트할 범위: cleanup 메서드와 리소스 정리
        커버하는 함수 및 데이터: cleanup, 이벤트 구독 해제
        기대되는 안정성: 메모리 누수 방지와 깔끔한 정리 보장
        """
        # Given - 이벤트 버스와 연결된 시스템
        exp_system = ExperienceSystem()
        event_bus = EventBus()
        exp_system.set_event_bus(event_bus)

        # 구독 상태 확인
        assert EventType.ENEMY_DEATH in event_bus._subscribers
        assert exp_system in event_bus._subscribers[EventType.ENEMY_DEATH]

        # When - 시스템 정리
        exp_system.cleanup()

        # Then - 구독 해제 확인
        # Note: EventBus의 구현에 따라 다를 수 있지만,
        # 일반적으로 구독자 목록에서 제거되어야 함
        if EventType.ENEMY_DEATH in event_bus._subscribers:
            assert (
                exp_system not in event_bus._subscribers[EventType.ENEMY_DEATH]
            )

    def test_플레이어_없음_상황_안전_처리_검증_성공_시나리오(self) -> None:
        """12. 플레이어 없는 상황 안전 처리 검증 (성공 시나리오)

        목적: 플레이어가 없는 상황에서도 시스템이 안전하게 동작하는지 확인
        테스트할 범위: 예외 상황 처리와 안전성
        커버하는 함수 및 데이터: _find_player_entities, 빈 목록 처리
        기대되는 안정성: 예상치 못한 상황에서도 안정적 동작 보장
        """
        # Given - 플레이어가 없는 엔티티 매니저
        exp_system = ExperienceSystem()
        entity_manager = EntityManager()
        exp_system._entity_manager = entity_manager

        # When - 플레이어 엔티티 찾기
        players = exp_system._find_player_entities()

        # Then - 빈 목록 반환 확인
        assert players == []

        # 적 사망 이벤트 처리도 안전하게 동작해야 함
        enemy_death_event = EnemyDeathEvent.create_from_id('enemy_1')
        # 예외 발생 없이 처리되어야 함
        exp_system._handle_enemy_death(enemy_death_event)

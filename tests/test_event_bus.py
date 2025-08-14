"""
Unit tests for EventBus queuing system.

Tests the comprehensive functionality of the EventBus class including
queue management, subscriber management, event processing, and performance monitoring.
"""

from dataclasses import dataclass
import time
from datetime import datetime

from src.core.events import event_types
from src.core.events.base_event import BaseEvent
from src.core.events.event_bus import EventBus
from src.core.events.event_types import EventType
from src.core.events.interfaces import IEventSubscriber


class TestEventBus:
    """Test class for EventBus queuing system functionality."""

    def test_이벤트버스_초기화_및_기본_상태_검증_성공_시나리오(self) -> None:
        """1. 이벤트버스 초기화 및 기본 상태 검증 (성공 시나리오)

        목적: EventBus 생성 시 초기 상태 및 기본 설정 확인
        테스트할 범위: EventBus __init__ 메서드
        커버하는 함수 및 데이터: 초기 큐, 구독자, 통계 상태
        기대되는 안정성: 일관된 초기 상태 보장
        """
        # Given & When - 기본 EventBus 생성
        event_bus = EventBus()

        # Then - 초기 상태 확인
        assert event_bus.get_queue_size() == 0, '초기 큐는 비어있어야 함'
        assert event_bus.is_queue_empty(), '초기 큐는 빈 상태여야 함'
        assert event_bus.get_subscriber_count() == 0, '초기 구독자는 없어야 함'
        assert len(event_bus.get_subscribed_event_types()) == 0, (
            '구독 이벤트 타입이 없어야 함'
        )

        # 통계 초기 상태 확인
        stats = event_bus.get_processing_stats()
        assert stats['events_published'] == 0, '발행된 이벤트 수는 0이어야 함'
        assert stats['events_processed'] == 0, '처리된 이벤트 수는 0이어야 함'
        assert stats['exceptions_caught'] == 0, '예외 수는 0이어야 함'
        assert stats['last_process_time'] == 0.0, (
            '마지막 처리 시간은 0이어야 함'
        )
        assert stats['is_processing'] is False, '처리 중이 아니어야 함'

    def test_커스텀_큐_크기_제한_설정_검증_성공_시나리오(self) -> None:
        """2. 커스텀 큐 크기 제한 설정 검증 (성공 시나리오)

        목적: 커스텀 큐 크기 제한 설정 확인
        테스트할 범위: max_queue_size 설정
        커버하는 함수 및 데이터: 큐 크기 제한 기능
        기대되는 안정성: 메모리 오버플로우 방지 보장
        """
        # Given & When - 커스텀 큐 크기로 EventBus 생성
        custom_size = 500
        event_bus = EventBus(max_queue_size=custom_size)

        # Then - 커스텀 설정 확인
        stats = event_bus.get_processing_stats()
        assert stats['max_queue_size'] == custom_size, (
            '커스텀 큐 크기가 설정되어야 함'
        )

        health = event_bus.get_health_status()
        assert health['max_queue_size'] == custom_size, (
            '헬스 상태에도 반영되어야 함'
        )

    def test_구독자_등록_및_해제_기능_검증_성공_시나리오(self) -> None:
        """3. 구독자 등록 및 해제 기능 검증 (성공 시나리오)

        목적: 구독자 등록/해제 시스템의 정상 동작 확인
        테스트할 범위: subscribe, unsubscribe 메서드
        커버하는 함수 및 데이터: 구독자 관리 시스템
        기대되는 안정성: 안정적인 구독자 관리 보장
        """

        # Given - Mock 구독자들
        class MockCombatSubscriber(IEventSubscriber):
            def get_subscribed_events(self) -> list[EventType]:
                return [EventType.ENEMY_DEATH, EventType.WEAPON_FIRED]

            def handle_event(self, event: BaseEvent) -> None:
                pass

        class MockItemSubscriber(IEventSubscriber):
            def get_subscribed_events(self) -> list[EventType]:
                return [EventType.ITEM_PICKUP, EventType.ITEM_DROP]

            def handle_event(self, event: BaseEvent) -> None:
                pass

        event_bus = EventBus()
        combat_subscriber = MockCombatSubscriber()
        item_subscriber = MockItemSubscriber()

        # When - 구독자 등록
        event_bus.subscribe(combat_subscriber)
        event_bus.subscribe(item_subscriber)

        # Then - 등록 확인
        assert event_bus.get_subscriber_count() == 4, (
            '총 4개 이벤트 타입에 구독자가 있어야 함'
        )
        assert event_bus.get_subscriber_count(EventType.ENEMY_DEATH) == 1, (
            '적 사망 이벤트에 1명 구독'
        )
        assert event_bus.get_subscriber_count(EventType.WEAPON_FIRED) == 1, (
            '무기 발사 이벤트에 1명 구독'
        )
        assert event_bus.get_subscriber_count(EventType.ITEM_PICKUP) == 1, (
            '아이템 획득 이벤트에 1명 구독'
        )
        assert event_bus.get_subscriber_count(EventType.ITEM_DROP) == 1, (
            '아이템 드롭 이벤트에 1명 구독'
        )

        subscribed_types = event_bus.get_subscribed_event_types()
        assert len(subscribed_types) == 4, '4개 이벤트 타입이 구독되어야 함'
        assert EventType.ENEMY_DEATH in subscribed_types
        assert EventType.WEAPON_FIRED in subscribed_types
        assert EventType.ITEM_PICKUP in subscribed_types
        assert EventType.ITEM_DROP in subscribed_types

        # When - 구독자 해제
        event_bus.unsubscribe(combat_subscriber)

        # Then - 해제 확인
        assert event_bus.get_subscriber_count() == 2, (
            '2개 이벤트 타입에만 구독자가 남아야 함'
        )
        assert event_bus.get_subscriber_count(EventType.ENEMY_DEATH) == 0, (
            '적 사망 이벤트 구독자 없음'
        )
        assert event_bus.get_subscriber_count(EventType.WEAPON_FIRED) == 0, (
            '무기 발사 이벤트 구독자 없음'
        )
        assert event_bus.get_subscriber_count(EventType.ITEM_PICKUP) == 1, (
            '아이템 획득 이벤트에 1명 구독'
        )
        assert event_bus.get_subscriber_count(EventType.ITEM_DROP) == 1, (
            '아이템 드롭 이벤트에 1명 구독'
        )

    def test_특정_이벤트_타입_구독_해제_검증_성공_시나리오(self) -> None:
        """4. 특정 이벤트 타입 구독 해제 검증 (성공 시나리오)

        목적: unsubscribe_from_event 메서드의 선택적 해제 기능 확인
        테스트할 범위: unsubscribe_from_event 메서드
        커버하는 함수 및 데이터: 부분 구독 해제 기능
        기대되는 안정성: 정밀한 구독자 관리 보장
        """

        # Given - 다중 이벤트 구독자
        class MockMultiSubscriber(IEventSubscriber):
            def get_subscribed_events(self) -> list[EventType]:
                return [
                    EventType.ENEMY_DEATH,
                    EventType.ITEM_PICKUP,
                    EventType.BOSS_SPAWNED,
                ]

            def handle_event(self, event: BaseEvent) -> None:
                pass

        event_bus = EventBus()
        subscriber = MockMultiSubscriber()
        event_bus.subscribe(subscriber)

        # When - 특정 이벤트 타입만 구독 해제
        result = event_bus.unsubscribe_from_event(
            subscriber, EventType.ITEM_PICKUP
        )

        # Then - 부분 해제 확인
        assert result is True, '구독 해제가 성공해야 함'
        assert event_bus.get_subscriber_count(EventType.ENEMY_DEATH) == 1, (
            '적 사망 이벤트는 여전히 구독 중'
        )
        assert event_bus.get_subscriber_count(EventType.ITEM_PICKUP) == 0, (
            '아이템 획득 이벤트는 구독 해제됨'
        )
        assert event_bus.get_subscriber_count(EventType.BOSS_SPAWNED) == 1, (
            '보스 등장 이벤트는 여전히 구독 중'
        )

        # When - 존재하지 않는 구독 해제 시도
        result = event_bus.unsubscribe_from_event(
            subscriber, EventType.GAME_STARTED
        )

        # Then - 실패 결과 확인
        assert result is False, '존재하지 않는 구독 해제는 실패해야 함'

    def test_이벤트_발행_및_큐잉_기능_검증_성공_시나리오(self) -> None:
        """5. 이벤트 발행 및 큐잉 기능 검증 (성공 시나리오)

        목적: publish 메서드의 이벤트 큐잉 기능 확인
        테스트할 범위: publish 메서드 및 큐 관리
        커버하는 함수 및 데이터: 이벤트 큐잉 시스템
        기대되는 안정성: 안정적인 이벤트 큐잉 보장
        """

        # Given - Mock 이벤트 클래스
        @dataclass
        class MockQueueEvent(BaseEvent):
            event_type :EventType
            def get_event_type(self) -> EventType:
                return self.event_type
            def validate(self) -> bool:
                return True

        event_bus = EventBus()

        # When - 이벤트 발행
        event1 = MockQueueEvent(
            event_type=EventType.ENEMY_DEATH,
            timestamp=1000.0,
            created_at=datetime.now(),
        )
        event2 = MockQueueEvent(
            event_type=EventType.ITEM_PICKUP,
            timestamp=1001.0,
            created_at=datetime.now(),
        )

        result1 = event_bus.publish(event1)
        result2 = event_bus.publish(event2)

        # Then - 발행 결과 및 큐 상태 확인
        assert result1 is True, '첫 번째 이벤트 발행 성공'
        assert result2 is True, '두 번째 이벤트 발행 성공'
        assert event_bus.get_queue_size() == 2, '큐에 2개 이벤트가 있어야 함'
        assert not event_bus.is_queue_empty(), '큐가 비어있지 않아야 함'

        # 통계 확인
        stats = event_bus.get_processing_stats()
        assert stats['events_published'] == 2, '발행된 이벤트 수는 2여야 함'
        assert stats['events_processed'] == 0, '아직 처리된 이벤트는 없어야 함'

    def test_잘못된_이벤트_발행_거부_검증_성공_시나리오(self) -> None:
        """6. 잘못된 이벤트 발행 거부 검증 (성공 시나리오)

        목적: validate 실패 이벤트의 발행 거부 확인
        테스트할 범위: publish 메서드의 검증 로직
        커버하는 함수 및 데이터: 이벤트 유효성 검사
        기대되는 안정성: 잘못된 이벤트 차단 보장
        """

        # Given - 유효하지 않은 이벤트
        class MockInvalidEvent(BaseEvent):
            def get_event_type(self) -> EventType:
                return EventType.WEAPON_FIRED
            def validate(self) -> bool:
                return False

        event_bus = EventBus()
        invalid_event = MockInvalidEvent(
            timestamp=2000.0,
            created_at=datetime.now(),
        )

        # When - 잘못된 이벤트 발행 시도
        result = event_bus.publish(invalid_event)

        # Then - 발행 거부 확인
        assert result is False, '유효하지 않은 이벤트는 거부되어야 함'
        assert event_bus.get_queue_size() == 0, (
            '큐에 이벤트가 추가되지 않아야 함'
        )
        assert event_bus.is_queue_empty(), '큐는 여전히 비어있어야 함'

        stats = event_bus.get_processing_stats()
        assert stats['events_published'] == 0, '발행된 이벤트 수는 0이어야 함'

    def test_큐_크기_제한_초과_시_이벤트_드롭_검증_성공_시나리오(self) -> None:
        """7. 큐 크기 제한 초과 시 이벤트 드롭 검증 (성공 시나리오)

        목적: 큐 오버플로우 방지 기능 확인
        테스트할 범위: 큐 크기 제한 처리
        커버하는 함수 및 데이터: 메모리 오버플로우 방지
        기대되는 안정성: 메모리 사용량 제한 보장
        """
        # Given - 작은 큐 크기로 EventBus 생성
        small_queue_size = 3
        event_bus = EventBus(max_queue_size=small_queue_size)

        class MockOverflowEvent(BaseEvent):
            def get_event_type(self) -> EventType:
                return EventType.ENEMY_SPAWNED
            def validate(self) -> bool:
                return True

        # When - 큐 크기를 초과하는 이벤트 발행
        events = []
        results = []
        for i in range(5):  # 3개 제한에 5개 시도
            event = MockOverflowEvent(
                timestamp=float(i),
                created_at=datetime.now(),
            )
            events.append(event)
            results.append(event_bus.publish(event))

        # Then - 초과 이벤트 드롭 확인
        assert results[0] is True, '첫 번째 이벤트는 성공'
        assert results[1] is True, '두 번째 이벤트는 성공'
        assert results[2] is True, '세 번째 이벤트는 성공'
        assert results[3] is False, '네 번째 이벤트는 드롭'
        assert results[4] is False, '다섯 번째 이벤트는 드롭'

        assert event_bus.get_queue_size() == small_queue_size, (
            f'큐 크기는 {small_queue_size}를 유지'
        )

        stats = event_bus.get_processing_stats()
        assert stats['events_published'] == 3, '성공한 이벤트만 카운트'

    def test_이벤트_처리_및_구독자_전달_검증_성공_시나리오(self) -> None:
        """8. 이벤트 처리 및 구독자 전달 검증 (성공 시나리오)

        목적: process_events 메서드의 이벤트 처리 및 전달 확인
        테스트할 범위: process_events 메서드
        커버하는 함수 및 데이터: 이벤트 처리 및 구독자 전달
        기대되는 안정성: 안정적인 이벤트 전달 보장
        """

        # Given - Mock 구독자와 이벤트
        class MockProcessingSubscriber(IEventSubscriber):
            def __init__(self, name: str):
                self.name = name
                self.received_events: list[BaseEvent] = []

            def get_subscribed_events(self) -> list[EventType]:
                return [EventType.ENEMY_DEATH, EventType.WEAPON_FIRED]

            def handle_event(self, event: BaseEvent) -> None:
                self.received_events.append(event)

            def get_subscriber_name(self) -> str:
                return self.name

        @dataclass
        class MockProcessEvent(BaseEvent):
            event_type : EventType
            def get_event_type(self) -> EventType:
                return self.event_type
            def validate(self) -> bool:
                return True

        event_bus = EventBus()
        subscriber1 = MockProcessingSubscriber('subscriber1')
        subscriber2 = MockProcessingSubscriber('subscriber2')

        # 구독자 등록
        event_bus.subscribe(subscriber1)
        event_bus.subscribe(subscriber2)

        # 이벤트 발행
        event1 = MockProcessEvent(
            event_type=EventType.ENEMY_DEATH,
            timestamp=3000.0,
            created_at=datetime.now(),
        )
        event2 = MockProcessEvent(
            event_type=EventType.WEAPON_FIRED,
            timestamp=3001.0,
            created_at=datetime.now(),
        )
        event3 = MockProcessEvent(
            event_type=EventType.ITEM_DROP,  # 구독되지 않은 이벤트
            timestamp=3002.0,
            created_at=datetime.now(),
        )

        event_bus.publish(event1)
        event_bus.publish(event2)
        event_bus.publish(event3)

        # When - 이벤트 처리
        processed_count = event_bus.process_events()

        # Then - 처리 결과 확인
        assert processed_count == 3, '3개 이벤트가 처리되어야 함'
        assert event_bus.is_queue_empty(), '처리 후 큐는 비어있어야 함'

        # 구독자별 수신 확인
        assert len(subscriber1.received_events) == 2, (
            'subscriber1이 2개 이벤트 수신'
        )
        assert len(subscriber2.received_events) == 2, (
            'subscriber2가 2개 이벤트 수신'
        )

        # 수신된 이벤트 타입 확인
        received_types1 = [e.event_type for e in subscriber1.received_events]
        received_types2 = [e.event_type for e in subscriber2.received_events]

        assert EventType.ENEMY_DEATH in received_types1
        assert EventType.WEAPON_FIRED in received_types1
        assert (
            EventType.ITEM_DROP not in received_types1
        )  # 구독하지 않은 이벤트

        assert EventType.ENEMY_DEATH in received_types2
        assert EventType.WEAPON_FIRED in received_types2
        assert (
            EventType.ITEM_DROP not in received_types2
        )  # 구독하지 않은 이벤트

        # 통계 확인
        stats = event_bus.get_processing_stats()
        assert stats['events_processed'] == 3, '처리된 이벤트 수 확인'
        assert stats['last_process_time'] > 0, '처리 시간이 기록되어야 함'

    def test_구독자_예외_격리_기능_검증_성공_시나리오(self) -> None:
        """9. 구독자 예외 격리 기능 검증 (성공 시나리오)

        목적: 구독자 예외 발생 시 다른 구독자에게 영향 없음 확인
        테스트할 범위: 예외 격리 처리
        커버하는 함수 및 데이터: 구독자 예외 격리 시스템
        기대되는 안정성: 예외 격리로 시스템 안정성 보장
        """

        # Given - 예외 발생 구독자와 정상 구독자
        class MockFailingSubscriber(IEventSubscriber):
            def get_subscribed_events(self) -> list[EventType]:
                return [EventType.PROJECTILE_HIT]

            def handle_event(self, event: BaseEvent) -> None:
                raise RuntimeError('Subscriber 처리 실패')

            def get_subscriber_name(self) -> str:
                return 'FailingSubscriber'

        class MockSuccessSubscriber(IEventSubscriber):
            def __init__(self):
                self.received_events: list[BaseEvent] = []

            def get_subscribed_events(self) -> list[EventType]:
                return [EventType.PROJECTILE_HIT]

            def handle_event(self, event: BaseEvent) -> None:
                self.received_events.append(event)

            def get_subscriber_name(self) -> str:
                return 'SuccessSubscriber'

        class MockExceptionEvent(BaseEvent):
            def get_event_type(self) -> EventType:
                return EventType.PROJECTILE_HIT
            def validate(self) -> bool:
                return True

        event_bus = EventBus()
        failing_subscriber = MockFailingSubscriber()
        success_subscriber = MockSuccessSubscriber()

        # 구독자 등록
        event_bus.subscribe(failing_subscriber)
        event_bus.subscribe(success_subscriber)

        # 이벤트 발행
        event = MockExceptionEvent(
            timestamp=4000.0,
            created_at=datetime.now(),
        )
        event_bus.publish(event)

        # When - 이벤트 처리 (예외 발생 예상)
        processed_count = event_bus.process_events()

        # Then - 예외 격리 확인
        assert processed_count == 1, '이벤트는 정상 처리되어야 함'
        assert len(success_subscriber.received_events) == 1, (
            '정상 구독자는 이벤트를 받아야 함'
        )

        # 예외 통계 확인
        stats = event_bus.get_processing_stats()
        assert stats['exceptions_caught'] == 1, '예외가 1번 포착되어야 함'
        assert stats['events_processed'] == 1, (
            '이벤트는 정상 처리된 것으로 카운트'
        )

    def test_재진입_방지_기능_검증_성공_시나리오(self) -> None:
        """10. 재진입 방지 기능 검증 (성공 시나리오)

        목적: process_events 호출 중 재진입 시도 시 방지 확인
        테스트할 범위: 재진입 방지 로직
        커버하는 함수 및 데이터: _processing_events 플래그
        기대되는 안정성: 무한 루프 및 스택 오버플로우 방지 보장
        """

        # Given - 재진입을 시도하는 구독자
        class MockReentrantSubscriber(IEventSubscriber):
            def __init__(self, event_bus: EventBus):
                self.event_bus = event_bus
                self.process_call_count = 0

            def get_subscribed_events(self) -> list[EventType]:
                return [EventType.BOSS_DEFEATED]

            def handle_event(self, event: BaseEvent) -> None:
                # 이벤트 처리 중 재진입 시도
                self.process_call_count = self.event_bus.process_events()

            def get_subscriber_name(self) -> str:
                return 'ReentrantSubscriber'

        class MockReentrantEvent(BaseEvent):
            def get_event_type(self) -> EventType:
                return EventType.BOSS_DEFEATED
            def validate(self) -> bool:
                return True

        event_bus = EventBus()
        reentrant_subscriber = MockReentrantSubscriber(event_bus)
        event_bus.subscribe(reentrant_subscriber)

        # 이벤트 발행
        event = MockReentrantEvent(
            timestamp=5000.0,
            created_at=datetime.now(),
        )
        event_bus.publish(event)

        # When - 이벤트 처리 (재진입 시도 포함)
        processed_count = event_bus.process_events()

        # Then - 재진입 방지 확인
        assert processed_count == 1, '원래 호출에서 1개 이벤트 처리'
        assert reentrant_subscriber.process_call_count == 0, (
            '재진입 호출은 0개 처리'
        )

    def test_큐_관리_기능_검증_성공_시나리오(self) -> None:
        """11. 큐 관리 기능 검증 (성공 시나리오)

        목적: 큐 조회 및 정리 기능 확인
        테스트할 범위: 큐 관리 메서드들
        커버하는 함수 및 데이터: clear_queue, get_queue_size 등
        기대되는 안정성: 안정적인 큐 관리 보장
        """

        # Given - 이벤트가 있는 EventBus
        class MockManagementEvent(BaseEvent):
            def get_event_type(self) -> EventType:
                return EventType.EXPERIENCE_GAIN
            def validate(self) -> bool:
                return True

        event_bus = EventBus()

        # 여러 이벤트 발행
        for i in range(5):
            event = MockManagementEvent(
                timestamp=float(i),
                created_at=datetime.now(),
            )
            event_bus.publish(event)

        # When & Then - 큐 상태 확인
        assert event_bus.get_queue_size() == 5, '큐에 5개 이벤트가 있어야 함'
        assert not event_bus.is_queue_empty(), '큐가 비어있지 않아야 함'

        # When - 큐 정리
        cleared_count = event_bus.clear_queue()

        # Then - 정리 결과 확인
        assert cleared_count == 5, '5개 이벤트가 정리되어야 함'
        assert event_bus.get_queue_size() == 0, '큐가 비어있어야 함'
        assert event_bus.is_queue_empty(), '큐가 빈 상태여야 함'

    def test_성능_통계_정확성_검증_성공_시나리오(self) -> None:
        """12. 성능 통계 정확성 검증 (성공 시나리오)

        목적: get_processing_stats 메서드의 통계 정확성 확인
        테스트할 범위: 성능 통계 수집 및 조회
        커버하는 함수 및 데이터: 모든 통계 항목
        기대되는 안정성: 정확한 성능 모니터링 보장
        """

        # Given - 통계 수집용 구독자
        class MockStatsSubscriber(IEventSubscriber):
            def get_subscribed_events(self) -> list[EventType]:
                return [EventType.LEVEL_UP]

            def handle_event(self, event: BaseEvent) -> None:
                time.sleep(0.001)  # 처리 시간 시뮬레이션

            def get_subscriber_name(self) -> str:
                return 'StatsSubscriber'

        class MockStatsEvent(BaseEvent):
            def get_event_type(self) -> EventType:
                return EventType.LEVEL_UP
            def validate(self) -> bool:
                return True

        event_bus = EventBus()
        subscriber = MockStatsSubscriber()
        event_bus.subscribe(subscriber)

        # When - 이벤트 발행 및 처리
        for i in range(3):
            event = MockStatsEvent(
                timestamp=float(i),
                created_at=datetime.now(),
            )
            event_bus.publish(event)

        processed_count = event_bus.process_events()

        # Then - 통계 정확성 확인
        stats = event_bus.get_processing_stats()
        assert stats['events_published'] == 3, '발행된 이벤트 수가 정확해야 함'
        assert stats['events_processed'] == 3, '처리된 이벤트 수가 정확해야 함'
        assert stats['exceptions_caught'] == 0, '예외 수가 정확해야 함'
        assert stats['last_process_time'] > 0.001, '처리 시간이 기록되어야 함'
        assert stats['queue_size'] == 0, '현재 큐 크기가 정확해야 함'
        assert stats['total_subscribers'] == 1, '구독자 수가 정확해야 함'
        assert stats['subscribed_event_types'] == 1, (
            '구독된 이벤트 타입 수가 정확해야 함'
        )
        assert stats['is_processing'] is False, (
            '처리 완료 후 플래그가 해제되어야 함'
        )

    def test_헬스_상태_모니터링_검증_성공_시나리오(self) -> None:
        """13. 헬스 상태 모니터링 검증 (성공 시나리오)

        목적: get_health_status 메서드의 상태 판단 로직 확인
        테스트할 범위: 헬스 상태 모니터링
        커버하는 함수 및 데이터: 상태 판단 알고리즘
        기대되는 안정성: 정확한 시스템 상태 진단 보장
        """
        # Given - 헬스 모니터링용 EventBus
        event_bus = EventBus(max_queue_size=100)

        class MockHealthSubscriber(IEventSubscriber):
            def get_subscribed_events(self) -> list[EventType]:
                return [EventType.GAME_STARTED]

            def handle_event(self, event: BaseEvent) -> None:
                pass

            def get_subscriber_name(self) -> str:
                return 'HealthSubscriber'

        # When & Then - 초기 상태 (구독자 없음)
        health = event_bus.get_health_status()
        assert health['status'] == 'healthy', '초기 상태는 healthy여야 함'
        assert health['queue_utilization'] == 0.0, '큐 사용률은 0%여야 함'
        assert health['has_subscribers'] is False, '구독자가 없어야 함'
        assert health['processing_errors'] == 0, '처리 에러가 없어야 함'
        assert health['is_operational'] is False, (
            '운영 상태가 아니어야 함 (구독자 없음)'
        )

        # When - 구독자 등록
        subscriber = MockHealthSubscriber()
        event_bus.subscribe(subscriber)

        # Then - 운영 상태 확인
        health = event_bus.get_health_status()
        assert health['has_subscribers'] is True, '구독자가 있어야 함'
        assert health['is_operational'] is True, '운영 상태여야 함'

    def test_큐_사용률_경고_및_에러_상태_검증_성공_시나리오(self) -> None:
        """14. 큐 사용률 경고 및 에러 상태 검증 (성공 시나리오)

        목적: 큐 사용률에 따른 헬스 상태 변화 확인
        테스트할 범위: 헬스 상태 임계치 판단
        커버하는 함수 및 데이터: 상태 판단 로직
        기대되는 안정성: 적절한 경고 및 에러 상태 감지 보장
        """
        # Given - 작은 큐 크기로 EventBus 생성
        small_queue = 10
        event_bus = EventBus(max_queue_size=small_queue)

        class MockHealthEvent(BaseEvent):
            def get_event_type(self) -> EventType:
                return EventType.GAME_OVER
            def validate(self) -> bool:
                return True

        # When - 70% 초과 사용률 (경고 상태)
        for i in range(8):  # 80% 사용률
            event = MockHealthEvent(
                timestamp=float(i),
                created_at=datetime.now(),
            )
            event_bus.publish(event)

        # Then - 경고 상태 확인
        health = event_bus.get_health_status()
        assert health['status'] == 'warning', (
            '70% 초과 사용률에서 warning 상태여야 함'
        )
        assert health['queue_utilization'] == 80.0, '큐 사용률이 80%여야 함'

        # When - 90% 초과 사용률 (에러 상태)
        for i in range(2):  # 추가로 2개 더 (총 100% 사용률)
            event = MockHealthEvent(
                timestamp=float(i + 8),
                created_at=datetime.now(),
            )
            event_bus.publish(event)

        # Then - 에러 상태 확인
        health = event_bus.get_health_status()
        assert health['status'] == 'error', (
            '90% 초과 사용률에서 error 상태여야 함'
        )
        assert health['queue_utilization'] == 100.0, '큐 사용률이 100%여야 함'

    def test_통계_리셋_기능_검증_성공_시나리오(self) -> None:
        """15. 통계 리셋 기능 검증 (성공 시나리오)

        목적: reset_stats 메서드의 통계 초기화 기능 확인
        테스트할 범위: 통계 리셋 기능
        커버하는 함수 및 데이터: 통계 초기화
        기대되는 안정성: 정확한 통계 초기화 보장
        """
        # Given - 통계가 있는 EventBus
        event_bus = EventBus()

        class MockResetSubscriber(IEventSubscriber):
            def get_subscribed_events(self) -> list[EventType]:
                return [EventType.GAME_PAUSED]

            def handle_event(self, event: BaseEvent) -> None:
                raise ValueError('통계용 예외')

            def get_subscriber_name(self) -> str:
                return 'ResetSubscriber'

        class MockResetEvent(BaseEvent):
            def get_event_type(self) -> EventType:
                return EventType.GAME_PAUSED
            def validate(self) -> bool:
                return True

        # 통계 누적
        subscriber = MockResetSubscriber()
        event_bus.subscribe(subscriber)

        event = MockResetEvent(
            timestamp=6000.0,
            created_at=datetime.now(),
        )
        event_bus.publish(event)
        event_bus.process_events()  # 예외 발생으로 통계 누적

        # 통계 확인
        stats_before = event_bus.get_processing_stats()
        assert stats_before['events_published'] > 0, '발행 통계가 있어야 함'
        assert stats_before['events_processed'] > 0, '처리 통계가 있어야 함'
        assert stats_before['exceptions_caught'] > 0, '예외 통계가 있어야 함'
        assert stats_before['last_process_time'] > 0, '처리 시간이 있어야 함'

        # When - 통계 리셋
        event_bus.reset_stats()

        # Then - 리셋 확인
        stats_after = event_bus.get_processing_stats()
        assert stats_after['events_published'] == 0, (
            '발행 통계가 리셋되어야 함'
        )
        assert stats_after['events_processed'] == 0, (
            '처리 통계가 리셋되어야 함'
        )
        assert stats_after['exceptions_caught'] == 0, (
            '예외 통계가 리셋되어야 함'
        )
        assert stats_after['last_process_time'] == 0.0, (
            '처리 시간이 리셋되어야 함'
        )

        # 리셋되지 않아야 하는 항목들
        assert stats_after['queue_size'] == stats_before['queue_size'], (
            '큐 크기는 유지되어야 함'
        )
        assert (
            stats_after['total_subscribers']
            == stats_before['total_subscribers']
        ), '구독자 수는 유지되어야 함'

    def test_문자열_표현_포맷_검증_성공_시나리오(self) -> None:
        """16. 문자열 표현 포맷 검증 (성공 시나리오)

        목적: __str__ 및 __repr__ 메서드의 출력 포맷 확인
        테스트할 범위: 문자열 표현 메서드
        커버하는 함수 및 데이터: 문자열 포맷팅
        기대되는 안정성: 일관된 디버깅 정보 제공 보장
        """
        # Given - 설정된 상태의 EventBus
        event_bus = EventBus(max_queue_size=500)

        class MockStringSubscriber(IEventSubscriber):
            def get_subscribed_events(self) -> list[EventType]:
                return [EventType.GAME_RESUMED]

            def handle_event(self, event: BaseEvent) -> None:
                pass

            def get_subscriber_name(self) -> str:
                return 'StringSubscriber'

        class MockStringEvent(BaseEvent):
            def get_event_type(self) -> EventType:
                return EventType.GAME_RESUMED
            def validate(self) -> bool:
                return True

        # 구독자 등록 및 이벤트 발행
        subscriber = MockStringSubscriber()
        event_bus.subscribe(subscriber)

        event = MockStringEvent(
            timestamp=7000.0,
            created_at=datetime.now(),
        )
        event_bus.publish(event)
        event_bus.process_events()

        # When - 문자열 표현 생성
        str_repr = str(event_bus)
        repr_str = repr(event_bus)

        # Then - 포맷 검증
        # __str__ 검증
        assert 'EventBus(' in str_repr, '__str__에 클래스명이 포함되어야 함'
        assert 'queue=' in str_repr, '__str__에 큐 정보가 포함되어야 함'
        assert 'subscribers=' in str_repr, (
            '__str__에 구독자 정보가 포함되어야 함'
        )
        assert 'processed=' in str_repr, '__str__에 처리 정보가 포함되어야 함'
        assert 'errors=' in str_repr, '__str__에 에러 정보가 포함되어야 함'

        # __repr__ 검증
        assert 'EventBus(' in repr_str, '__repr__에 클래스명이 포함되어야 함'
        assert 'max_queue_size=500' in repr_str, (
            '__repr__에 최대 큐 크기가 포함되어야 함'
        )
        assert 'current_queue_size=' in repr_str, (
            '__repr__에 현재 큐 크기가 포함되어야 함'
        )
        assert 'subscriber_count=' in repr_str, (
            '__repr__에 구독자 수가 포함되어야 함'
        )
        assert 'is_processing=' in repr_str, (
            '__repr__에 처리 상태가 포함되어야 함'
        )

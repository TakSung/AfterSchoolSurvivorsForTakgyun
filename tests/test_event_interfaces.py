"""
Unit tests for event system interfaces.

Tests the IEventSubscriber, IEventPublisher, and IEventHandler
interfaces to ensure proper contracts and implementation requirements.
"""

from dataclasses import dataclass
import pytest

from src.core.events.base_event import BaseEvent
from src.core.events.event_types import EventType
from src.core.events.interfaces import (
    IEventHandler,
    IEventPublisher,
    IEventSubscriber,
)


class TestIEventSubscriber:
    """Test class for IEventSubscriber interface functionality."""

    def test_구독자_인터페이스_구현_강제_검증_성공_시나리오(self) -> None:
        """1. 구독자 인터페이스 구현 강제 검증 (성공 시나리오)

        목적: IEventSubscriber 인터페이스의 추상 메서드 구현 강제 확인
        테스트할 범위: ABC 추상 메서드 구현 요구사항
        커버하는 함수 및 데이터: handle_event, get_subscribed_events 메서드
        기대되는 안정성: 인터페이스 구현 일관성 보장
        """

        # Given - 미완성 구독자 클래스
        class IncompleteSubscriber(IEventSubscriber):
            pass  # 추상 메서드 미구현

        # When & Then - 인스턴스 생성 시 에러 발생
        with pytest.raises(TypeError) as exc_info:
            IncompleteSubscriber()

        assert 'abstract' in str(exc_info.value).lower(), (
            '추상 메서드 구현 에러가 발생해야 함'
        )

    def test_완전한_구독자_구현_및_기본_메서드_검증_성공_시나리오(
        self,
    ) -> None:
        """2. 완전한 구독자 구현 및 기본 메서드 검증 (성공 시나리오)

        목적: 완전한 IEventSubscriber 구현체의 기본 기능 확인
        테스트할 범위: 완전 구현된 구독자 클래스
        커버하는 함수 및 데이터: 모든 인터페이스 메서드
        기대되는 안정성: 정상적인 구독자 동작 보장
        """

        # Given - 완전한 구독자 구현
        class MockEventSubscriber(IEventSubscriber):
            def __init__(self) -> None:
                self.handled_events: list[BaseEvent] = []
                self.subscribed_types = [
                    EventType.ENEMY_DEATH,
                    EventType.ITEM_PICKUP,
                ]

            def handle_event(self, event: BaseEvent) -> None:
                self.handled_events.append(event)

            def get_subscribed_events(self) -> list[EventType]:
                return self.subscribed_types.copy()

        # Mock Event 클래스
        class MockEvent(BaseEvent):
            def get_event_type(self) -> EventType:
                raise NotImplementedError()
            def validate(self) -> bool:
                return True

        # When - 구독자 생성 및 기본 기능 테스트
        subscriber = MockEventSubscriber()

        # Then - 구독 이벤트 목록 확인
        subscribed = subscriber.get_subscribed_events()
        assert len(subscribed) == 2, '구독하는 이벤트가 2개여야 함'
        assert EventType.ENEMY_DEATH in subscribed, (
            '적 사망 이벤트를 구독해야 함'
        )
        assert EventType.ITEM_PICKUP in subscribed, (
            '아이템 획득 이벤트를 구독해야 함'
        )

        # is_subscribed_to 메서드 테스트
        assert subscriber.is_subscribed_to(EventType.ENEMY_DEATH), (
            '적 사망 이벤트 구독 확인'
        )
        assert subscriber.is_subscribed_to(EventType.ITEM_PICKUP), (
            '아이템 획득 이벤트 구독 확인'
        )
        assert not subscriber.is_subscribed_to(EventType.BOSS_SPAWNED), (
            '보스 등장 이벤트는 구독하지 않아야 함'
        )

        # 구독자 이름 확인
        name = subscriber.get_subscriber_name()
        assert name == 'MockEventSubscriber', (
            '구독자 이름이 클래스명과 일치해야 함'
        )

    def test_이벤트_처리_기능_정상_동작_검증_성공_시나리오(self) -> None:
        """3. 이벤트 처리 기능 정상 동작 검증 (성공 시나리오)

        목적: handle_event 메서드의 정상적인 이벤트 처리 확인
        테스트할 범위: handle_event 메서드 동작
        커버하는 함수 및 데이터: 이벤트 처리 로직
        기대되는 안정성: 안정적인 이벤트 처리 보장
        """

        # Given - 이벤트 처리 구독자
        class EventProcessingSubscriber(IEventSubscriber):
            def __init__(self) -> None:
                self.processed_events: list[tuple[EventType, float]] = []

            def handle_event(self, event: BaseEvent) -> None:
                # 이벤트 타입과 타임스탬프 기록
                self.processed_events.append(
                    (event.get_event_type(), event.timestamp)
                )

            def get_subscribed_events(self) -> list[EventType]:
                return [EventType.WEAPON_FIRED, EventType.PROJECTILE_HIT]

        @dataclass
        class MockCombatEvent(BaseEvent):
            event_type:EventType
            def get_event_type(self) -> EventType:
                return self.event_type
            def validate(self) -> bool:
                return True

        # When - 구독자 생성 및 이벤트 처리
        subscriber = EventProcessingSubscriber()

        # 첫 번째 이벤트 처리
        event1 = MockCombatEvent(
            event_type=EventType.WEAPON_FIRED,
            timestamp=1000.0,
            created_at=None,
        )
        subscriber.handle_event(event1)

        # 두 번째 이벤트 처리
        event2 = MockCombatEvent(
            event_type=EventType.PROJECTILE_HIT,
            timestamp=1001.5,
            created_at=None,
        )
        subscriber.handle_event(event2)

        # Then - 이벤트 처리 결과 확인
        assert len(subscriber.processed_events) == 2, (
            '2개 이벤트가 처리되어야 함'
        )

        first_processed = subscriber.processed_events[0]
        assert first_processed[0] == EventType.WEAPON_FIRED, (
            '첫 번째 이벤트 타입 확인'
        )
        assert first_processed[1] == 1000.0, '첫 번째 이벤트 타임스탬프 확인'

        second_processed = subscriber.processed_events[1]
        assert second_processed[0] == EventType.PROJECTILE_HIT, (
            '두 번째 이벤트 타입 확인'
        )
        assert second_processed[1] == 1001.5, '두 번째 이벤트 타임스탬프 확인'


class TestIEventPublisher:
    """Test class for IEventPublisher interface functionality."""

    def test_발행자_인터페이스_구현_강제_검증_성공_시나리오(self) -> None:
        """4. 발행자 인터페이스 구현 강제 검증 (성공 시나리오)

        목적: IEventPublisher 인터페이스의 추상 메서드 구현 강제 확인
        테스트할 범위: ABC 추상 메서드 구현 요구사항
        커버하는 함수 및 데이터: publish_event, subscribe, unsubscribe 메서드
        기대되는 안정성: 발행자 인터페이스 구현 일관성 보장
        """

        # Given - 미완성 발행자 클래스
        class IncompletePublisher(IEventPublisher):
            pass  # 추상 메서드 미구현

        # When & Then - 인스턴스 생성 시 에러 발생
        with pytest.raises(TypeError) as exc_info:
            IncompletePublisher()

        assert 'abstract' in str(exc_info.value).lower(), (
            '추상 메서드 구현 에러가 발생해야 함'
        )

    def test_완전한_발행자_구현_기본_기능_검증_성공_시나리오(self) -> None:
        """5. 완전한 발행자 구현 기본 기능 검증 (성공 시나리오)

        목적: 완전한 IEventPublisher 구현체의 기본 기능 확인
        테스트할 범위: 완전 구현된 발행자 클래스
        커버하는 함수 및 데이터: 모든 발행자 인터페이스 메서드
        기대되는 안정성: 정상적인 이벤트 발행 시스템 동작 보장
        """

        # Given - 완전한 발행자 구현
        class MockEventPublisher(IEventPublisher):
            def __init__(self) -> None:
                self.subscribers: list[IEventSubscriber] = []
                self.published_events: list[BaseEvent] = []

            def publish_event(self, event: BaseEvent) -> None:
                self.published_events.append(event)
                # 구독자들에게 이벤트 전달
                for subscriber in self.subscribers:
                    if subscriber.is_subscribed_to(event.get_event_type()):
                        subscriber.handle_event(event)

            def subscribe(self, subscriber: IEventSubscriber) -> None:
                if subscriber not in self.subscribers:
                    self.subscribers.append(subscriber)

            def unsubscribe(self, subscriber: IEventSubscriber) -> None:
                if subscriber in self.subscribers:
                    self.subscribers.remove(subscriber)

        # Mock 구독자
        class TestSubscriber(IEventSubscriber):
            def __init__(self, name: str) -> None:
                self.name = name
                self.received_events: list[BaseEvent] = []

            def handle_event(self, event: BaseEvent) -> None:
                self.received_events.append(event)

            def get_subscribed_events(self) -> list[EventType]:
                return [EventType.ENEMY_DEATH]

        # When - 발행자와 구독자 설정
        publisher = MockEventPublisher()
        subscriber1 = TestSubscriber('subscriber1')
        subscriber2 = TestSubscriber('subscriber2')

        # 구독자 등록
        publisher.subscribe(subscriber1)
        publisher.subscribe(subscriber2)

        # Then - 구독자 등록 확인
        assert len(publisher.subscribers) == 2, '2명의 구독자가 등록되어야 함'
        assert subscriber1 in publisher.subscribers, (
            '첫 번째 구독자가 등록되어야 함'
        )
        assert subscriber2 in publisher.subscribers, (
            '두 번째 구독자가 등록되어야 함'
        )

        # 구독자 해제 테스트
        publisher.unsubscribe(subscriber1)
        assert len(publisher.subscribers) == 1, '구독자가 1명 남아야 함'
        assert subscriber1 not in publisher.subscribers, (
            '첫 번째 구독자가 해제되어야 함'
        )


class TestIEventHandler:
    """Test class for IEventHandler interface functionality."""

    def test_핸들러_인터페이스_구현_강제_검증_성공_시나리오(self) -> None:
        """6. 핸들러 인터페이스 구현 강제 검증 (성공 시나리오)

        목적: IEventHandler 인터페이스의 추상 메서드 구현 강제 확인
        테스트할 범위: ABC 추상 메서드 구현 요구사항
        커버하는 함수 및 데이터: handle, can_handle 메서드
        기대되는 안정성: 핸들러 인터페이스 구현 일관성 보장
        """

        # Given - 미완성 핸들러 클래스
        class IncompleteHandler(IEventHandler):
            pass  # 추상 메서드 미구현

        # When & Then - 인스턴스 생성 시 에러 발생
        with pytest.raises(TypeError) as exc_info:
            IncompleteHandler()

        assert 'abstract' in str(exc_info.value).lower(), (
            '추상 메서드 구현 에러가 발생해야 함'
        )

    def test_특정_이벤트_핸들러_구현_검증_성공_시나리오(self) -> None:
        """7. 특정 이벤트 핸들러 구현 검증 (성공 시나리오)

        목적: 특정 이벤트 타입만 처리하는 핸들러 구현 확인
        테스트할 범위: 완전 구현된 핸들러 클래스
        커버하는 함수 및 데이터: handle, can_handle 메서드 동작
        기대되는 안정성: 특화된 이벤트 처리 보장
        """

        # Given - 적 사망 이벤트 전용 핸들러
        class EnemyDeathHandler(IEventHandler):
            def __init__(self) -> None:
                self.handled_count = 0
                self.last_handled_event: BaseEvent | None = None

            def handle(self, event: BaseEvent) -> bool:
                if self.can_handle(event.get_event_type()):
                    self.handled_count += 1
                    self.last_handled_event = event
                    return True
                return False

            def can_handle(self, event_type: EventType) -> bool:
                return event_type == EventType.ENEMY_DEATH

        @dataclass
        class MockDeathEvent(BaseEvent):
            event_type:EventType
            def get_event_type(self) -> EventType:
                return self.event_type
            def validate(self) -> bool:
                return True

        # When - 핸들러 생성 및 테스트
        handler = EnemyDeathHandler()

        # 처리 가능한 이벤트 타입 확인
        assert handler.can_handle(EventType.ENEMY_DEATH), (
            '적 사망 이벤트를 처리할 수 있어야 함'
        )
        assert not handler.can_handle(EventType.ITEM_DROP), (
            '아이템 드롭 이벤트는 처리할 수 없어야 함'
        )
        assert not handler.can_handle(EventType.BOSS_SPAWNED), (
            '보스 등장 이벤트는 처리할 수 없어야 함'
        )

        # 이벤트 처리 테스트
        death_event = MockDeathEvent(
            event_type=EventType.ENEMY_DEATH,
            timestamp=2000.0,
            created_at=None
        )

        result = handler.handle(death_event)

        # Then - 처리 결과 확인
        assert result is True, '적 사망 이벤트 처리가 성공해야 함'
        assert handler.handled_count == 1, '처리된 이벤트 수가 1이어야 함'
        assert handler.last_handled_event == death_event, (
            '마지막 처리된 이벤트가 일치해야 함'
        )

        # 처리할 수 없는 이벤트 테스트
        item_event = MockDeathEvent(
            event_type=EventType.ITEM_PICKUP,
            timestamp=2001.0,
            created_at=None
        )

        result = handler.handle(item_event)

        assert result is False, '아이템 획득 이벤트 처리가 실패해야 함'
        assert handler.handled_count == 1, (
            '처리된 이벤트 수는 여전히 1이어야 함'
        )

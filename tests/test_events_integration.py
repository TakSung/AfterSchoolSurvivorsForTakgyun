"""
Integration tests for the complete event system.

Tests the integration between EnemyDeathEvent, EventBus, and event interfaces
to ensure the entire event system works together correctly.
"""

from unittest.mock import Mock

from src.core.events import (
    BaseEvent,
    EnemyDeathEvent,
    EventBus,
    EventType,
    IEventSubscriber,
)


class TestEventsIntegration:
    """Test class for event system integration."""

    def test_이벤트_시스템_전체_통합_동작_검증_성공_시나리오(self) -> None:
        """1. 이벤트 시스템 전체 통합 동작 검증 (성공 시나리오)

        목적: EnemyDeathEvent와 EventBus가 함께 올바르게 동작하는지 확인
        테스트할 범위: 이벤트 발행, 구독, 처리의 전체 흐름
        커버하는 함수 및 데이터: 통합된 이벤트 시스템
        기대되는 안정성: 완전한 이벤트 처리 파이프라인 보장
        """

        # Given - 이벤트 구독자와 이벤트 버스
        class MockEnemyDeathSubscriber(IEventSubscriber):
            def __init__(self):
                self.received_events: list[EnemyDeathEvent] = []

            def get_subscribed_events(self) -> list[EventType]:
                return [EventType.ENEMY_DEATH]

            def handle_event(self, event: BaseEvent) -> None:
                if isinstance(event, EnemyDeathEvent):
                    self.received_events.append(event)

            def get_subscriber_name(self) -> str:
                return 'MockEnemyDeathSubscriber'

        event_bus = EventBus()
        subscriber = MockEnemyDeathSubscriber()

        # When - 구독자 등록 및 이벤트 발행
        event_bus.subscribe(subscriber)

        enemy_death_event = EnemyDeathEvent.create_from_id(
            'enemy_integration_test'
        )
        published = event_bus.publish(enemy_death_event)
        processed_count = event_bus.process_events()

        # Then - 전체 플로우 검증
        assert published is True, '이벤트가 성공적으로 발행되어야 함'
        assert processed_count == 1, '1개 이벤트가 처리되어야 함'
        assert len(subscriber.received_events) == 1, (
            '구독자가 1개 이벤트를 받아야 함'
        )

        received_event = subscriber.received_events[0]
        assert received_event.enemy_entity_id == 'enemy_integration_test', (
            '받은 이벤트의 적 ID가 일치해야 함'
        )
        assert received_event.get_event_type() == EventType.ENEMY_DEATH, (
            '받은 이벤트의 타입이 ENEMY_DEATH여야 함'
        )

    def test_다중_구독자_이벤트_브로드캐스트_검증_성공_시나리오(self) -> None:
        """2. 다중 구독자 이벤트 브로드캐스트 검증 (성공 시나리오)

        목적: 하나의 EnemyDeathEvent가 여러 구독자에게 올바르게 전달되는지 확인
        테스트할 범위: 이벤트 브로드캐스팅
        커버하는 함수 및 데이터: 다중 구독자 관리
        기대되는 안정성: 모든 구독자 동시 이벤트 수신 보장
        """

        # Given - 다중 구독자
        class MockCombatSubscriber(IEventSubscriber):
            def __init__(self, name: str):
                self.name = name
                self.received_enemy_deaths: list[str] = []

            def get_subscribed_events(self) -> list[EventType]:
                return [EventType.ENEMY_DEATH, EventType.WEAPON_FIRED]

            def handle_event(self, event: BaseEvent) -> None:
                if isinstance(event, EnemyDeathEvent):
                    self.received_enemy_deaths.append(event.enemy_entity_id)

            def get_subscriber_name(self) -> str:
                return self.name

        event_bus = EventBus()
        subscriber1 = MockCombatSubscriber('CombatSubscriber1')
        subscriber2 = MockCombatSubscriber('CombatSubscriber2')
        subscriber3 = MockCombatSubscriber('CombatSubscriber3')

        # When - 모든 구독자 등록 및 이벤트 발행
        event_bus.subscribe(subscriber1)
        event_bus.subscribe(subscriber2)
        event_bus.subscribe(subscriber3)

        enemy_death_event = EnemyDeathEvent.create_from_id(
            'boss_multi_subscriber'
        )
        event_bus.publish(enemy_death_event)
        event_bus.process_events()

        # Then - 모든 구독자가 이벤트를 받았는지 확인
        assert len(subscriber1.received_enemy_deaths) == 1, (
            '첫 번째 구독자가 이벤트를 받아야 함'
        )
        assert len(subscriber2.received_enemy_deaths) == 1, (
            '두 번째 구독자가 이벤트를 받아야 함'
        )
        assert len(subscriber3.received_enemy_deaths) == 1, (
            '세 번째 구독자가 이벤트를 받아야 함'
        )

        for subscriber in [subscriber1, subscriber2, subscriber3]:
            assert (
                subscriber.received_enemy_deaths[0] == 'boss_multi_subscriber'
            ), f'{subscriber.name}이 올바른 적 ID를 받아야 함'

    def test_이벤트_타입_필터링_정확성_검증_성공_시나리오(self) -> None:
        """3. 이벤트 타입 필터링 정확성 검증 (성공 시나리오)

        목적: 구독자가 관심 있는 이벤트만 받는지 확인
        테스트할 범위: 이벤트 타입 기반 필터링
        커버하는 함수 및 데이터: 선택적 이벤트 수신
        기대되는 안정성: 불필요한 이벤트 차단 보장
        """

        # Given - 특정 이벤트만 구독하는 구독자
        class MockSelectiveSubscriber(IEventSubscriber):
            def __init__(self, subscribed_types: list[EventType]):
                self.subscribed_types = subscribed_types
                self.received_events: list[BaseEvent] = []

            def get_subscribed_events(self) -> list[EventType]:
                return self.subscribed_types

            def handle_event(self, event: BaseEvent) -> None:
                self.received_events.append(event)

            def get_subscriber_name(self) -> str:
                return 'SelectiveSubscriber'

        # Mock 다른 타입 이벤트
        class MockItemEvent(BaseEvent):
            def __init__(self):
                super().__init__(
                    timestamp=0.0,
                    created_at=None,
                )
                
            def get_event_type(self) -> EventType:
                return EventType.ITEM_DROP

            def validate(self) -> bool:
                return True

        event_bus = EventBus()

        # 적 사망 이벤트만 구독하는 구독자
        enemy_only_subscriber = MockSelectiveSubscriber(
            [EventType.ENEMY_DEATH]
        )
        # 아이템 이벤트만 구독하는 구독자
        item_only_subscriber = MockSelectiveSubscriber([EventType.ITEM_DROP])

        event_bus.subscribe(enemy_only_subscriber)
        event_bus.subscribe(item_only_subscriber)

        # When - 두 타입의 이벤트 발행
        enemy_event = EnemyDeathEvent.create_from_id('filtered_enemy')
        item_event = MockItemEvent()

        event_bus.publish(enemy_event)
        event_bus.publish(item_event)
        event_bus.process_events()

        # Then - 각 구독자가 관심 있는 이벤트만 받았는지 확인
        assert len(enemy_only_subscriber.received_events) == 1, (
            '적 사망 전용 구독자는 1개 이벤트만 받아야 함'
        )
        assert isinstance(
            enemy_only_subscriber.received_events[0], EnemyDeathEvent
        ), '적 사망 전용 구독자는 EnemyDeathEvent를 받아야 함'

        assert len(item_only_subscriber.received_events) == 1, (
            '아이템 전용 구독자는 1개 이벤트만 받아야 함'
        )
        assert (
            item_only_subscriber.received_events[0].get_event_type()
            == EventType.ITEM_DROP
        ), '아이템 전용 구독자는 ITEM_DROP 이벤트를 받아야 함'

    def test_모듈_임포트_완전성_검증_성공_시나리오(self) -> None:
        """4. 모듈 임포트 완전성 검증 (성공 시나리오)

        목적: 이벤트 시스템 모듈들이 올바르게 임포트되는지 확인
        테스트할 범위: 모듈 구조 및 임포트
        커버하는 함수 및 데이터: __init__.py 설정
        기대되는 안정성: 모듈 접근성 보장
        """
        # Given & When - 모듈 임포트 테스트
        from src.core.events import (
            BaseEvent,
            EnemyDeathEvent,
            EventBus,
            EventType,
            IEventHandler,
            IEventPublisher,
            IEventSubscriber,
        )

        # Then - 모든 클래스가 올바르게 임포트되었는지 확인
        assert BaseEvent is not None, 'BaseEvent가 임포트되어야 함'
        assert EnemyDeathEvent is not None, 'EnemyDeathEvent가 임포트되어야 함'
        assert EventBus is not None, 'EventBus가 임포트되어야 함'
        assert EventType is not None, 'EventType이 임포트되어야 함'
        assert IEventHandler is not None, 'IEventHandler가 임포트되어야 함'
        assert IEventPublisher is not None, 'IEventPublisher가 임포트되어야 함'
        assert IEventSubscriber is not None, (
            'IEventSubscriber가 임포트되어야 함'
        )

        # EnemyDeathEvent가 BaseEvent를 상속하는지 확인
        assert issubclass(EnemyDeathEvent, BaseEvent), (
            'EnemyDeathEvent가 BaseEvent를 상속해야 함'
        )

    def test_이벤트_생성_편의_메서드_통합_검증_성공_시나리오(self) -> None:
        """5. 이벤트 생성 편의 메서드 통합 검증 (성공 시나리오)

        목적: Entity 객체 기반 이벤트 생성이 전체 시스템에서 작동하는지 확인
        테스트할 범위: Entity 연동 이벤트 생성
        커버하는 함수 및 데이터: create_from_entity 메서드 통합
        기대되는 안정성: Entity 기반 이벤트 생성 및 처리 보장
        """

        # Given - Mock Entity와 구독자
        class MockEntitySubscriber(IEventSubscriber):
            def __init__(self):
                self.processed_entities: list[str] = []

            def get_subscribed_events(self) -> list[EventType]:
                return [EventType.ENEMY_DEATH]

            def handle_event(self, event: BaseEvent) -> None:
                if isinstance(event, EnemyDeathEvent):
                    self.processed_entities.append(event.enemy_entity_id)

            def get_subscriber_name(self) -> str:
                return 'EntitySubscriber'

        mock_entity = Mock()
        mock_entity.id = 'boss_entity_integration'

        event_bus = EventBus()
        subscriber = MockEntitySubscriber()
        event_bus.subscribe(subscriber)

        # When - Entity로부터 이벤트 생성 및 처리
        enemy_death_event = EnemyDeathEvent.create_from_entity(mock_entity)
        event_bus.publish(enemy_death_event)
        event_bus.process_events()

        # Then - 정상적인 처리 확인
        assert len(subscriber.processed_entities) == 1, (
            '1개 엔티티가 처리되어야 함'
        )
        assert subscriber.processed_entities[0] == 'boss_entity_integration', (
            '올바른 엔티티 ID가 처리되어야 함'
        )

    def test_이벤트_검증_실패_시_시스템_안정성_검증_성공_시나리오(
        self,
    ) -> None:
        """6. 이벤트 검증 실패 시 시스템 안정성 검증 (성공 시나리오)

        목적: 잘못된 이벤트가 시스템을 중단시키지 않는지 확인
        테스트할 범위: 잘못된 이벤트 처리
        커버하는 함수 및 데이터: 예외 상황 안정성
        기대되는 안정성: 시스템 견고성 보장
        """

        # Given - Mock 잘못된 이벤트
        class MockInvalidEvent(BaseEvent):
            def __init__(self):
                super().__init__(
                    timestamp=0.0,
                    created_at=None,
                )
                
            def get_event_type(self) -> EventType:
                return EventType.ENEMY_DEATH

            def validate(self) -> bool:
                return False  # 항상 검증 실패

        class MockRobustSubscriber(IEventSubscriber):
            def __init__(self):
                self.valid_events_received = 0

            def get_subscribed_events(self) -> list[EventType]:
                return [EventType.ENEMY_DEATH]

            def handle_event(self, event: BaseEvent) -> None:
                self.valid_events_received += 1

            def get_subscriber_name(self) -> str:
                return 'RobustSubscriber'

        event_bus = EventBus()
        subscriber = MockRobustSubscriber()
        event_bus.subscribe(subscriber)

        # When - 유효한 이벤트와 잘못된 이벤트 발행
        valid_event = EnemyDeathEvent.create_from_id('valid_enemy')
        invalid_event = MockInvalidEvent()

        valid_published = event_bus.publish(valid_event)
        invalid_published = event_bus.publish(invalid_event)
        processed_count = event_bus.process_events()

        # Then - 시스템이 견고하게 동작하는지 확인
        assert valid_published is True, '유효한 이벤트는 발행되어야 함'
        assert invalid_published is False, '잘못된 이벤트는 거부되어야 함'
        assert processed_count == 1, '유효한 이벤트 1개만 처리되어야 함'
        assert subscriber.valid_events_received == 1, (
            '구독자는 유효한 이벤트만 받아야 함'
        )

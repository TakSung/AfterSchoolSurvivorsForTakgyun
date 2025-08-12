"""
EventBus implementation for queue-based event publishing and processing.

This module provides a robust event bus system that ensures loose coupling
between game systems through queued event delivery and exception isolation.
"""

import logging
import time
from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base_event import BaseEvent
    from .event_types import EventType
    from .interfaces import IEventSubscriber


class EventBus:
    """
    Queue-based event bus for decoupled event-driven communication.

    The EventBus manages event publishing and processing through a queuing system
    that ensures proper isolation between systems and prevents blocking issues.
    All events are queued when published and processed in batch during the
    process_events call, providing predictable timing for game loops.
    """

    # AI-NOTE : 2025-08-12 큐 기반 이벤트 버스 시스템 도입
    # - 이유: ECS 시스템 간 독립성 보장 및 예측 가능한 이벤트 처리 필요
    # - 요구사항: 재진입 방지, 예외 격리, 성능 모니터링 지원
    # - 히스토리: 초기 EventBus 구현 - 큐잉 시스템과 구독자 관리

    def __init__(self, max_queue_size: int = 10000) -> None:
        """
        Initialize the EventBus with configurable queue size.

        Args:
            max_queue_size: Maximum number of events that can be queued.
                          Prevents memory overflow in extreme scenarios.
        """
        # AI-DEV : deque 사용으로 큐 성능 최적화
        # - 이유: deque는 양쪽 끝에서 O(1) 삽입/삭제 성능 제공
        # - 해결책: collections.deque 사용으로 큐 성능 극대화
        # - 주의사항: maxlen 설정으로 메모리 오버플로우 방지
        self._event_queue: deque[BaseEvent] = deque(maxlen=max_queue_size)

        # 구독자 관리: 이벤트 타입별로 구독자 Set 유지
        self._subscribers: dict[EventType, set[IEventSubscriber]] = {}

        # 재진입 방지 플래그
        self._processing_events: bool = False

        # 성능 모니터링 통계
        self._stats = {
            'events_published': 0,
            'events_processed': 0,
            'exceptions_caught': 0,
            'last_process_time': 0.0,
        }

        # 로깅 설정
        self._logger = logging.getLogger(
            f'{__name__}.{self.__class__.__name__}'
        )

        # 큐 크기 제한
        self._max_queue_size = max_queue_size

    def _enqueue_event(self, event: 'BaseEvent') -> bool:
        """
        Add an event to the internal queue.

        Args:
            event: Event to enqueue.

        Returns:
            True if event was successfully enqueued, False if queue is full.
        """
        if len(self._event_queue) >= self._max_queue_size:
            self._logger.warning(
                f'Event queue is full ({self._max_queue_size}). '
                f'Dropping event: {event}'
            )
            return False

        self._event_queue.append(event)
        return True

    def _dequeue_event(self) -> 'BaseEvent | None':
        """
        Remove and return the next event from the queue.

        Returns:
            Next event in queue, or None if queue is empty.
        """
        try:
            return self._event_queue.popleft()
        except IndexError:
            return None

    def get_queue_size(self) -> int:
        """
        Get the current number of events in the queue.

        Returns:
            Number of events currently queued.
        """
        return len(self._event_queue)

    def is_queue_empty(self) -> bool:
        """
        Check if the event queue is empty.

        Returns:
            True if queue is empty, False otherwise.
        """
        return len(self._event_queue) == 0

    def clear_queue(self) -> int:
        """
        Clear all events from the queue.

        Returns:
            Number of events that were cleared.
        """
        cleared_count = len(self._event_queue)
        self._event_queue.clear()
        self._logger.info(f'Cleared {cleared_count} events from queue')
        return cleared_count

    def subscribe(self, subscriber: 'IEventSubscriber') -> None:
        """
        Register a subscriber to receive events.

        The subscriber will receive all events of the types specified
        by its get_subscribed_events() method.

        Args:
            subscriber: The subscriber to register.
        """
        subscribed_events = subscriber.get_subscribed_events()

        for event_type in subscribed_events:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = set()

            # 중복 구독 방지
            if subscriber not in self._subscribers[event_type]:
                self._subscribers[event_type].add(subscriber)
                self._logger.debug(
                    f'Subscribed {subscriber.get_subscriber_name()} '
                    f'to {event_type.display_name}'
                )

    def unsubscribe(self, subscriber: 'IEventSubscriber') -> None:
        """
        Unregister a subscriber from receiving events.

        Args:
            subscriber: The subscriber to unregister.
        """
        removed_count = 0

        # 모든 이벤트 타입에서 구독자 제거
        for event_type, subscribers in self._subscribers.items():
            if subscriber in subscribers:
                subscribers.remove(subscriber)
                removed_count += 1
                self._logger.debug(
                    f'Unsubscribed {subscriber.get_subscriber_name()} '
                    f'from {event_type.display_name}'
                )

        # 빈 구독자 set 정리
        empty_types = [
            event_type
            for event_type, subscribers in self._subscribers.items()
            if len(subscribers) == 0
        ]
        for event_type in empty_types:
            del self._subscribers[event_type]

        if removed_count == 0:
            self._logger.warning(
                f'Attempted to unsubscribe {subscriber.get_subscriber_name()}, '
                f'but it was not found in any subscriptions'
            )

    def unsubscribe_from_event(
        self, subscriber: 'IEventSubscriber', event_type: 'EventType'
    ) -> bool:
        """
        Unregister a subscriber from a specific event type.

        Args:
            subscriber: The subscriber to unregister.
            event_type: The event type to unsubscribe from.

        Returns:
            True if subscriber was successfully unsubscribed, False otherwise.
        """
        if event_type not in self._subscribers:
            return False

        if subscriber not in self._subscribers[event_type]:
            return False

        self._subscribers[event_type].remove(subscriber)
        self._logger.debug(
            f'Unsubscribed {subscriber.get_subscriber_name()} '
            f'from {event_type.display_name}'
        )

        # 빈 구독자 set 정리
        if len(self._subscribers[event_type]) == 0:
            del self._subscribers[event_type]

        return True

    def get_subscriber_count(
        self, event_type: 'EventType | None' = None
    ) -> int:
        """
        Get the number of subscribers for a specific event type or total.

        Args:
            event_type: Event type to count subscribers for.
                       If None, returns total subscriber count across all types.

        Returns:
            Number of subscribers.
        """
        if event_type is None:
            return sum(
                len(subscribers) for subscribers in self._subscribers.values()
            )

        return len(self._subscribers.get(event_type, set()))

    def get_subscribed_event_types(self) -> list['EventType']:
        """
        Get all event types that have at least one subscriber.

        Returns:
            List of event types with active subscribers.
        """
        return list(self._subscribers.keys())

    def _get_subscribers_for_event(
        self, event_type: 'EventType'
    ) -> set['IEventSubscriber']:
        """
        Get all subscribers for a specific event type.

        Args:
            event_type: Event type to get subscribers for.

        Returns:
            Set of subscribers for the event type.
        """
        return self._subscribers.get(event_type, set()).copy()

    def publish(self, event: 'BaseEvent') -> bool:
        """
        Publish an event to be processed later.

        Events are queued and will be processed during the next call to
        process_events(). This ensures predictable timing and prevents
        immediate recursive event processing.

        Args:
            event: Event to publish.

        Returns:
            True if event was successfully queued, False if queue is full.
        """
        if not event.validate():
            self._logger.warning(f'Invalid event rejected: {event}')
            return False

        success = self._enqueue_event(event)
        if success:
            self._stats['events_published'] += 1
            self._logger.debug(f'Published event: {event}')

        return success

    def process_events(self) -> int:
        """
        Process all queued events by delivering them to subscribers.

        This method processes events in FIFO order and includes protection
        against reentrancy - if process_events is called while already
        processing, it will return immediately to prevent infinite loops.

        Returns:
            Number of events that were processed.
        """
        # AI-DEV : 재진입 방지로 무한 루프 및 스택 오버플로우 방지
        # - 문제: 이벤트 처리 중 새로운 이벤트 발행 시 무한 재귀 가능
        # - 해결책: _processing_events 플래그로 재진입 감지 및 방지
        # - 주의사항: 플래그 해제는 try-finally로 보장
        if self._processing_events:
            self._logger.debug('Reentrancy detected, skipping process_events')
            return 0

        self._processing_events = True
        process_start_time = time.time()
        processed_count = 0

        try:
            # 큐가 비어있을 때까지 반복 처리
            while not self.is_queue_empty():
                event = self._dequeue_event()
                if event is None:
                    break

                try:
                    self._deliver_event_to_subscribers(event)
                    processed_count += 1
                    self._stats['events_processed'] += 1

                except Exception as e:
                    self._logger.error(
                        f'Unexpected error processing event {event}: {e}',
                        exc_info=True,
                    )
                    self._stats['exceptions_caught'] += 1

        finally:
            self._processing_events = False
            process_time = time.time() - process_start_time
            self._stats['last_process_time'] = process_time

            if processed_count > 0:
                self._logger.debug(
                    f'Processed {processed_count} events in {process_time:.3f}s'
                )

        return processed_count

    def _deliver_event_to_subscribers(self, event: 'BaseEvent') -> None:
        """
        Deliver an event to all interested subscribers with exception isolation.

        Each subscriber is called individually with proper exception handling
        to ensure that one subscriber's failure doesn't affect others.

        Args:
            event: Event to deliver to subscribers.
        """
        subscribers = self._get_subscribers_for_event(event.event_type)

        if not subscribers:
            self._logger.debug(f'No subscribers for event: {event}')
            return

        for subscriber in subscribers:
            try:
                subscriber.handle_event(event)

            except Exception as e:
                # AI-DEV : 구독자 예외 격리로 시스템 안정성 확보
                # - 문제: 한 구독자의 예외가 전체 이벤트 처리 중단 가능
                # - 해결책: try-catch로 각 구독자별 예외 격리
                # - 주의사항: 예외 로깅으로 디버깅 지원, 통계 수집
                self._logger.error(
                    f'Subscriber {subscriber.get_subscriber_name()} '
                    f'failed to handle event {event}: {e}',
                    exc_info=True,
                )
                self._stats['exceptions_caught'] += 1

    def get_processing_stats(self) -> dict[str, int | float]:
        """
        Get performance and processing statistics.

        Returns:
            Dictionary containing processing statistics including:
            - events_published: Total events published
            - events_processed: Total events processed
            - exceptions_caught: Total exceptions caught during processing
            - last_process_time: Time taken for last process_events call
            - queue_size: Current queue size
            - total_subscribers: Total number of active subscribers
            - subscribed_event_types: Number of event types with subscribers
        """
        return {
            'events_published': self._stats['events_published'],
            'events_processed': self._stats['events_processed'],
            'exceptions_caught': self._stats['exceptions_caught'],
            'last_process_time': self._stats['last_process_time'],
            'queue_size': self.get_queue_size(),
            'total_subscribers': self.get_subscriber_count(),
            'subscribed_event_types': len(self._subscribers),
            'is_processing': self._processing_events,
            'max_queue_size': self._max_queue_size,
        }

    def reset_stats(self) -> None:
        """
        Reset all processing statistics.

        Useful for performance testing or periodic monitoring resets.
        Does not affect queue contents or subscriber registrations.
        """
        self._stats = {
            'events_published': 0,
            'events_processed': 0,
            'exceptions_caught': 0,
            'last_process_time': 0.0,
        }
        self._logger.info('Processing statistics reset')

    def get_health_status(self) -> dict[str, str | bool | int]:
        """
        Get overall health status of the EventBus.

        Returns:
            Dictionary containing health indicators:
            - status: 'healthy', 'warning', or 'error'
            - queue_utilization: Percentage of queue capacity used
            - has_subscribers: Whether any subscribers are registered
            - processing_errors: Number of recent exceptions
            - is_operational: Overall operational status
        """
        queue_utilization = (
            self.get_queue_size() / self._max_queue_size
        ) * 100
        has_subscribers = self.get_subscriber_count() > 0
        processing_errors = self._stats['exceptions_caught']

        # 상태 판단 로직
        if queue_utilization > 90:
            status = 'error'
        elif queue_utilization > 70 or processing_errors > 10:
            status = 'warning'
        else:
            status = 'healthy'

        return {
            'status': status,
            'queue_utilization': round(queue_utilization, 2),
            'has_subscribers': has_subscribers,
            'processing_errors': processing_errors,
            'is_operational': not self._processing_events and has_subscribers,
            'queue_size': self.get_queue_size(),
            'max_queue_size': self._max_queue_size,
        }

    def __str__(self) -> str:
        """String representation of the EventBus."""
        stats = self.get_processing_stats()
        return (
            f'EventBus('
            f'queue={stats["queue_size"]}/{stats["max_queue_size"]}, '
            f'subscribers={stats["total_subscribers"]}, '
            f'processed={stats["events_processed"]}, '
            f'errors={stats["exceptions_caught"]})'
        )

    def __repr__(self) -> str:
        """Detailed string representation of the EventBus."""
        return (
            f'EventBus(max_queue_size={self._max_queue_size}, '
            f'current_queue_size={self.get_queue_size()}, '
            f'subscriber_count={self.get_subscriber_count()}, '
            f'is_processing={self._processing_events})'
        )

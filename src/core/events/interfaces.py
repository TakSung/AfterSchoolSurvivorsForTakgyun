"""
Event system interfaces for standardized event handling.

This module defines the core interfaces that enable event-driven
communication between different systems in the game.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base_event import BaseEvent
    from .event_types import EventType


class IEventSubscriber(ABC):
    """
    Interface for objects that can subscribe to and handle events.

    Implementors of this interface can register with an event manager
    to receive notifications when specific types of events occur.
    This enables loose coupling between game systems.
    """

    # AI-NOTE : 2025-08-12 이벤트 구독자 표준 인터페이스 정의
    # - 이유: 시스템 간 일관된 이벤트 처리 메커니즘 제공 필요
    # - 요구사항: 타입 안전한 이벤트 처리, 구독 이벤트 타입 명시
    # - 히스토리: 초기 이벤트 시스템 구독자 인터페이스 정의

    @abstractmethod
    def handle_event(self, event: 'BaseEvent') -> None:
        """
        Handle an event that this subscriber is interested in.

        This method is called by the event manager when an event occurs
        that matches one of the event types returned by get_subscribed_events().

        Implementors should:
        1. Check the event type if handling multiple event types
        2. Extract relevant data from the event
        3. Perform the necessary actions
        4. Handle any exceptions gracefully to avoid breaking the event system

        Args:
            event: The event to handle. Guaranteed to be one of the types
                  returned by get_subscribed_events().

        Note:
            This method should not raise exceptions. If an error occurs,
            it should be logged and handled gracefully to maintain system stability.
        """
        pass

    @abstractmethod
    def get_subscribed_events(self) -> list['EventType']:
        """
        Get the list of event types this subscriber wants to receive.

        The event manager uses this method to determine which events
        to deliver to this subscriber. Only events of the returned types
        will be passed to handle_event().

        Returns:
            List of EventType values that this subscriber wants to receive.
            An empty list means this subscriber doesn't want any events.

        Note:
            This method may be called multiple times during the subscriber's
            lifetime, so it should be efficient and return consistent results
            unless the subscription requirements actually change.
        """
        pass

    def is_subscribed_to(self, event_type: 'EventType') -> bool:
        """
        Check if this subscriber is interested in a specific event type.

        This is a convenience method that checks if the given event type
        is in the list returned by get_subscribed_events().

        Args:
            event_type: The event type to check.

        Returns:
            True if this subscriber wants to receive events of this type.
        """
        return event_type in self.get_subscribed_events()

    def get_subscriber_name(self) -> str:
        """
        Get a human-readable name for this subscriber.

        This is useful for debugging and logging purposes.
        The default implementation returns the class name.

        Returns:
            A string identifying this subscriber.
        """
        return self.__class__.__name__


class IEventPublisher(ABC):
    """
    Interface for objects that can publish events to the event system.

    This interface defines the contract for publishing events and managing
    event subscribers in a decoupled event-driven architecture.
    """

    @abstractmethod
    def publish_event(self, event: 'BaseEvent') -> None:
        """
        Publish an event to all interested subscribers.

        Args:
            event: The event to publish. Must be a valid BaseEvent instance.
        """
        pass

    @abstractmethod
    def subscribe(self, subscriber: IEventSubscriber) -> None:
        """
        Register a subscriber to receive events.

        Args:
            subscriber: The subscriber to register.
        """
        pass

    @abstractmethod
    def unsubscribe(self, subscriber: IEventSubscriber) -> None:
        """
        Unregister a subscriber from receiving events.

        Args:
            subscriber: The subscriber to unregister.
        """
        pass


class IEventHandler(ABC):
    """
    Generic interface for handling specific event types.

    This interface provides a more specific contract than IEventSubscriber
    for handlers that only care about a single event type.
    """

    @abstractmethod
    def handle(self, event: 'BaseEvent') -> bool:
        """
        Handle a specific event.

        Args:
            event: The event to handle.

        Returns:
            True if the event was successfully handled, False otherwise.
        """
        pass

    @abstractmethod
    def can_handle(self, event_type: 'EventType') -> bool:
        """
        Check if this handler can process the given event type.

        Args:
            event_type: The event type to check.

        Returns:
            True if this handler can process events of this type.
        """
        pass

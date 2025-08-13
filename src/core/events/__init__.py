"""
Event system package for game-wide event-driven communication.

This package provides the core infrastructure for loose coupling between
game systems through an event-driven architecture.
"""

from .base_event import BaseEvent
from .camera_offset_changed_event import CameraOffsetChangedEvent
from .enemy_death_event import EnemyDeathEvent
from .event_bus import EventBus
from .event_types import EventType
from .interfaces import IEventHandler, IEventPublisher, IEventSubscriber

__all__ = [
    'BaseEvent',
    'CameraOffsetChangedEvent',
    'EnemyDeathEvent',
    'EventBus',
    'EventType',
    'IEventHandler',
    'IEventPublisher',
    'IEventSubscriber',
]

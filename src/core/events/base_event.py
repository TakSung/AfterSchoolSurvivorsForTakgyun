"""
BaseEvent abstract class for the game event system.

This module provides the foundation for all events in the game's event-driven
architecture, ensuring loose coupling between different systems.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from .event_types import EventType

if TYPE_CHECKING:
    pass


@dataclass
class BaseEvent(ABC):
    """
    Abstract base class for all events in the game event system.

    Events are immutable data containers that represent something that has
    happened in the game. They are used for loose coupling between systems
    and provide a way to communicate state changes across the game.

    All event classes should inherit from this class and implement the
    validate() method for event-specific data validation.
    """

    # AI-NOTE : 2025-08-12 이벤트 시스템 기반 아키텍처 도입
    # - 이유: 게임 시스템 간 느슨한 결합을 위한 이벤트 기반 통신 필요
    # - 요구사항: 타임스탬프 자동 설정, 데이터 불변성, 검증 메커니즘
    # - 히스토리: 초기 구현 - 모든 이벤트의 기본 구조 정의
    timestamp: float
    created_at: datetime | None
    
    @abstractmethod
    def get_event_type(self) -> EventType:
        """Event-Type은 반드시 있어야 한다.

        Returns:
            EventType: 이벤트 타입
        """
        pass

    def __post_init__(self) -> None:
        """
        Called after event initialization.

        Automatically sets timestamp and created_at if not provided.
        This ensures every event has consistent timing information.
        """
        # AI-DEV : time.time() 사용으로 성능 최적화
        # - 이유: datetime.now()보다 time.time()이 더 빠름
        # - 해결책: 게임 루프에서 필요한 정밀도 제공하면서 성능 확보
        # - 주의사항: timezone 정보가 필요한 경우 별도 처리 필요
        if not hasattr(self, '_initialized'):
            # 타임스탬프가 0.0이거나 None인 경우에만 자동 설정
            if self.timestamp == 0.0 or self.timestamp is None:
                self.timestamp = time.time()
            # created_at이 None인 경우에만 자동 설정
            if self.created_at is None:
                self.created_at = datetime.now()
            self._initialized = True

    @abstractmethod
    def validate(self) -> bool:
        """
        Validate event data integrity.

        Subclasses must implement this method to provide event-specific
        validation logic for their data fields.

        Returns:
            True if the event data is valid, False otherwise.
        """
        pass

    def get_age_seconds(self, current_time: float | None = None) -> float:
        """
        Get the age of this event in seconds.

        Args:
            current_time: Current time to compare against. If None, uses time.time().

        Returns:
            Age of the event in seconds.
        """
        if current_time is None:
            current_time = time.time()
        return current_time - self.timestamp

    def is_expired(
        self, max_age_seconds: float, current_time: float | None = None
    ) -> bool:
        """
        Check if this event has expired based on maximum age.

        Args:
            max_age_seconds: Maximum age in seconds before event is considered expired.
            current_time: Current time to compare against. If None, uses time.time().

        Returns:
            True if the event is expired, False otherwise.
        """
        return self.get_age_seconds(current_time) > max_age_seconds

    def __str__(self) -> str:
        """String representation of the event."""
        return (
            f'{self.__class__.__name__}('
            f'type={self.get_event_type().display_name}, '
            f'timestamp={self.timestamp:.3f})'
        )

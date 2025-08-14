import threading
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from ..utils.vector2 import Vector2
from .camera_based_transformer import CameraBasedTransformer
from .coordinate_transformer import ICoordinateTransformer
from .events.event_types import EventType
from .events.interfaces import IEventSubscriber

if TYPE_CHECKING:
    from .events.base_event import BaseEvent


class ICoordinateObserver(ABC):
    """좌표 변환기 변경에 대한 알림을 받는 옵저버 인터페이스"""

    @abstractmethod
    def on_transformer_changed(
        self, new_transformer: ICoordinateTransformer
    ) -> None:
        """변환기가 변경되었을 때 호출되는 메서드

        Args:
            new_transformer: 새로 설정된 좌표 변환기
        """
        pass


class CoordinateManager(IEventSubscriber):
    """좌표 변환 시스템을 전역적으로 관리하는 싱글톤 매니저

    # AI-NOTE : 2025-01-10 전역 좌표 변환 관리 시스템 도입
    # - 이유: 게임 전반의 좌표 변환을 일관성 있게 관리하기 위함
    # - 요구사항: 런타임 변환기 교체, 옵저버 패턴, 스레드 안전성 보장
    # - 히스토리: 개별 변환기 사용에서 중앙 집중 관리로 변경
    """

    _instance: 'CoordinateManager | None' = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        """CoordinateManager 초기화

        Note: 직접 생성하지 말고 get_instance()를 사용하세요.
        """
        self._transformer: ICoordinateTransformer | None = None
        self._observers: list[ICoordinateObserver] = []
        self._observer_lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> 'CoordinateManager':
        """싱글톤 인스턴스를 반환합니다.

        스레드 안전하게 구현된 싱글톤 패턴을 사용합니다.

        Returns:
            CoordinateManager 싱글톤 인스턴스
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def set_instance(cls, instance: 'CoordinateManager | None') -> None:
        """테스트용 의존성 주입을 위한 인스턴스 설정

        # AI-DEV : 테스트 격리를 위한 의존성 주입 지원
        # - 문제: 싱글톤으로 인한 테스트 간 상태 오염 가능성
        # - 해결책: 테스트에서 특정 인스턴스로 교체 가능하도록 함
        # - 주의사항: 프로덕션 코드에서는 사용하지 말 것

        Args:
            instance: 설정할 CoordinateManager 인스턴스 (None일 경우 리셋)
        """
        with cls._lock:
            cls._instance = instance

    def get_transformer(self) -> ICoordinateTransformer:
        """현재 좌표 변환기를 반환합니다.

        변환기가 설정되지 않은 경우 기본 CameraBasedTransformer를 생성하여 반환합니다.

        Returns:
            현재 설정된 좌표 변환기
        """
        if self._transformer is None:
            # 기본 변환기 생성 (화면 크기는 800x600으로 기본값 설정)
            self._transformer = CameraBasedTransformer(
                screen_size=Vector2(800.0, 600.0),
                camera_offset=Vector2.zero(),
                zoom_level=1.0,
            )
        return self._transformer

    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        """월드 좌표를 스크린 좌표로 변환합니다.

        Args:
            world_pos: 월드 좌표

        Returns:
            스크린 좌표
        """
        return self.get_transformer().world_to_screen(world_pos)

    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """스크린 좌표를 월드 좌표로 변환합니다.

        Args:
            screen_pos: 스크린 좌표

        Returns:
            월드 좌표
        """
        return self.get_transformer().screen_to_world(screen_pos)

    def add_observer(self, observer: ICoordinateObserver) -> None:
        """좌표 변환기 변경 알림을 받을 옵저버를 등록합니다.

        Args:
            observer: 등록할 옵저버
        """
        with self._observer_lock:
            if observer not in self._observers:
                self._observers.append(observer)

    def remove_observer(self, observer: ICoordinateObserver) -> None:
        """등록된 옵저버를 제거합니다.

        Args:
            observer: 제거할 옵저버
        """
        with self._observer_lock:
            if observer in self._observers:
                self._observers.remove(observer)

    def notify_observers(
        self, new_transformer: ICoordinateTransformer
    ) -> None:
        """모든 옵저버에게 변환기 변경을 알립니다.

        # AI-DEV : 예외 처리를 통한 옵저버 격리
        # - 문제: 한 옵저버의 오류가 다른 옵저버에 영향을 줄 수 있음
        # - 해결책: try-except로 개별 옵저버 오류 격리
        # - 주의사항: 오류 발생 시 로그를 남겨 디버깅 가능하도록 함

        Args:
            new_transformer: 새로 설정된 좌표 변환기
        """
        with self._observer_lock:
            observers_copy = self._observers.copy()

        for observer in observers_copy:
            try:
                observer.on_transformer_changed(new_transformer)
            except Exception as e:
                # 개별 옵저버 오류가 전체 시스템에 영향을 주지 않도록 처리
                print(
                    f'Warning: Observer {observer} failed to handle transformer change: {e}'
                )

    def set_transformer(self, transformer: ICoordinateTransformer) -> None:
        """좌표 변환기를 교체합니다.

        Args:
            transformer: 새로 설정할 좌표 변환기

        Raises:
            TypeError: transformer가 ICoordinateTransformer 인터페이스를 구현하지 않은 경우
        """
        if not isinstance(transformer, ICoordinateTransformer):
            raise TypeError(
                f'Expected ICoordinateTransformer, got {type(transformer)}'
            )

        # 기존 변환기의 캐시 무효화
        if self._transformer is not None:
            self._transformer.invalidate_cache()

        # 새 변환기 설정
        self._transformer = transformer

        # 새 변환기의 캐시도 무효화 (안전을 위해)
        transformer.invalidate_cache()

        # 옵저버들에게 알림
        self.notify_observers(transformer)

    def get_manager_stats(self) -> dict[str, Any]:
        """매니저의 현재 상태 정보를 반환합니다.

        Returns:
            매니저 상태 정보를 담은 딕셔너리
        """
        # get_transformer()를 호출하여 기본 변환기도 포함하여 상태 확인
        transformer = self.get_transformer()
        return {
            'has_transformer': transformer is not None,
            'transformer_type': type(transformer).__name__
            if transformer
            else None,
            'observer_count': len(self._observers),
            'transformer_stats': (
                transformer.get_cache_stats()
                if transformer and hasattr(transformer, 'get_cache_stats')
                else None
            ),
        }

    # AI-NOTE : 2025-08-13 이벤트 시스템 통합을 위한 IEventSubscriber 구현
    # - 이유: 카메라 오프셋 변경을 이벤트로 수신하여 자동으로 변환기 업데이트
    # - 요구사항: CameraOffsetChangedEvent 구독하여 느슨한 결합 구현
    # - 히스토리: 직접 호출 방식에서 이벤트 기반 시스템으로 개선

    def handle_event(self, event: 'BaseEvent') -> None:
        """
        Handle incoming events, specifically camera offset change events.

        Args:
            event: The event to handle. Expected to be CameraOffsetChangedEvent.
        """
        # 타입 체크를 통한 안전한 이벤트 처리
        if event.get_event_type() != EventType.CAMERA_OFFSET_CHANGED:
            return

        # TYPE_CHECKING을 위한 import 처리
        from .events.camera_offset_changed_event import (
            CameraOffsetChangedEvent,
        )

        if not isinstance(event, CameraOffsetChangedEvent):
            return

        try:
            # 현재 변환기에 카메라 오프셋 업데이트
            transformer = self.get_transformer()  # ICoordinateTransformer 보장

            # 카메라 오프셋을 Vector2로 변환하여 설정
            camera_offset = Vector2(
                event.world_offset[0], event.world_offset[1]
            )
            assert hasattr(transformer, 'set_camera_offset'), (
                '인터페이스 계약에 따라 set_camera_offset 반드시 존재'
            )
            assert hasattr(transformer, 'invalidate_cache'), (
                '인터페이스 계약에 따라 invalidate_cache 반드시 존재'
            )

            transformer.set_camera_offset(camera_offset)
            transformer.invalidate_cache()  # 캐시 무효화

            # 옵저버들에게 알림 (기존 시스템과의 호환성 유지)
            self.notify_observers(transformer)

        except Exception as e:
            # 이벤트 처리 중 오류가 발생해도 다른 시스템에 영향을 주지 않도록 처리
            print(
                f'Warning: CoordinateManager failed to handle camera offset event: {e}'
            )

    def get_subscribed_events(self) -> list[EventType]:
        """
        Get the list of event types this subscriber wants to receive.

        Returns:
            List containing CAMERA_OFFSET_CHANGED event type.
        """
        return [EventType.CAMERA_OFFSET_CHANGED]

    def get_subscriber_name(self) -> str:
        """
        Get a human-readable name for this subscriber.

        Returns:
            String identifying this subscriber for debugging purposes.
        """
        return 'CoordinateManager'

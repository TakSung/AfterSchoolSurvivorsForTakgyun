import threading
import time
from unittest.mock import Mock, MagicMock, patch

import pytest

from src.core.camera_based_transformer import CameraBasedTransformer
from src.core.coordinate_manager import CoordinateManager, ICoordinateObserver
from src.core.coordinate_transformer import ICoordinateTransformer
from src.core.events.base_event import BaseEvent
from src.core.events.camera_offset_changed_event import (
    CameraOffsetChangedEvent,
)
from src.core.events.event_types import EventType
from src.utils.vector2 import Vector2


class MockCoordinateTransformer(ICoordinateTransformer):
    """테스트용 좌표 변환기 Mock 클래스"""

    def __init__(self) -> None:
        self._cache_invalidated = False
        self._camera_offset = Vector2.zero()
        self._zoom_level = 1.0
        self._screen_size = Vector2(800.0, 600.0)

    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        return world_pos * 2.0  # 간단한 변환 (2배 스케일링)

    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        return screen_pos / 2.0  # 역변환

    def get_camera_offset(self) -> Vector2:
        return self._camera_offset.copy()

    def set_camera_offset(self, offset: Vector2) -> None:
        self._camera_offset = offset.copy()

    def invalidate_cache(self) -> None:
        self._cache_invalidated = True

    @property
    def zoom_level(self) -> float:
        return self._zoom_level

    @zoom_level.setter
    def zoom_level(self, value: float) -> None:
        self._zoom_level = value

    @property
    def screen_size(self) -> Vector2:
        return self._screen_size.copy()

    @screen_size.setter
    def screen_size(self, size: Vector2) -> None:
        self._screen_size = size.copy()

    def get_cache_invalidated(self) -> bool:
        return self._cache_invalidated


class MockObserver(ICoordinateObserver):
    """테스트용 옵저버 Mock 클래스"""

    def __init__(self) -> None:
        self.notifications: list = []
        self.should_fail = False

    def on_transformer_changed(self, new_transformer) -> None:
        if self.should_fail:
            raise RuntimeError('Observer intentionally failed')
        self.notifications.append(new_transformer)


class TestCoordinateManager:
    """CoordinateManager 테스트 클래스"""

    def setup_method(self) -> None:
        """각 테스트 전에 싱글톤 인스턴스 초기화"""
        CoordinateManager.set_instance(None)

    def teardown_method(self) -> None:
        """각 테스트 후에 싱글톤 인스턴스 정리"""
        CoordinateManager.set_instance(None)

    def test_싱글톤_패턴_동일_인스턴스_반환_검증_성공_시나리오(self) -> None:
        """1. 싱글톤 패턴으로 동일한 인스턴스 반환 검증 (성공 시나리오)

        목적: CoordinateManager가 싱글톤 패턴을 올바르게 구현했는지 검증
        테스트할 범위: get_instance() 메서드의 싱글톤 동작
        커버하는 함수 및 데이터: get_instance() 클래스 메서드
        기대되는 안정성: 항상 동일한 인스턴스 반환 보장
        """
        # Given & When - 여러 번 인스턴스 생성
        manager1 = CoordinateManager.get_instance()
        manager2 = CoordinateManager.get_instance()
        manager3 = CoordinateManager.get_instance()

        # Then - 모든 인스턴스가 동일함
        assert manager1 is manager2, '첫 번째와 두 번째 인스턴스가 동일해야 함'
        assert manager2 is manager3, '두 번째와 세 번째 인스턴스가 동일해야 함'
        assert manager1 is manager3, '첫 번째와 세 번째 인스턴스가 동일해야 함'

    def test_스레드_안전_싱글톤_생성_검증_성공_시나리오(self) -> None:
        """2. 멀티스레드 환경에서 싱글톤 생성 안전성 검증 (성공 시나리오)

        목적: 동시에 여러 스레드에서 인스턴스를 생성해도 하나만 생성되는지 검증
        테스트할 범위: 스레드 안전성과 _lock 메커니즘
        커버하는 함수 및 데이터: get_instance() 스레드 동시성
        기대되는 안정성: 스레드 경합 상황에서도 단일 인스턴스 보장
        """
        # Given - 결과를 저장할 리스트
        results = []
        barrier = threading.Barrier(5)  # 5개 스레드 동시 시작

        def create_instance():
            barrier.wait()  # 모든 스레드가 동시에 시작
            instance = CoordinateManager.get_instance()
            results.append(instance)

        # When - 5개 스레드에서 동시에 인스턴스 생성
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_instance)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Then - 모든 결과가 동일한 인스턴스
        assert len(results) == 5, '모든 스레드에서 인스턴스를 반환해야 함'
        for result in results[1:]:
            assert result is results[0], (
                '모든 스레드에서 동일한 인스턴스를 반환해야 함'
            )

    def test_기본_변환기_자동_생성_검증_성공_시나리오(self) -> None:
        """3. 변환기가 설정되지 않은 경우 기본 변환기 자동 생성 검증 (성공 시나리오)

        목적: 변환기가 설정되지 않았을 때 기본 CameraBasedTransformer가 생성되는지 검증
        테스트할 범위: get_transformer() 메서드의 기본값 생성 로직
        커버하는 함수 및 데이터: get_transformer(), 기본 CameraBasedTransformer 생성
        기대되는 안정성: 항상 유효한 변환기 인스턴스 제공 보장
        """
        # Given - 새로운 매니저 인스턴스
        manager = CoordinateManager.get_instance()

        # When - 변환기 조회 (아직 설정되지 않음)
        transformer = manager.get_transformer()

        # Then - 기본 CameraBasedTransformer 생성 확인
        assert transformer is not None, '변환기가 반환되어야 함'
        assert isinstance(transformer, CameraBasedTransformer), (
            '기본값으로 CameraBasedTransformer가 생성되어야 함'
        )
        assert transformer.screen_size == Vector2(800.0, 600.0), (
            '기본 화면 크기가 800x600이어야 함'
        )
        assert transformer.get_camera_offset() == Vector2.zero(), (
            '기본 카메라 오프셋이 0이어야 함'
        )
        assert transformer.zoom_level == 1.0, '기본 줌 레벨이 1.0이어야 함'

    def test_좌표_변환_래퍼_메서드_정확성_검증_성공_시나리오(self) -> None:
        """4. world_to_screen, screen_to_world 래퍼 메서드 정확성 검증 (성공 시나리오)

        목적: 매니저의 좌표 변환 래퍼 메서드가 내부 변환기에 올바르게 위임하는지 검증
        테스트할 범위: world_to_screen(), screen_to_world() 래퍼 메서드
        커버하는 함수 및 데이터: 좌표 변환 위임 로직, 변환 정확성
        기대되는 안정성: 내부 변환기와 동일한 결과 보장
        """
        # Given - 매니저와 테스트 좌표
        manager = CoordinateManager.get_instance()
        world_pos = Vector2(100.0, 200.0)
        screen_pos = Vector2(300.0, 400.0)

        # When - 래퍼 메서드로 변환 수행
        converted_screen = manager.world_to_screen(world_pos)
        converted_world = manager.screen_to_world(screen_pos)

        # Then - 내부 변환기와 동일한 결과 확인
        transformer = manager.get_transformer()
        expected_screen = transformer.world_to_screen(world_pos)
        expected_world = transformer.screen_to_world(screen_pos)

        assert converted_screen == expected_screen, (
            'world_to_screen 래퍼가 정확해야 함'
        )
        assert converted_world == expected_world, (
            'screen_to_world 래퍼가 정확해야 함'
        )

    def test_의존성_주입_set_instance_동작_검증_성공_시나리오(self) -> None:
        """5. 테스트용 의존성 주입 set_instance() 동작 검증 (성공 시나리오)

        목적: 테스트 격리를 위한 set_instance() 메서드가 올바르게 동작하는지 검증
        테스트할 범위: set_instance() 클래스 메서드, 인스턴스 교체 기능
        커버하는 함수 및 데이터: set_instance(), 싱글톤 인스턴스 교체
        기대되는 안정성: 테스트용 인스턴스 교체 및 복구 보장
        """
        # Given - 커스텀 매니저 인스턴스 생성
        custom_manager = CoordinateManager()
        custom_transformer = MockCoordinateTransformer()
        custom_manager.set_transformer(custom_transformer)

        # When - 커스텀 인스턴스로 교체
        CoordinateManager.set_instance(custom_manager)
        retrieved_manager = CoordinateManager.get_instance()

        # Then - 커스텀 인스턴스가 반환됨
        assert retrieved_manager is custom_manager, (
            'set_instance로 설정한 인스턴스가 반환되어야 함'
        )
        assert retrieved_manager.get_transformer() is custom_transformer, (
            '커스텀 변환기가 설정되어 있어야 함'
        )

        # When - None으로 리셋
        CoordinateManager.set_instance(None)
        new_manager = CoordinateManager.get_instance()

        # Then - 새로운 인스턴스가 생성됨
        assert new_manager is not custom_manager, (
            '리셋 후 새로운 인스턴스가 생성되어야 함'
        )

    def test_매니저_상태_정보_조회_정확성_검증_성공_시나리오(self) -> None:
        """6. get_manager_stats() 상태 정보 조회 정확성 검증 (성공 시나리오)

        목적: 매니저의 현재 상태 정보가 정확하게 반환되는지 검증
        테스트할 범위: get_manager_stats() 메서드, 상태 정보 수집
        커버하는 함수 및 데이터: 매니저 상태, 변환기 정보, 옵저버 수
        기대되는 안정성: 현재 상태에 대한 정확한 정보 제공 보장
        """
        # Given - 매니저와 옵저버 설정
        manager = CoordinateManager.get_instance()
        observer1 = MockObserver()
        observer2 = MockObserver()
        manager.add_observer(observer1)
        manager.add_observer(observer2)

        # When - 상태 정보 조회
        stats = manager.get_manager_stats()

        # Then - 정확한 상태 정보 확인
        assert stats['has_transformer'] is True, '변환기가 설정되어 있어야 함'
        assert stats['transformer_type'] == 'CameraBasedTransformer', (
            '변환기 타입이 정확해야 함'
        )
        assert stats['observer_count'] == 2, '옵저버 개수가 정확해야 함'
        assert stats['transformer_stats'] is not None, (
            '변환기 통계 정보가 있어야 함'
        )

        # When - 커스텀 변환기로 교체 후 다시 조회
        custom_transformer = MockCoordinateTransformer()
        manager.set_transformer(custom_transformer)
        updated_stats = manager.get_manager_stats()

        # Then - 업데이트된 상태 정보 확인
        assert (
            updated_stats['transformer_type'] == 'MockCoordinateTransformer'
        ), '변경된 변환기 타입이 반영되어야 함'
        assert updated_stats['transformer_stats'] is None, (
            'Mock 변환기는 통계가 없어야 함'
        )

    def test_변환기_교체_기본_동작_검증_성공_시나리오(self) -> None:
        """7. set_transformer()로 변환기 교체 기본 동작 검증 (성공 시나리오)

        목적: 런타임에 변환기를 안전하게 교체할 수 있는지 검증
        테스트할 범위: set_transformer() 메서드, 변환기 교체 로직
        커버하는 함수 및 데이터: 변환기 설정, 캐시 무효화, 유효성 검사
        기대되는 안정성: 안전한 변환기 교체 및 상태 일관성 보장
        """
        # Given - 매니저와 새로운 변환기
        manager = CoordinateManager.get_instance()
        original_transformer = manager.get_transformer()
        custom_transformer = MockCoordinateTransformer()

        # When - 변환기 교체
        manager.set_transformer(custom_transformer)

        # Then - 새로운 변환기가 설정됨
        current_transformer = manager.get_transformer()
        assert current_transformer is custom_transformer, (
            '새로운 변환기가 설정되어야 함'
        )
        assert current_transformer is not original_transformer, (
            '기존 변환기와는 다른 인스턴스여야 함'
        )

        # 캐시 무효화 확인
        assert custom_transformer.get_cache_invalidated(), (
            '새 변환기의 캐시가 무효화되어야 함'
        )

    def test_변환기_교체_시_캐시_무효화_검증_성공_시나리오(self) -> None:
        """8. 변환기 교체 시 기존 캐시 무효화 검증 (성공 시나리오)

        목적: 변환기 교체 시 기존 및 새 변환기의 캐시가 적절히 무효화되는지 검증
        테스트할 범위: 캐시 무효화 로직, invalidate_cache() 호출
        커버하는 함수 및 데이터: 캐시 무효화, 변환기 교체 프로세스
        기대되는 안정성: 변환기 교체 시 캐시 일관성 보장
        """
        # Given - 매니저와 두 개의 Mock 변환기
        manager = CoordinateManager.get_instance()
        old_transformer = MockCoordinateTransformer()
        new_transformer = MockCoordinateTransformer()

        # 첫 번째 변환기 설정
        manager.set_transformer(old_transformer)
        old_transformer._cache_invalidated = False  # 상태 초기화

        # When - 두 번째 변환기로 교체
        manager.set_transformer(new_transformer)

        # Then - 새 변환기의 캐시가 무효화됨
        assert new_transformer.get_cache_invalidated(), (
            '새 변환기의 캐시가 무효화되어야 함'
        )

    def test_잘못된_변환기_타입_교체_실패_시나리오(self) -> None:
        """9. 잘못된 타입의 변환기 교체 시도 실패 검증 (실패 시나리오)

        목적: ICoordinateTransformer 인터페이스를 구현하지 않은 객체로 교체 시도 시 예외 발생 검증
        테스트할 범위: set_transformer() 유효성 검사 로직
        커버하는 함수 및 데이터: 타입 검증, TypeError 예외 처리
        기대되는 안정성: 잘못된 타입의 변환기 교체 방지 보장
        """
        # Given - 매니저와 잘못된 타입의 객체
        manager = CoordinateManager.get_instance()
        invalid_transformer = '이것은 변환기가 아닙니다'

        # When & Then - TypeError 예외 발생 확인
        with pytest.raises(TypeError) as exc_info:
            manager.set_transformer(invalid_transformer)

        assert 'Expected ICoordinateTransformer' in str(exc_info.value), (
            '적절한 에러 메시지가 출력되어야 함'
        )

    def test_옵저버_등록_제거_기본_동작_검증_성공_시나리오(self) -> None:
        """10. 옵저버 등록 및 제거 기본 동작 검증 (성공 시나리오)

        목적: 옵저버 등록, 제거, 중복 등록 방지가 올바르게 동작하는지 검증
        테스트할 범위: add_observer(), remove_observer() 메서드
        커버하는 함수 및 데이터: 옵저버 리스트 관리, 중복 방지 로직
        기대되는 안정성: 옵저버 등록/제거의 정확성과 일관성 보장
        """
        # Given - 매니저와 옵저버
        manager = CoordinateManager.get_instance()
        observer1 = MockObserver()
        observer2 = MockObserver()

        # When - 옵저버 등록
        manager.add_observer(observer1)
        manager.add_observer(observer2)

        # Then - 옵저버 개수 확인
        stats = manager.get_manager_stats()
        assert stats['observer_count'] == 2, '두 개의 옵저버가 등록되어야 함'

        # When - 중복 등록 시도
        manager.add_observer(observer1)

        # Then - 중복 등록이 방지됨
        stats = manager.get_manager_stats()
        assert stats['observer_count'] == 2, '중복 등록이 방지되어야 함'

        # When - 옵저버 제거
        manager.remove_observer(observer1)

        # Then - 옵저버 개수 감소
        stats = manager.get_manager_stats()
        assert stats['observer_count'] == 1, '옵저버가 제거되어야 함'

        # When - 존재하지 않는 옵저버 제거 시도
        manager.remove_observer(observer1)  # 이미 제거됨

        # Then - 에러 없이 처리됨
        stats = manager.get_manager_stats()
        assert stats['observer_count'] == 1, '옵저버 개수가 변경되지 않아야 함'

    def test_변환기_교체_시_옵저버_알림_검증_성공_시나리오(self) -> None:
        """11. 변환기 교체 시 등록된 옵저버들에게 알림 전송 검증 (성공 시나리오)

        목적: 변환기 교체 시 모든 등록된 옵저버에게 알림이 전송되는지 검증
        테스트할 범위: notify_observers() 메서드, 옵저버 알림 로직
        커버하는 함수 및 데이터: 옵저버 알림, 변환기 교체 이벤트
        기대되는 안정성: 모든 옵저버에게 정확한 알림 전송 보장
        """
        # Given - 매니저와 여러 옵저버
        manager = CoordinateManager.get_instance()
        observer1 = MockObserver()
        observer2 = MockObserver()
        observer3 = MockObserver()

        manager.add_observer(observer1)
        manager.add_observer(observer2)
        manager.add_observer(observer3)

        new_transformer = MockCoordinateTransformer()

        # When - 변환기 교체
        manager.set_transformer(new_transformer)

        # Then - 모든 옵저버가 알림을 받음
        assert len(observer1.notifications) == 1, (
            '첫 번째 옵저버가 알림을 받아야 함'
        )
        assert len(observer2.notifications) == 1, (
            '두 번째 옵저버가 알림을 받아야 함'
        )
        assert len(observer3.notifications) == 1, (
            '세 번째 옵저버가 알림을 받아야 함'
        )

        assert observer1.notifications[0] is new_transformer, (
            '올바른 변환기 정보가 전달되어야 함'
        )
        assert observer2.notifications[0] is new_transformer, (
            '올바른 변환기 정보가 전달되어야 함'
        )
        assert observer3.notifications[0] is new_transformer, (
            '올바른 변환기 정보가 전달되어야 함'
        )

    def test_옵저버_예외_처리_격리_검증_성공_시나리오(self) -> None:
        """12. 옵저버 알림 중 예외 발생 시 다른 옵저버 격리 검증 (성공 시나리오)

        목적: 한 옵저버에서 예외가 발생해도 다른 옵저버들에게는 정상적으로 알림이 전송되는지 검증
        테스트할 범위: 옵저버 예외 처리 로직, 에러 격리 메커니즘
        커버하는 함수 및 데이터: 예외 처리, 옵저버 격리, 시스템 안정성
        기대되는 안정성: 개별 옵저버 오류가 전체 시스템에 영향을 주지 않음 보장
        """
        # Given - 매니저와 정상/실패 옵저버
        manager = CoordinateManager.get_instance()
        normal_observer = MockObserver()
        failing_observer = MockObserver()
        another_normal_observer = MockObserver()

        failing_observer.should_fail = True  # 예외 발생하도록 설정

        manager.add_observer(normal_observer)
        manager.add_observer(failing_observer)
        manager.add_observer(another_normal_observer)

        new_transformer = MockCoordinateTransformer()

        # When - 변환기 교체 (예외가 발생해도 계속 실행되어야 함)
        manager.set_transformer(new_transformer)

        # Then - 정상 옵저버들은 알림을 받음
        assert len(normal_observer.notifications) == 1, (
            '정상 옵저버는 알림을 받아야 함'
        )
        assert len(another_normal_observer.notifications) == 1, (
            '또 다른 정상 옵저버도 알림을 받아야 함'
        )

        # 실패한 옵저버는 알림을 처리하지 못했지만 시스템은 계속 동작
        assert len(failing_observer.notifications) == 0, (
            '실패 옵저버는 알림 처리에 실패해야 함'
        )

    def test_스레드_안전_옵저버_관리_검증_성공_시나리오(self) -> None:
        """13. 멀티스레드 환경에서 옵저버 관리 스레드 안전성 검증 (성공 시나리오)

        목적: 동시에 여러 스레드에서 옵저버 등록/제거/알림이 안전하게 동작하는지 검증
        테스트할 범위: 옵저버 관리의 스레드 안전성, _observer_lock 메커니즘
        커버하는 함수 및 데이터: 동시 옵저버 관리, 스레드 동시성
        기대되는 안정성: 스레드 경합 상황에서도 옵저버 관리 무결성 보장
        """
        # Given - 매니저와 여러 옵저버
        manager = CoordinateManager.get_instance()
        observers = [MockObserver() for _ in range(10)]
        results = []
        barrier = threading.Barrier(4)  # 3개 스레드 + 메인 스레드

        def add_observers():
            barrier.wait()
            for observer in observers[:5]:
                manager.add_observer(observer)
            results.append('add_completed')

        def remove_observers():
            barrier.wait()
            for observer in observers[2:7]:  # 일부 겹치는 범위
                manager.remove_observer(observer)
            results.append('remove_completed')

        def notify_observers():
            barrier.wait()
            time.sleep(0.01)  # 등록/제거 작업이 일부 완료될 때까지 대기
            new_transformer = MockCoordinateTransformer()
            manager.set_transformer(new_transformer)
            results.append('notify_completed')

        # When - 여러 스레드에서 동시에 옵저버 관리 작업 수행
        threads = [
            threading.Thread(target=add_observers),
            threading.Thread(target=remove_observers),
            threading.Thread(target=notify_observers),
        ]

        for thread in threads:
            thread.start()

        barrier.wait()  # 모든 스레드가 동시에 시작

        for thread in threads:
            thread.join()

        # Then - 모든 작업이 완료되고 시스템이 안정적으로 동작
        assert len(results) == 3, '모든 스레드 작업이 완료되어야 함'
        assert 'add_completed' in results, '옵저버 추가 작업이 완료되어야 함'
        assert 'remove_completed' in results, (
            '옵저버 제거 작업이 완료되어야 함'
        )
        assert 'notify_completed' in results, '알림 작업이 완료되어야 함'

        # 시스템이 일관된 상태를 유지하는지 확인
        stats = manager.get_manager_stats()
        assert stats['observer_count'] >= 0, '옵저버 개수가 음수가 되면 안됨'
        assert stats['has_transformer'] is True, '변환기가 설정되어 있어야 함'

    def test_이벤트_처리_CAMERA_OFFSET_CHANGED_정상_처리_검증_성공_시나리오(
        self,
    ) -> None:
        """14. 카메라 오프셋 변경 이벤트 정상 처리 검증 (성공 시나리오)

        목적: CameraOffsetChangedEvent를 수신했을 때 변환기가 올바르게 업데이트되는지 검증
        테스트할 범위: handle_event() 메서드의 이벤트 처리 로직
        커버하는 함수 및 데이터: 이벤트 타입 검증, 변환기 업데이트, 캐시 무효화, 옵저버 알림
        기대되는 안정성: 이벤트 기반 좌표 변환기 자동 업데이트 보장
        """
        # Given - CoordinateManager와 mock 변환기 설정
        manager = CoordinateManager.get_instance()
        mock_transformer = Mock(spec=ICoordinateTransformer)
        mock_transformer.set_camera_offset = Mock()
        mock_transformer.invalidate_cache = Mock()

        with (
            patch.object(
                manager, 'get_transformer', return_value=mock_transformer
            ),
            patch.object(manager, 'notify_observers') as mock_notify,
        ):
            # 카메라 오프셋 변경 이벤트 생성
            with patch('time.time', return_value=1234567890.5):
                event = CameraOffsetChangedEvent(
                    timestamp=0.0,  # __post_init__에서 자동 설정됨
                    created_at=None,  # __post_init__에서 자동 설정됨
                    world_offset=(100.0, 150.0),
                    screen_center=(400, 300),
                    camera_entity_id='test-camera-uuid',
                )

            # When - 이벤트 처리
            manager.handle_event(event)

            # Then - 변환기 메서드들이 올바른 순서로 호출됨
            mock_transformer.set_camera_offset.assert_called_once()
            called_offset = mock_transformer.set_camera_offset.call_args[0][0]
            assert called_offset.x == 100.0, (
                'X 오프셋이 올바르게 설정되어야 함'
            )
            assert called_offset.y == 150.0, (
                'Y 오프셋이 올바르게 설정되어야 함'
            )

            mock_transformer.invalidate_cache.assert_called_once()
            mock_notify.assert_called_once_with(mock_transformer)

    def test_이벤트_처리_다른_타입_이벤트_무시_검증_성공_시나리오(
        self,
    ) -> None:
        """15. 다른 타입 이벤트 무시 처리 검증 (성공 시나리오)

        목적: CAMERA_OFFSET_CHANGED가 아닌 이벤트는 무시되는지 검증
        테스트할 범위: handle_event() 메서드의 이벤트 타입 필터링
        커버하는 함수 및 데이터: 이벤트 타입 구분 처리, early return
        기대되는 안정성: 관련 없는 이벤트에 대한 무시 처리 보장
        """
        # Given - CoordinateManager와 mock 변환기 설정
        manager = CoordinateManager.get_instance()
        mock_transformer = Mock(spec=ICoordinateTransformer)

        with (
            patch.object(
                manager, 'get_transformer', return_value=mock_transformer
            ),
            patch.object(manager, 'notify_observers') as mock_notify,
        ):
            # 다른 타입의 이벤트 생성
            other_event= MagicMock(spec=BaseEvent)
            other_event.get_event_type.return_value = EventType.ENEMY_DEATH

            # When - 이벤트 처리
            manager.handle_event(other_event)

            # Then - 어떤 변환기 메서드도 호출되지 않음
            mock_transformer.set_camera_offset.assert_not_called()
            mock_transformer.invalidate_cache.assert_not_called()
            mock_notify.assert_not_called()

    def test_이벤트_처리_잘못된_인스턴스_타입_무시_검증_성공_시나리오(
        self,
    ) -> None:
        """16. CameraOffsetChangedEvent가 아닌 BaseEvent 무시 검증 (성공 시나리오)

        목적: event_type은 올바르지만 인스턴스가 CameraOffsetChangedEvent가 아닌 경우 무시되는지 검증
        테스트할 범위: handle_event() 메서드의 인스턴스 타입 검증
        커버하는 함수 및 데이터: isinstance 검증, 타입 안전성
        기대되는 안정성: 타입 안전성을 통한 잘못된 이벤트 처리 방지 보장
        """
        # Given - CoordinateManager와 mock 변환기 설정
        manager = CoordinateManager.get_instance()
        mock_transformer = Mock(spec=ICoordinateTransformer)

        with (
            patch.object(
                manager, 'get_transformer', return_value=mock_transformer
            ),
            patch.object(manager, 'notify_observers') as mock_notify,
        ):
            # 올바른 event_type이지만 잘못된 인스턴스 타입
            wrong_instance_event = MagicMock(spec=BaseEvent)
            wrong_instance_event.get_event_type.return_value = EventType.CAMERA_OFFSET_CHANGED

            # When - 이벤트 처리
            manager.handle_event(wrong_instance_event)

            # Then - 어떤 변환기 메서드도 호출되지 않음
            mock_transformer.set_camera_offset.assert_not_called()
            mock_transformer.invalidate_cache.assert_not_called()
            mock_notify.assert_not_called()

    def test_이벤트_처리_예외_발생_시_격리_처리_검증_성공_시나리오(
        self,
    ) -> None:
        """17. 변환기 처리 중 예외 발생 시 격리 처리 검증 (성공 시나리오)

        목적: 예외가 발생해도 다른 시스템에 영향을 주지 않고 경고 메시지를 출력하는지 검증
        테스트할 범위: handle_event() 메서드의 예외 처리 및 격리
        커버하는 함수 및 데이터: try-except 블록, 예외 격리, 경고 메시지 출력
        기대되는 안정성: 예외 상황에서도 시스템 안정성 유지 보장
        """
        # Given - CoordinateManager와 예외를 발생시키는 mock 변환기
        manager = CoordinateManager.get_instance()
        mock_transformer = Mock(spec=ICoordinateTransformer)
        mock_transformer.set_camera_offset.side_effect = RuntimeError(
            'Test exception'
        )

        with (
            patch.object(
                manager, 'get_transformer', return_value=mock_transformer
            ),
            patch('builtins.print') as mock_print,
        ):
            # 카메라 오프셋 변경 이벤트 생성
            with patch('time.time', return_value=1234567890.5):
                event = CameraOffsetChangedEvent(
                    timestamp=0.0,  # __post_init__에서 자동 설정됨
                    created_at=None,  # __post_init__에서 자동 설정됨
                    world_offset=(100.0, 150.0),
                    screen_center=(400, 300),
                    camera_entity_id='test-camera-uuid',
                )

            # When - 이벤트 처리 (예외가 발생하지만 메서드는 정상 종료되어야 함)
            try:
                manager.handle_event(event)
            except Exception as e:
                pytest.fail(f'handle_event()에서 예외가 누출되었습니다: {e}')

            # Then - 예외가 잡혀서 경고 메시지가 출력됨
            mock_transformer.set_camera_offset.assert_called_once()
            mock_print.assert_called_once()

            # 경고 메시지 내용 확인
            print_call_args = mock_print.call_args[0][0]
            assert (
                'Warning: CoordinateManager failed to handle camera offset event'
                in print_call_args
            ), '적절한 경고 메시지가 출력되어야 함'
            assert 'Test exception' in print_call_args, (
                '실제 예외 메시지가 포함되어야 함'
            )

    def test_구독_이벤트_타입_목록_반환_검증_성공_시나리오(
        self,
    ) -> None:
        """18. 구독 이벤트 타입 목록 반환 검증 (성공 시나리오)

        목적: get_subscribed_events() 메서드가 올바른 이벤트 타입을 반환하는지 검증
        테스트할 범위: IEventSubscriber 인터페이스 구현
        커버하는 함수 및 데이터: get_subscribed_events() 메서드
        기대되는 안정성: 이벤트 구독 시스템과의 정확한 연동 보장
        """
        # Given - CoordinateManager 인스턴스
        manager = CoordinateManager.get_instance()

        # When - 구독 이벤트 목록 조회
        subscribed_events = manager.get_subscribed_events()

        # Then - CAMERA_OFFSET_CHANGED 이벤트 타입이 포함됨
        assert isinstance(subscribed_events, list), (
            '구독 이벤트 목록은 리스트여야 함'
        )
        assert len(subscribed_events) == 1, (
            'CAMERA_OFFSET_CHANGED 하나의 이벤트 타입만 구독해야 함'
        )
        assert EventType.CAMERA_OFFSET_CHANGED in subscribed_events, (
            'CAMERA_OFFSET_CHANGED 이벤트 타입을 구독해야 함'
        )

    def test_구독자_이름_반환_검증_성공_시나리오(
        self,
    ) -> None:
        """19. 구독자 이름 반환 검증 (성공 시나리오)

        목적: get_subscriber_name() 메서드가 올바른 이름을 반환하는지 검증
        테스트할 범위: IEventSubscriber 인터페이스 구현
        커버하는 함수 및 데이터: get_subscriber_name() 메서드
        기대되는 안정성: 디버깅을 위한 정확한 구독자 식별 보장
        """
        # Given - CoordinateManager 인스턴스
        manager = CoordinateManager.get_instance()

        # When - 구독자 이름 조회
        subscriber_name = manager.get_subscriber_name()

        # Then - 올바른 이름이 반환됨
        assert isinstance(subscriber_name, str), (
            '구독자 이름은 문자열이어야 함'
        )
        assert subscriber_name == 'CoordinateManager', (
            '구독자 이름이 CoordinateManager여야 함'
        )
        assert len(subscriber_name) > 0, '구독자 이름은 비어있지 않아야 함'

"""
Unit tests for CameraOffsetChangedEvent.

Tests camera offset event creation, validation, delta calculation,
and significant change detection functionality.
"""

from datetime import datetime
from unittest.mock import patch

from src.core.events.camera_offset_changed_event import (
    CameraOffsetChangedEvent,
)
from src.core.events.event_types import EventType


class TestCameraOffsetChangedEvent:
    """Test class for CameraOffsetChangedEvent functionality."""

    def test_기본_이벤트_생성_및_자동_초기화_검증_성공_시나리오(self) -> None:
        """1. 기본 이벤트 생성 및 자동 초기화 검증 (성공 시나리오)

        목적: CameraOffsetChangedEvent 객체 생성 시 자동 초기화 검증
        테스트할 범위: __post_init__ 메서드의 자동 설정 기능
        커버하는 함수 및 데이터: event_type, timestamp, created_at 등
        기대되는 안정성: 이벤트 객체 생성 시 모든 필수 속성 자동 설정 보장
        """
        # Given - 유효한 파라미터들
        world_offset = (100.0, 150.0)
        screen_center = (400, 300)
        camera_entity_id = 'test-camera-uuid-1234'

        with (
            patch('time.time', return_value=1234567890.5),
            patch('datetime.datetime') as mock_datetime,
        ):
            mock_now = datetime(2023, 8, 13, 12, 0, 0)
            mock_datetime.now.return_value = mock_now

            # When - 이벤트 객체 생성 (BaseEvent 필수 파라미터 포함)
            event = CameraOffsetChangedEvent(
                event_type=None,  # __post_init__에서 자동 설정됨
                timestamp=0.0,  # __post_init__에서 자동 설정됨
                created_at=None,  # __post_init__에서 자동 설정됨
                world_offset=world_offset,
                screen_center=screen_center,
                camera_entity_id=camera_entity_id,
            )

            # Then - 자동 초기화 검증
            assert event.event_type == EventType.CAMERA_OFFSET_CHANGED, (
                '이벤트 타입이 자동 설정되어야 함'
            )
            assert event.timestamp == 1234567890.5, (
                '타임스탬프가 자동 설정되어야 함'
            )
            assert event.created_at == mock_now, (
                '생성시간이 자동 설정되어야 함'
            )
            assert event._initialized, (
                '_initialized가 True로 설정되어야 함'
            )

            # 입력 파라미터 불변성 검증
            assert event.world_offset == world_offset, (
                'world_offset이 변경되지 않아야 함'
            )
            assert event.screen_center == screen_center, (
                'screen_center가 변경되지 않아야 함'
            )
            assert event.camera_entity_id == camera_entity_id, (
                'camera_entity_id가 변경되지 않아야 함'
            )

    def test_validate_메서드_성공_시나리오_검증_성공_시나리오(self) -> None:
        """2. validate() 메서드 성공 시나리오 검증 (성공 시나리오)

        목적: 모든 필드가 올바른 형식일 때 validate() 성공 검증
        테스트할 범위: validate() 메서드의 유효성 검사 로직
        커버하는 함수 및 데이터: 모든 필드 타입 및 형식 검증
        기대되는 안정성: 올바른 데이터에 대해 True 반환 보장
        """
        # Given - 모든 필드가 올바른 이벤트 객체
        with patch('time.time', return_value=1234567890.5):
            event = CameraOffsetChangedEvent(
                event_type=None,  # __post_init__에서 자동 설정됨
                timestamp=0.0,  # __post_init__에서 자동 설정됨
                created_at=None,  # __post_init__에서 자동 설정됨
                world_offset=(100.0, 150.0),
                screen_center=(400, 300),
                camera_entity_id='valid-uuid-string',
                previous_offset=(50.0, 75.0),
            )

            # 상태 저장 (불변성 검증용)
            original_world_offset = event.world_offset
            original_screen_center = event.screen_center

            # When - validate() 호출
            result = event.validate()

            # Then - 검증 성공 및 불변성 확인
            assert result, '유효한 이벤트에 대해 True를 반환해야 함'
            assert event.world_offset == original_world_offset, (
                'validate 후 world_offset 불변성 유지'
            )
            assert event.screen_center == original_screen_center, (
                'validate 후 screen_center 불변성 유지'
            )

    def test_get_offset_delta_정상_계산_검증_성공_시나리오(self) -> None:
        """3. get_offset_delta() 정상 계산 검증 (성공 시나리오)

        목적: previous_offset이 있을 때 올바른 델타 계산 검증
        테스트할 범위: get_offset_delta() 메서드의 계산 로직
        커버하는 함수 및 데이터: 델타 계산 정확성
        기대되는 안정성: 정확한 변화량 계산 보장
        """
        # Given - previous_offset이 설정된 이벤트 객체
        with patch('time.time', return_value=1234567890.5):
            event = CameraOffsetChangedEvent(
                event_type=None,  # __post_init__에서 자동 설정됨
                timestamp=0.0,  # __post_init__에서 자동 설정됨
                created_at=None,  # __post_init__에서 자동 설정됨
                world_offset=(200.0, 300.0),
                screen_center=(400, 300),
                camera_entity_id='test-uuid',
                previous_offset=(100.0, 150.0),
            )

            # When - get_offset_delta() 호출
            delta = event.get_offset_delta()

            # Then - 올바른 계산 결과 검증
            expected_delta = (100.0, 150.0)  # (200-100, 300-150)
            assert delta == expected_delta, (
                f'델타 계산이 정확해야 함: 예상 {expected_delta}, 실제 {delta}'
            )

            # 불변성 검증
            assert event.world_offset == (200.0, 300.0), (
                '원본 데이터 불변성 유지'
            )
            assert event.previous_offset == (100.0, 150.0), (
                '원본 데이터 불변성 유지'
            )

    def test_has_significant_change_임계값_이상_변화_감지_성공_시나리오(
        self,
    ) -> None:
        """4. has_significant_change() 임계값 이상 변화 감지 (성공 시나리오)

        목적: 임계값보다 큰 변화량일 때 True 반환 검증
        테스트할 범위: has_significant_change() 메서드의 임계값 판단 로직
        커버하는 함수 및 데이터: 변화량 크기 계산 및 임계값 비교
        기대되는 안정성: 유의미한 변화에 대해 True 반환 보장
        """
        # Given - 임계값보다 큰 변화량을 가진 이벤트
        with patch('time.time', return_value=1234567890.5):
            event = CameraOffsetChangedEvent(
                event_type=None,  # __post_init__에서 자동 설정됨
                timestamp=0.0,  # __post_init__에서 자동 설정됨
                created_at=None,  # __post_init__에서 자동 설정됨
                world_offset=(105.0, 100.0),
                screen_center=(400, 300),
                camera_entity_id='test-uuid',
                previous_offset=(100.0, 100.0),  # 델타: (5.0, 0.0), 크기: 5.0
            )

            # When - has_significant_change() 호출 (임계값 1.0)
            is_significant = event.has_significant_change(threshold=1.0)

            # Then - True 반환 검증 (5.0 > 1.0)
            assert is_significant, '임계값보다 큰 변화는 유의미해야 함'

    def test_validate_메서드_실패_시나리오들_검증_성공_시나리오(self) -> None:
        """5. validate() 메서드 실패 시나리오들 검증 (경계 조건)

        목적: 잘못된 형식의 데이터에 대해 False 반환 검증
        테스트할 범위: validate() 메서드의 경계 조건 처리
        커버하는 함수 및 데이터: 각 필드별 유효성 검사 경계값
        기대되는 안정성: 잘못된 데이터에 대해 False 반환 보장
        """
        # Test Case 1: world_offset 길이 부족
        with patch('time.time', return_value=1234567890.5):
            event = CameraOffsetChangedEvent(
                event_type=None,  # __post_init__에서 자동 설정됨
                timestamp=0.0,  # __post_init__에서 자동 설정됨
                created_at=None,  # __post_init__에서 자동 설정됨
                world_offset=(100.0, 150.0),
                screen_center=(400, 300),
                camera_entity_id='test-uuid',
            )
            # 강제로 잘못된 값 설정 (개발자 가정 우회하여 테스트)
            object.__setattr__(event, 'world_offset', (100.0,))

            assert not event.validate(), (
                'world_offset 길이 부족 시 False 반환'
            )

        # Test Case 2: screen_center 타입 오류
        with patch('time.time', return_value=1234567890.5):
            event = CameraOffsetChangedEvent(
                event_type=None,  # __post_init__에서 자동 설정됨
                timestamp=0.0,  # __post_init__에서 자동 설정됨
                created_at=None,  # __post_init__에서 자동 설정됨
                world_offset=(100.0, 150.0),
                screen_center=(400, 300),
                camera_entity_id='test-uuid',
            )
            # 강제로 잘못된 값 설정
            object.__setattr__(
                event, 'screen_center', ('400', '300')
            )  # 문자열 (잘못됨)

            assert not event.validate(), (
                'screen_center 타입 오류 시 False 반환'
            )

        # Test Case 3: camera_entity_id 타입 오류
        with patch('time.time', return_value=1234567890.5):
            event = CameraOffsetChangedEvent(
                event_type=None,  # __post_init__에서 자동 설정됨
                timestamp=0.0,  # __post_init__에서 자동 설정됨
                created_at=None,  # __post_init__에서 자동 설정됨
                world_offset=(100.0, 150.0),
                screen_center=(400, 300),
                camera_entity_id='test-uuid',
            )
            # 강제로 잘못된 값 설정
            object.__setattr__(event, 'camera_entity_id', 123)  # 정수 (잘못됨)

            assert not event.validate(), (
                'camera_entity_id 타입 오류 시 False 반환'
            )

    def test_get_offset_delta_previous_offset_None_케이스_검증_성공_시나리오(
        self,
    ) -> None:
        """6. get_offset_delta() previous_offset None 케이스 검증 (경계 조건)

        목적: previous_offset이 None일 때 None 반환 검증
        테스트할 범위: get_offset_delta() 메서드의 None 처리
        커버하는 함수 및 데이터: None 값 처리 로직
        기대되는 안정성: None 입력에 대해 None 반환 보장
        """
        # Given - previous_offset=None인 이벤트 객체
        with patch('time.time', return_value=1234567890.5):
            event = CameraOffsetChangedEvent(
                event_type=None,  # __post_init__에서 자동 설정됨
                timestamp=0.0,  # __post_init__에서 자동 설정됨
                created_at=None,  # __post_init__에서 자동 설정됨
                world_offset=(200.0, 300.0),
                screen_center=(400, 300),
                camera_entity_id='test-uuid',
                previous_offset=None,
            )

            # When - get_offset_delta() 호출
            delta = event.get_offset_delta()

            # Then - None 반환 검증
            assert delta is None, (
                'previous_offset이 None이면 delta도 None이어야 함'
            )

    def test_has_significant_change_previous_offset_None_검증_성공_시나리오(
        self,
    ) -> None:
        """7. has_significant_change() previous_offset None 케이스 검증 (경계).

        목적: previous_offset이 None일 때 True 반환 검증 (첫 번째 변화)
        테스트할 범위: has_significant_change() 메서드의 첫 번째 변화 처리
        커버하는 함수 및 데이터: 첫 번째 변화 감지 로직
        기대되는 안정성: 첫 번째 변화는 항상 유의미함 보장
        """
        # Given - previous_offset=None인 이벤트 객체
        with patch('time.time', return_value=1234567890.5):
            event = CameraOffsetChangedEvent(
                event_type=None,  # __post_init__에서 자동 설정됨
                timestamp=0.0,  # __post_init__에서 자동 설정됨
                created_at=None,  # __post_init__에서 자동 설정됨
                world_offset=(200.0, 300.0),
                screen_center=(400, 300),
                camera_entity_id='test-uuid',
                previous_offset=None,
            )

            # When - has_significant_change() 호출
            is_significant = event.has_significant_change(
                threshold=1000.0
            )  # 큰 임계값

            # Then - True 반환 검증 (첫 번째는 항상 유의미)
            assert is_significant, '첫 번째 변화는 항상 유의미해야 함'

    def test_has_significant_change_임계값_이하_변화_검증_성공_시나리오(
        self,
    ) -> None:
        """8. has_significant_change() 임계값 이하 변화 검증 (경계 조건)

        목적: 임계값보다 작은 변화량일 때 False 반환 검증
        테스트할 범위: has_significant_change() 메서드의 임계값 경계 처리
        커버하는 함수 및 데이터: 임계값 미만 변화량 판단
        기대되는 안정성: 미미한 변화에 대해 False 반환 보장
        """
        # Given - 임계값보다 작은 변화량을 가진 이벤트
        with patch('time.time', return_value=1234567890.5):
            event = CameraOffsetChangedEvent(
                event_type=None,  # __post_init__에서 자동 설정됨
                timestamp=0.0,  # __post_init__에서 자동 설정됨
                created_at=None,  # __post_init__에서 자동 설정됨
                world_offset=(100.5, 100.3),
                screen_center=(400, 300),
                camera_entity_id='test-uuid',
                previous_offset=(
                    100.0,
                    100.0,
                ),  # 델타: (0.5, 0.3), 크기: ~0.58
            )

            # When - has_significant_change() 호출 (임계값 1.0)
            is_significant = event.has_significant_change(threshold=1.0)

            # Then - False 반환 검증 (0.58 < 1.0)
            assert not is_significant, (
                '임계값보다 작은 변화는 유의미하지 않아야 함'
            )

    def test_str_문자열_표현_검증_성공_시나리오(self) -> None:
        """9. __str__() 문자열 표현 검증 (출력 형식)

        목적: __str__() 메서드가 예상 형식의 문자열을 반환하는지 검증
        테스트할 범위: __str__() 메서드의 문자열 포매팅
        커버하는 함수 및 데이터: 문자열 표현 형식
        기대되는 안정성: 일관된 문자열 형식 보장
        """
        # Given - 완전히 설정된 이벤트 객체
        with patch('time.time', return_value=1234567890.5):
            event = CameraOffsetChangedEvent(
                event_type=None,  # __post_init__에서 자동 설정됨
                timestamp=0.0,  # __post_init__에서 자동 설정됨
                created_at=None,  # __post_init__에서 자동 설정됨
                world_offset=(100.0, 150.0),
                screen_center=(400, 300),
                camera_entity_id='test-camera-uuid',
            )

            # When - __str__() 호출
            str_repr = str(event)

            # Then - 예상 형식 검증
            expected_parts = [
                'CameraOffsetChangedEvent(',
                'entity=test-camera-uuid',
                'offset=(100.0, 150.0)',
                'timestamp=1234567890.500',
            ]

            for part in expected_parts:
                assert part in str_repr, (
                    f"문자열 표현에 '{part}'가 포함되어야 함"
                )

            # 전체 형식 검증
            expected_format = (
                'CameraOffsetChangedEvent('
                'entity=test-camera-uuid, '
                'offset=(100.0, 150.0), '
                'timestamp=1234567890.500)'
            )
            assert str_repr == expected_format, (
                f'예상: {expected_format}, 실제: {str_repr}'
            )

    def test_timestamp_자동_설정_mocking_검증_성공_시나리오(self) -> None:
        """10. timestamp 자동 설정 mocking 검증 (Mock 검증)

        목적: time.time() 모킹이 올바르게 동작하는지 검증
        테스트할 범위: 모킹 대상의 정확한 동작
        커버하는 함수 및 데이터: 시간 관련 부수 효과 제어
        기대되는 안정성: 테스트 시간 일관성 보장
        """
        # Given - 특정 시간으로 모킹
        mock_time = 9999999999.123

        with patch('time.time', return_value=mock_time):
            # When - 이벤트 생성
            event = CameraOffsetChangedEvent(
                event_type=None,  # __post_init__에서 자동 설정됨
                timestamp=0.0,  # __post_init__에서 자동 설정됨
                created_at=None,  # __post_init__에서 자동 설정됨
                world_offset=(0.0, 0.0),
                screen_center=(0, 0),
                camera_entity_id='mock-test-uuid',
            )

            # Then - 모킹된 시간이 설정되었는지 검증
            assert event.timestamp == mock_time, (
                f'모킹된 시간이 설정되어야 함: {mock_time}'
            )

    def test_created_at_자동_설정_mocking_검증_성공_시나리오(self) -> None:
        """11. created_at 자동 설정 mocking 검증 (Mock 검증)

        목적: datetime.now() 모킹이 올바르게 동작하는지 검증
        테스트할 범위: 모킹 대상의 정확한 동작
        커버하는 함수 및 데이터: 날짜/시간 관련 부수 효과 제어
        기대되는 안정성: 테스트 날짜/시간 일관성 보장
        """
        # Given - 특정 날짜/시간으로 모킹
        mock_datetime_obj = datetime(2025, 12, 25, 15, 30, 45)

        with (
            patch('time.time', return_value=1234567890.5),
            patch('datetime.datetime') as mock_datetime,
        ):
            mock_datetime.now.return_value = mock_datetime_obj

            # When - 이벤트 생성
            event = CameraOffsetChangedEvent(
                event_type=None,  # __post_init__에서 자동 설정됨
                timestamp=0.0,  # __post_init__에서 자동 설정됨
                created_at=None,  # __post_init__에서 자동 설정됨
                world_offset=(0.0, 0.0),
                screen_center=(0, 0),
                camera_entity_id='datetime-test-uuid',
            )

            # Then - 모킹된 날짜/시간이 설정되었는지 검증
            assert event.created_at == mock_datetime_obj, (
                '모킹된 날짜/시간이 설정되어야 함'
            )
            (
                mock_datetime.now.assert_called_once(),
                'datetime.now()가 정확히 한 번 호출되어야 함',
            )

    def test_screen_center_float_자동_변환_검증_성공_시나리오(self) -> None:
        """12. screen_center float 자동 변환 검증 (자동 변환)

        목적: screen_center에 float 값 전달 시 자동 int 변환 검증
        테스트할 범위: __post_init__ 메서드의 float to int 변환 로직
        커버하는 함수 및 데이터: screen_center 자동 변환 기능
        기대되는 안정성: float 입력에 대해 int로 자동 변환 보장
        """
        # Given - float 타입의 screen_center
        with patch('time.time', return_value=1234567890.5):
            # When - float screen_center로 이벤트 생성
            event = CameraOffsetChangedEvent(
                event_type=None,  # __post_init__에서 자동 설정됨
                timestamp=0.0,    # __post_init__에서 자동 설정됨
                created_at=None,  # __post_init__에서 자동 설정됨
                world_offset=(100.0, 150.0),
                screen_center=(400.7, 300.3),  # float 값 입력
                camera_entity_id="float-test-uuid"
            )

            # Then - int로 자동 변환 검증
            assert event.screen_center == (400, 300), (
                "float screen_center가 int로 자동 변환되어야 함"
            )
            assert isinstance(event.screen_center[0], int), (
                "변환된 screen_center[0]이 int 타입이어야 함"
            )
            assert isinstance(event.screen_center[1], int), (
                "변환된 screen_center[1]이 int 타입이어야 함"
            )

            # validate() 메서드 통과 검증
            assert event.validate(), (
                "변환된 screen_center로 validate가 성공해야 함"
            )

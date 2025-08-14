"""
Unit tests for BaseEvent abstract class.

Tests the core functionality of the BaseEvent class including
timestamp generation, validation, and event age calculations.
"""

import time
from datetime import datetime
from unittest.mock import patch

import pytest

from src.core.events.base_event import BaseEvent
from src.core.events.event_types import EventType


class TestBaseEvent:
    """Test class for BaseEvent abstract class functionality."""

    def test_이벤트_생성_및_타임스탬프_자동_설정_검증_성공_시나리오(
        self,
    ) -> None:
        """1. 이벤트 생성 시 타임스탬프 자동 설정 검증 (성공 시나리오)

        목적: BaseEvent 생성 시 timestamp와 created_at 자동 설정 확인
        테스트할 범위: BaseEvent의 __post_init__ 메서드
        커버하는 함수 및 데이터: timestamp, created_at 자동 설정
        기대되는 안정성: 일관된 시간 정보 생성 보장
        """

        # Given - Mock 이벤트 클래스 정의
        class MockGameEvent(BaseEvent):
            def get_event_type(self) -> EventType:
                return EventType.ENEMY_DEATH
            def validate(self) -> bool:
                return True

        start_time = time.time()

        # When - 이벤트 생성
        event = MockGameEvent(
            timestamp=0.0,  # 이 값은 __post_init__에서 덮어써짐
            created_at=None,  # 이 값도 덮어써짐
        )

        end_time = time.time()

        # Then - 타임스탬프 자동 설정 확인
        assert start_time <= event.timestamp <= end_time, (
            '타임스탬프가 생성 시점 범위 내에 있어야 함'
        )
        assert isinstance(event.created_at, datetime), (
            'created_at이 datetime 타입이어야 함'
        )
        assert event.created_at.timestamp() >= start_time, (
            'created_at이 생성 시점 이후여야 함'
        )
        assert hasattr(event, '_initialized'), '초기화 플래그가 설정되어야 함'

    def test_이벤트_타입_및_표시명_정확성_검증_성공_시나리오(self) -> None:
        """2. 이벤트 타입 및 표시명 정확성 검증 (성공 시나리오)

        목적: EventType enum과의 연동 및 한국어 표시명 확인
        테스트할 범위: event_type 속성과 EventType의 display_name
        커버하는 함수 및 데이터: EventType enum 연동
        기대되는 안정성: 정확한 이벤트 타입 식별 보장
        """

        # Given - Mock 이벤트 클래스
        class MockCombatEvent(BaseEvent):
            def get_event_type(self) -> EventType:
                return EventType.WEAPON_FIRED
            def validate(self) -> bool:
                return True

        # When - 전투 이벤트 생성
        event = MockCombatEvent(
            timestamp=time.time(),
            created_at=datetime.now(),
        )

        # Then - 이벤트 타입 정확성 확인
        assert event.get_event_type() == EventType.WEAPON_FIRED, (
            '이벤트 타입이 정확해야 함'
        )
        assert event.get_event_type().display_name == '무기 발사', (
            '한국어 표시명이 정확해야 함'
        )
        assert event.get_event_type().is_combat_event, '전투 이벤트로 분류되어야 함'

    def test_이벤트_나이_계산_정확성_검증_성공_시나리오(self) -> None:
        """3. 이벤트 나이 계산 정확성 검증 (성공 시나리오)

        목적: get_age_seconds 메서드의 정확한 시간 차이 계산 확인
        테스트할 범위: get_age_seconds 메서드
        커버하는 함수 및 데이터: 시간 차이 계산 로직
        기대되는 안정성: 정확한 이벤트 경과 시간 측정 보장
        """

        # Given - 특정 시간의 Mock 이벤트
        class MockTimedEvent(BaseEvent):
            def get_event_type(self) -> EventType:
                return EventType.ITEM_DROP
            def validate(self) -> bool:
                return True

        base_time = 1000.0
        event = MockTimedEvent(
            timestamp=base_time,
            created_at=datetime.now(),
        )

        # When - 다른 시간에서 나이 계산
        current_time = base_time + 5.5
        age = event.get_age_seconds(current_time)

        # Then - 정확한 나이 계산 확인
        assert age == 5.5, '이벤트 나이가 정확히 계산되어야 함'

        # When - 현재 시간 없이 호출
        with patch('time.time', return_value=base_time + 3.2):
            age_auto = event.get_age_seconds()

        # Then - 자동 시간 계산 확인 (부동소수점 오차 허용)
        assert abs(age_auto - 3.2) < 1e-6, '자동 시간 계산이 정확해야 함'

    def test_이벤트_만료_검사_로직_검증_성공_시나리오(self) -> None:
        """4. 이벤트 만료 검사 로직 검증 (성공 시나리오)

        목적: is_expired 메서드의 만료 판단 로직 확인
        테스트할 범위: is_expired 메서드
        커버하는 함수 및 데이터: 만료 시간 비교 로직
        기대되는 안정성: 정확한 이벤트 만료 판단 보장
        """

        # Given - 과거 시점의 이벤트
        class MockExpirableEvent(BaseEvent):
            def get_event_type(self) -> EventType:
                return EventType.BOSS_SPAWNED
            def validate(self) -> bool:
                return True

        old_time = 1000.0
        event = MockExpirableEvent(
            timestamp=old_time,
            created_at=datetime.now(),
        )

        # When & Then - 만료되지 않은 경우
        current_time = old_time + 2.0
        max_age = 5.0
        assert not event.is_expired(max_age, current_time), (
            '만료되지 않아야 함'
        )

        # When & Then - 만료된 경우
        current_time = old_time + 7.0
        assert event.is_expired(max_age, current_time), '만료되어야 함'

        # When & Then - 경계 조건
        current_time = old_time + 5.0
        assert not event.is_expired(max_age, current_time), (
            '정확히 max_age에서는 만료되지 않아야 함'
        )

    def test_이벤트_문자열_표현_포맷_검증_성공_시나리오(self) -> None:
        """5. 이벤트 문자열 표현 포맷 검증 (성공 시나리오)

        목적: __str__ 메서드의 출력 포맷 확인
        테스트할 범위: __str__ 메서드
        커버하는 함수 및 데이터: 문자열 표현 형식
        기대되는 안정성: 일관된 디버깅 정보 제공 보장
        """

        # Given - Mock 이벤트
        class MockStringEvent(BaseEvent):
            def get_event_type(self) -> EventType:
                return EventType.LEVEL_UP
            def validate(self) -> bool:
                return True

        timestamp = 1234.567
        event = MockStringEvent(
            timestamp=timestamp,
            created_at=datetime.now(),
        )

        # When - 문자열 변환
        str_repr = str(event)

        # Then - 포맷 검증
        assert 'MockStringEvent' in str_repr, '클래스명이 포함되어야 함'
        assert '레벨 업' in str_repr, '한국어 이벤트 타입명이 포함되어야 함'
        # 타임스탬프는 정확한 값보다는 포맷 확인
        assert 'timestamp=' in str_repr, '타임스탬프 라벨이 포함되어야 함'
        assert str(timestamp) in str_repr, (
            '설정된 타임스탬프 값이 포함되어야 함'
        )
        assert 'type=' in str_repr, 'type 라벨이 포함되어야 함'
        assert 'timestamp=' in str_repr, 'timestamp 라벨이 포함되어야 함'

    def test_추상_메서드_validate_구현_강제_검증_성공_시나리오(self) -> None:
        """6. 추상 메서드 validate 구현 강제 검증 (성공 시나리오)

        목적: 하위 클래스에서 validate 메서드 구현 강제 확인
        테스트할 범위: ABC 추상 메서드 강제 구현
        커버하는 함수 및 데이터: 추상 클래스 제약
        기대되는 안정성: 하위 클래스 구현 일관성 보장
        """

        # Given - validate 미구현 클래스
        class IncompleteEvent(BaseEvent):
            pass  # validate 구현 없음

        # When & Then - 인스턴스 생성 시 에러 발생
        with pytest.raises(TypeError) as exc_info:
            IncompleteEvent(
                timestamp=time.time(),
                created_at=datetime.now(),
            )

        assert 'abstract' in str(exc_info.value).lower(), (
            '추상 메서드 에러가 발생해야 함'
        )

    def test_dataclass_불변성_및_타입_힌트_검증_성공_시나리오(self) -> None:
        """7. dataclass 불변성 및 타입 힌트 검증 (성공 시나리오)

        목적: @dataclass 적용 및 Python 3.13+ 타입 힌트 확인
        테스트할 범위: 클래스 속성 및 타입 정보
        커버하는 함수 및 데이터: dataclass 메타데이터
        기대되는 안정성: 타입 안전성 및 데이터 구조 일관성 보장
        """

        # Given - Mock 이벤트 클래스
        class MockDataclassEvent(BaseEvent):
            def get_event_type(self) -> EventType:
                return EventType.LEVEL_UP
            def validate(self) -> bool:
                return True

        # When - 부모 클래스 메타데이터 검사 (BaseEvent의 애노테이션)
        base_annotations = BaseEvent.__annotations__

        # Then - 타입 힌트 확인
        assert 'timestamp' in base_annotations, 'timestamp 필드가 있어야 함'
        assert 'created_at' in base_annotations, 'created_at 필드가 있어야 함'

        # dataclass 필드 확인
        assert hasattr(MockDataclassEvent, '__dataclass_fields__'), (
            'dataclass로 정의되어야 함'
        )
        fields = MockDataclassEvent.__dataclass_fields__
        assert len(fields) >= 2, '최소 2개 필드가 있어야 함'

"""
Unit tests for EnemyDeathEvent class.

Tests the enemy death event implementation including data validation,
creation methods, and integration with the base event system.
"""

from datetime import datetime
from unittest.mock import Mock

import pytest

from src.core.events.enemy_death_event import EnemyDeathEvent
from src.core.events.event_types import EventType


class TestEnemyDeathEvent:
    """Test class for EnemyDeathEvent functionality."""

    def test_적_사망_이벤트_생성_및_기본_속성_검증_성공_시나리오(self) -> None:
        """1. 적 사망 이벤트 생성 및 기본 속성 검증 (성공 시나리오)

        목적: EnemyDeathEvent 생성 시 기본 속성들이 올바르게 설정되는지 확인
        테스트할 범위: EnemyDeathEvent 생성자 및 기본 속성
        커버하는 함수 및 데이터: __init__, 기본 속성 설정
        기대되는 안정성: 일관된 이벤트 객체 생성 보장
        """
        # Given - 적 엔티티 ID
        enemy_id = 'enemy_123'

        # When - EnemyDeathEvent 생성
        event = EnemyDeathEvent.create_from_id(enemy_id)

        # Then - 기본 속성 확인
        assert event.enemy_entity_id == enemy_id, '적 엔티티 ID가 정확해야 함'
        assert event.event_type == EventType.ENEMY_DEATH, (
            '이벤트 타입이 ENEMY_DEATH여야 함'
        )
        assert event.timestamp > 0, '타임스탬프가 설정되어야 함'
        assert event.created_at is not None, 'created_at이 설정되어야 함'
        assert isinstance(event.created_at, datetime), (
            'created_at이 datetime 타입이어야 함'
        )

    def test_적_사망_이벤트_데이터_검증_성공_시나리오(self) -> None:
        """2. 적 사망 이벤트 데이터 검증 성공 시나리오

        목적: validate 메서드가 올바른 데이터에 대해 True를 반환하는지 확인
        테스트할 범위: validate 메서드
        커버하는 함수 및 데이터: 데이터 유효성 검증 로직
        기대되는 안정성: 유효한 데이터 정확히 인식 보장
        """
        # Given - 유효한 적 엔티티 ID
        valid_ids = ['enemy_001', 'boss_dragon', 'zombie_123', 'e1']

        for enemy_id in valid_ids:
            # When - EnemyDeathEvent 생성
            event = EnemyDeathEvent.create_from_id(enemy_id)

            # Then - 검증 통과 확인
            assert event.validate() is True, (
                f'유효한 ID {enemy_id}에 대해 검증이 통과해야 함'
            )

    def test_적_사망_이벤트_잘못된_데이터_검증_실패_시나리오(self) -> None:
        """3. 적 사망 이벤트 잘못된 데이터 검증 실패 시나리오

        목적: validate 메서드가 잘못된 데이터에 대해 예외를 발생시키는지 확인
        테스트할 범위: validate 메서드 및 생성자 예외 처리
        커버하는 함수 및 데이터: 잘못된 데이터 처리 로직
        기대되는 안정성: 잘못된 데이터 차단 보장
        """
        # Given - 잘못된 적 엔티티 ID들
        invalid_ids = ['', '   ', '\n\t', None]

        for invalid_id in invalid_ids:
            # When & Then - EnemyDeathEvent 생성 시 예외 발생 확인
            with pytest.raises(ValueError) as exc_info:
                EnemyDeathEvent.create_from_id(invalid_id)

            assert 'Invalid EnemyDeathEvent data' in str(exc_info.value), (
                f'잘못된 ID {invalid_id}에 대해 적절한 에러 메시지가 나와야 함'
            )

    def test_엔티티_객체로부터_이벤트_생성_성공_시나리오(self) -> None:
        """4. 엔티티 객체로부터 이벤트 생성 성공 시나리오

        목적: create_from_entity 클래스 메서드의 정상 동작 확인
        테스트할 범위: create_from_entity 메서드
        커버하는 함수 및 데이터: 엔티티 객체 연동 생성
        기대되는 안정성: 엔티티 기반 이벤트 생성 보장
        """
        # Given - Mock 엔티티 객체
        mock_entity = Mock()
        mock_entity.id = 'enemy_456'

        # When - 엔티티로부터 이벤트 생성
        event = EnemyDeathEvent.create_from_entity(mock_entity)

        # Then - 올바른 생성 확인
        assert event.enemy_entity_id == 'enemy_456', (
            '엔티티 ID가 올바르게 추출되어야 함'
        )
        assert event.validate() is True, '생성된 이벤트가 유효해야 함'
        assert event.event_type == EventType.ENEMY_DEATH, (
            '이벤트 타입이 올바르게 설정되어야 함'
        )

    def test_잘못된_엔티티_객체_이벤트_생성_실패_시나리오(self) -> None:
        """5. 잘못된 엔티티 객체 이벤트 생성 실패 시나리오

        목적: create_from_entity 메서드의 예외 처리 확인
        테스트할 범위: create_from_entity 메서드 예외 처리
        커버하는 함수 및 데이터: 잘못된 엔티티 객체 처리
        기대되는 안정성: 잘못된 엔티티 차단 보장
        """
        # Given & When & Then - None 엔티티
        with pytest.raises(ValueError) as exc_info:
            EnemyDeathEvent.create_from_entity(None)
        assert 'Entity cannot be None' in str(exc_info.value), (
            'None 엔티티에 대해 적절한 에러 메시지가 나와야 함'
        )

        # Given & When & Then - ID 없는 엔티티
        mock_entity_no_id = Mock()
        mock_entity_no_id.id = None

        with pytest.raises(ValueError) as exc_info:
            EnemyDeathEvent.create_from_entity(mock_entity_no_id)
        assert 'Entity must have a valid ID' in str(exc_info.value), (
            'ID 없는 엔티티에 대해 적절한 에러 메시지가 나와야 함'
        )

        # Given & When & Then - 빈 ID 엔티티
        mock_entity_empty_id = Mock()
        mock_entity_empty_id.id = ''

        with pytest.raises(ValueError) as exc_info:
            EnemyDeathEvent.create_from_entity(mock_entity_empty_id)
        assert 'Entity must have a valid ID' in str(exc_info.value), (
            '빈 ID 엔티티에 대해 적절한 에러 메시지가 나와야 함'
        )

    def test_커스텀_타임스탬프_이벤트_생성_검증_성공_시나리오(self) -> None:
        """6. 커스텀 타임스탬프 이벤트 생성 검증 성공 시나리오

        목적: 커스텀 타임스탬프로 이벤트를 생성할 수 있는지 확인
        테스트할 범위: 커스텀 타임스탬프 설정
        커버하는 함수 및 데이터: 타임스탬프 커스터마이제이션
        기대되는 안정성: 정확한 타임스탬프 설정 보장
        """
        # Given - 커스텀 타임스탬프
        custom_timestamp = 1234567890.0
        custom_datetime = datetime(2023, 1, 1, 12, 0, 0)
        enemy_id = 'enemy_789'

        # When - 커스텀 타임스탬프로 이벤트 생성
        event = EnemyDeathEvent.create_from_id(
            enemy_id, timestamp=custom_timestamp, created_at=custom_datetime
        )

        # Then - 커스텀 값 확인
        assert event.timestamp == custom_timestamp, (
            '커스텀 타임스탬프가 설정되어야 함'
        )
        assert event.created_at == custom_datetime, (
            '커스텀 created_at이 설정되어야 함'
        )
        assert event.enemy_entity_id == enemy_id, (
            '적 ID가 올바르게 설정되어야 함'
        )

    def test_이벤트_나이_계산_정확성_검증_성공_시나리오(self) -> None:
        """7. 이벤트 나이 계산 정확성 검증 성공 시나리오

        목적: get_age_seconds 메서드가 정확한 시간 차이를 계산하는지 확인
        테스트할 범위: 상속받은 BaseEvent 메서드들
        커버하는 함수 및 데이터: 시간 차이 계산 로직
        기대되는 안정성: 정확한 이벤트 수명 측정 보장
        """
        # Given - 특정 시간의 이벤트
        base_time = 1000.0
        event = EnemyDeathEvent.create_from_id(
            'enemy_age_test', timestamp=base_time
        )

        # When - 나이 계산
        current_time = base_time + 5.0
        age = event.get_age_seconds(current_time)

        # Then - 정확한 나이 확인
        assert age == 5.0, '이벤트 나이가 정확히 계산되어야 함'

    def test_이벤트_만료_검사_로직_검증_성공_시나리오(self) -> None:
        """8. 이벤트 만료 검사 로직 검증 성공 시나리오

        목적: is_expired 메서드가 올바른 만료 판단을 하는지 확인
        테스트할 범위: 상속받은 BaseEvent 메서드들
        커버하는 함수 및 데이터: 만료 판단 로직
        기대되는 안정성: 정확한 이벤트 만료 판단 보장
        """
        # Given - 과거 시간의 이벤트
        old_time = 1000.0
        event = EnemyDeathEvent.create_from_id(
            'enemy_expiry_test', timestamp=old_time
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

    def test_이벤트_문자열_표현_포맷_검증_성공_시나리오(self) -> None:
        """9. 이벤트 문자열 표현 포맷 검증 성공 시나리오

        목적: __str__ 메서드의 출력 포맷 확인
        테스트할 범위: __str__ 메서드
        커버하는 함수 및 데이터: 문자열 표현 형식
        기대되는 안정성: 일관된 디버깅 정보 제공 보장
        """
        # Given - 테스트용 이벤트
        enemy_id = 'enemy_string_test'
        event = EnemyDeathEvent.create_from_id(enemy_id)

        # When - 문자열 변환
        str_repr = str(event)

        # Then - 포맷 검증
        assert 'EnemyDeathEvent(' in str_repr, '클래스명이 포함되어야 함'
        assert enemy_id in str_repr, '적 ID가 포함되어야 함'
        assert 'enemy_id=' in str_repr, 'enemy_id 라벨이 포함되어야 함'
        assert 'timestamp=' in str_repr, 'timestamp 라벨이 포함되어야 함'

    def test_이벤트_타입_일관성_검증_성공_시나리오(self) -> None:
        """10. 이벤트 타입 일관성 검증 성공 시나리오

        목적: 모든 생성 방법에서 event_type이 일관되게 설정되는지 확인
        테스트할 범위: 이벤트 타입 설정 일관성
        커버하는 함수 및 데이터: event_type 자동 설정
        기대되는 안정성: 이벤트 타입 일관성 보장
        """
        # Given - 다양한 생성 방법
        enemy_id = 'enemy_type_test'
        mock_entity = Mock()
        mock_entity.id = enemy_id

        # When - 다양한 방법으로 이벤트 생성
        event1 = EnemyDeathEvent.create_from_id(enemy_id)
        event2 = EnemyDeathEvent.create_from_entity(mock_entity)

        # Then - 모든 이벤트의 타입 일관성 확인
        assert event1.event_type == EventType.ENEMY_DEATH, (
            '첫 번째 이벤트 타입 확인'
        )
        assert event2.event_type == EventType.ENEMY_DEATH, (
            '두 번째 이벤트 타입 확인'
        )
        assert event1.event_type == event2.event_type, (
            '모든 이벤트 타입이 동일해야 함'
        )

    def test_get_enemy_id_메서드_동작_검증_성공_시나리오(self) -> None:
        """11. get_enemy_id 메서드 동작 검증 성공 시나리오

        목적: get_enemy_id 메서드가 올바른 적 ID를 반환하는지 확인
        테스트할 범위: get_enemy_id 메서드
        커버하는 함수 및 데이터: 적 ID 접근자 메서드
        기대되는 안정성: 정확한 적 ID 반환 보장
        """
        # Given - 테스트용 적 ID
        enemy_id = 'boss_final_stage'
        event = EnemyDeathEvent.create_from_id(enemy_id)

        # When - get_enemy_id 호출
        retrieved_id = event.get_enemy_id()

        # Then - 올바른 ID 반환 확인
        assert retrieved_id == enemy_id, (
            'get_enemy_id가 올바른 ID를 반환해야 함'
        )
        assert retrieved_id == event.enemy_entity_id, '내부 필드와 일치해야 함'

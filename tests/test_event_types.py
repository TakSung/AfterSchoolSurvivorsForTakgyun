"""
Unit tests for EventType IntEnum.

Tests the multi-layer structure, performance optimization features,
and Korean display names of the EventType enum.
"""

from src.core.events.event_types import EventType


class TestEventType:
    """Test class for EventType IntEnum functionality."""

    def test_이벤트_타입_값_및_순서_정확성_검증_성공_시나리오(self) -> None:
        """1. 이벤트 타입 값 및 순서 정확성 검증 (성공 시나리오)

        목적: EventType enum의 정수 값 및 카테고리별 순서 확인
        테스트할 범위: IntEnum 값 할당 및 카테고리 분류
        커버하는 함수 및 데이터: 각 이벤트 타입의 정수 값
        기대되는 안정성: 일관된 이벤트 타입 값 할당 보장
        """
        # Given & When & Then - Combat Events (0-19)
        assert EventType.ENEMY_DEATH == 0, '적 사망 이벤트는 0이어야 함'
        assert EventType.WEAPON_FIRED == 1, '무기 발사 이벤트는 1이어야 함'
        assert EventType.PROJECTILE_HIT == 2, '투사체 적중 이벤트는 2여야 함'
        assert EventType.PLAYER_DAMAGED == 3, (
            '플레이어 피해 이벤트는 3이어야 함'
        )
        assert EventType.ENEMY_SPAWNED == 4, '적 생성 이벤트는 4여야 함'

        # Item Events (20-39)
        assert EventType.ITEM_DROP == 20, '아이템 드롭 이벤트는 20이어야 함'
        assert EventType.ITEM_PICKUP == 21, '아이템 획득 이벤트는 21이어야 함'
        assert EventType.ITEM_SYNERGY_ACTIVATED == 22, (
            '아이템 시너지 활성화는 22여야 함'
        )

        # Experience Events (40-59)
        assert EventType.EXPERIENCE_GAIN == 40, (
            '경험치 획득 이벤트는 40이어야 함'
        )
        assert EventType.LEVEL_UP == 41, '레벨 업 이벤트는 41이어야 함'

        # Boss Events (60-79)
        assert EventType.BOSS_SPAWNED == 60, '보스 등장 이벤트는 60이어야 함'
        assert EventType.BOSS_PHASE_CHANGE == 61, (
            '보스 페이즈 변경은 61이어야 함'
        )
        assert EventType.BOSS_DEFEATED == 62, '보스 처치 이벤트는 62여야 함'

        # Game State Events (80-99)
        assert EventType.GAME_STARTED == 80, '게임 시작 이벤트는 80이어야 함'
        assert EventType.GAME_PAUSED == 81, '게임 일시정지는 81이어야 함'
        assert EventType.GAME_RESUMED == 82, '게임 재개 이벤트는 82여야 함'
        assert EventType.GAME_OVER == 83, '게임 오버 이벤트는 83이어야 함'

    def test_한국어_표시명_정확성_검증_성공_시나리오(self) -> None:
        """2. 한국어 표시명 정확성 검증 (성공 시나리오)

        목적: display_name 프로퍼티의 한국어 표시명 확인
        테스트할 범위: display_name 프로퍼티
        커버하는 함수 및 데이터: _display_names 딕셔너리
        기대되는 안정성: 정확한 한국어 UI 텍스트 제공 보장
        """
        # Given & When & Then - Combat Events
        assert EventType.ENEMY_DEATH.display_name == '적 사망', (
            '적 사망 표시명 확인'
        )
        assert EventType.WEAPON_FIRED.display_name == '무기 발사', (
            '무기 발사 표시명 확인'
        )
        assert EventType.PROJECTILE_HIT.display_name == '투사체 적중', (
            '투사체 적중 표시명 확인'
        )

        # Item Events
        assert EventType.ITEM_DROP.display_name == '아이템 드롭', (
            '아이템 드롭 표시명 확인'
        )
        assert EventType.ITEM_PICKUP.display_name == '아이템 획득', (
            '아이템 획득 표시명 확인'
        )
        assert (
            EventType.ITEM_SYNERGY_ACTIVATED.display_name
            == '아이템 시너지 활성화'
        ), '시너지 표시명 확인'

        # Experience Events
        assert EventType.EXPERIENCE_GAIN.display_name == '경험치 획득', (
            '경험치 획득 표시명 확인'
        )
        assert EventType.LEVEL_UP.display_name == '레벨 업', (
            '레벨 업 표시명 확인'
        )

        # Boss Events
        assert EventType.BOSS_SPAWNED.display_name == '보스 등장', (
            '보스 등장 표시명 확인'
        )
        assert EventType.BOSS_DEFEATED.display_name == '보스 처치', (
            '보스 처치 표시명 확인'
        )

        # Game State Events
        assert EventType.GAME_STARTED.display_name == '게임 시작', (
            '게임 시작 표시명 확인'
        )
        assert EventType.GAME_OVER.display_name == '게임 오버', (
            '게임 오버 표시명 확인'
        )

    def test_카테고리_분류_및_속성_검증_성공_시나리오(self) -> None:
        """3. 카테고리 분류 및 속성 검증 (성공 시나리오)

        목적: 카테고리별 이벤트 분류 및 is_* 속성 확인
        테스트할 범위: category 프로퍼티 및 is_* 메서드들
        커버하는 함수 및 데이터: 카테고리 분류 로직
        기대되는 안정성: 정확한 이벤트 카테고리 식별 보장
        """
        # Given & When & Then - Combat Events
        combat_event = EventType.WEAPON_FIRED
        assert combat_event.category == '전투', '전투 카테고리여야 함'
        assert combat_event.is_combat_event, '전투 이벤트로 분류되어야 함'
        assert not combat_event.is_item_event, '아이템 이벤트가 아니어야 함'
        assert not combat_event.is_boss_event, '보스 이벤트가 아니어야 함'

        # Item Events
        item_event = EventType.ITEM_PICKUP
        assert item_event.category == '아이템', '아이템 카테고리여야 함'
        assert item_event.is_item_event, '아이템 이벤트로 분류되어야 함'
        assert not item_event.is_combat_event, '전투 이벤트가 아니어야 함'

        # Experience Events
        exp_event = EventType.LEVEL_UP
        assert exp_event.category == '경험치', '경험치 카테고리여야 함'
        assert exp_event.is_experience_event, '경험치 이벤트로 분류되어야 함'
        assert not exp_event.is_game_state_event, (
            '게임 상태 이벤트가 아니어야 함'
        )

        # Boss Events
        boss_event = EventType.BOSS_SPAWNED
        assert boss_event.category == '보스', '보스 카테고리여야 함'
        assert boss_event.is_boss_event, '보스 이벤트로 분류되어야 함'
        assert not boss_event.is_combat_event, '일반 전투 이벤트가 아니어야 함'

        # Game State Events
        state_event = EventType.GAME_PAUSED
        assert state_event.category == '게임상태', '게임상태 카테고리여야 함'
        assert state_event.is_game_state_event, (
            '게임 상태 이벤트로 분류되어야 함'
        )
        assert not state_event.is_boss_event, '보스 이벤트가 아니어야 함'

    def test_카테고리별_이벤트_조회_기능_검증_성공_시나리오(self) -> None:
        """4. 카테고리별 이벤트 조회 기능 검증 (성공 시나리오)

        목적: get_events_by_category 클래스 메서드 기능 확인
        테스트할 범위: get_events_by_category 클래스 메서드
        커버하는 함수 및 데이터: 카테고리별 이벤트 필터링 로직
        기대되는 안정성: 정확한 카테고리별 이벤트 목록 제공 보장
        """
        # Given & When - 전투 카테고리 이벤트 조회
        combat_events = EventType.get_events_by_category('전투')

        # Then - 전투 이벤트 목록 확인
        expected_combat = [
            EventType.ENEMY_DEATH,
            EventType.WEAPON_FIRED,
            EventType.PROJECTILE_HIT,
            EventType.PLAYER_DAMAGED,
            EventType.ENEMY_SPAWNED,
        ]
        assert len(combat_events) == len(expected_combat), (
            '전투 이벤트 개수가 일치해야 함'
        )
        for event in expected_combat:
            assert event in combat_events, (
                f'{event.display_name}이 전투 카테고리에 있어야 함'
            )

        # When - 아이템 카테고리 이벤트 조회
        item_events = EventType.get_events_by_category('아이템')

        # Then - 아이템 이벤트 목록 확인
        expected_item = [
            EventType.ITEM_DROP,
            EventType.ITEM_PICKUP,
            EventType.ITEM_SYNERGY_ACTIVATED,
        ]
        assert len(item_events) == len(expected_item), (
            '아이템 이벤트 개수가 일치해야 함'
        )
        for event in expected_item:
            assert event in item_events, (
                f'{event.display_name}이 아이템 카테고리에 있어야 함'
            )

        # When - 존재하지 않는 카테고리 조회
        empty_events = EventType.get_events_by_category('존재하지않음')

        # Then - 빈 리스트 반환
        assert empty_events == [], (
            '존재하지 않는 카테고리는 빈 리스트를 반환해야 함'
        )

    def test_성능_최적화_IntEnum_값_비교_검증_성공_시나리오(self) -> None:
        """5. 성능 최적화 IntEnum 값 비교 검증 (성공 시나리오)

        목적: IntEnum의 정수 값 비교 성능 최적화 확인
        테스트할 범위: .value 속성을 통한 정수 비교
        커버하는 함수 및 데이터: IntEnum의 정수 값 접근
        기대되는 안정성: 게임 루프에서 빠른 이벤트 타입 비교 보장
        """
        # Given - 다양한 이벤트 타입
        combat_event = EventType.ENEMY_DEATH
        item_event = EventType.ITEM_DROP
        boss_event = EventType.BOSS_SPAWNED

        # When & Then - .value를 통한 빠른 정수 비교
        assert combat_event.value == 0, '전투 이벤트 값 비교'
        assert item_event.value == 20, '아이템 이벤트 값 비교'
        assert boss_event.value == 60, '보스 이벤트 값 비교'

        # 범위 기반 카테고리 판단 (성능 최적화)
        assert 0 <= combat_event.value <= 19, '전투 이벤트 범위 확인'
        assert 20 <= item_event.value <= 39, '아이템 이벤트 범위 확인'
        assert 60 <= boss_event.value <= 79, '보스 이벤트 범위 확인'

    def test_다층_구조_일관성_및_확장성_검증_성공_시나리오(self) -> None:
        """6. 다층 구조 일관성 및 확장성 검증 (성공 시나리오)

        목적: _display_names와 _categories 매핑의 일관성 확인
        테스트할 범위: 내부 매핑 테이블의 데이터 일관성
        커버하는 함수 및 데이터: _display_names, _categories 딕셔너리
        기대되는 안정성: 매핑 테이블 데이터 일관성 보장
        """
        # Given - 모든 이벤트 타입 순회
        all_event_types = list(EventType)

        # When & Then - 모든 이벤트의 표시명 존재 확인
        for event_type in all_event_types:
            display_name = event_type.display_name
            assert isinstance(display_name, str), '표시명은 문자열이어야 함'
            assert len(display_name) > 0, '표시명은 비어있지 않아야 함'
            assert not display_name.startswith('Unknown_'), (
                f'{event_type}의 표시명이 누락됨'
            )

        # 카테고리 인덱스 일관성 확인
        categories = [
            '전투',
            '아이템',
            '경험치',
            '보스',
            '게임상태',
            '카메라',
        ]  # 예상 카테고리 목록
        for event_type in all_event_types:
            category_index = event_type.value // 20
            assert category_index < len(categories), (
                f'{event_type}의 카테고리 인덱스가 범위 초과'
            )
            category = event_type.category
            assert category == categories[category_index], (
                '카테고리 매핑이 일치해야 함'
            )

    def test_이벤트_타입_문자열_표현_검증_성공_시나리오(self) -> None:
        """7. 이벤트 타입 문자열 표현 검증 (성공 시나리오)

        목적: EventType enum의 기본 문자열 표현 확인
        테스트할 범위: EventType의 __str__ 및 __repr__
        커버하는 함수 및 데이터: IntEnum의 기본 문자열 표현
        기대되는 안정성: 디버깅 시 명확한 이벤트 타입 식별 보장
        """
        # Given - 대표적인 이벤트 타입
        event_type = EventType.WEAPON_FIRED

        # When - 문자열 변환
        str_repr = str(event_type)

        # Then - 문자열 표현 확인 (IntEnum은 정수 값을 반환)
        assert str_repr == '1', 'IntEnum은 정수 값을 문자열로 표현해야 함'

        # enum name과 repr 접근 확인
        assert event_type.name == 'WEAPON_FIRED', 'enum name이 정확해야 함'
        assert hasattr(event_type, 'value'), 'value 속성이 존재해야 함'
        # repr은 더 자세한 정보를 포함
        repr_str = repr(event_type)
        assert (
            'EventType.WEAPON_FIRED' in repr_str or 'WEAPON_FIRED' in repr_str
        ), 'repr에는 이벤트 타입명이 포함되어야 함'

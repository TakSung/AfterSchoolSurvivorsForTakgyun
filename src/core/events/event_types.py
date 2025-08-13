"""
EventType IntEnum for performance-optimized event classification.

This module defines all event types used in the game's event system
with multi-layer structure for both performance optimization and
display purposes.
"""

from enum import IntEnum


class EventType(IntEnum):
    """
    Types of events that can occur in the game.

    This enum uses the multi-layer pattern for performance optimization:
    - IntEnum for fast integer comparisons in game loops
    - display_name property for Korean UI text
    - category grouping for future event filtering
    """

    # AI-NOTE : 2025-08-12 다층 구조 이벤트 타입 시스템 도입
    # - 이유: 성능 최적화와 UI 표시를 위한 이중 목적 지원 필요
    # - 요구사항: 게임 루프에서 빠른 비교, 한국어 표시명, 확장성
    # - 히스토리: 초기 게임 이벤트 타입 정의

    # Combat Events (0-19)
    ENEMY_DEATH = 0
    WEAPON_FIRED = 1
    PROJECTILE_HIT = 2
    PLAYER_DAMAGED = 3
    ENEMY_SPAWNED = 4

    # Item Events (20-39)
    ITEM_DROP = 20
    ITEM_PICKUP = 21
    ITEM_SYNERGY_ACTIVATED = 22

    # Experience Events (40-59)
    EXPERIENCE_GAIN = 40
    LEVEL_UP = 41

    # Boss Events (60-79)
    BOSS_SPAWNED = 60
    BOSS_PHASE_CHANGE = 61
    BOSS_DEFEATED = 62

    # Game State Events (80-99)
    GAME_STARTED = 80
    GAME_PAUSED = 81
    GAME_RESUMED = 82
    GAME_OVER = 83

    # Camera Events (100-119)
    CAMERA_OFFSET_CHANGED = 100
    CAMERA_TARGET_CHANGED = 101
    CAMERA_BOUNDS_CHANGED = 102

    @property
    def display_name(self) -> str:
        """Get the Korean display name for the event type."""
        display_names = {
            0: '적 사망',  # ENEMY_DEATH
            1: '무기 발사',  # WEAPON_FIRED
            2: '투사체 적중',  # PROJECTILE_HIT
            3: '플레이어 피해',  # PLAYER_DAMAGED
            4: '적 생성',  # ENEMY_SPAWNED
            20: '아이템 드롭',  # ITEM_DROP
            21: '아이템 획득',  # ITEM_PICKUP
            22: '아이템 시너지 활성화',  # ITEM_SYNERGY_ACTIVATED
            40: '경험치 획득',  # EXPERIENCE_GAIN
            41: '레벨 업',  # LEVEL_UP
            60: '보스 등장',  # BOSS_SPAWNED
            61: '보스 페이즈 변경',  # BOSS_PHASE_CHANGE
            62: '보스 처치',  # BOSS_DEFEATED
            80: '게임 시작',  # GAME_STARTED
            81: '게임 일시정지',  # GAME_PAUSED
            82: '게임 재개',  # GAME_RESUMED
            83: '게임 오버',  # GAME_OVER
            100: '카메라 오프셋 변경',  # CAMERA_OFFSET_CHANGED
            101: '카메라 대상 변경',  # CAMERA_TARGET_CHANGED
            102: '카메라 경계 변경',  # CAMERA_BOUNDS_CHANGED
        }
        return display_names.get(self.value, f'Unknown_{self.value}')

    @property
    def category(self) -> str:
        """Get the category this event belongs to."""
        categories = [
            '전투',  # 0-19: Combat Events
            '아이템',  # 20-39: Item Events
            '경험치',  # 40-59: Experience Events
            '보스',  # 60-79: Boss Events
            '게임상태',  # 80-99: Game State Events
            '카메라',  # 100-119: Camera Events
        ]
        category_index = self.value // 20
        return (
            categories[category_index]
            if category_index < len(categories)
            else 'Unknown'
        )

    @property
    def is_combat_event(self) -> bool:
        """Check if this is a combat-related event."""
        return 0 <= self.value <= 19

    @property
    def is_item_event(self) -> bool:
        """Check if this is an item-related event."""
        return 20 <= self.value <= 39

    @property
    def is_experience_event(self) -> bool:
        """Check if this is an experience-related event."""
        return 40 <= self.value <= 59

    @property
    def is_boss_event(self) -> bool:
        """Check if this is a boss-related event."""
        return 60 <= self.value <= 79

    @property
    def is_game_state_event(self) -> bool:
        """Check if this is a game state event."""
        return 80 <= self.value <= 99

    @property
    def is_camera_event(self) -> bool:
        """Check if this is a camera-related event."""
        return 100 <= self.value <= 119

    @classmethod
    def get_events_by_category(cls, category: str) -> list['EventType']:
        """
        Get all event types that belong to a specific category.

        Args:
            category: Category name to filter by.

        Returns:
            List of EventType values in the specified category.
        """
        categories = [
            '전투',  # 0-19: Combat Events
            '아이템',  # 20-39: Item Events
            '경험치',  # 40-59: Experience Events
            '보스',  # 60-79: Boss Events
            '게임상태',  # 80-99: Game State Events
            '카메라',  # 100-119: Camera Events
        ]

        category_index = None
        for i, cat in enumerate(categories):
            if cat == category:
                category_index = i
                break

        if category_index is None:
            return []

        start_value = category_index * 20
        end_value = start_value + 20

        return [
            event for event in cls if start_value <= event.value < end_value
        ]

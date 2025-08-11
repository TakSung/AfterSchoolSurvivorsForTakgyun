"""
PlayerComponent for identifying player entities.

This component serves as a tag to identify entities that represent the player,
enabling special handling in rendering and other systems.
"""

from dataclasses import dataclass

from ..core.component import Component


@dataclass
class PlayerComponent(Component):
    """
    Component that identifies an entity as the player.

    The PlayerComponent is a tag component used to identify player entities
    for special handling like center-screen rendering, input processing, etc.
    """

    # AI-NOTE : 2025-08-11 플레이어 식별자 태그 컴포넌트
    # - 이유: 렌더링 시스템에서 플레이어를 다른 엔티티와 구분하여 처리
    # - 요구사항: 플레이어는 항상 화면 중앙에 고정 렌더링되어야 함
    # - 히스토리: 일반 엔티티에서 특별한 플레이어 처리로 분리

    # 플레이어 고유 식별자 (선택사항)
    player_id: int = 0

    def validate(self) -> bool:
        """
        Validate player component data.

        Returns:
            True if player data is valid, False otherwise.
        """
        return isinstance(self.player_id, int) and self.player_id >= 0

    def is_main_player(self) -> bool:
        """
        Check if this is the main player (ID 0).

        Returns:
            True if this is the main player, False otherwise.
        """
        return self.player_id == 0

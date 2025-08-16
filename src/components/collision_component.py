"""
Collision component for ECS architecture.

Defines collision properties for entities including hitbox dimensions,
collision masks, and collision layers.
"""

from dataclasses import dataclass, field
from enum import IntEnum

from ..core.component import Component


class CollisionLayer(IntEnum):
    """
    Collision layers for organizing collision detection.

    Different layers can be used to control which entities
    can collide with each other.
    """

    PLAYER = 0
    ENEMY = 1
    PROJECTILE = 2
    ITEM = 3
    OBSTACLE = 4
    BOUNDARY = 5

    @property
    def display_name(self) -> str:
        """Get display name for the collision layer."""
        display_names = {
            CollisionLayer.PLAYER: '플레이어',
            CollisionLayer.ENEMY: '적',
            CollisionLayer.PROJECTILE: '투사체',
            CollisionLayer.ITEM: '아이템',
            CollisionLayer.OBSTACLE: '장애물',
            CollisionLayer.BOUNDARY: '경계',
        }
        return display_names[self]


@dataclass
class CollisionComponent(Component):
    """
    Component that defines collision properties for an entity.

    Contains hitbox dimensions, collision layers, and collision masks
    to control which entities can collide with each other.
    """

    width: float
    height: float
    layer: CollisionLayer = CollisionLayer.PLAYER
    collision_mask: set[CollisionLayer] = field(default_factory=set)
    is_trigger: bool = False
    is_solid: bool = True

    def __post_init__(self) -> None:
        """
        Initialize collision component after creation.

        Validates input parameters and sets up default collision mask
        if none is provided.
        """
        # AI-NOTE : 2025-01-11 충돌 컴포넌트 유효성 검증 및 기본값 설정
        # - 이유: 잘못된 충돌 박스 크기나 설정으로 인한 버그 방지
        # - 요구사항: 양수 크기, 적절한 기본 충돌 마스크 설정
        # - 히스토리: 기본 충돌 속성 정의 및 검증 로직 구현

        if self.width <= 0 or self.height <= 0:
            raise ValueError(
                f'Collision dimensions must be positive: '
                f'{self.width}x{self.height}'
            )

        # 기본 충돌 마스크 설정 (모든 레이어와 충돌 가능)
        if not self.collision_mask:
            self.collision_mask = set(CollisionLayer)

    def can_collide_with(self, other_layer: CollisionLayer) -> bool:
        """
        Check if this entity can collide with another layer.

        Args:
            other_layer: The collision layer to check against.

        Returns:
            True if collision is possible, False otherwise.
        """
        return other_layer in self.collision_mask

    def add_collision_layer(self, layer: CollisionLayer) -> None:
        """
        Add a layer to the collision mask.

        Args:
            layer: Collision layer to add to the mask.
        """
        self.collision_mask.add(layer)

    def remove_collision_layer(self, layer: CollisionLayer) -> None:
        """
        Remove a layer from the collision mask.

        Args:
            layer: Collision layer to remove from the mask.
        """
        self.collision_mask.discard(layer)

    def set_collision_layers(self, layers: set[CollisionLayer]) -> None:
        """
        Set the collision mask to a specific set of layers.

        Args:
            layers: Set of collision layers to use as the new mask.
        """
        self.collision_mask = layers.copy()

    def get_bounds(
        self, center_x: float, center_y: float
    ) -> tuple[float, float, float, float]:
        """
        Get the bounding box coordinates for this collision component.

        Args:
            center_x: X coordinate of the entity center.
            center_y: Y coordinate of the entity center.

        Returns:
            Tuple of (left, top, right, bottom) coordinates.
        """
        half_width = self.width / 2
        half_height = self.height / 2

        return (
            center_x - half_width,  # left
            center_y - half_height,  # top
            center_x + half_width,  # right
            center_y + half_height,  # bottom
        )

    def validate(self) -> bool:
        """
        Validate collision component data.

        Returns:
            True if all collision data is valid, False otherwise.
        """
        return (
            isinstance(self.width, int | float)
            and isinstance(self.height, int | float)
            and self.width > 0
            and self.height > 0
            and isinstance(self.layer, CollisionLayer)
            and isinstance(self.collision_mask, set)
            and all(
                isinstance(layer, CollisionLayer)
                for layer in self.collision_mask
            )
            and isinstance(self.is_trigger, bool)
            and isinstance(self.is_solid, bool)
        )

    def __str__(self) -> str:
        """String representation of the collision component."""
        trigger_text = ' (trigger)' if self.is_trigger else ''
        solid_text = ' (solid)' if self.is_solid else ' (non-solid)'
        return (
            f'CollisionComponent({self.width}x{self.height}, '
            f'layer={self.layer.display_name}, '
            f'mask={len(self.collision_mask)} layers'
            f'{trigger_text}{solid_text})'
        )

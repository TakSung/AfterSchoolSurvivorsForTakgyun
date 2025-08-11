"""
RenderComponent for storing visual rendering properties of entities.

This component contains all data needed to render an entity on screen,
including sprite, color, size, and layer information.
"""

from dataclasses import dataclass, field
from enum import IntEnum

import pygame

from ..core.component import Component


class RenderLayer(IntEnum):
    """Enumeration for render layer priorities."""

    BACKGROUND = 0
    GROUND = 10
    ENTITIES = 20
    PROJECTILES = 30
    EFFECTS = 40
    UI = 50

    @property
    def display_name(self) -> str:
        """Get display name for the render layer."""
        display_names = {
            RenderLayer.BACKGROUND: '배경',
            RenderLayer.GROUND: '지면',
            RenderLayer.ENTITIES: '엔티티',
            RenderLayer.PROJECTILES: '발사체',
            RenderLayer.EFFECTS: '이펙트',
            RenderLayer.UI: 'UI',
        }
        return display_names[self]


@dataclass
class RenderComponent(Component):
    """
    Component that stores visual rendering properties for entities.

    The RenderComponent contains all information needed to render an entity,
    including sprite image, color, size, visibility, and render layer.
    """

    # AI-NOTE : 2025-08-11 렌더링 데이터 구조 설계
    # - 이유: 엔티티별 다양한 렌더링 속성을 중앙 집중식으로 관리
    # - 요구사항: 스프라이트, 색상, 크기, 레이어 등 렌더링에 필요한 모든 정보
    # - 히스토리: 기본 렌더링에서 확장성 있는 컴포넌트 기반 시스템으로 발전

    # 스프라이트 이미지 (None이면 기본 사각형으로 렌더링)
    sprite: pygame.Surface | None = None

    # 기본 색상 (스프라이트가 없을 때 사용)
    color: tuple[int, int, int] = (255, 255, 255)

    # 렌더링 크기 (픽셀 단위)
    size: tuple[int, int] = (32, 32)

    # 가시성 제어
    visible: bool = True

    # 렌더 레이어 (깊이 정렬용)
    layer: RenderLayer = RenderLayer.ENTITIES

    # 투명도 (0-255)
    alpha: int = 255

    # AI-DEV : 렌더링 최적화를 위한 더티 플래그
    # - 문제: 매 프레임마다 모든 엔티티 렌더링으로 인한 성능 저하
    # - 해결책: 변경사항이 있을 때만 다시 렌더링하도록 더티 플래그 사용
    # - 주의사항: 플래그 관리를 위한 적절한 업데이트 로직 필요
    _dirty: bool = field(default=True, init=False)

    def validate(self) -> bool:
        """
        Validate render component data.

        Returns:
            True if all render data is valid, False otherwise.
        """
        # 색상 유효성 검사
        if (
            not isinstance(self.color, tuple)
            or len(self.color) != 3
            or not all(
                isinstance(c, int) and 0 <= c <= 255 for c in self.color
            )
        ):
            return False

        # 크기 유효성 검사
        if (
            not isinstance(self.size, tuple)
            or len(self.size) != 2
            or not all(isinstance(s, int) and s > 0 for s in self.size)
        ):
            return False

        # 투명도 유효성 검사
        if not isinstance(self.alpha, int) or not 0 <= self.alpha <= 255:
            return False

        # 레이어 유효성 검사
        if not isinstance(self.layer, RenderLayer):
            return False

        return True

    def set_sprite(self, sprite: pygame.Surface) -> None:
        """
        Set the sprite image and mark as dirty.

        Args:
            sprite: New sprite surface
        """
        self.sprite = sprite
        self._dirty = True

    def set_color(self, color: tuple[int, int, int]) -> None:
        """
        Set the color and mark as dirty.

        Args:
            color: RGB color tuple
        """
        self.color = color
        self._dirty = True

    def set_size(self, width: int, height: int) -> None:
        """
        Set the size and mark as dirty.

        Args:
            width: Width in pixels
            height: Height in pixels
        """
        self.size = (width, height)
        self._dirty = True

    def set_alpha(self, alpha: int) -> None:
        """
        Set the transparency and mark as dirty.

        Args:
            alpha: Alpha value (0-255)
        """
        self.alpha = max(0, min(255, alpha))
        self._dirty = True

    def set_layer(self, layer: RenderLayer) -> None:
        """
        Set the render layer and mark as dirty.

        Args:
            layer: New render layer
        """
        self.layer = layer
        self._dirty = True

    def set_visible(self, visible: bool) -> None:
        """
        Set visibility and mark as dirty.

        Args:
            visible: Visibility state
        """
        self.visible = visible
        self._dirty = True

    def is_dirty(self) -> bool:
        """
        Check if the component has been modified.

        Returns:
            True if component needs re-rendering, False otherwise.
        """
        return self._dirty

    def clear_dirty(self) -> None:
        """Clear the dirty flag after rendering."""
        self._dirty = False

    def get_effective_surface(self) -> pygame.Surface:
        """
        Get the surface to render (sprite or generated rectangle).

        Returns:
            Surface ready for rendering.
        """
        if self.sprite is not None:
            # 스프라이트가 있으면 스프라이트 사용
            surface = self.sprite.copy()
            if self.alpha < 255:
                surface.set_alpha(self.alpha)
            return surface
        else:
            # 스프라이트가 없으면 색상 사각형 생성
            surface = pygame.Surface(self.size)
            surface.fill(self.color)
            if self.alpha < 255:
                surface.set_alpha(self.alpha)
            return surface

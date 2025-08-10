from collections.abc import Callable
from enum import IntEnum
from typing import Any

import pygame

from ..core.coordinate_transformer import ICoordinateTransformer
from ..utils.vector2 import Vector2


class RenderLayer(IntEnum):
    BACKGROUND = 0
    GROUND = 10
    ENTITIES = 20
    PROJECTILES = 30
    EFFECTS = 40
    UI = 50

    @property
    def display_name(self) -> str:
        display_names = {
            RenderLayer.BACKGROUND: '배경',
            RenderLayer.GROUND: '지면',
            RenderLayer.ENTITIES: '엔티티',
            RenderLayer.PROJECTILES: '발사체',
            RenderLayer.EFFECTS: '이펙트',
            RenderLayer.UI: 'UI',
        }
        return display_names[self]


class RenderableSprite(pygame.sprite.Sprite):
    __slots__ = ('_layer', '_world_position')

    def __init__(self, layer: RenderLayer = RenderLayer.ENTITIES) -> None:
        super().__init__()
        self._layer = layer
        self._world_position = Vector2()
        self.image = pygame.Surface((1, 1))
        self.rect = self.image.get_rect()

    @property
    def layer(self) -> RenderLayer:
        return self._layer

    @layer.setter
    def layer(self, value: RenderLayer) -> None:
        self._layer = value

    @property
    def world_position(self) -> Vector2:
        return self._world_position

    @world_position.setter
    def world_position(self, position: Vector2) -> None:
        self._world_position = position

    def update_screen_position(self, screen_position: Vector2) -> None:
        self.rect.centerx = int(screen_position.x)
        self.rect.centery = int(screen_position.y)


class LayeredSpriteGroup:
    __slots__ = ('_all_sprites', '_groups', '_layers')

    def __init__(self) -> None:
        self._groups: dict[RenderLayer, pygame.sprite.Group] = {}
        self._all_sprites = pygame.sprite.Group()
        self._layers = sorted(RenderLayer)

        for layer in self._layers:
            self._groups[layer] = pygame.sprite.Group()

    def add_sprite(self, sprite: RenderableSprite) -> None:
        layer = sprite.layer
        self._groups[layer].add(sprite)
        self._all_sprites.add(sprite)

    def remove_sprite(self, sprite: RenderableSprite) -> None:
        layer = sprite.layer
        if sprite in self._groups[layer]:
            self._groups[layer].remove(sprite)
        self._all_sprites.remove(sprite)

    def move_sprite_to_layer(
        self, sprite: RenderableSprite, new_layer: RenderLayer
    ) -> None:
        old_layer = sprite.layer
        if sprite in self._groups[old_layer]:
            self._groups[old_layer].remove(sprite)

        sprite.layer = new_layer
        self._groups[new_layer].add(sprite)

    def get_sprites_in_layer(self, layer: RenderLayer) -> pygame.sprite.Group:
        return self._groups[layer]

    def get_all_sprites(self) -> pygame.sprite.Group:
        return self._all_sprites

    def clear_layer(self, layer: RenderLayer) -> None:
        sprites_to_remove = list(self._groups[layer].sprites())
        for sprite in sprites_to_remove:
            self.remove_sprite(sprite)

    def clear_all(self) -> None:
        for layer in self._layers:
            self._groups[layer].empty()
        self._all_sprites.empty()

    def get_layer_sprite_count(self, layer: RenderLayer) -> int:
        return len(self._groups[layer])

    def get_total_sprite_count(self) -> int:
        return len(self._all_sprites)

    def render_layer(
        self, surface: pygame.Surface, layer: RenderLayer
    ) -> None:
        self._groups[layer].draw(surface)

    def render_all_layers(self, surface: pygame.Surface) -> None:
        for layer in self._layers:
            self.render_layer(surface, layer)


class RenderSystem:
    __slots__ = (
        '_background_color',
        '_camera_transformer',
        '_dirty_rects',
        '_layered_sprites',
        '_post_render_callbacks',
        '_pre_render_callbacks',
        '_render_bounds',
        '_screen_size',
        '_surface',
        '_track_dirty_rects',
        '_update_callbacks',
    )

    def __init__(
        self,
        surface: pygame.Surface,
        camera_transformer: ICoordinateTransformer | None = None,
        background_color: tuple[int, int, int] = (0, 0, 0),
        track_dirty_rects: bool = False,
    ) -> None:
        self._surface = surface
        self._screen_size = Vector2(surface.get_width(), surface.get_height())
        self._camera_transformer = camera_transformer
        self._background_color = background_color
        self._track_dirty_rects = track_dirty_rects

        self._layered_sprites = LayeredSpriteGroup()
        self._update_callbacks: list[Callable[[], None]] = []
        self._pre_render_callbacks: list[Callable[[pygame.Surface], None]] = []
        self._post_render_callbacks: list[
            Callable[[pygame.Surface], None]
        ] = []

        self._dirty_rects: list[pygame.Rect] = []
        self._render_bounds = pygame.Rect(
            0, 0, int(self._screen_size.x), int(self._screen_size.y)
        )

    @property
    def surface(self) -> pygame.Surface:
        return self._surface

    @surface.setter
    def surface(self, value: pygame.Surface) -> None:
        self._surface = value
        self._screen_size = Vector2(value.get_width(), value.get_height())
        self._render_bounds = pygame.Rect(
            0, 0, int(self._screen_size.x), int(self._screen_size.y)
        )

    @property
    def screen_size(self) -> Vector2:
        return self._screen_size.copy()

    @property
    def background_color(self) -> tuple[int, int, int]:
        return self._background_color

    @background_color.setter
    def background_color(self, color: tuple[int, int, int]) -> None:
        self._background_color = color

    @property
    def camera_transformer(self) -> ICoordinateTransformer | None:
        return self._camera_transformer

    @camera_transformer.setter
    def camera_transformer(
        self, transformer: ICoordinateTransformer | None
    ) -> None:
        self._camera_transformer = transformer

    def add_sprite(self, sprite: RenderableSprite) -> None:
        self._layered_sprites.add_sprite(sprite)

    def remove_sprite(self, sprite: RenderableSprite) -> None:
        self._layered_sprites.remove_sprite(sprite)

    def move_sprite_to_layer(
        self, sprite: RenderableSprite, layer: RenderLayer
    ) -> None:
        self._layered_sprites.move_sprite_to_layer(sprite, layer)

    def clear_layer(self, layer: RenderLayer) -> None:
        self._layered_sprites.clear_layer(layer)

    def clear_all_sprites(self) -> None:
        self._layered_sprites.clear_all()

    def add_update_callback(self, callback: Callable[[], None]) -> None:
        if callback not in self._update_callbacks:
            self._update_callbacks.append(callback)

    def add_pre_render_callback(
        self, callback: Callable[[pygame.Surface], None]
    ) -> None:
        if callback not in self._pre_render_callbacks:
            self._pre_render_callbacks.append(callback)

    def add_post_render_callback(
        self, callback: Callable[[pygame.Surface], None]
    ) -> None:
        if callback not in self._post_render_callbacks:
            self._post_render_callbacks.append(callback)

    def remove_update_callback(self, callback: Callable[[], None]) -> None:
        if callback in self._update_callbacks:
            self._update_callbacks.remove(callback)

    def remove_pre_render_callback(
        self, callback: Callable[[pygame.Surface], None]
    ) -> None:
        if callback in self._pre_render_callbacks:
            self._pre_render_callbacks.remove(callback)

    def remove_post_render_callback(
        self, callback: Callable[[pygame.Surface], None]
    ) -> None:
        if callback in self._post_render_callbacks:
            self._post_render_callbacks.remove(callback)

    def update_sprite_positions(self) -> None:
        if not self._camera_transformer:
            return

        all_sprites = self._layered_sprites.get_all_sprites()

        for sprite in all_sprites:
            if isinstance(sprite, RenderableSprite):
                world_pos = sprite.world_position

                if self._camera_transformer.is_point_visible(world_pos):
                    screen_pos = self._camera_transformer.world_to_screen(
                        world_pos
                    )
                    sprite.update_screen_position(screen_pos)
                    sprite.visible = True
                else:
                    sprite.visible = False

    def update(self, delta_time: float) -> None:
        for callback in self._update_callbacks:
            callback()

        self.update_sprite_positions()

    def clear_screen(self) -> None:
        if self._track_dirty_rects:
            for rect in self._dirty_rects:
                self._surface.fill(self._background_color, rect)
            self._dirty_rects.clear()
        else:
            self._surface.fill(self._background_color)

    def render(self) -> list[pygame.Rect]:
        self.clear_screen()

        for callback in self._pre_render_callbacks:
            callback(self._surface)

        rendered_rects = []

        if self._track_dirty_rects:
            for layer in RenderLayer:
                group = self._layered_sprites.get_sprites_in_layer(layer)
                layer_rects = group.draw(self._surface)
                rendered_rects.extend(layer_rects)
                self._dirty_rects.extend(layer_rects)
        else:
            self._layered_sprites.render_all_layers(self._surface)

        for callback in self._post_render_callbacks:
            callback(self._surface)

        return rendered_rects

    def get_sprites_in_layer(self, layer: RenderLayer) -> pygame.sprite.Group:
        return self._layered_sprites.get_sprites_in_layer(layer)

    def get_all_sprites(self) -> pygame.sprite.Group:
        return self._layered_sprites.get_all_sprites()

    def get_visible_sprites_count(self) -> int:
        visible_count = 0
        all_sprites = self._layered_sprites.get_all_sprites()

        for sprite in all_sprites:
            if hasattr(sprite, 'visible') and getattr(sprite, 'visible', True):
                visible_count += 1
            else:
                visible_count += 1

        return visible_count

    def get_render_stats(self) -> dict[str, Any]:
        layer_stats = {}
        total_sprites = 0

        for layer in RenderLayer:
            count = self._layered_sprites.get_layer_sprite_count(layer)
            layer_stats[layer.display_name] = count
            total_sprites += count

        return {
            'total_sprites': total_sprites,
            'visible_sprites': self.get_visible_sprites_count(),
            'layer_counts': layer_stats,
            'screen_size': (
                int(self._screen_size.x),
                int(self._screen_size.y),
            ),
            'background_color': self._background_color,
            'dirty_rects_tracking': self._track_dirty_rects,
            'dirty_rects_count': len(self._dirty_rects),
            'update_callbacks_count': len(self._update_callbacks),
            'pre_render_callbacks_count': len(self._pre_render_callbacks),
            'post_render_callbacks_count': len(self._post_render_callbacks),
            'has_camera_transformer': self._camera_transformer is not None,
        }

    def set_render_bounds(self, bounds: pygame.Rect) -> None:
        self._render_bounds = bounds

    def get_render_bounds(self) -> pygame.Rect:
        return self._render_bounds.copy()

    def enable_dirty_rect_tracking(self, enabled: bool = True) -> None:
        self._track_dirty_rects = enabled
        if not enabled:
            self._dirty_rects.clear()

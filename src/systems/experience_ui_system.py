"""
Experience UI System for rendering experience bars and level information.

This system handles the rendering of experience-related UI elements
using ExperienceUIComponent and ExperienceComponent data.
"""

import pygame

from src.components.experience_component import ExperienceComponent
from src.components.experience_ui_component import ExperienceUIComponent
from src.components.player_component import PlayerComponent
from src.core.entity_manager import EntityManager
from src.core.system import System


class ExperienceUISystem(System):
    """
    System responsible for rendering experience UI elements.

    This system renders experience bars, level displays, and related
    UI elements for entities that have both ExperienceComponent and
    ExperienceUIComponent.
    """

    def __init__(self, surface: pygame.Surface, priority: int = 60) -> None:
        """
        Initialize the Experience UI System.

        Args:
            surface: The pygame surface to render on
            priority: System execution priority (higher numbers run later)
        """
        super().__init__(priority)
        self.surface = surface
        self._fonts: dict[int, pygame.font.Font] = {}
        self._font_cache_limit = 10

    def initialize(self) -> None:
        """Initialize the system."""
        super().initialize()

    def update(self, delta_time: float) -> None:
        """
        Update and render experience UI for all applicable entities.

        Args:
            delta_time: Time elapsed since last update in seconds
        """
        if not self.enabled:
            return

        # Get all entities with both experience and UI components
        entities_with_ui = self._entity_manager.get_entities_with_component(
            ExperienceUIComponent
        )

        for entity, ui_comp in entities_with_ui:
            exp_comp = self._entity_manager.get_component(
                entity, ExperienceComponent
            )
            if exp_comp is None:
                continue

            # Update animations
            ui_comp.update_animation(delta_time)

            # Check for level up to trigger animation
            if exp_comp.level > ui_comp.previous_level:
                ui_comp.trigger_level_up_animation(exp_comp.level)

            # Render the experience UI
            self._render_experience_ui(exp_comp, ui_comp)

    def _render_experience_ui(
        self, exp_comp: ExperienceComponent, ui_comp: ExperienceUIComponent
    ) -> None:
        """
        Render experience UI elements for a single entity.

        Args:
            exp_comp: The experience component with data to display
            ui_comp: The UI component with rendering configuration
        """
        # Render level text
        if ui_comp.show_level:
            self._render_level_text(exp_comp, ui_comp)

        # Render experience bar
        if ui_comp.show_experience_bar:
            self._render_experience_bar(exp_comp, ui_comp)

        # Render experience text over the bar
        if ui_comp.show_experience_text:
            self._render_experience_text(exp_comp, ui_comp)

    def _render_level_text(
        self, exp_comp: ExperienceComponent, ui_comp: ExperienceUIComponent
    ) -> None:
        """Render the level text display."""
        font = self._get_font(ui_comp.level_font_size)
        text = f'레벨: {exp_comp.level}'

        # Apply level-up flash effect to text color if active
        text_color = ui_comp.level_text_color
        if ui_comp.is_flashing:
            # Use flash color for text during level-up animation
            text_color = ui_comp.level_up_flash_color

        text_surface = font.render(text, True, text_color)
        position = ui_comp.get_level_text_position()
        self.surface.blit(text_surface, position)

    def _render_experience_bar(
        self, exp_comp: ExperienceComponent, ui_comp: ExperienceUIComponent
    ) -> None:
        """Render the experience progress bar."""
        bar_pos = ui_comp.get_bar_position()
        bar_rect = pygame.Rect(
            bar_pos[0], bar_pos[1], ui_comp.bar_width, ui_comp.bar_height
        )

        # Draw background
        pygame.draw.rect(self.surface, ui_comp.background_color, bar_rect)

        # Draw experience fill
        exp_ratio = exp_comp.get_exp_progress_ratio()
        fill_width = int(ui_comp.bar_width * exp_ratio)

        if fill_width > 0:
            fill_rect = pygame.Rect(
                bar_pos[0], bar_pos[1], fill_width, ui_comp.bar_height
            )
            fill_color = ui_comp.get_current_fill_color()
            pygame.draw.rect(self.surface, fill_color, fill_rect)

        # Draw border
        pygame.draw.rect(self.surface, ui_comp.border_color, bar_rect, 1)

    def _render_experience_text(
        self, exp_comp: ExperienceComponent, ui_comp: ExperienceUIComponent
    ) -> None:
        """Render experience text over the progress bar."""
        font = self._get_font(ui_comp.exp_text_font_size)

        # Determine text content
        if ui_comp.show_progress_percentage:
            progress = exp_comp.get_exp_progress_ratio() * 100
            text = f'{progress:.1f}%'
        else:
            current_exp = exp_comp.current_exp
            exp_to_next = exp_comp.get_exp_to_next_level()
            text = f'EXP: {current_exp}/{exp_to_next}'

        text_surface = font.render(text, True, ui_comp.text_color)
        position = ui_comp.get_exp_text_position()
        self.surface.blit(text_surface, position)

    def _get_font(self, size: int) -> pygame.font.Font:
        """
        Get or create a font of the specified size.

        Args:
            size: Font size in pixels

        Returns:
            pygame.font.Font object
        """
        if size not in self._fonts:
            # Manage cache size
            if len(self._fonts) >= self._font_cache_limit:
                # Remove oldest font (simple cleanup)
                oldest_size = next(iter(self._fonts))
                del self._fonts[oldest_size]

            self._fonts[size] = pygame.font.Font(None, size)

        return self._fonts[size]

    def get_system_name(self) -> str:
        """Get the system name for identification."""
        return 'ExperienceUISystem'

    def cleanup(self) -> None:
        """Clean up system resources."""
        self._fonts.clear()
        super().cleanup()

    def render_player_experience_panel(
        self,
        entity_manager: EntityManager,
        position: tuple[int, int] = (10, 10),
        panel_width: int = 350,
        panel_height: int = 120,
    ) -> None:
        """
        Render a complete experience panel for the player.

        This is a convenience method that renders a styled panel containing
        level, experience bar, and additional stats for the player.

        Args:
            entity_manager: Entity manager to find player
            position: Top-left position of the panel
            panel_width: Width of the panel background
            panel_height: Height of the panel background
        """
        # Find player entity
        player_entities = entity_manager.get_entities_with_component(
            PlayerComponent
        )
        if not player_entities:
            return

        player_entity, _ = player_entities[0]
        exp_comp = entity_manager.get_component(
            player_entity, ExperienceComponent
        )
        if not exp_comp:
            return

        # Draw panel background
        panel_rect = pygame.Rect(
            position[0], position[1], panel_width, panel_height
        )
        panel_color = (64, 64, 64)  # Dark gray
        border_color = (255, 255, 255)  # White

        # Create semi-transparent panel
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(200)
        panel_surface.fill(panel_color)
        self.surface.blit(panel_surface, panel_rect)
        pygame.draw.rect(self.surface, border_color, panel_rect, 2)

        # Render level text
        level_font = self._get_font(24)
        level_text = level_font.render(
            f'레벨: {exp_comp.level}', True, (255, 255, 255)
        )
        self.surface.blit(level_text, (position[0] + 20, position[1] + 20))

        # Render experience bar
        bar_y = position[1] + 50
        bar_rect = pygame.Rect(position[0] + 20, bar_y, panel_width - 40, 20)

        # Background
        pygame.draw.rect(self.surface, (80, 80, 80), bar_rect)

        # Fill
        exp_ratio = exp_comp.get_exp_progress_ratio()
        fill_width = int((panel_width - 40) * exp_ratio)
        if fill_width > 0:
            fill_rect = pygame.Rect(position[0] + 20, bar_y, fill_width, 20)
            pygame.draw.rect(self.surface, (255, 255, 0), fill_rect)

        # Border
        pygame.draw.rect(self.surface, (255, 255, 255), bar_rect, 2)

        # Experience text
        exp_font = self._get_font(18)
        exp_text = (
            f'EXP: {exp_comp.current_exp}/{exp_comp.get_exp_to_next_level()}'
        )
        exp_surface = exp_font.render(exp_text, True, (255, 255, 255))
        self.surface.blit(exp_surface, (position[0] + 22, bar_y + 2))

        # Total experience earned
        total_font = self._get_font(16)
        total_text = f'총 경험치: {exp_comp.total_exp_earned}'
        total_surface = total_font.render(total_text, True, (200, 200, 255))
        self.surface.blit(total_surface, (position[0] + 20, position[1] + 80))

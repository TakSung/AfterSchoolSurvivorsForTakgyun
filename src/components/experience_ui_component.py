"""
Experience UI Component for rendering experience bars and level information.

This component handles the visual representation of experience and level data
with customizable styling and layout options.
"""

from dataclasses import dataclass, field

from src.core.component import Component


@dataclass
class ExperienceUIComponent(Component):
    """
    UI component for rendering experience bars, levels, and related info.

    This component provides configuration for how experience information
    should be visually displayed in the game UI.
    """

    # Display settings
    show_level: bool = True
    show_experience_bar: bool = True
    show_experience_text: bool = True
    show_progress_percentage: bool = False

    # Layout configuration
    ui_position: tuple[int, int] = (20, 20)  # (x, y) screen position
    bar_width: int = 280
    bar_height: int = 16
    level_text_offset: tuple[int, int] = (0, -30)  # Relative to ui_position
    exp_text_offset: tuple[int, int] = (2, 2)  # Relative to bar position

    # Visual styling
    background_color: tuple[int, int, int] = (80, 80, 80)
    fill_color: tuple[int, int, int] = (255, 255, 0)  # Yellow
    border_color: tuple[int, int, int] = (255, 255, 255)  # White
    text_color: tuple[int, int, int] = (255, 255, 255)  # White
    level_text_color: tuple[int, int, int] = (255, 255, 255)  # White

    # Font settings
    level_font_size: int = 24
    exp_text_font_size: int = 16

    # Animation settings
    animate_level_up: bool = True
    level_up_flash_duration: float = 1.0  # seconds
    level_up_flash_color: tuple[int, int, int] = (255, 255, 100)

    # Internal animation state
    level_up_flash_timer: float = field(default=0.0, init=False)
    is_flashing: bool = field(default=False, init=False)
    previous_level: int = field(default=1, init=False)

    def trigger_level_up_animation(self, new_level: int) -> None:
        """
        Trigger level-up animation effects.

        Args:
            new_level: The new level that was reached
        """
        if self.animate_level_up and new_level > self.previous_level:
            self.is_flashing = True
            self.level_up_flash_timer = self.level_up_flash_duration
            self.previous_level = new_level

    def update_animation(self, delta_time: float) -> None:
        """
        Update animation timers and states.

        Args:
            delta_time: Time elapsed since last update in seconds
        """
        if self.is_flashing:
            self.level_up_flash_timer -= delta_time
            if self.level_up_flash_timer <= 0:
                self.is_flashing = False
                self.level_up_flash_timer = 0.0

    def get_current_fill_color(self) -> tuple[int, int, int]:
        """
        Get the current fill color, considering animation effects.

        Returns:
            Current color tuple for the experience bar fill
        """
        if self.is_flashing and int(self.level_up_flash_timer * 8) % 2:
            # Flash effect: alternate between normal and flash color
            return self.level_up_flash_color

        return self.fill_color

    def get_level_text_position(self) -> tuple[int, int]:
        """Get the absolute position for level text rendering."""
        return (
            self.ui_position[0] + self.level_text_offset[0],
            self.ui_position[1] + self.level_text_offset[1],
        )

    def get_bar_position(self) -> tuple[int, int]:
        """Get the absolute position for experience bar rendering."""
        return self.ui_position

    def get_exp_text_position(self) -> tuple[int, int]:
        """Get the absolute position for experience text rendering."""
        bar_pos = self.get_bar_position()
        return (
            bar_pos[0] + self.exp_text_offset[0],
            bar_pos[1] + self.exp_text_offset[1],
        )

    def set_position(self, x: int, y: int) -> None:
        """
        Set the UI position for the experience display.

        Args:
            x: X coordinate in screen space
            y: Y coordinate in screen space
        """
        self.ui_position = (x, y)

    def set_bar_size(self, width: int, height: int) -> None:
        """
        Set the size of the experience bar.

        Args:
            width: Bar width in pixels
            height: Bar height in pixels
        """
        self.bar_width = width
        self.bar_height = height

    def set_colors(
        self,
        background: tuple[int, int, int] | None = None,
        fill: tuple[int, int, int] | None = None,
        border: tuple[int, int, int] | None = None,
        text: tuple[int, int, int] | None = None,
    ) -> None:
        """
        Set UI colors for the experience display.

        Args:
            background: Background color for the experience bar
            fill: Fill color for the experience progress
            border: Border color for the experience bar
            text: Text color for experience text
        """
        if background is not None:
            self.background_color = background
        if fill is not None:
            self.fill_color = fill
        if border is not None:
            self.border_color = border
        if text is not None:
            self.text_color = text

    def validate(self) -> bool:
        """
        Validate experience UI component data.

        Returns:
            True if all UI data is valid, False otherwise.
        """

        def is_valid_color(color: tuple[int, int, int]) -> bool:
            return (
                isinstance(color, tuple)
                and len(color) == 3
                and all(isinstance(c, int) and 0 <= c <= 255 for c in color)
            )

        def is_valid_position(pos: tuple[int, int]) -> bool:
            return (
                isinstance(pos, tuple)
                and len(pos) == 2
                and all(isinstance(p, int) for p in pos)
            )

        return (
            isinstance(self.show_level, bool)
            and isinstance(self.show_experience_bar, bool)
            and isinstance(self.show_experience_text, bool)
            and isinstance(self.show_progress_percentage, bool)
            and is_valid_position(self.ui_position)
            and isinstance(self.bar_width, int)
            and isinstance(self.bar_height, int)
            and self.bar_width > 0
            and self.bar_height > 0
            and is_valid_position(self.level_text_offset)
            and is_valid_position(self.exp_text_offset)
            and is_valid_color(self.background_color)
            and is_valid_color(self.fill_color)
            and is_valid_color(self.border_color)
            and is_valid_color(self.text_color)
            and is_valid_color(self.level_text_color)
            and isinstance(self.level_font_size, int)
            and isinstance(self.exp_text_font_size, int)
            and self.level_font_size > 0
            and self.exp_text_font_size > 0
            and isinstance(self.animate_level_up, bool)
            and isinstance(self.level_up_flash_duration, int | float)
            and self.level_up_flash_duration >= 0
            and is_valid_color(self.level_up_flash_color)
            and isinstance(self.level_up_flash_timer, int | float)
            and isinstance(self.is_flashing, bool)
            and isinstance(self.previous_level, int)
            and self.previous_level >= 0
        )

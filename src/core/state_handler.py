from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from src.core.game_state_manager import GameState, GameStateManager


class IStateHandler(ABC):
    @abstractmethod
    def handle_input(self, event: Any) -> bool:
        pass

    @abstractmethod
    def handle_rendering(self, renderer: Any) -> None:
        pass

    @abstractmethod
    def update(self, delta_time: float) -> None:
        pass


class StateDispatcher:
    __slots__ = (
        '_handlers',
        '_input_processors',
        '_render_processors',
        '_state_manager',
        '_update_processors',
    )

    def __init__(self, state_manager: GameStateManager) -> None:
        self._state_manager = state_manager
        self._handlers: dict[GameState, IStateHandler] = {}

        self._input_processors: dict[
            GameState, list[Callable[[Any], bool]]
        ] = {
            GameState.RUNNING: [],
            GameState.PAUSED: [],
            GameState.STOPPED: [],
        }

        self._render_processors: dict[
            GameState, list[Callable[[Any], None]]
        ] = {
            GameState.RUNNING: [],
            GameState.PAUSED: [],
            GameState.STOPPED: [],
        }

        self._update_processors: dict[
            GameState, list[Callable[[float], None]]
        ] = {
            GameState.RUNNING: [],
            GameState.PAUSED: [],
            GameState.STOPPED: [],
        }

    def register_handler(
        self, state: GameState, handler: IStateHandler
    ) -> None:
        self._handlers[state] = handler

    def unregister_handler(self, state: GameState) -> None:
        if state in self._handlers:
            del self._handlers[state]

    def add_input_processor(
        self, state: GameState, processor: Callable[[Any], bool]
    ) -> None:
        if processor not in self._input_processors[state]:
            self._input_processors[state].append(processor)

    def remove_input_processor(
        self, state: GameState, processor: Callable[[Any], bool]
    ) -> None:
        if processor in self._input_processors[state]:
            self._input_processors[state].remove(processor)

    def add_render_processor(
        self, state: GameState, processor: Callable[[Any], None]
    ) -> None:
        if processor not in self._render_processors[state]:
            self._render_processors[state].append(processor)

    def remove_render_processor(
        self, state: GameState, processor: Callable[[Any], None]
    ) -> None:
        if processor in self._render_processors[state]:
            self._render_processors[state].remove(processor)

    def add_update_processor(
        self, state: GameState, processor: Callable[[float], None]
    ) -> None:
        if processor not in self._update_processors[state]:
            self._update_processors[state].append(processor)

    def remove_update_processor(
        self, state: GameState, processor: Callable[[float], None]
    ) -> None:
        if processor in self._update_processors[state]:
            self._update_processors[state].remove(processor)

    def handle_input(self, event: Any) -> bool:
        current_state = self._state_manager.current_state

        # Try handler first
        if current_state in self._handlers:
            handler = self._handlers[current_state]
            try:
                if handler.handle_input(event):
                    return True
            except Exception:
                pass  # Log error in real implementation

        # Try processors
        for processor in self._input_processors[current_state]:
            try:
                if processor(event):
                    return True
            except Exception:
                pass  # Log error in real implementation

        return False

    def handle_rendering(self, renderer: Any) -> None:
        current_state = self._state_manager.current_state

        # Try handler first
        if current_state in self._handlers:
            handler = self._handlers[current_state]
            try:
                handler.handle_rendering(renderer)
            except Exception:
                pass  # Log error in real implementation

        # Try processors
        for processor in self._render_processors[current_state]:
            try:
                processor(renderer)
            except Exception:
                pass  # Log error in real implementation

    def update(self, delta_time: float) -> None:
        current_state = self._state_manager.current_state

        # Only update when running (pause logic can be customized)
        if current_state != GameState.RUNNING:
            return

        # Try handler first
        if current_state in self._handlers:
            handler = self._handlers[current_state]
            try:
                handler.update(delta_time)
            except Exception:
                pass  # Log error in real implementation

        # Try processors
        for processor in self._update_processors[current_state]:
            try:
                processor(delta_time)
            except Exception:
                pass  # Log error in real implementation

    def clear_all_processors(self) -> None:
        for processors_dict in [
            self._input_processors,
            self._render_processors,
            self._update_processors,
        ]:
            for processors in processors_dict.values():
                processors.clear()

    def clear_state_processors(self, state: GameState) -> None:
        self._input_processors[state].clear()
        self._render_processors[state].clear()
        self._update_processors[state].clear()


class DefaultGameStateHandler(IStateHandler):
    def __init__(self, state_manager: GameStateManager) -> None:
        self._state_manager = state_manager

    def handle_input(self, event: Any) -> bool:
        if hasattr(event, 'key'):
            input_config = self._state_manager.get_input_config()
            key_bindings = input_config.get('keyboard_bindings', {})

            key_name = getattr(event, 'key', '')

            if key_name == key_bindings.get('pause', 'p'):
                return self._state_manager.toggle_pause()
            elif key_name == key_bindings.get('quit', 'escape'):
                return self._state_manager.stop()

        return False

    def handle_rendering(self, renderer: Any) -> None:
        if self._state_manager.is_paused():
            self._render_pause_overlay(renderer)

    def update(self, delta_time: float) -> None:
        pass

    def _render_pause_overlay(self, renderer: Any) -> None:
        pass

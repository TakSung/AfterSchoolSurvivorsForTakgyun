import json
import threading
from collections.abc import Callable
from enum import IntEnum
from pathlib import Path
from typing import Any


class GameState(IntEnum):
    RUNNING = 0
    PAUSED = 1
    STOPPED = 2

    @property
    def display_name(self) -> str:
        display_names = {
            GameState.RUNNING: '실행 중',
            GameState.PAUSED: '일시정지',
            GameState.STOPPED: '정지됨',
        }
        return display_names[self]


class GameStateManager:
    __slots__ = (
        '_auto_save',
        '_config_data',
        '_config_lock',
        '_config_path',
        '_current_state',
        '_previous_state',
        '_state_callbacks',
        '_transition_callbacks',
    )

    def __init__(
        self, config_path: str | Path = 'config.json', auto_save: bool = True
    ) -> None:
        self._current_state = GameState.STOPPED
        self._previous_state = GameState.STOPPED
        self._state_callbacks: dict[GameState, list[Callable[[], None]]] = {
            GameState.RUNNING: [],
            GameState.PAUSED: [],
            GameState.STOPPED: [],
        }
        self._transition_callbacks: list[
            Callable[[GameState, GameState], None]
        ] = []

        self._config_path = Path(config_path)
        self._config_data: dict[str, Any] = {}
        self._config_lock = threading.RLock()
        self._auto_save = auto_save

        # Load default configuration
        self._load_default_config()

        # Try to load existing config file
        if self._config_path.exists():
            self.load_config()

    def _load_default_config(self) -> None:
        default_config = {
            'display': {
                'width': 1280,
                'height': 720,
                'fullscreen': False,
                'vsync': True,
                'fps_target': 60,
            },
            'audio': {
                'master_volume': 1.0,
                'music_volume': 0.8,
                'sfx_volume': 1.0,
                'muted': False,
            },
            'input': {
                'mouse_sensitivity': 1.0,
                'keyboard_bindings': {
                    'pause': 'p',
                    'quit': 'escape',
                    'fullscreen_toggle': 'f11',
                },
            },
            'gameplay': {
                'difficulty': 'normal',
                'auto_save_interval': 300,
                'show_fps': False,
            },
        }

        with self._config_lock:
            self._config_data = default_config.copy()

    @property
    def current_state(self) -> GameState:
        return self._current_state

    @property
    def previous_state(self) -> GameState:
        return self._previous_state

    def is_running(self) -> bool:
        return self._current_state == GameState.RUNNING

    def is_paused(self) -> bool:
        return self._current_state == GameState.PAUSED

    def is_stopped(self) -> bool:
        return self._current_state == GameState.STOPPED

    def can_transition_to(self, new_state: GameState) -> bool:
        valid_transitions = {
            GameState.STOPPED: [GameState.RUNNING],
            GameState.RUNNING: [
                GameState.PAUSED
            ],  # Removed STOPPED for stricter rules
            GameState.PAUSED: [GameState.RUNNING, GameState.STOPPED],
        }
        return new_state in valid_transitions.get(self._current_state, [])

    def transition_to(self, new_state: GameState) -> bool:
        if not self.can_transition_to(new_state):
            return False

        old_state = self._current_state
        self._previous_state = old_state
        self._current_state = new_state

        # Call transition callbacks
        for callback in self._transition_callbacks:
            try:
                callback(old_state, new_state)
            except Exception:
                pass  # Log error in real implementation

        # Call state-specific callbacks
        for callback in self._state_callbacks[new_state]:
            try:
                callback()
            except Exception:
                pass  # Log error in real implementation

        return True

    def start(self) -> bool:
        return self.transition_to(GameState.RUNNING)

    def pause(self) -> bool:
        return self.transition_to(GameState.PAUSED)

    def resume(self) -> bool:
        if self._current_state == GameState.PAUSED:
            return self.transition_to(GameState.RUNNING)
        return False

    def stop(self) -> bool:
        # First try to pause if running, then stop
        if self._current_state == GameState.RUNNING:
            if self.transition_to(GameState.PAUSED):
                return self.transition_to(GameState.STOPPED)
            return False
        return self.transition_to(GameState.STOPPED)

    def toggle_pause(self) -> bool:
        if self._current_state == GameState.RUNNING:
            return self.pause()
        elif self._current_state == GameState.PAUSED:
            return self.resume()
        return False

    def add_state_callback(
        self, state: GameState, callback: Callable[[], None]
    ) -> None:
        if callback not in self._state_callbacks[state]:
            self._state_callbacks[state].append(callback)

    def remove_state_callback(
        self, state: GameState, callback: Callable[[], None]
    ) -> None:
        if callback in self._state_callbacks[state]:
            self._state_callbacks[state].remove(callback)

    def add_transition_callback(
        self, callback: Callable[[GameState, GameState], None]
    ) -> None:
        if callback not in self._transition_callbacks:
            self._transition_callbacks.append(callback)

    def remove_transition_callback(
        self, callback: Callable[[GameState, GameState], None]
    ) -> None:
        if callback in self._transition_callbacks:
            self._transition_callbacks.remove(callback)

    def clear_callbacks(self) -> None:
        for callbacks in self._state_callbacks.values():
            callbacks.clear()
        self._transition_callbacks.clear()

    def get_config(self, key: str, default: Any = None) -> Any:
        with self._config_lock:
            keys = key.split('.')
            value = self._config_data

            try:
                for k in keys:
                    value = value[k]
                return value
            except (KeyError, TypeError):
                return default

    def set_config(self, key: str, value: Any) -> None:
        with self._config_lock:
            keys = key.split('.')
            config = self._config_data

            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]

            # Set the final key
            config[keys[-1]] = value

            if self._auto_save:
                self._save_config_async()

    def load_config(self) -> bool:
        try:
            with self._config_lock:
                if self._config_path.exists():
                    with open(self._config_path, encoding='utf-8') as f:
                        loaded_data = json.load(f)

                    # Merge loaded data into defaults to preserve all keys
                    self._config_data = self._merge_configs(
                        self._config_data, loaded_data
                    )
                    return True
        except (json.JSONDecodeError, OSError, ValueError):
            return False
        return False

    def save_config(self) -> bool:
        try:
            with self._config_lock:
                # Ensure parent directory exists
                self._config_path.parent.mkdir(parents=True, exist_ok=True)

                with open(self._config_path, 'w', encoding='utf-8') as f:
                    json.dump(
                        self._config_data, f, indent=2, ensure_ascii=False
                    )
                return True
        except (OSError, ValueError):
            return False

    def _save_config_async(self) -> None:
        def _save() -> None:
            self.save_config()

        thread = threading.Thread(target=_save, daemon=True)
        thread.start()

    def _merge_config(
        self, source: dict[str, Any], target: dict[str, Any]
    ) -> None:
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                self._merge_config(value, target[key])
            else:
                target[key] = value

    def _merge_configs(
        self, base: dict[str, Any], override: dict[str, Any]
    ) -> dict[str, Any]:
        import copy

        result = copy.deepcopy(base)
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    def get_display_config(self) -> dict[str, Any]:
        return self.get_config('display', {})

    def get_audio_config(self) -> dict[str, Any]:
        return self.get_config('audio', {})

    def get_input_config(self) -> dict[str, Any]:
        return self.get_config('input', {})

    def get_gameplay_config(self) -> dict[str, Any]:
        return self.get_config('gameplay', {})

    def update_display_config(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            self.set_config(f'display.{key}', value)

    def update_audio_config(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            self.set_config(f'audio.{key}', value)

    def update_input_config(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            self.set_config(f'input.{key}', value)

    def update_gameplay_config(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            self.set_config(f'gameplay.{key}', value)

    def reset_to_defaults(self) -> None:
        with self._config_lock:
            self._load_default_config()
            if self._auto_save:
                self._save_config_async()

    def get_state_info(self) -> dict[str, Any]:
        return {
            'current_state': self._current_state.display_name,
            'previous_state': self._previous_state.display_name,
            'state_callbacks_count': {
                state.display_name: len(callbacks)
                for state, callbacks in self._state_callbacks.items()
            },
            'transition_callbacks_count': len(self._transition_callbacks),
            'config_path': str(self._config_path),
            'auto_save': self._auto_save,
        }

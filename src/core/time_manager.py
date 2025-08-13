import time
from collections.abc import Callable
from enum import IntEnum
from typing import Any


class TimeMode(IntEnum):
    FIXED_TIMESTEP = 0
    VARIABLE_TIMESTEP = 1

    @property
    def display_name(self) -> str:
        display_names = {
            TimeMode.FIXED_TIMESTEP: '고정 시간 간격',
            TimeMode.VARIABLE_TIMESTEP: '가변 시간 간격',
        }
        return display_names[self]


class TimeManager:
    __slots__ = (
        '_accumulated_time',
        '_current_time',
        '_delta_time',
        '_fixed_timestep',
        '_last_frame_time',
        '_max_frame_time',
        '_time_mode',
        '_time_scale',
        '_total_game_time',
        '_update_callbacks',
    )

    def __init__(
        self,
        time_mode: TimeMode = TimeMode.VARIABLE_TIMESTEP,
        fixed_timestep: float = 1.0 / 60.0,
        max_frame_time: float = 1.0 / 20.0,
    ) -> None:
        self._time_mode = time_mode
        self._fixed_timestep = max(0.001, fixed_timestep)
        self._max_frame_time = max(0.001, max_frame_time)

        self._time_scale = 1.0
        self._delta_time = 0.0
        self._accumulated_time = 0.0
        self._total_game_time = 0.0

        self._current_time = time.perf_counter()
        self._last_frame_time = self._current_time

        self._update_callbacks: list[Callable[[float], None]] = []

    @property
    def time_mode(self) -> TimeMode:
        return self._time_mode

    @time_mode.setter
    def time_mode(self, mode: TimeMode) -> None:
        self._time_mode = mode
        self._accumulated_time = 0.0

    @property
    def fixed_timestep(self) -> float:
        return self._fixed_timestep

    @fixed_timestep.setter
    def fixed_timestep(self, timestep: float) -> None:
        self._fixed_timestep = max(0.001, timestep)

    @property
    def max_frame_time(self) -> float:
        return self._max_frame_time

    @max_frame_time.setter
    def max_frame_time(self, max_time: float) -> None:
        self._max_frame_time = max(0.001, max_time)

    @property
    def time_scale(self) -> float:
        return self._time_scale

    @time_scale.setter
    def time_scale(self, scale: float) -> None:
        self._time_scale = max(0.0, scale)

    @property
    def delta_time(self) -> float:
        return self._delta_time

    @property
    def unscaled_delta_time(self) -> float:
        return self._delta_time / max(0.001, self._time_scale)

    @property
    def total_game_time(self) -> float:
        return self._total_game_time

    @property
    def is_paused(self) -> bool:
        return self._time_scale == 0.0

    def pause(self) -> None:
        self._time_scale = 0.0

    def resume(self, scale: float = 1.0) -> None:
        self._time_scale = max(0.0, scale)

    def set_slow_motion(self, scale: float = 0.5) -> None:
        self._time_scale = max(0.0, min(1.0, scale))

    def reset_time_scale(self) -> None:
        self._time_scale = 1.0

    def add_update_callback(self, callback: Callable[[float], None]) -> None:
        if callback not in self._update_callbacks:
            self._update_callbacks.append(callback)

    def remove_update_callback(
        self, callback: Callable[[float], None]
    ) -> None:
        if callback in self._update_callbacks:
            self._update_callbacks.remove(callback)

    def clear_update_callbacks(self) -> None:
        self._update_callbacks.clear()

    def update(self, raw_delta_time: float | None = None) -> int:
        if raw_delta_time is None:
            current_time = time.perf_counter()
            raw_delta_time = current_time - self._last_frame_time
            self._last_frame_time = current_time

        raw_delta_time = min(raw_delta_time, self._max_frame_time)
        scaled_delta_time = raw_delta_time * self._time_scale

        if self._time_mode == TimeMode.VARIABLE_TIMESTEP:
            return self._update_variable_timestep(scaled_delta_time)
        else:
            return self._update_fixed_timestep(scaled_delta_time)

    def _update_variable_timestep(self, delta_time: float) -> int:
        self._delta_time = delta_time
        self._total_game_time += delta_time

        for callback in self._update_callbacks:
            callback(delta_time)

        return 1

    def _update_fixed_timestep(self, delta_time: float) -> int:
        self._accumulated_time += delta_time
        update_count = 0

        while self._accumulated_time >= self._fixed_timestep:
            self._delta_time = self._fixed_timestep
            self._total_game_time += self._fixed_timestep
            self._accumulated_time -= self._fixed_timestep

            for callback in self._update_callbacks:
                callback(self._fixed_timestep)

            update_count += 1

            if update_count >= 10:
                self._accumulated_time = 0.0
                break

        return update_count

    def get_interpolation_factor(self) -> float:
        if self._time_mode == TimeMode.FIXED_TIMESTEP:
            return self._accumulated_time / self._fixed_timestep
        return 0.0

    def get_time_stats(self) -> dict[str, Any]:
        return {
            'time_mode': self._time_mode.display_name,
            'time_scale': self._time_scale,
            'delta_time': self._delta_time,
            'unscaled_delta_time': self.unscaled_delta_time,
            'total_game_time': self._total_game_time,
            'fixed_timestep': self._fixed_timestep,
            'max_frame_time': self._max_frame_time,
            'accumulated_time': self._accumulated_time,
            'interpolation_factor': self.get_interpolation_factor(),
            'is_paused': self.is_paused,
            'update_callbacks_count': len(self._update_callbacks),
        }

    def reset(self) -> None:
        self._delta_time = 0.0
        self._accumulated_time = 0.0
        self._total_game_time = 0.0
        self._time_scale = 1.0
        self._current_time = time.perf_counter()
        self._last_frame_time = self._current_time

import time
from collections.abc import Callable
from enum import IntEnum

import pygame


class GameState(IntEnum):
    STOPPED = 0
    RUNNING = 1
    PAUSED = 2

    @property
    def display_name(self) -> str:
        display_names = {
            GameState.STOPPED: '정지됨',
            GameState.RUNNING: '실행중',
            GameState.PAUSED: '일시정지',
        }
        return display_names[self]


class GameLoop:
    __slots__ = (
        '_clock',
        '_current_state',
        '_delta_time',
        '_fps_history',
        '_frame_count',
        '_last_fps_update',
        '_render_callback',
        '_running',
        '_target_fps',
        '_total_time',
        '_update_callback',
    )

    def __init__(self, target_fps: int = 60) -> None:
        pygame.init()

        self._clock = pygame.time.Clock()
        self._target_fps = max(1, min(240, target_fps))
        self._delta_time = 0.0
        self._current_state = GameState.STOPPED
        self._running = False

        # 콜백 함수들
        self._update_callback: Callable[[float], None] | None = None
        self._render_callback: Callable[[], None] | None = None

        # FPS 모니터링
        self._fps_history: list[float] = []
        self._frame_count = 0
        self._total_time = 0.0
        self._last_fps_update = 0.0

    @property
    def target_fps(self) -> int:
        return self._target_fps

    @target_fps.setter
    def target_fps(self, value: int) -> None:
        self._target_fps = max(1, min(240, value))

    @property
    def delta_time(self) -> float:
        return self._delta_time

    @property
    def current_state(self) -> GameState:
        return self._current_state

    @property
    def is_running(self) -> bool:
        return self._running and self._current_state != GameState.STOPPED

    @property
    def average_fps(self) -> float:
        if not self._fps_history:
            return 0.0
        return sum(self._fps_history) / len(self._fps_history)

    @property
    def current_fps(self) -> float:
        return self._clock.get_fps()

    def set_update_callback(self, callback: Callable[[float], None]) -> None:
        self._update_callback = callback

    def set_render_callback(self, callback: Callable[[], None]) -> None:
        self._render_callback = callback

    def initialize(self) -> bool:
        try:
            if self._current_state != GameState.STOPPED:
                return False

            # pygame 디스플레이 초기화 확인
            if not pygame.get_init():
                pygame.init()

            self._current_state = GameState.RUNNING
            self._running = True
            self._frame_count = 0
            self._total_time = 0.0
            self._fps_history.clear()
            self._last_fps_update = time.perf_counter()

            return True

        except Exception:
            self._current_state = GameState.STOPPED
            self._running = False
            return False

    def run(self) -> None:
        if not self.initialize():
            return

        try:
            while self._running:
                self._process_frame()
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()

    def _process_frame(self) -> None:
        # pygame 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.stop()
                    return
                elif event.key == pygame.K_SPACE:
                    self.toggle_pause()

        # FPS 제한과 delta time 계산
        self._delta_time = self._clock.tick(self._target_fps) / 1000.0

        # FPS 모니터링 업데이트
        self._update_fps_monitoring()

        # 게임 로직 업데이트 (일시정지 상태가 아닐 때만)
        if self._current_state == GameState.RUNNING:
            if self._update_callback:
                self._update_callback(self._delta_time)

        # 렌더링은 항상 수행 (일시정지 화면도 표시해야 함)
        if self._render_callback:
            self._render_callback()

    def _update_fps_monitoring(self) -> None:
        self._frame_count += 1
        current_time = time.perf_counter()
        self._total_time += self._delta_time

        # 1초마다 FPS 기록 업데이트
        if current_time - self._last_fps_update >= 1.0:
            current_fps = self._clock.get_fps()
            self._fps_history.append(current_fps)

            # 최근 60개 FPS 기록만 유지 (1분간)
            if len(self._fps_history) > 60:
                self._fps_history.pop(0)

            self._last_fps_update = current_time

    def pause(self) -> None:
        if self._current_state == GameState.RUNNING:
            self._current_state = GameState.PAUSED

    def resume(self) -> None:
        if self._current_state == GameState.PAUSED:
            self._current_state = GameState.RUNNING

    def toggle_pause(self) -> None:
        if self._current_state == GameState.RUNNING:
            self.pause()
        elif self._current_state == GameState.PAUSED:
            self.resume()

    def stop(self) -> None:
        self._running = False
        self._current_state = GameState.STOPPED

    def shutdown(self) -> None:
        self._current_state = GameState.STOPPED
        self._running = False

        # pygame 정리
        try:
            pygame.quit()
        except Exception:
            pass

    def get_performance_stats(self) -> dict[str, any]:
        return {
            'target_fps': self._target_fps,
            'current_fps': self.current_fps,
            'average_fps': self.average_fps,
            'delta_time': self._delta_time,
            'frame_count': self._frame_count,
            'total_time': self._total_time,
            'state': self._current_state.display_name,
            'fps_history_size': len(self._fps_history),
        }

    def is_maintaining_target_fps(self, tolerance: float = 0.1) -> bool:
        if not self._fps_history:
            return False

        recent_fps = (
            self._fps_history[-10:]
            if len(self._fps_history) >= 10
            else self._fps_history
        )
        avg_recent_fps = sum(recent_fps) / len(recent_fps)

        target_min = self._target_fps * (1 - tolerance)
        return avg_recent_fps >= target_min

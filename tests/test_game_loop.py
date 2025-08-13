from unittest.mock import MagicMock, Mock, patch

import pygame
import pytest

from src.core.game_loop import GameLoop
from src.core.game_state_manager import GameState, GameStateManager


@pytest.fixture
def mock_game_state_manager() -> MagicMock:
    """GameStateManager에 대한 모의 객체를 생성하는 Fixture"""
    mgr = MagicMock(spec=GameStateManager)
    # is_stopped()가 True를 반환하도록 기본 설정하여, 테스트 중 무한 루프 방지
    mgr.is_stopped.return_value = True
    mgr.is_running.return_value = False
    mgr.is_paused.return_value = False
    mgr.current_state = GameState.STOPPED
    return mgr


@pytest.fixture
@patch('pygame.init')  # pygame.init()이 자동으로 호출되는 것을 막음
def game_loop(
    mock_pygame_init: MagicMock, mock_game_state_manager: MagicMock
) -> GameLoop:
    """테스트용 GameLoop 인스턴스를 생성하는 Fixture"""
    return GameLoop(game_state_manager=mock_game_state_manager, target_fps=60)


class TestGameLoopRefactored:
    """리팩토링된 GameLoop 클래스를 테스트합니다."""

    def test_gameloop_initialization_with_valid_manager(
        self, game_loop: GameLoop, mock_game_state_manager: MagicMock
    ) -> None:
        """Test 1.1: GameLoop 초기화 및 GameStateManager 의존성 주입 검증"""
        assert game_loop._game_state_manager is mock_game_state_manager
        assert game_loop.target_fps == 60

    def test_gameloop_initialization_with_none_manager_fails(self) -> None:
        """Test 2.1: GameStateManager가 None일 때 AssertionError 발생 검증"""
        with pytest.raises(
            AssertionError, match='GameStateManager must be provided.'
        ):
            GameLoop(game_state_manager=None, target_fps=60)

    @patch('pygame.time.Clock')
    @patch('pygame.event.get', return_value=[])
    def test_callbacks_called_correctly_in_running_state(
        self,
        mock_event_get: MagicMock,
        mock_clock: MagicMock,
        game_loop: GameLoop,
        mock_game_state_manager: MagicMock,
    ) -> None:
        """Test: RUNNING 상태에서 update와 render 콜백 호출 검증"""
        # Given
        mock_game_state_manager.is_running.return_value = True
        update_callback = Mock()
        render_callback = Mock()
        game_loop.set_update_callback(update_callback)
        game_loop.set_render_callback(render_callback)

        # When
        game_loop._process_frame()

        # Then
        update_callback.assert_called_once()
        render_callback.assert_called_once()

    @patch('pygame.time.Clock')
    @patch('pygame.event.get', return_value=[])
    def test_only_render_callback_called_in_paused_state(
        self,
        mock_event_get: MagicMock,
        mock_clock: MagicMock,
        game_loop: GameLoop,
        mock_game_state_manager: MagicMock,
    ) -> None:
        """Test: PAUSED 상태에서 render 콜백만 호출되는지 검증"""
        # Given
        mock_game_state_manager.is_running.return_value = False
        mock_game_state_manager.is_paused.return_value = True
        update_callback = Mock()
        render_callback = Mock()
        game_loop.set_update_callback(update_callback)
        game_loop.set_render_callback(render_callback)

        # When
        game_loop._process_frame()

        # Then
        update_callback.assert_not_called()
        render_callback.assert_called_once()

    @patch('pygame.event.get')
    @patch('pygame.time.Clock')
    def test_quit_event_calls_manager_stop(
        self,
        mock_clock: MagicMock,
        mock_event_get: MagicMock,
        game_loop: GameLoop,
        mock_game_state_manager: MagicMock,
    ) -> None:
        """Test: Pygame QUIT 이벤트 발생 시 GameStateManager.stop() 호출 검증"""
        # Given
        mock_event_get.return_value = [pygame.event.Event(pygame.QUIT)]

        # When
        game_loop._process_frame()

        # Then
        mock_game_state_manager.stop.assert_called_once()

    @patch('pygame.event.get')
    @patch('pygame.time.Clock')
    def test_keyboard_event_calls_manager_toggle_pause(
        self,
        mock_clock: MagicMock,
        mock_event_get: MagicMock,
        game_loop: GameLoop,
        mock_game_state_manager: MagicMock,
    ) -> None:
        """Test: 스페이스바 입력 시 GameStateManager.toggle_pause() 호출 검증"""
        # Given
        mock_event_get.return_value = [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        ]

        # When
        game_loop._process_frame()

        # Then
        mock_game_state_manager.toggle_pause.assert_called_once()

    @patch('pygame.quit')
    def test_shutdown_calls_manager_stop_and_pygame_quit(
        self,
        mock_pygame_quit: MagicMock,
        game_loop: GameLoop,
        mock_game_state_manager: MagicMock,
    ) -> None:
        """Test: shutdown 시 GameStateManager.stop()과 pygame.quit() 호출 검증"""
        # When
        game_loop.shutdown()

        # Then
        mock_game_state_manager.stop.assert_called_once()
        mock_pygame_quit.assert_called_once()

    def test_performance_stats_retrieval(
        self, game_loop: GameLoop, mock_game_state_manager: MagicMock
    ) -> None:
        """Test: get_performance_stats가 GameStateManager의 상태를 올바르게 반영하는지 검증"""
        # Given
        mock_game_state_manager.current_state = GameState.RUNNING

        # When
        stats = game_loop.get_performance_stats()

        # Then
        assert stats['state'] == '실행 중'

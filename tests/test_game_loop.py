import time
import pytest
from unittest.mock import Mock, patch

from src.core.game_loop import GameLoop, GameState


class TestGameLoop:
    def test_게임_루프_초기화_상태_확인_성공_시나리오(self) -> None:
        """1. 게임 루프 초기화 상태 확인 (성공 시나리오)
        
        목적: GameLoop 생성자와 초기 상태 설정 검증
        테스트할 범위: __init__, 초기 속성값
        커버하는 함수 및 데이터: target_fps, current_state, is_running 등
        기대되는 안정성: 올바른 초기 상태 설정 보장
        """
        # Given & When - GameLoop 객체 생성
        game_loop = GameLoop(target_fps=60)
        
        # Then - 초기 상태 확인
        assert game_loop.target_fps == 60, "목표 FPS가 정확히 설정되어야 함"
        assert game_loop.current_state == GameState.STOPPED, "초기 상태는 STOPPED여야 함"
        assert not game_loop.is_running, "초기에는 실행 중이 아니어야 함"
        assert game_loop.delta_time == 0.0, "초기 delta time은 0이어야 함"
        assert game_loop.current_fps == 0.0, "초기 FPS는 0이어야 함"

    def test_게임_루프_FPS_설정_범위_제한_검증_성공_시나리오(self) -> None:
        """2. 게임 루프 FPS 설정 범위 제한 검증 (성공 시나리오)
        
        목적: target_fps 설정 시 유효한 범위로 제한되는지 검증
        테스트할 범위: target_fps 프로퍼티 setter
        커버하는 함수 및 데이터: FPS 범위 제한 (1-240)
        기대되는 안정성: 잘못된 FPS 값에 대한 안전한 처리 보장
        """
        # Given - GameLoop 객체 생성
        game_loop = GameLoop()
        
        # When & Then - 유효한 FPS 설정
        game_loop.target_fps = 40
        assert game_loop.target_fps == 40, "유효한 FPS 값이 설정되어야 함"
        
        # When & Then - 최소값 미만 설정 시 제한
        game_loop.target_fps = 0
        assert game_loop.target_fps == 1, "최소 FPS는 1로 제한되어야 함"
        
        # When & Then - 최대값 초과 설정 시 제한
        game_loop.target_fps = 300
        assert game_loop.target_fps == 240, "최대 FPS는 240으로 제한되어야 함"

    def test_게임_루프_콜백_함수_설정_및_호출_검증_성공_시나리오(self) -> None:
        """3. 게임 루프 콜백 함수 설정 및 호출 검증 (성공 시나리오)
        
        목적: update/render 콜백 함수 설정과 호출 동작 검증
        테스트할 범위: set_update_callback, set_render_callback
        커버하는 함수 및 데이터: 콜백 함수 저장과 호출
        기대되는 안정성: 콜백 함수의 정확한 설정과 호출 보장
        """
        # Given - GameLoop와 Mock 콜백 함수들
        game_loop = GameLoop(target_fps=60)
        update_callback = Mock()
        render_callback = Mock()
        
        # When - 콜백 함수 설정
        game_loop.set_update_callback(update_callback)
        game_loop.set_render_callback(render_callback)
        
        # Then - 콜백 함수가 설정됨
        assert game_loop._update_callback is update_callback, "업데이트 콜백이 설정되어야 함"
        assert game_loop._render_callback is render_callback, "렌더 콜백이 설정되어야 함"

    @patch('pygame.time.Clock')
    @patch('pygame.init')
    @patch('pygame.get_init', return_value=True)
    def test_게임_루프_초기화_과정_검증_성공_시나리오(self, mock_get_init, mock_init, mock_clock) -> None:
        """4. 게임 루프 초기화 과정 검증 (성공 시나리오)
        
        목적: initialize 메서드의 정상 동작 검증
        테스트할 범위: initialize 메서드
        커버하는 함수 및 데이터: pygame 초기화, 상태 변경, 통계 초기화
        기대되는 안정성: 정확한 초기화 과정 보장
        """
        # Given - GameLoop 객체
        game_loop = GameLoop(target_fps=40)
        
        # When - 초기화 수행
        result = game_loop.initialize()
        
        # Then - 초기화 성공 확인
        assert result, "초기화가 성공해야 함"
        assert game_loop.current_state == GameState.RUNNING, "초기화 후 RUNNING 상태여야 함"
        assert game_loop.is_running, "초기화 후 실행 중이어야 함"
        assert game_loop._frame_count == 0, "프레임 카운트가 초기화되어야 함"
        assert game_loop._total_time == 0.0, "총 시간이 초기화되어야 함"
        assert len(game_loop._fps_history) == 0, "FPS 히스토리가 초기화되어야 함"

    def test_게임_상태_전환_동작_검증_성공_시나리오(self) -> None:
        """5. 게임 상태 전환 동작 검증 (성공 시나리오)
        
        목적: pause, resume, toggle_pause, stop 메서드 동작 검증
        테스트할 범위: 상태 전환 메서드들
        커버하는 함수 및 데이터: 게임 상태 변경 로직
        기대되는 안정성: 올바른 상태 전환 보장
        """
        # Given - 초기화된 GameLoop
        game_loop = GameLoop()
        game_loop._current_state = GameState.RUNNING
        game_loop._running = True
        
        # When & Then - 일시정지
        game_loop.pause()
        assert game_loop.current_state == GameState.PAUSED, "일시정지 상태로 전환되어야 함"
        
        # When & Then - 재개
        game_loop.resume()
        assert game_loop.current_state == GameState.RUNNING, "실행 상태로 전환되어야 함"
        
        # When & Then - 토글 (RUNNING -> PAUSED)
        game_loop.toggle_pause()
        assert game_loop.current_state == GameState.PAUSED, "토글로 일시정지되어야 함"
        
        # When & Then - 토글 (PAUSED -> RUNNING)
        game_loop.toggle_pause()
        assert game_loop.current_state == GameState.RUNNING, "토글로 재개되어야 함"
        
        # When & Then - 정지
        game_loop.stop()
        assert game_loop.current_state == GameState.STOPPED, "정지 상태로 전환되어야 함"
        assert not game_loop.is_running, "실행 중이 아니어야 함"

    def test_FPS_모니터링_기능_정확성_검증_성공_시나리오(self) -> None:
        """6. FPS 모니터링 기능 정확성 검증 (성공 시나리오)
        
        목적: FPS 히스토리 기록과 평균 FPS 계산 검증
        테스트할 범위: _update_fps_monitoring, average_fps 프로퍼티
        커버하는 함수 및 데이터: FPS 통계 계산
        기대되는 안정성: 정확한 FPS 통계 제공 보장
        """
        # Given - GameLoop 객체
        game_loop = GameLoop()
        
        # When - FPS 히스토리에 직접 데이터 추가 (테스트용)
        test_fps_values = [58.5, 59.2, 60.1, 59.8, 60.0]
        game_loop._fps_history = test_fps_values
        
        # Then - 평균 FPS 계산 확인
        expected_average = sum(test_fps_values) / len(test_fps_values)
        assert abs(game_loop.average_fps - expected_average) < 0.001, "평균 FPS가 정확해야 함"
        
        # When - FPS 히스토리가 비어있을 때
        game_loop._fps_history.clear()
        
        # Then - 0.0 반환 확인
        assert game_loop.average_fps == 0.0, "빈 히스토리일 때 평균 FPS는 0이어야 함"

    def test_목표_FPS_유지_확인_기능_검증_성공_시나리오(self) -> None:
        """7. 목표 FPS 유지 확인 기능 검증 (성공 시나리오)
        
        목적: is_maintaining_target_fps 메서드의 정확성 검증
        테스트할 범위: is_maintaining_target_fps 메서드
        커버하는 함수 및 데이터: FPS 허용오차 기반 판단
        기대되는 안정성: 정확한 FPS 성능 평가 보장
        """
        # Given - 40 FPS 목표 GameLoop
        game_loop = GameLoop(target_fps=40)
        
        # When - 목표 FPS를 잘 유지하는 경우
        good_fps_values = [39.5, 40.2, 39.8, 40.1, 39.9] * 3  # 최근 10개 이상
        game_loop._fps_history = good_fps_values
        
        # Then - 목표 FPS 유지 확인
        assert game_loop.is_maintaining_target_fps(tolerance=0.1), "목표 FPS를 유지한다고 판단되어야 함"
        
        # When - 목표 FPS를 유지하지 못하는 경우
        poor_fps_values = [30.0, 32.5, 31.2, 29.8, 33.1] * 3
        game_loop._fps_history = poor_fps_values
        
        # Then - 목표 FPS 미달 확인
        assert not game_loop.is_maintaining_target_fps(tolerance=0.1), "목표 FPS 미달로 판단되어야 함"
        
        # When - FPS 히스토리가 비어있는 경우
        game_loop._fps_history.clear()
        
        # Then - False 반환
        assert not game_loop.is_maintaining_target_fps(), "히스토리가 없으면 False를 반환해야 함"

    def test_성능_통계_정보_제공_정확성_검증_성공_시나리오(self) -> None:
        """8. 성능 통계 정보 제공 정확성 검증 (성공 시나리오)
        
        목적: get_performance_stats 메서드의 정확한 통계 정보 제공 검증
        테스트할 범위: get_performance_stats 메서드
        커버하는 함수 및 데이터: 게임 루프 성능 통계
        기대되는 안정성: 완전하고 정확한 성능 데이터 제공 보장
        """
        # Given - 설정된 GameLoop
        game_loop = GameLoop(target_fps=40)
        game_loop._delta_time = 0.025  # 40 FPS 상당
        game_loop._frame_count = 100
        game_loop._total_time = 2.5
        game_loop._current_state = GameState.RUNNING
        game_loop._fps_history = [39.8, 40.1, 39.9]
        
        # When - 성능 통계 조회
        stats = game_loop.get_performance_stats()
        
        # Then - 통계 정보 확인
        assert stats['target_fps'] == 40, "목표 FPS가 정확해야 함"
        assert stats['delta_time'] == 0.025, "Delta time이 정확해야 함"
        assert stats['frame_count'] == 100, "프레임 카운트가 정확해야 함"
        assert stats['total_time'] == 2.5, "총 시간이 정확해야 함"
        assert stats['state'] == "실행중", "상태 표시명이 정확해야 함"
        assert stats['fps_history_size'] == 3, "FPS 히스토리 크기가 정확해야 함"
        
        # 평균 FPS 확인
        expected_avg = sum(game_loop._fps_history) / len(game_loop._fps_history)
        assert abs(stats['average_fps'] - expected_avg) < 0.001, "평균 FPS가 정확해야 함"

    @patch('pygame.quit')
    def test_게임_루프_종료_처리_검증_성공_시나리오(self, mock_pygame_quit) -> None:
        """9. 게임 루프 종료 처리 검증 (성공 시나리오)
        
        목적: shutdown 메서드의 정확한 정리 작업 검증
        테스트할 범위: shutdown 메서드
        커버하는 함수 및 데이터: pygame 정리, 상태 초기화
        기대되는 안정성: 안전한 리소스 정리 보장
        """
        # Given - 실행 중인 GameLoop
        game_loop = GameLoop()
        game_loop._current_state = GameState.RUNNING
        game_loop._running = True
        
        # When - 종료 처리
        game_loop.shutdown()
        
        # Then - 종료 상태 확인
        assert game_loop.current_state == GameState.STOPPED, "종료 후 STOPPED 상태여야 함"
        assert not game_loop.is_running, "종료 후 실행 중이 아니어야 함"
        mock_pygame_quit.assert_called_once(), "pygame.quit()이 호출되어야 함"

    def test_게임_상태_열거형_표시명_정확성_검증_성공_시나리오(self) -> None:
        """10. 게임 상태 열거형 표시명 정확성 검증 (성공 시나리오)
        
        목적: GameState 열거형의 표시명 기능 검증
        테스트할 범위: GameState.display_name 프로퍼티
        커버하는 함수 및 데이터: 한국어 상태 표시명
        기대되는 안정성: 일관된 상태 표시명 제공 보장
        """
        # When & Then - 각 상태별 표시명 확인
        assert GameState.STOPPED.display_name == "정지됨", "STOPPED 표시명이 정확해야 함"
        assert GameState.RUNNING.display_name == "실행중", "RUNNING 표시명이 정확해야 함"
        assert GameState.PAUSED.display_name == "일시정지", "PAUSED 표시명이 정확해야 함"
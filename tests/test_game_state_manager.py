import json
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock

from src.core.game_state_manager import GameState, GameStateManager


class TestGameStateManager:
    def test_게임_상태_초기화_및_기본값_검증_성공_시나리오(self) -> None:
        """1. 게임 상태 초기화 및 기본값 검증 (성공 시나리오)

        목적: GameStateManager 초기화 시 올바른 기본 상태 및 설정 확인
        테스트할 범위: 초기 상태, 기본 설정 로딩
        커버하는 함수 및 데이터: __init__, _load_default_config
        기대되는 안정성: 일관된 초기 상태 보장
        """
        # Given & When - GameStateManager 초기화
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            manager = GameStateManager(config_path=config_path)

            # Then - 초기 상태 검증
            assert manager.current_state == GameState.STOPPED, "초기 상태는 STOPPED이어야 함"
            assert manager.previous_state == GameState.STOPPED, "이전 상태도 STOPPED이어야 함"
            assert manager.is_stopped(), "is_stopped()가 True를 반환해야 함"
            assert not manager.is_running(), "is_running()이 False를 반환해야 함"
            assert not manager.is_paused(), "is_paused()가 False를 반환해야 함"

            # 기본 설정 검증
            display_config = manager.get_display_config()
            assert display_config['width'] == 1280, "기본 해상도 너비가 1280이어야 함"
            assert display_config['height'] == 720, "기본 해상도 높이가 720이어야 함"
            assert display_config['fps_target'] == 60, "기본 FPS 목표가 60이어야 함"

    def test_게임_상태_전환_유효성_및_콜백_호출_검증_성공_시나리오(self) -> None:
        """2. 게임 상태 전환 유효성 및 콜백 호출 검증 (성공 시나리오)

        목적: 상태 전환 규칙 준수 및 콜백 메커니즘 정상 동작 확인
        테스트할 범위: 상태 전환 로직, 콜백 시스템
        커버하는 함수 및 데이터: transition_to, can_transition_to, 콜백 관리
        기대되는 안정성: 유효한 상태 전환만 허용, 콜백 정상 실행
        """
        # Given - GameStateManager와 콜백 준비
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            manager = GameStateManager(config_path=config_path)

            running_callback_called = False
            paused_callback_called = False
            transition_calls = []

            def running_callback() -> None:
                nonlocal running_callback_called
                running_callback_called = True

            def paused_callback() -> None:
                nonlocal paused_callback_called
                paused_callback_called = True

            def transition_callback(old: GameState, new: GameState) -> None:
                transition_calls.append((old, new))

            manager.add_state_callback(GameState.RUNNING, running_callback)
            manager.add_state_callback(GameState.PAUSED, paused_callback)
            manager.add_transition_callback(transition_callback)

            # When & Then - 유효한 상태 전환 테스트
            # STOPPED -> RUNNING
            assert manager.can_transition_to(GameState.RUNNING), "STOPPED에서 RUNNING으로 전환 가능해야 함"
            assert manager.start(), "start() 성공해야 함"
            assert manager.is_running(), "RUNNING 상태여야 함"
            assert running_callback_called, "RUNNING 콜백이 호출되어야 함"
            assert len(transition_calls) == 1, "전환 콜백이 1회 호출되어야 함"
            assert transition_calls[0] == (GameState.STOPPED, GameState.RUNNING), "올바른 전환 정보여야 함"

            # RUNNING -> PAUSED
            assert manager.can_transition_to(GameState.PAUSED), "RUNNING에서 PAUSED로 전환 가능해야 함"
            assert manager.pause(), "pause() 성공해야 함"
            assert manager.is_paused(), "PAUSED 상태여야 함"
            assert paused_callback_called, "PAUSED 콜백이 호출되어야 함"

            # PAUSED -> RUNNING (resume)
            assert manager.resume(), "resume() 성공해야 함"
            assert manager.is_running(), "RUNNING 상태로 복귀해야 함"

            # 무효한 전환 테스트
            assert not manager.can_transition_to(GameState.STOPPED), "RUNNING에서 STOPPED로 직접 전환 불가해야 함"

    def test_설정_파일_로딩_저장_및_병합_검증_성공_시나리오(self) -> None:
        """3. 설정 파일 로딩, 저장 및 병합 검증 (성공 시나리오)

        목적: JSON 설정 파일의 로딩, 저장, 기본값과 병합 기능 확인
        테스트할 범위: 설정 파일 I/O, 설정 병합 로직
        커버하는 함수 및 데이터: load_config, save_config, _merge_config
        기대되는 안정성: 설정 데이터 무결성 보장
        """
        # Given - 임시 설정 파일 준비
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"

            # 사전 설정 파일 생성
            initial_config = {
                "display": {"width": 1920, "height": 1080},
                "audio": {"master_volume": 0.5},
                "custom_section": {"custom_value": "test"}
            }

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(initial_config, f)

            # When - GameStateManager 초기화 (설정 파일 자동 로딩)
            manager = GameStateManager(config_path=config_path)

            # Then - 병합된 설정 검증
            assert manager.get_config('display.width') == 1920, "로딩된 해상도 너비가 적용되어야 함"
            assert manager.get_config('display.height') == 1080, "로딩된 해상도 높이가 적용되어야 함"
            assert manager.get_config('display.fps_target') == 60, "기본값이 유지되어야 함"
            assert manager.get_config('audio.master_volume') == 0.5, "로딩된 볼륨이 적용되어야 함"
            assert manager.get_config('audio.music_volume') == 0.8, "기본 음악 볼륨이 유지되어야 함"
            assert manager.get_config('custom_section.custom_value') == "test", "커스텀 설정이 추가되어야 함"

            # 설정 변경 및 저장
            manager.set_config('display.fullscreen', True)
            manager.set_config('custom_section.new_value', 42)

            assert manager.save_config(), "설정 저장이 성공해야 함"

            # 새 인스턴스로 검증 (auto_save=True to match original)
            manager2 = GameStateManager(config_path=config_path)
            assert manager2.get_config('display.fullscreen') is True, "저장된 풀스크린 설정이 로딩되어야 함"
            assert manager2.get_config('custom_section.new_value') == 42, "저장된 커스텀 값이 로딩되어야 함"

    def test_런타임_설정_변경_및_자동_저장_검증_성공_시나리오(self) -> None:
        """4. 런타임 설정 변경 및 자동 저장 검증 (성공 시나리오)

        목적: 런타임 중 설정 변경 및 자동 저장 기능 동작 확인
        테스트할 범위: 설정 get/set, 자동 저장 메커니즘
        커버하는 함수 및 데이터: get_config, set_config, 자동 저장
        기대되는 안정성: 즉시 설정 반영 및 데이터 지속성 보장
        """
        # Given - 자동 저장 활성화된 GameStateManager
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            manager = GameStateManager(config_path=config_path, auto_save=True)

            # When - 다양한 설정 변경
            manager.update_display_config(width=2560, height=1440, fullscreen=True)
            manager.update_audio_config(master_volume=0.75, muted=True)
            manager.update_input_config(mouse_sensitivity=1.5)
            manager.update_gameplay_config(difficulty='hard', show_fps=True)

            # 복합 키 설정
            manager.set_config('input.keyboard_bindings.pause', 'space')
            manager.set_config('custom.nested.deep.value', 'deep_test')

            # Then - 즉시 반영 확인
            assert manager.get_config('display.width') == 2560, "해상도 너비 변경이 즉시 반영되어야 함"
            assert manager.get_config('audio.muted') is True, "음소거 설정이 즉시 반영되어야 함"
            assert manager.get_config('input.mouse_sensitivity') == 1.5, "마우스 감도 변경이 즉시 반영되어야 함"
            assert manager.get_config('gameplay.difficulty') == 'hard', "난이도 변경이 즉시 반영되어야 함"
            assert manager.get_config('input.keyboard_bindings.pause') == 'space', "키 바인딩 변경이 즉시 반영되어야 함"
            assert manager.get_config('custom.nested.deep.value') == 'deep_test', "깊은 중첩 설정이 즉시 반영되어야 함"

            # 기본값 테스트
            assert manager.get_config('nonexistent.key', 'default') == 'default', "존재하지 않는 키는 기본값을 반환해야 함"

            # 자동 저장 대기 (비동기 저장이므로 잠깐 대기)
            time.sleep(0.1)

            # 새 인스턴스로 지속성 확인
            manager2 = GameStateManager(config_path=config_path)
            assert manager2.get_config('display.width') == 2560, "변경된 설정이 파일에 저장되어야 함"
            assert manager2.get_config('custom.nested.deep.value') == 'deep_test', "중첩된 설정도 파일에 저장되어야 함"

    def test_상태_토글_및_편의_메서드_검증_성공_시나리오(self) -> None:
        """5. 상태 토글 및 편의 메서드 검증 (성공 시나리오)

        목적: 상태 토글 기능과 편의 메서드들의 정상 동작 확인
        테스트할 범위: toggle_pause, 편의 메서드들
        커버하는 함수 및 데이터: toggle_pause, start, pause, resume, stop
        기대되는 안정성: 직관적인 상태 조작 인터페이스 제공
        """
        # Given - GameStateManager 준비
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            manager = GameStateManager(config_path=config_path)

            # When & Then - 상태 시작
            assert manager.start(), "start() 성공해야 함"
            assert manager.is_running(), "시작 후 RUNNING 상태여야 함"

            # 토글 기능 테스트
            assert manager.toggle_pause(), "토글로 일시정지 성공해야 함"
            assert manager.is_paused(), "토글 후 PAUSED 상태여야 함"

            assert manager.toggle_pause(), "토글로 재개 성공해야 함"
            assert manager.is_running(), "토글 후 RUNNING 상태여야 함"

            # STOPPED 상태에서 토글 시도 (실패해야 함)
            assert manager.stop(), "stop() 성공해야 함"
            assert not manager.toggle_pause(), "STOPPED 상태에서 토글은 실패해야 함"
            assert manager.is_stopped(), "여전히 STOPPED 상태여야 함"

            # resume 실패 케이스 (PAUSED 상태가 아닐 때)
            assert not manager.resume(), "STOPPED 상태에서 resume은 실패해야 함"

    def test_설정_초기화_및_콜백_관리_검증_성공_시나리오(self) -> None:
        """6. 설정 초기화 및 콜백 관리 검증 (성공 시나리오)

        목적: 설정 초기화 기능과 콜백 관리 시스템 동작 확인
        테스트할 범위: reset_to_defaults, 콜백 추가/제거
        커버하는 함수 및 데이터: reset_to_defaults, 콜백 관리 메서드들
        기대되는 안정성: 설정 리셋 및 콜백 생명주기 관리 보장
        """
        # Given - GameStateManager와 콜백들 준비
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            manager = GameStateManager(config_path=config_path)

            # 설정 변경
            manager.set_config('display.width', 3840)
            manager.set_config('custom.value', 'changed')

            # 콜백 준비
            callback1 = MagicMock()
            callback2 = MagicMock()
            transition_callback = MagicMock()

            manager.add_state_callback(GameState.RUNNING, callback1)
            manager.add_state_callback(GameState.RUNNING, callback2)
            manager.add_transition_callback(transition_callback)

            # When - 설정 초기화
            manager.reset_to_defaults()

            # Then - 설정이 기본값으로 복원되는지 확인
            time.sleep(0.1)  # 비동기 저장 대기
            assert manager.get_config('display.width') == 1280, "해상도가 기본값으로 복원되어야 함"
            assert manager.get_config('custom.value', 'not_found') == 'not_found', "커스텀 설정이 제거되어야 함"

            # 콜백 동작 확인
            assert manager.start(), "상태 전환 성공해야 함"
            callback1.assert_called_once()
            callback2.assert_called_once()
            transition_callback.assert_called_once()

            # 콜백 제거 테스트
            manager.remove_state_callback(GameState.RUNNING, callback1)
            manager.remove_transition_callback(transition_callback)

            callback1.reset_mock()
            callback2.reset_mock()
            transition_callback.reset_mock()

            # 다시 상태 전환 (PAUSED 상태로)
            assert manager.pause(), "일시정지 성공해야 함"

            callback1.assert_not_called()  # 제거된 콜백은 호출되지 않아야 함
            # PAUSED 콜백은 별도로 등록하지 않았으므로 callback2는 호출되지 않음
            transition_callback.assert_not_called()  # 제거된 전환 콜백은 호출되지 않아야 함

            # 모든 콜백 정리
            manager.clear_callbacks()

    def test_스레드_안전성_및_동시성_검증_성공_시나리오(self) -> None:
        """7. 스레드 안전성 및 동시성 검증 (성공 시나리오)

        목적: 멀티스레드 환경에서 설정 관리의 안전성 확인
        테스트할 범위: 설정 변경의 스레드 안전성
        커버하는 함수 및 데이터: 멀티스레드 설정 접근
        기대되는 안정성: 동시 접근 시 데이터 무결성 보장
        """
        # Given - GameStateManager와 동시성 테스트 준비
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            manager = GameStateManager(config_path=config_path)

            results = []
            errors = []

            def worker(thread_id: int) -> None:
                try:
                    for i in range(100):
                        # 설정 변경
                        manager.set_config(f'thread_{thread_id}.value_{i}', i * thread_id)
                        
                        # 설정 읽기
                        value = manager.get_config(f'thread_{thread_id}.value_{i}')
                        results.append((thread_id, i, value))
                        
                        # 기본 설정 변경
                        manager.set_config('display.width', 1920 + thread_id)
                        
                except Exception as e:
                    errors.append((thread_id, str(e)))

            # When - 동시 실행
            threads = []
            for i in range(5):
                thread = threading.Thread(target=worker, args=(i,))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            # Then - 결과 검증
            assert len(errors) == 0, f"스레드 실행 중 오류가 발생하지 않아야 함: {errors}"
            assert len(results) == 500, "모든 설정 작업이 완료되어야 함 (5 threads × 100 operations)"

            # 데이터 무결성 확인
            for thread_id, i, value in results:
                expected = i * thread_id
                assert value == expected, f"스레드 {thread_id}의 값 {i}가 예상값 {expected}와 일치해야 함"

            # 마지막 display.width 값이 유효한 범위에 있는지 확인
            final_width = manager.get_config('display.width')
            assert 1920 <= final_width <= 1924, f"최종 해상도 너비가 유효 범위에 있어야 함: {final_width}"

    def test_상태_정보_조회_및_디버깅_기능_검증_성공_시나리오(self) -> None:
        """8. 상태 정보 조회 및 디버깅 기능 검증 (성공 시나리오)

        목적: 상태 정보 조회 및 디버깅을 위한 메서드들 동작 확인
        테스트할 범위: get_state_info, 각종 설정 조회 메서드들
        커버하는 함수 및 데이터: 정보 조회 메서드들
        기대되는 안정성: 정확한 상태 및 설정 정보 제공
        """
        # Given - GameStateManager와 다양한 설정 준비
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            manager = GameStateManager(config_path=config_path, auto_save=False)

            # 콜백 추가
            dummy_callback = lambda: None
            manager.add_state_callback(GameState.RUNNING, dummy_callback)
            manager.add_state_callback(GameState.PAUSED, dummy_callback)
            manager.add_transition_callback(lambda old, new: None)

            # 상태 변경
            manager.start()
            manager.pause()

            # When - 상태 정보 조회
            state_info = manager.get_state_info()

            # Then - 상태 정보 검증
            assert state_info['current_state'] == '일시정지', "현재 상태가 정확해야 함"
            assert state_info['previous_state'] == '실행 중', "이전 상태가 정확해야 함"
            assert state_info['state_callbacks_count']['실행 중'] == 1, "RUNNING 콜백 수가 정확해야 함"
            assert state_info['state_callbacks_count']['일시정지'] == 1, "PAUSED 콜백 수가 정확해야 함"
            assert state_info['transition_callbacks_count'] == 1, "전환 콜백 수가 정확해야 함"
            assert str(config_path) in state_info['config_path'], "설정 파일 경로가 포함되어야 함"
            assert state_info['auto_save'] is False, "auto_save 설정이 정확해야 함"

            # 개별 설정 섹션 조회
            display_config = manager.get_display_config()
            audio_config = manager.get_audio_config()
            input_config = manager.get_input_config()
            gameplay_config = manager.get_gameplay_config()

            assert isinstance(display_config, dict), "display 설정이 dict 타입이어야 함"
            assert isinstance(audio_config, dict), "audio 설정이 dict 타입이어야 함"
            assert isinstance(input_config, dict), "input 설정이 dict 타입이어야 함"
            assert isinstance(gameplay_config, dict), "gameplay 설정이 dict 타입이어야 함"

            assert 'width' in display_config, "display 설정에 width가 있어야 함"
            assert 'master_volume' in audio_config, "audio 설정에 master_volume이 있어야 함"
            assert 'mouse_sensitivity' in input_config, "input 설정에 mouse_sensitivity가 있어야 함"
            assert 'difficulty' in gameplay_config, "gameplay 설정에 difficulty가 있어야 함"
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from src.core.game_state_manager import GameState, GameStateManager
from src.core.state_handler import (
    DefaultGameStateHandler,
    IStateHandler,
    StateDispatcher,
)


class MockEvent:
    def __init__(self, key: str) -> None:
        self.key = key


class MockHandler(IStateHandler):
    def __init__(self) -> None:
        self.input_calls = []
        self.render_calls = []
        self.update_calls = []

    def handle_input(self, event) -> bool:
        self.input_calls.append(event)
        return True

    def handle_rendering(self, renderer) -> None:
        self.render_calls.append(renderer)

    def update(self, delta_time: float) -> None:
        self.update_calls.append(delta_time)


class TestStateHandler:
    def test_상태_디스패처_핸들러_등록_및_호출_검증_성공_시나리오(
        self,
    ) -> None:
        """1. 상태 디스패처 핸들러 등록 및 호출 검증 (성공 시나리오)

        목적: StateDispatcher의 핸들러 등록 및 상태별 호출 메커니즘 확인
        테스트할 범위: 핸들러 등록, 상태별 처리 분기
        커버하는 함수 및 데이터: register_handler, handle_input/rendering/update
        기대되는 안정성: 올바른 핸들러가 현재 상태에 따라 호출됨
        """
        # Given - StateDispatcher와 핸들러 준비
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'test_config.json'
            state_manager = GameStateManager(config_path=config_path)
            dispatcher = StateDispatcher(state_manager)

            running_handler = MockHandler()
            paused_handler = MockHandler()

            dispatcher.register_handler(GameState.RUNNING, running_handler)
            dispatcher.register_handler(GameState.PAUSED, paused_handler)

            # When & Then - RUNNING 상태에서 테스트
            state_manager.start()
            assert state_manager.is_running(), 'RUNNING 상태여야 함'

            # 입력 처리
            test_event = MockEvent('test_key')
            result = dispatcher.handle_input(test_event)
            assert result is True, '입력 처리가 성공해야 함'
            assert len(running_handler.input_calls) == 1, (
                'RUNNING 핸들러가 호출되어야 함'
            )
            assert len(paused_handler.input_calls) == 0, (
                'PAUSED 핸들러는 호출되지 않아야 함'
            )
            assert running_handler.input_calls[0] == test_event, (
                '올바른 이벤트가 전달되어야 함'
            )

            # 렌더링 처리
            test_renderer = MagicMock()
            dispatcher.handle_rendering(test_renderer)
            assert len(running_handler.render_calls) == 1, (
                'RUNNING 핸들러 렌더링이 호출되어야 함'
            )
            assert len(paused_handler.render_calls) == 0, (
                'PAUSED 핸들러 렌더링은 호출되지 않아야 함'
            )
            assert running_handler.render_calls[0] == test_renderer, (
                '올바른 렌더러가 전달되어야 함'
            )

            # 업데이트 처리
            dispatcher.update(0.016)
            assert len(running_handler.update_calls) == 1, (
                'RUNNING 핸들러 업데이트가 호출되어야 함'
            )
            assert len(paused_handler.update_calls) == 0, (
                'PAUSED 핸들러 업데이트는 호출되지 않아야 함'
            )
            assert running_handler.update_calls[0] == 0.016, (
                '올바른 delta_time이 전달되어야 함'
            )

            # PAUSED 상태로 전환하여 테스트
            state_manager.pause()
            assert state_manager.is_paused(), 'PAUSED 상태여야 함'

            # PAUSED 상태에서는 update가 호출되지 않아야 함
            dispatcher.update(0.016)
            assert len(running_handler.update_calls) == 1, (
                'RUNNING 핸들러 업데이트 호출 수가 변하지 않아야 함'
            )
            assert len(paused_handler.update_calls) == 0, (
                'PAUSED 상태에서는 업데이트가 호출되지 않아야 함'
            )

            # 하지만 렌더링은 호출되어야 함
            dispatcher.handle_rendering(test_renderer)
            assert len(paused_handler.render_calls) == 1, (
                'PAUSED 핸들러 렌더링이 호출되어야 함'
            )

    def test_상태_프로세서_등록_및_체인_호출_검증_성공_시나리오(self) -> None:
        """2. 상태 프로세서 등록 및 체인 호출 검증 (성공 시나리오)

        목적: 프로세서 기반의 이벤트 처리 체인 메커니즘 확인
        테스트할 범위: 프로세서 등록, 체인 호출, 우선순위 처리
        커버하는 함수 및 데이터: add_*_processor, 프로세서 체인 실행
        기대되는 안정성: 등록된 프로세서들이 순서대로 호출됨
        """
        # Given - StateDispatcher와 프로세서들 준비
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'test_config.json'
            state_manager = GameStateManager(config_path=config_path)
            dispatcher = StateDispatcher(state_manager)

            input_calls = []
            render_calls = []
            update_calls = []

            def input_processor1(event) -> bool:
                input_calls.append(f'processor1_{event.key}')
                return False  # 다음 프로세서로 전달

            def input_processor2(event) -> bool:
                input_calls.append(f'processor2_{event.key}')
                return True  # 처리 완료

            def input_processor3(event) -> bool:
                input_calls.append(f'processor3_{event.key}')
                return False

            def render_processor1(renderer) -> None:
                render_calls.append('render1')

            def render_processor2(renderer) -> None:
                render_calls.append('render2')

            def update_processor1(delta_time: float) -> None:
                update_calls.append(f'update1_{delta_time}')

            def update_processor2(delta_time: float) -> None:
                update_calls.append(f'update2_{delta_time}')

            # 프로세서 등록
            dispatcher.add_input_processor(GameState.RUNNING, input_processor1)
            dispatcher.add_input_processor(GameState.RUNNING, input_processor2)
            dispatcher.add_input_processor(GameState.RUNNING, input_processor3)

            dispatcher.add_render_processor(
                GameState.RUNNING, render_processor1
            )
            dispatcher.add_render_processor(
                GameState.RUNNING, render_processor2
            )

            dispatcher.add_update_processor(
                GameState.RUNNING, update_processor1
            )
            dispatcher.add_update_processor(
                GameState.RUNNING, update_processor2
            )

            # When - RUNNING 상태에서 처리
            state_manager.start()

            # 입력 처리 (processor2에서 True 반환하므로 processor3는 호출되지 않아야 함)
            test_event = MockEvent('test')
            result = dispatcher.handle_input(test_event)

            # Then - 입력 처리 검증
            assert result is True, '입력 처리가 성공해야 함'
            assert len(input_calls) == 2, '두 개의 프로세서만 호출되어야 함'
            assert input_calls[0] == 'processor1_test', (
                '첫 번째 프로세서가 호출되어야 함'
            )
            assert input_calls[1] == 'processor2_test', (
                '두 번째 프로세서가 호출되어야 함'
            )

            # 렌더링 처리 (모든 프로세서 호출)
            dispatcher.handle_rendering(MagicMock())
            assert len(render_calls) == 2, '모든 렌더 프로세서가 호출되어야 함'
            assert render_calls[0] == 'render1', (
                '첫 번째 렌더 프로세서가 호출되어야 함'
            )
            assert render_calls[1] == 'render2', (
                '두 번째 렌더 프로세서가 호출되어야 함'
            )

            # 업데이트 처리 (모든 프로세서 호출)
            dispatcher.update(0.032)
            assert len(update_calls) == 2, (
                '모든 업데이트 프로세서가 호출되어야 함'
            )
            assert update_calls[0] == 'update1_0.032', (
                '첫 번째 업데이트 프로세서가 호출되어야 함'
            )
            assert update_calls[1] == 'update2_0.032', (
                '두 번째 업데이트 프로세서가 호출되어야 함'
            )

    def test_기본_게임_상태_핸들러_키_바인딩_검증_성공_시나리오(self) -> None:
        """3. 기본 게임 상태 핸들러 키 바인딩 검증 (성공 시나리오)

        목적: DefaultGameStateHandler의 기본 키 바인딩 처리 확인
        테스트할 범위: 키 바인딩 처리, 상태 전환 트리거
        커버하는 함수 및 데이터: DefaultGameStateHandler.handle_input
        기대되는 안정성: 설정된 키로 올바른 상태 전환 수행
        """
        # Given - GameStateManager와 DefaultGameStateHandler 준비
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'test_config.json'
            state_manager = GameStateManager(config_path=config_path)
            handler = DefaultGameStateHandler(state_manager)

            # 커스텀 키 바인딩 설정
            state_manager.set_config('input.keyboard_bindings.pause', 'space')
            state_manager.set_config('input.keyboard_bindings.quit', 'q')

            # When & Then - 게임 시작 후 키 입력 테스트
            state_manager.start()
            assert state_manager.is_running(), '게임이 실행 중이어야 함'

            # 일시정지 키 입력
            pause_event = MockEvent('space')
            result = handler.handle_input(pause_event)
            assert result is True, '일시정지 키 처리가 성공해야 함'
            assert state_manager.is_paused(), '일시정지 상태로 전환되어야 함'

            # 다시 일시정지 키 입력 (재개)
            resume_event = MockEvent('space')
            result = handler.handle_input(resume_event)
            assert result is True, '재개 키 처리가 성공해야 함'
            assert state_manager.is_running(), '실행 상태로 복귀해야 함'

            # 종료 키 입력
            quit_event = MockEvent('q')
            result = handler.handle_input(quit_event)
            assert result is True, '종료 키 처리가 성공해야 함'
            assert state_manager.is_stopped(), '정지 상태로 전환되어야 함'

            # 인식하지 않는 키 입력
            unknown_event = MockEvent('x')
            result = handler.handle_input(unknown_event)
            assert result is False, '인식하지 않는 키는 처리되지 않아야 함'

    def test_프로세서_등록_해제_및_정리_검증_성공_시나리오(self) -> None:
        """4. 프로세서 등록 해제 및 정리 검증 (성공 시나리오)

        목적: 프로세서의 동적 등록/해제 및 정리 기능 확인
        테스트할 범위: 프로세서 추가/제거, 전체 정리
        커버하는 함수 및 데이터: remove_*_processor, clear_* 메서드들
        기대되는 안정성: 프로세서 생명주기 관리 정확성
        """
        # Given - StateDispatcher와 프로세서들 준비
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'test_config.json'
            state_manager = GameStateManager(config_path=config_path)
            dispatcher = StateDispatcher(state_manager)

            calls = []

            def processor1(event) -> bool:
                calls.append('proc1')
                return False

            def processor2(event) -> bool:
                calls.append('proc2')
                return False

            def render_proc(renderer) -> None:
                calls.append('render')

            def update_proc(delta_time: float) -> None:
                calls.append('update')

            # 프로세서들 등록
            dispatcher.add_input_processor(GameState.RUNNING, processor1)
            dispatcher.add_input_processor(GameState.RUNNING, processor2)
            dispatcher.add_render_processor(GameState.RUNNING, render_proc)
            dispatcher.add_update_processor(GameState.RUNNING, update_proc)

            state_manager.start()

            # When - 초기 상태 테스트
            dispatcher.handle_input(MockEvent('test'))
            dispatcher.handle_rendering(MagicMock())
            dispatcher.update(0.016)

            # Then - 모든 프로세서가 호출되었는지 확인
            assert 'proc1' in calls, 'processor1이 호출되어야 함'
            assert 'proc2' in calls, 'processor2가 호출되어야 함'
            assert 'render' in calls, 'render_proc이 호출되어야 함'
            assert 'update' in calls, 'update_proc이 호출되어야 함'

            calls.clear()

            # 특정 프로세서 제거
            dispatcher.remove_input_processor(GameState.RUNNING, processor1)

            dispatcher.handle_input(MockEvent('test2'))
            assert 'proc1' not in calls, (
                '제거된 processor1은 호출되지 않아야 함'
            )
            assert 'proc2' in calls, 'processor2는 여전히 호출되어야 함'

            calls.clear()

            # 특정 상태의 모든 프로세서 정리
            dispatcher.clear_state_processors(GameState.RUNNING)

            dispatcher.handle_input(MockEvent('test3'))
            dispatcher.handle_rendering(MagicMock())
            dispatcher.update(0.016)

            assert len(calls) == 0, (
                '정리 후에는 어떤 프로세서도 호출되지 않아야 함'
            )

            # 새 프로세서 추가 후 전체 정리 테스트
            dispatcher.add_input_processor(GameState.RUNNING, processor1)
            dispatcher.add_input_processor(GameState.PAUSED, processor2)

            dispatcher.clear_all_processors()

            state_manager.pause()
            dispatcher.handle_input(MockEvent('test4'))

            assert len(calls) == 0, (
                '전체 정리 후에는 어떤 상태에서도 프로세서가 호출되지 않아야 함'
            )

    def test_핸들러와_프로세서_혼합_사용_검증_성공_시나리오(self) -> None:
        """5. 핸들러와 프로세서 혼합 사용 검증 (성공 시나리오)

        목적: 핸들러와 프로세서가 함께 사용될 때의 상호작용 확인
        테스트할 범위: 핸들러 우선순위, 프로세서와의 연계
        커버하는 함수 및 데이터: 핸들러-프로세서 체인 실행
        기대되는 안정성: 핸들러 우선 실행, 필요시 프로세서 체인 계속
        """
        # Given - StateDispatcher, 핸들러, 프로세서 모두 준비
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'test_config.json'
            state_manager = GameStateManager(config_path=config_path)
            dispatcher = StateDispatcher(state_manager)

            execution_order = []

            # 핸들러가 True를 반환하는 경우
            class SuccessHandler(IStateHandler):
                def handle_input(self, event) -> bool:
                    execution_order.append('handler_success')
                    return True

                def handle_rendering(self, renderer) -> None:
                    execution_order.append('handler_render')

                def update(self, delta_time: float) -> None:
                    execution_order.append('handler_update')

            # 핸들러가 False를 반환하는 경우
            class FailHandler(IStateHandler):
                def handle_input(self, event) -> bool:
                    execution_order.append('handler_fail')
                    return False

                def handle_rendering(self, renderer) -> None:
                    execution_order.append('handler_render')

                def update(self, delta_time: float) -> None:
                    execution_order.append('handler_update')

            def input_processor(event) -> bool:
                execution_order.append('processor_input')
                return True

            def render_processor(renderer) -> None:
                execution_order.append('processor_render')

            def update_processor(delta_time: float) -> None:
                execution_order.append('processor_update')

            # When & Then - 성공 핸들러 테스트 (프로세서는 호출되지 않아야 함)
            success_handler = SuccessHandler()
            dispatcher.register_handler(GameState.RUNNING, success_handler)
            dispatcher.add_input_processor(GameState.RUNNING, input_processor)

            state_manager.start()

            dispatcher.handle_input(MockEvent('test'))
            assert execution_order[-1] == 'handler_success', (
                '핸들러가 마지막에 실행되어야 함'
            )
            assert 'processor_input' not in execution_order, (
                '핸들러가 True 반환 시 프로세서는 호출되지 않아야 함'
            )

            execution_order.clear()

            # 실패 핸들러 테스트 (프로세서가 호출되어야 함)
            fail_handler = FailHandler()
            dispatcher.register_handler(GameState.RUNNING, fail_handler)

            dispatcher.handle_input(MockEvent('test2'))
            assert 'handler_fail' in execution_order, '핸들러가 호출되어야 함'
            assert 'processor_input' in execution_order, (
                '핸들러가 False 반환 시 프로세서가 호출되어야 함'
            )
            assert execution_order.index(
                'handler_fail'
            ) < execution_order.index('processor_input'), (
                '핸들러가 프로세서보다 먼저 실행되어야 함'
            )

            execution_order.clear()

            # 렌더링과 업데이트는 항상 모두 호출
            dispatcher.add_render_processor(
                GameState.RUNNING, render_processor
            )
            dispatcher.add_update_processor(
                GameState.RUNNING, update_processor
            )

            dispatcher.handle_rendering(MagicMock())
            assert 'handler_render' in execution_order, (
                '핸들러 렌더링이 호출되어야 함'
            )
            assert 'processor_render' in execution_order, (
                '프로세서 렌더링도 호출되어야 함'
            )

            execution_order.clear()

            dispatcher.update(0.016)
            assert 'handler_update' in execution_order, (
                '핸들러 업데이트가 호출되어야 함'
            )
            assert 'processor_update' in execution_order, (
                '프로세서 업데이트도 호출되어야 함'
            )

    def test_예외_상황_처리_및_안정성_검증_성공_시나리오(self) -> None:
        """6. 예외 상황 처리 및 안정성 검증 (성공 시나리오)

        목적: 핸들러나 프로세서에서 예외 발생 시 시스템 안정성 확인
        테스트할 범위: 예외 처리, 시스템 연속성 보장
        커버하는 함수 및 데이터: 예외 발생 시 처리 로직
        기대되는 안정성: 일부 컴포넌트 실패 시에도 시스템 정상 동작
        """
        # Given - StateDispatcher와 예외 발생 컴포넌트들 준비
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'test_config.json'
            state_manager = GameStateManager(config_path=config_path)
            dispatcher = StateDispatcher(state_manager)

            execution_log = []

            class ExceptionHandler(IStateHandler):
                def handle_input(self, event) -> bool:
                    execution_log.append('handler_input_start')
                    raise ValueError('Handler input error')

                def handle_rendering(self, renderer) -> None:
                    execution_log.append('handler_render_start')
                    raise RuntimeError('Handler render error')

                def update(self, delta_time: float) -> None:
                    execution_log.append('handler_update_start')
                    raise TypeError('Handler update error')

            def exception_input_processor(event) -> bool:
                execution_log.append('processor_input_exception')
                raise Exception('Processor input error')

            def safe_input_processor(event) -> bool:
                execution_log.append('processor_input_safe')
                return True

            def exception_render_processor(renderer) -> None:
                execution_log.append('processor_render_exception')
                raise Exception('Processor render error')

            def safe_render_processor(renderer) -> None:
                execution_log.append('processor_render_safe')

            def exception_update_processor(delta_time: float) -> None:
                execution_log.append('processor_update_exception')
                raise Exception('Processor update error')

            def safe_update_processor(delta_time: float) -> None:
                execution_log.append('processor_update_safe')

            # 핸들러와 프로세서 등록
            dispatcher.register_handler(GameState.RUNNING, ExceptionHandler())
            dispatcher.add_input_processor(
                GameState.RUNNING, exception_input_processor
            )
            dispatcher.add_input_processor(
                GameState.RUNNING, safe_input_processor
            )
            dispatcher.add_render_processor(
                GameState.RUNNING, exception_render_processor
            )
            dispatcher.add_render_processor(
                GameState.RUNNING, safe_render_processor
            )
            dispatcher.add_update_processor(
                GameState.RUNNING, exception_update_processor
            )
            dispatcher.add_update_processor(
                GameState.RUNNING, safe_update_processor
            )

            state_manager.start()

            # When & Then - 입력 처리 예외 테스트
            result = dispatcher.handle_input(MockEvent('test'))

            # 핸들러에서 예외가 발생했지만 프로세서는 계속 실행되어야 함
            assert 'handler_input_start' in execution_log, (
                '핸들러가 실행을 시작했어야 함'
            )
            assert 'processor_input_exception' in execution_log, (
                '첫 번째 프로세서가 실행되었어야 함'
            )
            assert 'processor_input_safe' in execution_log, (
                '예외 후에도 안전한 프로세서가 실행되어야 함'
            )
            assert result is True, (
                '안전한 프로세서가 True를 반환했으므로 전체 결과는 True여야 함'
            )

            execution_log.clear()

            # 렌더링 예외 테스트
            dispatcher.handle_rendering(MagicMock())

            assert 'handler_render_start' in execution_log, (
                '핸들러 렌더링이 시작했어야 함'
            )
            assert 'processor_render_exception' in execution_log, (
                '예외 프로세서가 실행되었어야 함'
            )
            assert 'processor_render_safe' in execution_log, (
                '예외 후에도 안전한 프로세서가 실행되어야 함'
            )

            execution_log.clear()

            # 업데이트 예외 테스트
            dispatcher.update(0.016)

            assert 'handler_update_start' in execution_log, (
                '핸들러 업데이트가 시작했어야 함'
            )
            assert 'processor_update_exception' in execution_log, (
                '예외 프로세서가 실행되었어야 함'
            )
            assert 'processor_update_safe' in execution_log, (
                '예외 후에도 안전한 프로세서가 실행되어야 함'
            )

            # 시스템이 여전히 정상 동작하는지 확인
            assert state_manager.is_running(), (
                '예외 발생에도 불구하고 상태 관리자는 정상 동작해야 함'
            )
            assert state_manager.pause(), '상태 전환도 정상 동작해야 함'

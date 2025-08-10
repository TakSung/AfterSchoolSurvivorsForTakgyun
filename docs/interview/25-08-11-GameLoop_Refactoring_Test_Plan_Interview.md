# Unit Test Specification for `GameLoop` Refactoring

- **Date**: 2025-08-11
- **Participants**: Unit Test Design Expert (AI), Project Owner
- **Target**: `GameLoop` class refactoring to integrate `GameStateManager`.

---

### 1. Core Function
- **Responsibility**: `GameStateManager`로부터 상태를 받아 게임의 메인 루프 실행, 업데이트 및 렌더링 콜백 호출을 관리하는 상태 없는(stateless) 실행자.
- **Business Logic**:
    - `GameStateManager`의 현재 상태가 `RUNNING`일 때만 `update` 콜백을 호출한다.
    - `GameStateManager`의 상태와 관계없이 `render` 콜백은 계속 호출한다 (일시정지 화면 등).
    - `pygame` 이벤트(예: 키보드 입력)를 감지하여 `GameStateManager`의 상태 변경 메서드(예: `toggle_pause`, `stop`)를 호출한다.

### 2. Function Signature (Target)
```python
# src/core/game_loop.py
class GameLoop:
    def __init__(self, game_state_manager: GameStateManager, target_fps: int = 60):
        assert game_state_manager is not None, "GameStateManager must be provided."
        # ...
```

### 3. Pre-conditions & Assumptions
- **Pre-conditions**:
    - `GameLoop` 생성 시 유효한 `GameStateManager` 인스턴스가 전달되어야 한다.
    - `pygame` 라이브러리가 초기화되어 있어야 한다.
- **Assumptions (Not tested in unit tests)**:
    - `GameStateManager`의 내부 로직은 자체 테스트에서 완벽히 검증되었다.
    - `update`/`render` 콜백 함수는 그 자체로 올바르게 동작한다.
    - `pygame` 라이브러리는 정상 동작한다.

### 4. Post-conditions & Invariants
- **Post-conditions**:
    - **On Success**: `GameLoop`는 `GameStateManager`의 상태에 따라 콜백을 정확히 호출하고, `STOPPED` 상태가 되면 정상적으로 루프를 종료한다.
    - **On Failure**: `game_state_manager`가 `None`으로 주입되면 `AssertionError`가 발생한다.
- **Invariants**:
    - `GameLoop`는 실행 중에 `target_fps` 값을 스스로 변경하지 않는다.
    - `GameLoop`는 주입된 `GameStateManager` 인스턴스를 다른 인스턴스로 교체하지 않는다.

### 5. Mocking Targets
- **Dependencies to Mock**:
    - `GameStateManager`
    - `update_callback`, `render_callback`
    - `pygame.time.Clock`, `pygame.event.get`, `pygame.quit`

### 6. Test Scenarios (Given-When-Then)

**A. Success Scenarios**
- **Test 1.1**: `RUNNING` 상태에서 `update`와 `render` 콜백이 모두 호출되는지 검증
    - **Given**: `GameStateManager` Mock이 `is_running()`에서 `True`를 반환하도록 설정. `update`, `render` 콜백 Mock 준비.
    - **When**: `_process_frame()`을 1회 실행.
    - **Then**: `update_callback`과 `render_callback`이 각각 1회씩 호출되었는지 확인.

- **Test 1.2**: `PAUSED` 상태에서 `render` 콜백만 호출되는지 검증
    - **Given**: `GameStateManager` Mock이 `is_running()`에서 `False`를, `is_paused()`에서 `True`를 반환하도록 설정.
    - **When**: `_process_frame()`을 1회 실행.
    - **Then**: `render_callback`은 1회 호출되고, `update_callback`은 호출되지 않았는지 확인.

- **Test 1.3**: `pygame`의 `QUIT` 이벤트 발생 시 `stop` 메서드가 호출되는지 검증
    - **Given**: `pygame.event.get` Mock이 `QUIT` 이벤트를 반환하도록 설정. `GameStateManager` Mock 준비.
    - **When**: `_process_frame()`을 1회 실행.
    - **Then**: `game_state_manager.stop()` 메서드가 1회 호출되었는지 확인.

- **Test 1.4**: 키보드 입력 시 `toggle_pause`가 호출되는지 검증
    - **Given**: `pygame.event.get` Mock이 `SPACE` 키다운 이벤트를 반환하도록 설정. `GameStateManager` Mock 준비.
    - **When**: `_process_frame()`을 1회 실행.
    - **Then**: `game_state_manager.toggle_pause()` 메서드가 1회 호출되었는지 확인.

**B. Failure & Edge Case Scenarios**
- **Test 2.1**: `GameStateManager`가 `None`일 때 `AssertionError` 발생 검증
    - **Given**: `game_state_manager` 파라미터에 `None`을 전달.
    - **When**: `GameLoop`를 초기화.
    - **Then**: `pytest.raises(AssertionError)`를 통해 `AssertionError`가 발생하는지 확인.

### 7. Validation Coverage Verification
- **입력 검증**: Test 2.1에서 검증됨.
- **`RUNNING` 상태 로직**: Test 1.1에서 검증됨.
- **`PAUSED` 상태 로직**: Test 1.2에서 검증됨.
- **`QUIT` 이벤트 처리**: Test 1.3에서 검증됨.
- **키보드 이벤트 처리**: Test 1.4에서 검증됨.

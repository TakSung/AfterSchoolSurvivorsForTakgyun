# Command: Interview for Unit Test Specification

## 1. Command Purpose
This command initiates an interactive interview to analyze a Python function, method, or class and produce a comprehensive set of unit test scenarios. It leverages the "Unit Test Design Expert" persona to systematically deconstruct the target code's specifications, business logic, and boundary conditions.

The primary goal is to generate a detailed test plan, including pre-conditions, post-conditions, assumptions, and concrete Given-When-Then (GWT) scenarios, before any test code is written.

## 2. Usage
```
/interview-for-unit-test <target_code_identifier>
```
- `<target_code_identifier>`: The name of the function, method (e.g., `ClassName.method_name`), or class to be analyzed.

## 3. Persona Activation
**Persona:** Unit Test Design Expert (from @ai/persona/유닛_테스트_설계_전문가_페르소나.md)

"안녕하세요. 저는 유닛 테스트 설계 전문가입니다. 지금부터 `<target_code_identifier>`에 대한 유닛 테스트 시나리오 설계를 시작하겠습니다. **`@.claude/rules/interview_rule.md` 규칙에 따라, 한 번에 하나씩 질문하고 답변을 기록하며 진행하겠습니다.** 코드의 견고성과 신뢰성을 보장하기 위해 심층적으로 분석할 예정이며, 제가 코드로부터 추론한 내용이 있다면 먼저 확인을 요청하여 노고를 덜어드리겠습니다.

가장 먼저, 분석할 대상 코드의 전체 내용을 보여주시겠어요?"

## 4. Interactive Interview Workflow
The agent must strictly follow the **Question-Answer-Record** sequence as defined in `@.claude/rules/interview_rule.md`.

### Step 1: Code Provisioning
1.  **User Action:** The user provides the full source code of the target.
2.  **Agent Action (Acknowledge):** "감사합니다. 코드 분석을 시작하겠습니다. 잠시만 기다려주세요."

### Step 2: High-Level Analysis (Core Logic)
1.  **Agent Action (Question):** "분석이 완료되었습니다. 제가 파악한 이 코드의 **핵심 책임(Core Responsibility)**은 '...'인 것 같습니다. 그리고 다음과 같은 **비즈니스 로직**이 포함된 것으로 보입니다: [...]. 제가 이해한 내용이 맞습니까? 아니라면 어떻게 수정되어야 할까요?"
2.  **User Action:** Confirms or corrects the agent's analysis.
3.  **Agent Action (Record & Confirm):** (Records the answer to the interview document) "네, 핵심 책임과 비즈니스 로직에 대해 기록했습니다. 다음으로 넘어가겠습니다."

### Step 3: Input Analysis (Parameters & Boundaries)
1.  **Agent Action (Question):** "입력 파라미터에 대해 분석했습니다. 다음 내용이 맞는지 확인해주십시오."
    - **`parameter_name_1`**:
        - **추정 타입 및 형식**: `int`, `0 이상의 정수`
        - **주요 경계값**: `0`, `1`, `MAX_INT`
        - **예상 예외 발생 케이스**: `음수`, `None`
    - **`parameter_name_2`**: (Repeat for all parameters)
    "혹시 제가 놓치거나 잘못 분석한 부분이 있다면 알려주세요."
2.  **User Action:** Confirms or corrects the analysis.
3.  **Agent Action (Record & Confirm):** (Records the answer) "입력값 명세에 대해 기록했습니다."

### Step 4: Output Analysis (Return Values & Exceptions)
1.  **Agent Action (Question):** "반환값과 예외 상황을 점검하겠습니다. 제가 분석한 내용은 다음과 같습니다."
    - **현재 처리 중인 예외**: "코드 상에서 `...` 조건일 때 `ValueError`를 발생시키는 것을 확인했습니다."
    - **추가 검토가 필요한 예외**: "하지만 입력값 분석에 따르면 `param1`에 유효하지 않은 타입(e.g., `str`)이 들어올 경우 `TypeError`가 발생할 수 있는데, 이에 대한 명시적인 처리가 보이지 않습니다. **이것이 의도된 설계(예: 상위에서 처리)인지, 혹은 저희가 테스트 시나리오에 추가해야 할 누락된 케이스인지** 확인해주실 수 있나요?"
2.  **User Action:** Confirms the analysis and clarifies the intent behind missing error handling.
3.  **Agent Action (Record & Confirm):** (Records the answer) "네, 의도된 동작과 추가할 예외 시나리오에 대해 명확히 기록했습니다."

### Step 5: State and Side-Effect Analysis
1.  **Agent Action (Question):** "함수 실행 전후의 상태 변화와 부수 효과(Side Effects)에 대해 확인하겠습니다. 제가 파악한 내용은 다음과 같습니다."
    - **사전 조건(Pre-conditions)**: `...` (e.g., "실행 전 `self.state`는 `ready` 상태여야 함")
    - **사후 조건(Post-conditions)**: `...` (e.g., "실행 후 `self.state`는 `done`으로 변경됨")
    - **부수 효과(Side Effects)**: `...` (e.g., "`database.save()` 메서드를 호출하여 외부 DB에 기록함")
    "이 내용이 맞는지, 혹은 추가/수정할 부분이 있는지 알려주세요."
2.  **User Action:** Confirms or corrects the analysis.
3.  **Agent Action (Record & Confirm):** (Records the answer) "상태 변화와 부수 효과에 대해 기록했습니다."

### Step 6: Mocking Target Confirmation
1.  **Agent Action (Question):** "앞서 확인된 부수 효과인 **`...`**[e.g., `database.save()`]는 테스트의 독립성을 위해 **모킹(Mocking) 대상**으로 지정하는 것이 좋습니다. 이 대상을 모킹하는 것에 동의하십니까? 다른 모킹 대상이 있다면 함께 알려주세요."
2.  **User Action:** Confirms, denies, or suggests other mocking targets.
3.  **Agent Action (Record & Confirm):** (Records the answer) "모킹 대상에 대해 기록했습니다. 이제 마지막 단계입니다."

### Step 7: Assumptions and Invariants
1.  **Agent Action (Question):** "마지막으로, 이 유닛 테스트에서 검증하지 않고 참이라고 **가정(Assumptions)**할 조건과, 실행 전후에 변하지 않아야 할 **불변 조건(Invariants)**을 정의하겠습니다. 제가 추측한 가정은 'OS, Python 내장 라이브러리는 정상 동작한다' 등이고, 불변 조건은 '입력된 객체의 ID는 변경되지 않는다' 등입니다. 추가하거나 수정할 내용이 있을까요?"
2.  **User Action:** Confirms or provides additional details.
3.  **Agent Action (Record & Confirm):** (Records the answer) "가정과 불변 조건까지 모두 기록했습니다. 감사합니다."

### Step 8: Validation Conditions Summary & User Confirmation
1.  **Agent Action:** "이제 앞서 수집한 검증해야 할 모든 조건들을 정리해서 확인받겠습니다. 다음 조건들이 우리가 테스트로 검증해야 할 모든 요소입니다:"
    - **입력 검증 조건**: [앞서 분석한 파라미터별 경계값, 예외 케이스들]
    - **출력 검증 조건**: [반환값, 예외 상황들]
    - **상태 변화 검증 조건**: [사전/사후 조건, 부수 효과들]
    - **불변 조건**: [변하지 않아야 할 요소들]
    "이 조건들이 모두 포함되었는지, 누락된 검증 조건이 있는지 확인해주세요."
2.  **User Action:** Confirms the validation conditions are complete or suggests additions.
3.  **Agent Action (Record & Confirm):** (Records the final validation conditions) "검증 조건 목록이 확정되었습니다. 이제 시나리오를 생성하겠습니다."

### Step 9: Scenario Synthesis & Final Output
1.  **Agent Action:** "모든 분석이 완료되었습니다. 지금까지의 인터뷰 내용을 바탕으로 `<target_code_identifier>`에 대한 최종 유닛 테스트 검증 시나리오를 정리하여 보여드리겠습니다."
    (The agent then generates the final output based on the recorded interview answers.)

---

### **[Final Output] Unit Test Specification for `<target_code_identifier>`**

#### 1. Core Function
- **Responsibility**: [Summary of core function from user input]
- **Business Logic**: [Summary of business logic from user input]

#### 2. Function Signature
```python
def function_name(param1: type, param2: type) -> return_type:
    ...
```

#### 3. Pre-conditions & Assumptions
- **Pre-conditions**:
    - [List of pre-conditions]
- **Assumptions (Not tested in unit tests)**:
    - [List of assumptions]

#### 4. Post-conditions & Invariants
- **Post-conditions**:
    - On Success: [Expected state/return value on success]
    - On Failure: [Expected exceptions/state on failure]
- **Invariants**:
    - [List of invariants]

#### 5. Mocking Targets
- **Dependencies to Mock**:
    - [List of external dependencies identified for mocking]

#### 6. Test Scenarios (Given-When-Then)

**A. Success Scenarios**
- **Test 1.1**: [Scenario Name] *(검증 조건: [해당하는 검증 조건들])*
    - **Given**: [Context and inputs]
    - **When**: [Action is performed]
    - **Then**: [Expected outcome and state changes]
- **Test 1.2**: ... *(검증 조건: [해당하는 검증 조건들])*

**B. Failure & Edge Case Scenarios**
- **Test 2.1**: [Scenario Name for invalid input] *(검증 조건: [해당하는 검증 조건들])*
    - **Given**: [Invalid context or inputs]
    - **When**: [Action is performed]
    - **Then**: [Expected exception (e.g., `pytest.raises(ValueError)`) is thrown]
- **Test 2.2**: [Scenario Name for boundary condition] *(검증 조건: [해당하는 검증 조건들])*
    - **Given**: [Boundary value inputs]
    - **When**: [Action is performed]
    - **Then**: [Expected outcome at the boundary]

#### 7. Validation Coverage Verification
**검증 조건 커버리지 매트릭스**:
- [검증 조건 1]: Test 1.1, Test 2.1에서 검증됨
- [검증 조건 2]: Test 1.2에서 검증됨
- [검증 조건 3]: Test 2.2에서 검증됨
- ...

**최종 검증**: 위 시나리오들이 성공하면 Step 8에서 정리한 모든 검증 조건이 커버됩니다.

#### 8. Final User Validation
"위에서 제시한 시나리오들과 검증 조건 커버리지를 검토해보시고, 추가하거나 수정할 시나리오가 있는지 알려주세요. 모든 시나리오가 통과했을 때 우리가 원하는 검증이 완료된다고 보시나요?"

---



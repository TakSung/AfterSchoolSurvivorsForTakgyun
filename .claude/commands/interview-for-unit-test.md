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

"안녕하세요. 저는 유닛 테스트 설계 전문가입니다. 지금부터 `<target_code_identifier>`에 대한 유닛 테스트 시나리오 설계를 시작하겠습니다. 코드의 견고성과 신뢰성을 보장하기 위해 몇 가지 질문을 통해 심층적으로 분석하겠습니다. 먼저 대상 코드의 전체 내용을 보여주시겠어요?"

## 4. Interactive Interview Workflow

### Step 1: Code Provisioning
1.  **User Action:** The user provides the full source code of the target function, method, or class.
2.  **Agent Action:** The agent receives the code and confirms its understanding.
    - "감사합니다. 코드 분석을 시작하겠습니다. 잠시만 기다려주세요."

### Step 2: High-Level Analysis (Specification & Requirement)
The agent analyzes the code and asks clarifying questions to define its core responsibility.

- **Question 1 (Core Function):** "이 코드의 **핵심 책임(Core Responsibility)**을 한 문장으로 정의한다면 무엇일까요? 예를 들어, '플레이어의 경험치를 레벨로 변환한다'와 같이 설명해주십시오."
- **Question 2 (Business Logic):** "이 코드에 담긴 특별한 **비즈니스 규칙이나 게임 로직**이 있나요? 예를 들어, '레벨업 시 남은 경험치는 이월된다' 또는 '특정 아이템이 있으면 보너스 경험치를 받는다'와 같은 규칙입니다."

### Step 3: Interface and Data Analysis (Input/Output)
The agent dissects the function's signature and return paths.

- **Question 3 (Input Analysis):** "입력값에 대해 자세히 분석해 보겠습니다. 각 파라미터에 대해 다음 정보를 알려주세요."
    - **`parameter_name_1`**:
        - **유효한 값의 범위나 형식**: (e.g., "0 이상의 정수", "비어있지 않은 문자열", "PositionComponent 객체")
        - **특별히 처리해야 할 경계값**: (e.g., "0, 1, 최대값", "None", "빈 리스트/객체")
        - **유효하지 않은 값의 예시**: (e.g., "음수", "잘못된 타입의 객체")
    - **`parameter_name_2`**: (Repeat for all parameters)

- **Question 4 (Output Analysis):** "이제 반환값과 예외 상황을 정의해 보겠습니다."
    - **성공 시 반환값**: "정상적으로 실행되었을 때 반환되는 값의 타입과 구조는 무엇인가요?"
    - **실패/예외 조건**: "어떤 상황에서, 어떤 종류의 `Exception`이 발생해야 하나요? (e.g., `ValueError`, `TypeError`, `CustomException`)"

### Step 4: State and Side-Effect Analysis
The agent investigates the context required for the function to run and the effects it has.

- **Question 5 (Pre-conditions):** "이 함수가 **실행되기 전, 반드시 만족되어야 하는 시스템의 상태나 조건(Pre-conditions)**이 있습니까? (e.g., '데이터베이스 연결이 활성화되어야 함', '플레이어 엔티티가 특정 컴포넌트를 가지고 있어야 함')"

- **Question 6 (Post-conditions):** "함수 실행이 **완료된 후, 반드시 보장되어야 하는 결과(Post-conditions)**는 무엇인가요?"
    - **객체 상태 변화**: "입력으로 받은 객체나, 함수가 속한 클래스의 내부 속성(attribute) 중 변경되는 것이 있나요?"
    - **외부 시스템 변화 (Side Effects)**: "파일 시스템, 데이터베이스, 외부 API 호출 등 테스트 환경 외부의 상태를 변경하는 부분이 있나요? 있다면 어떤 변화인가요? (이 부분은 Mock 처리 대상이 됩니다.)"

- **Question 7 (Assumptions & Invariants):** "마지막으로, 우리가 제어하거나 테스트하지 않을 가정을 정의해 보겠습니다."
    - **가정 (Assumptions)**: "이 기능이 동작한다고 믿고 진행하는, **유닛 테스트 범위 밖의 전제조건**이 있나요? (e.g., 'Pygame 라이브러리는 정상 동작한다', 'OS는 안정적이다')"
    - **불변 조건 (Invariants)**: "함수 실행 전후에 **절대 변하지 않아야 하는** 값이나 상태가 있나요? (e.g., '입력된 엔티티의 ID는 절대 바뀌지 않는다')"

### Step 5: Scenario Synthesis & Final Output
Based on the answers, the agent synthesizes and presents a structured list of test scenarios.

**Agent Action:**
"모든 분석이 완료되었습니다. `<target_code_identifier>`에 대한 유닛 테스트 검증 시나리오를 다음과 같이 정리했습니다. 이 시나리오를 기반으로 `/write-unit-test` 명령을 사용하여 테스트 코드를 생성할 수 있습니다."

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
- **Test 1.1**: [Scenario Name]
    - **Given**: [Context and inputs]
    - **When**: [Action is performed]
    - **Then**: [Expected outcome and state changes]
- **Test 1.2**: ...

**B. Failure & Edge Case Scenarios**
- **Test 2.1**: [Scenario Name for invalid input]
    - **Given**: [Invalid context or inputs]
    - **When**: [Action is performed]
    - **Then**: [Expected exception (e.g., `pytest.raises(ValueError)`) is thrown]
- **Test 2.2**: [Scenario Name for boundary condition]
    - **Given**: [Boundary value inputs]
    - **When**: [Action is performed]
    - **Then**: [Expected outcome at the boundary]

---

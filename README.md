# AfterSchoolSurvivors

---

## 개발 환경 설정 (Development Environment Setup)

이 프로젝트를 개발하기 위한 환경을 설정하는 방법입니다. Anaconda와 `uv`를 사용하여 빠르고 일관된 환경을 구성합니다.

### 1. Anaconda 가상환경 생성

먼저, `python=3.13` 버전으로 `as-game`이라는 이름의 새로운 Anaconda 가상환경을 생성합니다.

```bash
conda create -n as-game python=3.13
```

### 2. 가상환경 활성화 및 `uv` 설치

생성한 `as-game` 환경을 활성화합니다. 이 환경 내에서 모든 개발 작업이 이루어집니다.

```bash
conda activate as-game
```

환경이 활성화되면, 초고속 파이썬 패키지 설치 도구인 `uv`를 설치합니다. `uv`는 `pip`을 대체하여 훨씬 빠른 속도를 제공합니다.

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```
*참고: `uv`는 시스템에 한 번만 설치하면 됩니다. 이미 설치되어 있다면 이 단계를 건너뛸 수 있습니다.*

### 3. 프로젝트 의존성 설치

마지막으로, `uv`를 사용하여 프로젝트에 필요한 모든 라이브러리를 `requirements.txt` 파일로부터 설치합니다.

```bash
uv pip install -r requirements.txt
```

이 명령어를 실행하면 `pygame`, `numpy` 등 게임 개발에 필요한 모든 라이브러리가 활성화된 `as-game` 환경에 자동으로 설치됩니다.

---

이제 개발 환경 설정이 완료되었습니다. 코드를 실행하거나 테스트를 진행할 수 있습니다.


# Taskmater ai

## 시작 세팅

### 첫 세팅
```bash
task-master init
# 이후 설정을 해준다.
# 설정 이후 PRD 문서를 준비한다.
task-master parse-prd docs/PRD.md
```

### 명령어 목록
```bash
# 파싱한 테스크 목록확인
task-master list

# 테스크 목록 복잡도 분석
task-master analyze-complexity

# 복잡도 분석 레포트
task-master complexity-report 

# 서브 테스크로 분리
task-master expand --all

# 분리된 테스트 확인
task-master list --with-subtasks
```

### 테스크 수정 방법

명령어 형식:
```bash
task-master update-subtask --id=<서브태스크_ID> --prompt="<변경할 내용>"
```

설명:
* --id: 변경하고 싶은 서브태스크의 ID를 지정합니다. (예: 1.1, 2.3.1)
* --prompt: 서브태스크에 추가하거나 변경하고 싶은 구체적인 내용을 문자열로 전달합니다.

명령어 모음
```bash
task-master update-subtask --id=<서브태스크_ID> --prompt="<변경할 내용>" # 서브태스크를 변경
task-master remove-subtask --id=<서브태스크_ID> # 서브태스크 삭제
task-master add-subtask --parent=<부모태스크_ID> --prompt="<새로운 내용>" # 새로운 서브태스크 추가
```

서브 도메인 분할 예시 (feat 유닛테스트 추가):
```bash
task-master update-subtask --id=1.7 --prompt="1.1로 순서를 옮겨줘. 설계문서는 모든 작업 이전에 가장 먼저할 일이야. ECS 프레임워크 기반 구조를 디자인하고, 머메이드를 사용해서 시각적으로 구조를 표현해줘. 코드는 삽입할 필요 없고 설명을 위해 필요하다면 간략화한 수도코드 정도로만 표현해줘"
task-master add-subtask --parent=1 --prompt="docs/design.md 문서를 작성해줘. ECS 프레임워크 기반 구조를 디자인하고, 머메이드를 사용해서 시각적으로 구조를 표현해줘. 코드는 삽입할 필요 없고 설명을 위해 필요하다면 간략화한 수도코드 정도로만 표현해줘." # 새로운 서브태스크 추가
```

유닛테스트 구현을 위한 인터뷰를 진행하고(@.claude/commands/interview-for-unit-test.md), 인터뷰에서 추출한 테스트 시나리오를 바탕으로 테스트 케이스를 작성합니다. 마지막으로 앞서 작성한 기능이 정상적으로 작동하는지 테스트 하며 테스트가 통과할 때까지 반복합니다. 단 같은 오류가 3번 이상 반복되면, 잠시 멈추고 사용자와 소통하며 오류를 고쳐 나가세요.
---

## 코딩 스타일 및 Linter 설정 (Coding Style & Linter Setup)

이 프로젝트는 코드의 일관성과 품질을 유지하기 위해 **Ruff**를 Linter 및 Formatter로 사용합니다. 모든 코드는 `pyproject.toml` 파일에 정의된 규칙에 따라 검사되고 포맷팅됩니다.

### 1. Ruff란?

Ruff는 Rust로 작성된 매우 빠른 Python Linter 및 Formatter입니다. `Flake8`, `isort`, `Black` 등 여러 도구의 기능을 하나로 합쳐 개발 생산성을 높여줍니다.

### 2. CLI (명령줄 인터페이스) 사용법

프로젝트의 모든 코드에 대해 Linter를 실행하고 자동으로 수정하려면 다음 명령어를 사용하세요.

```bash
# 코드 스타일 및 오류 검사
ruff check .

# 자동으로 수정 가능한 문제 해결
ruff check . --fix

# 코드 포맷팅 (서식 맞추기)
ruff format .
```

### 3. VSCode / Cursor 편집기 설정

VSCode 또는 Cursor에서 실시간으로 코드 검사 및 자동 포맷팅을 설정하면 개발 효율이 크게 향상됩니다.

1.  **Ruff 확장 프로그램 설치**:
    *   편집기의 확장 프로그램 마켓플레이스에서 `Ruff` (게시자: `charliermarsh`)를 검색하여 설치합니다.

2.  **`settings.json` 파일 설정**:
    *   `Cmd + Shift + P` (또는 `Ctrl + Shift + P`)를 눌러 `Preferences: Open User Settings (JSON)`을 엽니다.
    *   아래 설정을 추가하면, Python 파일을 저장할 때마다 Ruff가 자동으로 코드 포맷팅 및 수정을 수행합니다.

    ```json
    {
        "[python]": {
            "editor.defaultFormatter": "charliermarsh.ruff",
            "editor.formatOnSave": true,
            "editor.codeActionsOnSave": {
                "source.fixAll": "explicit"
            }
        }
    }
    ```

이 설정을 통해 모든 팀원이 동일한 코드 스타일을 유지하며, 잠재적인 오류를 조기에 발견할 수 있습니다. 프로젝트의 상세한 Linter 및 Formatter 규칙은 `pyproject.toml` 파일에 정의되어 있습니다.
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
task-master add-subtask --parent-id=<부모태스크_ID> --prompt="<새로운 내용>" # 새로운 서브태스크 추가
```

task-master update-subtask --id=1.6 --prompt="1.1 이후로 순서를 옮겨줘. uv 툴을.@docs/game-dependency.md 를 참고하여 종속성을 세팅해줘."
# AfterSchoolSurvivors



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